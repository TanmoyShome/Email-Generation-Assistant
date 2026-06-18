import json
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from app.api.dependencies import EmailGenerationService, get_email_generation_service
from app.config.settings import settings


class GenerateEmailEvaluationService:
    def __init__(self):
        self.eval_dir = Path(settings.EVAL_OUTPUT_DIR)
        self.report_dir = Path(settings.EVAL_REPORT_DIR)
        
    def safe_eval_output_path(self, filename: str) -> Path:
        input_name = Path(filename).stem or "uploaded_evaluation"
        safe_name = "".join(
            character if character.isalnum() or character in {"-", "_"} else "_"
            for character in input_name
        )
        return self.eval_dir / f"{safe_name}_eval.json"


    def safe_report_output_path(self, filename: str) -> Path:
        input_name = Path(filename).stem or "uploaded_evaluation"
        safe_name = "".join(
            character if character.isalnum() or character in {"-", "_"} else "_"
            for character in input_name
        )
        return self.report_dir / f"{safe_name}_report.json"


    def parse_results(self, data) -> list[dict]:
        results = data.get("results") if isinstance(data, dict) else data
        if not isinstance(results, list) or not results:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Uploaded JSON must contain a non-empty results list.",
            )
        if not all(isinstance(item, dict) for item in results):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Each result must be a JSON object.",
            )
        return results


    def metric_logic(self) -> dict[str, dict[str, str]]:
        return {
            "fact_recall": {
                "definition": "Measures how many required key facts are present in the generated email.",
                "logic": (
                    "For each required fact, tokenize the fact and email, then count the fact as recalled "
                    "when at least 55% of fact tokens and at least 50% of important tokens "
                    "(numbers or words longer than four characters) appear in the email. "
                    "The final score is matched facts divided by total facts."
                ),
            },
            "tone_accuracy": {
                "definition": "Checks whether wording matches the requested email tone.",
                "logic": (
                    "Map requested tone words such as formal, urgent, empathetic, proactive, warm, "
                    "and concise to curated marker words. Score the strongest requested tone match "
                    "as 0.45 plus the fraction of marker words found in the email, capped at 1.0. "
                    "Unknown tones receive a neutral baseline of 0.75."
                ),
            },
            "conciseness_fluency": {
                "definition": "Scores concise length, readable sentence flow, and basic email fluency.",
                "logic": (
                    "Check seven email-quality signals: total length between 45 and 220 words, "
                    "average sentence length between 8 and 28 words, subject line, greeting, sign-off, "
                    "no excessive whitespace, and a clean ending or multi-line email structure. "
                    "The score is passed checks divided by seven."
                ),
            },
        }


    def build_report(self, data: dict) -> dict:
        results = self.parse_results(data)
        metric_names = ["fact_recall", "tone_accuracy", "conciseness_fluency"]
        raw_scores = []

        for index, item in enumerate(results, start=1):
            metrics = item.get("metrics")
            if not isinstance(metrics, dict):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Each result must include a metrics object.",
                )

            missing_metrics = [name for name in metric_names if name not in metrics]
            if missing_metrics:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Missing metric scores: {', '.join(missing_metrics)}.",
                )

            raw_scores.append(
                {
                    "scenario_id": item.get("id", index),
                    "scores": {
                        name: round(float(metrics[name]), 3)
                        for name in metric_names
                    },
                }
            )

        average_scores = {
            name: round(
                sum(score["scores"][name] for score in raw_scores) / len(raw_scores),
                3,
            )
            for name in metric_names
        }
        average_scores["overall_model_score"] = round(
            sum(average_scores.values()) / len(metric_names),
            3,
        )

        return {
            "custom_metrics": self.metric_logic(),
            "raw_scores": raw_scores,
            "average_scores": average_scores,
            "scenario_count": len(raw_scores),
        }


    def extract_result(self, item: dict) -> tuple[str, list[str], str, str]:
        intent = str(item.get("intent", "")).strip()
        tone = str(item.get("tone", "")).strip()
        email = str(item.get("email", "")).strip()
        raw_facts = item.get("key_facts", item.get("facts", []))

        if isinstance(raw_facts, str):
            raw_facts = raw_facts.splitlines()

        facts = [str(fact).strip() for fact in raw_facts if str(fact).strip()]

        if not intent or not tone or not email or not facts:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Each result must include intent, tone, email, and facts/key_facts.",
            )

        return intent, facts, tone, email
    
evaluation_service = GenerateEmailEvaluationService()