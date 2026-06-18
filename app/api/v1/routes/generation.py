import json
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from app.api.dependencies import EmailGenerationService, get_email_generation_service
from app.config.settings import settings
from app.schemas.generation import EmailGenerationResponse
from app.repository.generation import email_generation

router = APIRouter()
OUTPUT_DIR = Path(settings.FRONTEND_OUTPUT_DIR)


@router.post("/generates", response_model=EmailGenerationResponse)
async def generate_emails_from_file(
    service: Annotated[
        EmailGenerationService,
        Depends(get_email_generation_service),
    ],
    file: UploadFile = File(...),
):
    filename = file.filename or "uploaded_test_case.json"
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

    results = []
    for case in email_generation.parse_cases(data):
        intent, facts, tone = email_generation.extract_case(case)
        generated = service.generate_email(intent, facts, tone)
        results.append(
            {
                "id": case.get("id"),
                "intent": intent,
                "key_facts": facts,
                "tone": tone,
                "email": generated["email"],
            }
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = email_generation.safe_output_path(filename)
    email_response = {"results": results}
    output_path.write_text(json.dumps(email_response, indent=2), encoding="utf-8")
    return email_response














