import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

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
    docs_url="/api/docs",    # <--- A DOCUMENTAÇÃO OFICIAL AGORA MORA AQUI
    redoc_url="/api/redoc",
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


# ── Redirecionamento "Salva-Vidas" do Link Antigo ────────────────────────────
@app.get("/docs", include_in_schema=False)
def redirect_old_docs():
    """
    Quem clicar no link antigo '/docs' será jogado direto para o Frontend na raiz '/'
    """
    return RedirectResponse(url="/")


# ── Rota do Frontend (A Pintura do Carro) ────────────────────────────────────
# Pega o caminho absoluto da pasta do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Define os dois lugares possíveis onde o front pode estar:
# 1. 'static' -> Usado pela Azure após o GitHub Actions rodar
# 2. 'frontend/dist' -> Usado por você no seu computador (ambiente local)
static_azure_path = BASE_DIR / "static"
local_dist_path = BASE_DIR / "frontend" / "dist"

# Descobre qual pasta está existindo no momento
if static_azure_path.is_dir():
    frontend_path = static_azure_path
elif local_dist_path.is_dir():
    frontend_path = local_dist_path
else:
    frontend_path = None

if frontend_path:
    print(f"✅ Frontend encontrado em: {frontend_path}")

    # Serve os arquivos CSS e JS compilados
    app.mount("/assets", StaticFiles(directory=str(frontend_path / "assets")), name="assets")


    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Ignora rotas do backend
        if full_path.startswith("api/") or full_path.startswith("health/") or \
                full_path.startswith("openapi.json"):
            return

            # Se for um arquivo (ex: favicon.ico, logo.png)
        file_path = frontend_path / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))

        # Fallback padrão: Devolve o React (Dashboard)
        return FileResponse(str(frontend_path / "index.html"))
else:
    print("⚠️ ALERTA: Nenhuma pasta de frontend encontrada. Redirecionando para API.")


    @app.get("/")
    def read_root():
        return RedirectResponse(url="/api/docs")