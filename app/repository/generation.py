"""
Generation result handling for email generation.
"""

from pathlib import Path
from fastapi import Depends, File, HTTPException, status
from app.config.settings import settings

class GenerationResult:
    def __init__(self):
        self.output_dir = Path(settings.FRONTEND_OUTPUT_DIR)

    def safe_output_path(self, filename: str) -> Path:
        input_name = Path(filename).stem or "uploaded_test_case"
        safe_name = "".join(
            character if character.isalnum() or character in {"-", "_"} else "_"
            for character in input_name
        )   
        return self.output_dir / f"{safe_name}_output.json"


    def parse_cases(self, data) -> list[dict]:
        cases = data if isinstance(data, list) else [data]
        if not cases or not all(isinstance(case, dict) for case in cases):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Uploaded JSON must be an object or a list of objects.",
            )
        return cases


    def extract_case(self, case: dict) -> tuple[str, list[str], str]:
        intent = str(case.get("intent", "")).strip()
        tone = str(case.get("tone", "")).strip()
        raw_facts = case.get("key_facts", case.get("facts", []))
        if isinstance(raw_facts, str):
            raw_facts = raw_facts.splitlines()
        facts = [str(fact).strip() for fact in raw_facts if str(fact).strip()]


        if not intent or not tone or not facts:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Each case must include intent, tone, and facts/key_facts.",
            )
        return intent, facts, tone
    
email_generation = GenerationResult()

