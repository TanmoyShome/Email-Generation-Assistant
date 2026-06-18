import json
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from app.api.dependencies import EmailGenerationService, get_email_generation_service
from app.config.settings import settings
from app.repository.evaluation import evaluation_service
from app.schemas.evaluation import (
    EvaluationReportResponse,
    FileEvaluationResponse,
)
router = APIRouter()
EVAL_OUTPUT_DIR = Path(settings.EVAL_OUTPUT_DIR)
EVAL_REPORT_DIR = Path(settings.EVAL_REPORT_DIR)

@router.post("/evaluations", response_model=FileEvaluationResponse)
async def evaluate_emails_from_file(
    service: Annotated[
        EmailGenerationService,
        Depends(get_email_generation_service),
    ],
    file: UploadFile = File(...),
):
    filename = file.filename or "uploaded_output.json"
    if not filename.lower().endswith(".json"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only JSON files are supported.",
        )

    try:
        data = json.loads((await file.read()).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file must contain valid JSON.",
        ) from exc

    evaluated_results = []
    metric_definitions = {}

    for item in evaluation_service.parse_results(data):
        intent, facts, tone, email = evaluation_service.extract_result(item)
        evaluation = service.evaluate_email(email, intent, facts, tone)
        metric_definitions = evaluation["metric_definitions"]
        evaluated_results.append(
            {
                "id": item.get("id"),
                "intent": intent,
                "key_facts": facts,
                "tone": tone,
                "email": email,
                "metrics": evaluation["metrics"],
            }
        )

    EVAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = evaluation_service.safe_eval_output_path(filename)
    payload = {
        "results": evaluated_results,
        "metric_definitions": metric_definitions,
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


@router.post("/evaluates-report", response_model=EvaluationReportResponse)
async def evaluate_report_from_file(
    service: Annotated[
        EmailGenerationService,
        Depends(get_email_generation_service),
    ],
    file: UploadFile = File(...),
):
    filename = file.filename or "uploaded_evaluation.json"
    if not filename.lower().endswith(".json"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only JSON files are supported for report generation.",
        )

    try:
        data = json.loads((await file.read()).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file must contain valid JSON.",
        ) from exc

    report = evaluation_service.build_report(data)

    EVAL_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = evaluation_service.safe_report_output_path(filename)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return report
