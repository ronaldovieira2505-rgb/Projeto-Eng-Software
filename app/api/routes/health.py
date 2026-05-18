from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/")
async def health():
    return {"status": "ok", "service": settings.SERVICE_NAME}

@router.get("/ready")
async def ready():
    is_ready = bool(settings.GEMINI_API_KEY or settings.ANTHROPIC_API_KEY)
    return {
        "status": "ok",
        "ready": is_ready
    }