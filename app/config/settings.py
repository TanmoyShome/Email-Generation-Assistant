from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings."""

    PROJECT_NAME: str
    VERSION: str
    API_V1_STR: str
    OPENAI_API_KEY: Optional[str]
    GEMINI_API_KEY: Optional[str]
    DEFAULT_MODEL: str
    JUDGE_MODEL: str
    SCENARIOS_PATH: str
    PROMPT_TEMPLATES_DIR: str
    OUTPUT_DIR: str
    FRONTEND_BASE_URL: str
    FRONTEND_OUTPUT_DIR: str
    EVAL_OUTPUT_DIR: str
    EVAL_REPORT_DIR: str

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
    }


settings = Settings()

ALLOWED_ORIGINS = ["*"]
