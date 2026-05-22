from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.routes import presentations, health
from app.core.config import settings
from app.api.routes import github


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 Presentation Service starting — env: {settings.ENVIRONMENT}")
    yield
    print("🛑 Presentation Service shutting down")



app = FastAPI(
    title="Presentation Service",
    description="Microsserviço de geração de apresentações com IA",
    version="1.0.0",
    lifespan=lifespan,
)

from fastapi.responses import RedirectResponse

@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(presentations.router, prefix="/api/v1/presentations", tags=["presentations"])
app.include_router(github.router, prefix="/api/v1/github", tags=["github"])  # registro
