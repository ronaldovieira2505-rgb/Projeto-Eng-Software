from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    SERVICE_NAME: str = "presentation-service"

    LLM_PROVIDER: str = "anthropic"
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "claude-sonnet-4-20250514"
    LLM_MAX_TOKENS: int = 4096

    GITHUB_TOKEN: str = ""
    GEMINI_API_KEY: str | None = None

    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_PATH: str = "/tmp/presentations"
    S3_BUCKET: str = ""

    ALLOWED_ORIGINS: List[str] = ["*"]

    INGEST_SERVICE_URL: str = "http://ingest-service:8001"
    AUTH_SERVICE_URL: str = "http://auth-service:8002"

    model_config = ConfigDict(  # <- substituir o class Config
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
