from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.routes import presentations, health, github
from app.core.config import settings
from app.core.logging_config import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    print(f"🚀 {settings.SERVICE_NAME} starting — env={settings.ENVIRONMENT} provider={settings.LLM_PROVIDER}")
    yield
    print(f"🛑 {settings.SERVICE_NAME} shutting down")


app = FastAPI(
    title="Presentation Service",
    description=(
        "Microsserviço de geração de apresentações com IA. "
        "Parte da Plataforma de Documentação Inteligente — Mackenzie 2026-1."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router,         prefix="/health",                   tags=["health"])
app.include_router(presentations.router,  prefix="/api/v1/presentations",     tags=["presentations"])
app.include_router(github.router,         prefix="/api/v1/github",            tags=["github"])
