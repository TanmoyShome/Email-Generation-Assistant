"""
Pydantic schemas for email generation.
"""
from pydantic import BaseModel

class GeneratedEmailItem(BaseModel):
    id: int | str | None = None
    intent: str
    key_facts: list[str]
    tone: str
    email: str

class EmailGenerationResponse(BaseModel):
    results: list[GeneratedEmailItem]

