"""
Testes unitários — Presentation Service.
Sem dependência real de LLM, GitHub ou disco.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from app.main import app
from app.schemas.presentation import SlideContent

client = TestClient(app)

MOCK_SLIDES = [
    SlideContent(title="Sprint Review", bullets=["Entrega A", "Entrega B"]),
    SlideContent(title="Próximos Passos", bullets=["Tarefa 1", "Tarefa 2"]),
]
MOCK_TITLE = "Sprint 42 Review"
MOCK_EXPORT = ("caminho/fake.pptx", "arquivo_fake.pptx")


# ── Health ────────────────────────────────────────────────────────────────────

def test_health():
    resp = client.get("/health/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    assert resp.json()["service"] == "presentation-service"


def test_readiness():
    resp = client.get("/health/ready")
    assert resp.status_code == 200
    assert "ready" in resp.json()


# ── US5 — Summarize ───────────────────────────────────────────────────────────

@patch("app.api.routes.presentations.llm_service.summarize_text")
def test_summarize_text(mock_summarize):
    mock_summarize.return_value = {"bullets": ["Ponto 1", "Ponto 2"], "summary": "Resumo curto."}
    resp = client.post("/api/v1/presentations/summarize", json={
        "text": "Texto longo de entrada.", "max_bullets": 3
    })
    assert resp.status_code == 200
    assert len(resp.json()["bullets"]) == 2
    assert "summary" in resp.json()


@patch("app.api.routes.presentations.llm_service.summarize_text")
def test_summarize_simplified_flag_is_passed(mock_summarize):
    """US7 — garante que simplify_technical=True chega ao serviço."""
    mock_summarize.return_value = {"bullets": ["Ponto simples"], "summary": "Resumo."}
    client.post("/api/v1/presentations/summarize", json={
        "text": "Deploy via Kubernetes.", "simplify_technical": True, "tone": "simplified"
    })
    call_kwargs = mock_summarize.call_args.kwargs
    assert call_kwargs["simplify_technical"] is True


# ── US1 — Generate from text ──────────────────────────────────────────────────

@patch("app.api.routes.presentations.pptx_service.export_to_pptx")
@patch("app.api.routes.presentations.llm_service.generate_slides_from_text")
def test_generate_from_text(mock_llm, mock_pptx):
    mock_llm.return_value = (MOCK_TITLE, MOCK_SLIDES)
    mock_pptx.return_value = MOCK_EXPORT
    resp = client.post("/api/v1/presentations/generate/text", json={
        "content": "Entregamos autenticação JWT.",
        "presentation_type": "sprint_review",
        "tone": "formal",
        "num_slides": 5,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == MOCK_TITLE
    assert len(data["slides"]) == 2
    assert "download_url" in data
    assert "share_url" in data


@patch("app.api.routes.presentations.pptx_service.export_to_pptx")
@patch("app.api.routes.presentations.llm_service.generate_slides_from_text")
def test_generate_persuasive_tone_is_passed(mock_llm, mock_pptx):
    """US6 — garante que o tom chega ao serviço."""
    mock_llm.return_value = (MOCK_TITLE, MOCK_SLIDES)
    mock_pptx.return_value = MOCK_EXPORT
    client.post("/api/v1/presentations/generate/text", json={
        "content": "Melhorias de performance.", "tone": "persuasive"
    })
    assert mock_llm.call_args.kwargs["tone"].value == "persuasive"


@patch("app.api.routes.presentations.pptx_service.export_to_pptx")
@patch("app.api.routes.presentations.llm_service.generate_slides_from_text")
def test_generate_next_steps_type(mock_llm, mock_pptx):
    """US9 — garante que next_steps é aceito como tipo válido."""
    mock_llm.return_value = ("Próximos Passos Q3", MOCK_SLIDES)
    mock_pptx.return_value = MOCK_EXPORT
    resp = client.post("/api/v1/presentations/generate/text", json={
        "content": "Tarefas pendentes: autenticação, testes, deploy.",
        "presentation_type": "next_steps",
    })
    assert resp.status_code == 200
    assert mock_llm.call_args.kwargs["presentation_type"] == "next_steps"


# ── US4 — Generate from commits ───────────────────────────────────────────────

@patch("app.api.routes.presentations.pptx_service.export_to_pptx")
@patch("app.api.routes.presentations.llm_service.generate_slides_from_text")
@patch("app.api.routes.presentations.fetch_commits", new_callable=AsyncMock)
def test_generate_from_commits(mock_fetch, mock_llm, mock_pptx):
    mock_fetch.return_value = ["feat: add JWT auth", "fix: bug no login"]
    mock_llm.return_value = (MOCK_TITLE, MOCK_SLIDES)
    mock_pptx.return_value = MOCK_EXPORT
    resp = client.post("/api/v1/presentations/generate/commits", json={
        "repo": "owner/repo", "branch": "main", "num_commits": 10
    })
    assert resp.status_code == 200
    assert "presentation_id" in resp.json()


def test_generate_from_commits_missing_repo():
    """Validação Pydantic — repo é obrigatório."""
    resp = client.post("/api/v1/presentations/generate/commits", json={"branch": "main"})
    assert resp.status_code == 422


# ── US2 — Export pptx ────────────────────────────────────────────────────────

@patch("app.api.routes.presentations.pptx_service.export_to_pptx")
def test_export_pptx(mock_pptx):
    mock_pptx.return_value = MOCK_EXPORT
    resp = client.post("/api/v1/presentations/export/pptx", json={
        "title": "Minha Apresentação",
        "slides": [
            {"title": "Slide 1", "bullets": ["A", "B"]},
            {"title": "Slide 2", "bullets": ["C", "D"]},
        ],
    })
    assert resp.status_code == 200
    assert "download_url" in resp.json()


# ── US10 — Share link ─────────────────────────────────────────────────────────

def test_share_link_contains_id():
    resp = client.get("/api/v1/presentations/abc123/share")
    assert resp.status_code == 200
    assert resp.json()["presentation_id"] == "abc123"
    assert "view_url" in resp.json()


# ── Robustez — LLM failure ───────────────────────────────────────────────────

@patch("app.api.routes.presentations.llm_service.summarize_text")
def test_llm_failure_returns_500(mock_summarize):
    """Garante que erro do LLM retorna 500, não deixa a aplicação travar."""
    mock_summarize.side_effect = RuntimeError("LLM call failed after 3 attempts")
    resp = client.post("/api/v1/presentations/summarize", json={"text": "Qualquer texto."})
    assert resp.status_code == 500
    assert "detail" in resp.json()


@patch("app.api.routes.presentations.fetch_commits", new_callable=AsyncMock)
def test_github_failure_returns_502(mock_fetch):
    """Garante que erro do GitHub retorna 502 (bad gateway), não 500."""
    mock_fetch.side_effect = Exception("Connection refused")
    resp = client.post("/api/v1/presentations/generate/commits", json={
        "repo": "owner/repo", "branch": "main"
    })
    assert resp.status_code == 502
