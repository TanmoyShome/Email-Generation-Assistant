from functools import lru_cache
from fastapi import HTTPException, status
from openai import OpenAIError
from app.config.settings import settings
from app.src.evaluator import Evaluator
from app.src.llm_client import OpenAIClient
from app.src.prompt_engine import PromptEngine


class EmailGenerationService:
    def __init__(self):
        self.prompt_engine = PromptEngine(settings.PROMPT_TEMPLATES_DIR)
        self.evaluator = Evaluator()

    def generate_email(self, intent: str, facts: list[str], tone: str) -> dict:
        facts = [fact.strip() for fact in facts if fact.strip()]
        if not intent.strip() or not tone.strip() or not facts:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Intent, tone, and at least one key fact are required.",
            )

        if not settings.OPENAI_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OPENAI_API_KEY is required to generate emails.",
            )

        try:
            prompt = self.prompt_engine.build_prompt(intent, facts, tone)
        except FileNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(exc),
            ) from exc

        client = OpenAIClient(
            model=settings.DEFAULT_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.6,
        )
        try:
            email = client.generate(prompt)
        except OpenAIError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"OpenAI request failed: {exc}",
            ) from exc

        return {
            "email": email,
            "prompt_technique": self.prompt_engine.technique_summary(),
        }

    def evaluate_email(self, email: str, intent: str, facts: list[str], tone: str) -> dict:
        context = {"intent": intent, "facts": facts, "tone": tone}
        return {
            "metrics": self.evaluator.evaluate(email, context),
            "metric_definitions": self.evaluator.definitions(),
            "prompt_technique": self.prompt_engine.technique_summary(),
        }


@lru_cache
def get_email_generation_service() -> EmailGenerationService:
    return EmailGenerationService()
