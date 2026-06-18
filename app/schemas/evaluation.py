
from pydantic import BaseModel, Field

class EmailEvaluationRequest(BaseModel):
    email: str = Field(..., min_length=10)
    intent: str = Field(..., min_length=3)
    key_facts: list[str] = Field(..., min_length=1)
    tone: str = Field(..., min_length=3)


class EmailEvaluationResponse(BaseModel):
    metrics: dict[str, float]
    metric_definitions: dict[str, str]
    prompt_technique: str


class EvaluationItem(BaseModel):
    id: int | str | None = None
    intent: str
    key_facts: list[str]
    tone: str
    email: str
    metrics: dict[str, float]


class FileEvaluationResponse(BaseModel):
    results: list[EvaluationItem]
    metric_definitions: dict[str, str]


class EvaluationReportResponse(BaseModel):
    custom_metrics: dict[str, dict[str, str]]
    raw_scores: list[dict]
    average_scores: dict[str, float]
    scenario_count: int