import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles

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

# ── Rotas da API (O Motor) ───────────────────────────────────────────────────
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(presentations.router, prefix="/api/v1/presentations", tags=["presentations"])
app.include_router(github.router, prefix="/api/v1/github", tags=["github"])

# ── Rota do Frontend (A Pintura do Carro) ────────────────────────────────────
# Verifica se a pasta 'static' foi criada pelo processo de build do React
if os.path.isdir("static"):
    # Serve os arquivos CSS e JS compilados
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")


    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Ignora as rotas que pertencem à API ou ao Swagger
        if full_path.startswith("api/") or full_path.startswith("health/") or full_path.startswith(
                "docs") or full_path.startswith("openapi.json"):
            pass

            # Se for um arquivo específico na raiz (ex: favicon.ico)
        file_path = os.path.join("static", full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)

        # Fallback padrão: Devolve a tela principal do React
        return FileResponse("static/index.html")
else:
    # Se estiver rodando localmente sem compilar o front, joga pro Swagger
    @app.get("/")
    def read_root():
        return RedirectResponse(url="/docs")