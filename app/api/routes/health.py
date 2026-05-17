from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/")
async def health():
    return {"status": "ok", "service": settings.SERVICE_NAME}

@router.get("/ready")
async def ready():
    return {
        "ready": bool(settings.ANTHROPIC_API_KEY or settings.OPENAI_API_KEY),
        "checks": {"llm_key_configured": bool(settings.ANTHROPIC_API_KEY or settings.OPENAI_API_KEY)}
    }