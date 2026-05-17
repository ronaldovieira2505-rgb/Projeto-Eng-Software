"""
Testes unitários — sem dependência de LLM nem GitHub.
Cobrem o fluxo principal do microsserviço.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.schemas.presentation import SlideContent

client = TestClient(app)

MOCK_SLIDES = [
    SlideContent(title="Sprint Review", bullets=["Entrega A", "Entrega B"]),
    SlideContent(title="Próximos Passos", bullets=["Tarefa 1", "Tarefa 2"]),
]

def test_health():
    resp = client.get("/health/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@patch("app.api.routes.presentations.llm_service.generate_slides_from_text")
@patch("app.api.routes.presentations.pptx_service.export_to_pptx")
def test_generate_from_text(mock_export, mock_llm):
    # Simula o retorno da IA e do gerador de PPTX
    mock_llm.return_value = ("Sprint 42 Review", MOCK_SLIDES)
    mock_export.return_value = ("caminho/fake.pptx", "arquivo_fake.pptx")

    payload = {
        "content": "Entregamos autenticação JWT e refatoramos o módulo de usuários.",
        "presentation_type": "sprint_review",
        "tone": "formal",
        "num_slides": 5,
    }
    # Batendo na URL correta
    resp = client.post("/api/v1/presentations/generate/text", json=payload)

    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Sprint 42 Review"
    assert "download_url" in data
    assert "share_url" in data
    mock_llm.assert_called_once()


@patch("app.api.routes.presentations.fetch_commits", new_callable=AsyncMock)
@patch("app.api.routes.presentations.llm_service.generate_slides_from_text")
@patch("app.api.routes.presentations.pptx_service.export_to_pptx")
def test_generate_from_commits(mock_export, mock_llm, mock_fetch):
    # Simula o retorno do GitHub, da IA e do PPTX
    mock_fetch.return_value = ["feat: add JWT auth", "fix: bug"]
    mock_llm.return_value = ("Resumo Commits", MOCK_SLIDES)
    mock_export.return_value = ("caminho/fake.pptx", "arquivo_fake.pptx")

    payload = {
        "repo": "my-project",
        "branch": "main",
        "tone": "formal",
        "presentation_type": "sprint_review",
        "num_commits": 10
    }
    resp = client.post("/api/v1/presentations/generate/commits", json=payload)

    assert resp.status_code == 200
    assert "presentation_id" in resp.json()


def test_generate_from_commits_validation_error():
    # Testa se a API bloqueia requisições sem os campos obrigatórios (ex: repo)
    payload = {
        "branch": "main",
    }
    resp = client.post("/api/v1/presentations/generate/commits", json=payload)
    assert resp.status_code == 422  # 422 Unprocessable Entity (Padrão do FastAPI)