from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # App
    ENVIRONMENT: str = "development"
    SERVICE_NAME: str = "presentation-service"
    LOG_LEVEL: str = "INFO"

    # LLM — provider principal: "anthropic" ou "google"
    LLM_PROVIDER: str = "google"
    # Fallback automático se o provider principal falhar (deixe vazio para desativar)
    LLM_FALLBACK_PROVIDER: Optional[str] = None
    LLM_MAX_TOKENS: int = 4096

    # Anthropic
    ANTHROPIC_API_KEY: str = ""
    LLM_MODEL: str = "claude-sonnet-4-20250514"

    # Google Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # GitHub
    GITHUB_TOKEN: str = ""

    # Storage
    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_PATH: str = "./outputs"
    S3_BUCKET: str = ""

    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]

    # URLs dos outros microsserviços
    INGEST_SERVICE_URL: str = "http://ingest-service:8001"
    AUTH_SERVICE_URL: str = "http://auth-service:8002"


settings = Settings()
