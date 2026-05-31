"""
Testes unitários — Presentation Service (US1–US20).
Sem dependência real de LLM, GitHub ou disco.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from app.main import app
from app.schemas.presentation import SlideContent, FAQItem, SlideImprovement

client = TestClient(app)

# ── Fixtures ──────────────────────────────────────────────────────────────────

SLIDES = [
    SlideContent(title="Sprint Review", bullets=["Entrega A", "Entrega B"]),
    SlideContent(title="Próximos Passos", bullets=["Tarefa 1", "Tarefa 2"]),
]
TITLE   = "Sprint 42 Review"
EXPORT  = ("caminho/fake.pptx", "fake.pptx")
COMMITS = ["feat: add JWT auth", "fix: bug no login", "refactor: clean services"]
PRS     = [{"number": 1, "title": "Add auth", "body": "JWT implementation", "merged": True, "user": "dev"}]
RELEASES = [{"tag": "v1.0.0", "name": "Release 1.0", "date": "2025-05-01", "body": "First stable release"}]


# ── Health ────────────────────────────────────────────────────────────────────

def test_health():
    r = client.get("/health/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_readiness():
    r = client.get("/health/ready")
    assert r.status_code == 200
    assert "ready" in r.json()


# ── US5/US7 — Summarize ───────────────────────────────────────────────────────

@patch("app.api.routes.presentations.llm_service.summarize_text")
def test_summarize(mock):
    mock.return_value = {"bullets": ["P1", "P2"], "summary": "Resumo."}
    r = client.post("/api/v1/presentations/summarize", json={"text": "Texto longo."})
    assert r.status_code == 200
    assert len(r.json()["bullets"]) == 2


@patch("app.api.routes.presentations.llm_service.summarize_text")
def test_summarize_simplify_flag_passed(mock):
    """US7 — simplify_technical deve chegar ao serviço."""
    mock.return_value = {"bullets": ["P"], "summary": "S."}
    client.post("/api/v1/presentations/summarize", json={
        "text": "Deploy Kubernetes.", "simplify_technical": True, "tone": "simplified"
    })
    assert mock.call_args.kwargs["simplify_technical"] is True


# ── US1 — Generate from text ──────────────────────────────────────────────────

@patch("app.api.routes.presentations.pptx_service.export_to_pptx")
@patch("app.api.routes.presentations.llm_service.generate_slides_from_text")
def test_generate_from_text(mock_llm, mock_pptx):
    mock_llm.return_value = (TITLE, SLIDES)
    mock_pptx.return_value = EXPORT
    r = client.post("/api/v1/presentations/generate/text", json={
        "content": "Entregamos JWT.", "presentation_type": "sprint_review",
        "tone": "formal", "num_slides": 5,
    })
    assert r.status_code == 200
    assert r.json()["title"] == TITLE
    assert "download_url" in r.json()


@patch("app.api.routes.presentations.pptx_service.export_to_pptx")
@patch("app.api.routes.presentations.llm_service.generate_slides_from_text")
def test_generate_tone_passed(mock_llm, mock_pptx):
    """US6 — tom deve chegar ao serviço."""
    mock_llm.return_value = (TITLE, SLIDES)
    mock_pptx.return_value = EXPORT
    client.post("/api/v1/presentations/generate/text", json={
        "content": "Melhorias.", "tone": "persuasive"
    })
    assert mock_llm.call_args.kwargs["tone"].value == "persuasive"


@patch("app.api.routes.presentations.pptx_service.export_to_pptx")
@patch("app.api.routes.presentations.llm_service.generate_slides_from_text")
def test_generate_next_steps(mock_llm, mock_pptx):
    """US9 — next_steps deve ser aceito como tipo válido."""
    mock_llm.return_value = ("Próximos Passos Q3", SLIDES)
    mock_pptx.return_value = EXPORT
    r = client.post("/api/v1/presentations/generate/text", json={
        "content": "Tarefas: auth, testes, deploy.",
        "presentation_type": "next_steps",
    })
    assert r.status_code == 200
    assert mock_llm.call_args.kwargs["presentation_type"] == "next_steps"


@patch("app.api.routes.presentations.pptx_service.export_to_pptx")
@patch("app.api.routes.presentations.llm_service.generate_slides_from_text")
def test_new_types_accepted(mock_llm, mock_pptx):
    """US14–US17 — novos tipos devem ser aceitos."""
    mock_llm.return_value = (TITLE, SLIDES)
    mock_pptx.return_value = EXPORT
    for ptype in ["risks", "lessons_learned", "technical_debt", "architecture_evolution"]:
        r = client.post("/api/v1/presentations/generate/text", json={
            "content": "Conteúdo.", "presentation_type": ptype
        })
        assert r.status_code == 200, f"Tipo '{ptype}' falhou: {r.json()}"


# ── US4 — Generate from commits ───────────────────────────────────────────────

@patch("app.api.routes.presentations.pptx_service.export_to_pptx")
@patch("app.api.routes.presentations.llm_service.generate_slides_from_text")
@patch("app.api.routes.presentations.fetch_commits", new_callable=AsyncMock)
def test_generate_from_commits(mock_gh, mock_llm, mock_pptx):
    mock_gh.return_value = COMMITS
    mock_llm.return_value = (TITLE, SLIDES)
    mock_pptx.return_value = EXPORT
    r = client.post("/api/v1/presentations/generate/commits", json={
        "repo": "owner/repo", "branch": "main", "num_commits": 10
    })
    assert r.status_code == 200
    assert "presentation_id" in r.json()


def test_generate_from_commits_missing_repo():
    r = client.post("/api/v1/presentations/generate/commits", json={"branch": "main"})
    assert r.status_code == 422


# ── US2 — Export ─────────────────────────────────────────────────────────────

@patch("app.api.routes.presentations.pptx_service.export_to_pptx")
def test_export_pptx(mock_pptx):
    mock_pptx.return_value = EXPORT
    r = client.post("/api/v1/presentations/export/pptx", json={
        "title": "Apresentação",
        "slides": [{"title": "S1", "bullets": ["A", "B"]}],
    })
    assert r.status_code == 200
    assert "download_url" in r.json()


# ── US10 — Share ─────────────────────────────────────────────────────────────

def test_share_link():
    r = client.get("/api/v1/presentations/abc123/share")
    assert r.status_code == 200
    assert r.json()["presentation_id"] == "abc123"


# ── US11 — Changelog ─────────────────────────────────────────────────────────

@patch("app.api.routes.presentations.pptx_service.export_to_pptx")
@patch("app.api.routes.presentations.llm_service.generate_changelog")
@patch("app.api.routes.presentations.fetch_commits_detailed", new_callable=AsyncMock)
def test_changelog(mock_gh, mock_llm, mock_pptx):
    mock_gh.return_value = [{"sha": "abc1234", "message": "feat: auth", "author": "dev", "date": "2025-05-01"}]
    mock_llm.return_value = {
        "title": "Changelog v1.2",
        "entries": [{"type": "feat", "message": "auth implementada", "sha": "abc1234"}],
        "slides": [{"title": "Novas Features", "bullets": ["Auth JWT"], "notes": None, "code_snippet": None, "code_language": None}],
    }
    mock_pptx.return_value = EXPORT
    r = client.post("/api/v1/presentations/changelog", json={"repo": "owner/repo"})
    assert r.status_code == 200
    data = r.json()
    assert "entries" in data
    assert len(data["entries"]) > 0


# ── US13 — FAQ ────────────────────────────────────────────────────────────────

@patch("app.api.routes.presentations.llm_service.generate_faq")
def test_faq(mock_llm):
    mock_llm.return_value = [
        FAQItem(question="Como funciona a autenticação?", answer="Via JWT com expiração de 1h."),
        FAQItem(question="Há limite de requisições?", answer="Sim, 1000/min por usuário."),
    ]
    r = client.post("/api/v1/presentations/faq", json={
        "content": "Sistema de autenticação JWT.", "num_questions": 5, "audience": "clientes"
    })
    assert r.status_code == 200
    assert len(r.json()["items"]) == 2
    assert r.json()["audience"] == "clientes"


# ── US18 — PR Summary ─────────────────────────────────────────────────────────

@patch("app.api.routes.presentations.pptx_service.export_to_pptx")
@patch("app.api.routes.presentations.llm_service.generate_from_pull_requests")
@patch("app.api.routes.presentations.get_pull_requests", new_callable=AsyncMock)
def test_pr_summary(mock_gh, mock_llm, mock_pptx):
    mock_gh.return_value = PRS
    mock_llm.return_value = (TITLE, SLIDES)
    mock_pptx.return_value = EXPORT
    r = client.post("/api/v1/presentations/generate/pull-requests", json={"repo": "owner/repo"})
    assert r.status_code == 200
    assert "slides" in r.json()


@patch("app.api.routes.presentations.get_pull_requests", new_callable=AsyncMock)
def test_pr_summary_empty(mock_gh):
    mock_gh.return_value = []
    r = client.post("/api/v1/presentations/generate/pull-requests", json={"repo": "owner/repo"})
    assert r.status_code == 404


# ── US19 — Releases ───────────────────────────────────────────────────────────

@patch("app.api.routes.presentations.pptx_service.export_to_pptx")
@patch("app.api.routes.presentations.llm_service.generate_from_releases")
@patch("app.api.routes.presentations.fetch_releases", new_callable=AsyncMock)
def test_releases(mock_gh, mock_llm, mock_pptx):
    mock_gh.return_value = RELEASES
    mock_llm.return_value = ("Marcos do Projeto", SLIDES)
    mock_pptx.return_value = EXPORT
    r = client.post("/api/v1/presentations/generate/releases", json={"repo": "owner/repo"})
    assert r.status_code == 200
    assert "presentation_id" in r.json()


# ── US12 — TODOs ─────────────────────────────────────────────────────────────

@patch("app.api.routes.presentations.pptx_service.export_to_pptx")
@patch("app.api.routes.presentations.llm_service.generate_from_todos")
@patch("app.api.routes.presentations.fetch_todos", new_callable=AsyncMock)
def test_todos(mock_gh, mock_llm, mock_pptx):
    from app.schemas.presentation import TodoItem
    mock_gh.return_value = [
        TodoItem(file="app/main.py", line=42, tag="TODO", message="Adicionar autenticação"),
    ]
    mock_llm.return_value = ("Roadmap Técnico", SLIDES)
    mock_pptx.return_value = EXPORT
    r = client.post("/api/v1/presentations/generate/todos", json={"repo": "owner/repo"})
    assert r.status_code == 200
    assert r.json()["total"] == 1


@patch("app.api.routes.presentations.fetch_todos", new_callable=AsyncMock)
def test_todos_empty(mock_gh):
    mock_gh.return_value = []
    r = client.post("/api/v1/presentations/generate/todos", json={"repo": "owner/repo"})
    assert r.status_code == 200
    assert r.json()["total"] == 0


# ── US20 — Improve ────────────────────────────────────────────────────────────

@patch("app.api.routes.presentations.llm_service.suggest_improvements")
def test_improve(mock_llm):
    mock_llm.return_value = (
        "Slides claros mas podem ser mais objetivos.",
        [SlideImprovement(
            slide_index=0, original_title="Sprint Review",
            suggestions=["Adicionar métricas quantitativas"],
            improved_bullets=["Entregou 12 features", "Velocidade: 40 pontos"],
        )],
    )
    r = client.post("/api/v1/presentations/improve", json={
        "slides": [{"title": "Sprint Review", "bullets": ["Entregamos coisas"]}],
        "audience": "diretoria",
        "tone": "formal",
    })
    assert r.status_code == 200
    assert len(r.json()["improvements"]) == 1
    assert "summary" in r.json()


def test_improve_empty_slides():
    r = client.post("/api/v1/presentations/improve", json={
        "slides": [], "audience": "diretoria"
    })
    assert r.status_code == 422


# ── Robustez ─────────────────────────────────────────────────────────────────

@patch("app.api.routes.presentations.llm_service.summarize_text")
def test_llm_failure_returns_500(mock):
    mock.side_effect = RuntimeError("LLM failed after 3 attempts")
    r = client.post("/api/v1/presentations/summarize", json={"text": "Texto."})
    assert r.status_code == 500


@patch("app.api.routes.presentations.fetch_commits", new_callable=AsyncMock)
def test_github_failure_returns_502(mock):
    mock.side_effect = Exception("Connection refused")
    r = client.post("/api/v1/presentations/generate/commits", json={"repo": "owner/repo"})
    assert r.status_code == 502


# ── Mais testes para atingir 31 (Edge cases e falhas) ──────────────────────

def test_download_not_found():
    """Garante que tentar baixar um arquivo que não existe retorna 404."""
    r = client.get("/api/v1/presentations/download/arquivo_inexistente_123.pptx")
    assert r.status_code == 404


@patch("app.api.routes.presentations.fetch_todos", new_callable=AsyncMock)
def test_todos_no_slides(mock_gh):
    """US12 — Testa o comportamento quando generate_slides é False (retorna só os dados)."""
    from app.schemas.presentation import TodoItem
    mock_gh.return_value = [TodoItem(file="app/main.py", line=10, tag="TODO", message="Fix")]

    r = client.post("/api/v1/presentations/generate/todos", json={
        "repo": "owner/repo", "generate_slides": False
    })

    assert r.status_code == 200
    assert r.json()["total"] == 1
    assert r.json().get("slides") is None


@patch("app.api.routes.presentations.fetch_releases", new_callable=AsyncMock)
def test_releases_empty(mock_gh):
    """US19 — Se não houver releases, deve retornar erro 404 claro."""
    mock_gh.return_value = []
    r = client.post("/api/v1/presentations/generate/releases", json={"repo": "owner/repo"})
    assert r.status_code == 404


@patch("app.api.routes.presentations.fetch_commits_detailed", new_callable=AsyncMock)
def test_changelog_github_failure(mock_gh):
    """US11 — Se a API do GitHub cair durante a geração de changelog, devolve 502."""
    mock_gh.side_effect = Exception("API rate limit")
    r = client.post("/api/v1/presentations/changelog", json={"repo": "owner/repo"})
    assert r.status_code == 502


@patch("app.api.routes.presentations.llm_service.generate_faq")
def test_faq_llm_failure(mock_llm):
    """US13 — Se o LLM cair durante a geração de FAQ, devolve 500."""
    mock_llm.side_effect = Exception("LLM fora do ar")
    r = client.post("/api/v1/presentations/faq", json={
        "content": "Conteúdo", "num_questions": 3
    })
    assert r.status_code == 500


@patch("app.api.routes.presentations.llm_service.suggest_improvements")
def test_improve_llm_failure(mock_llm):
    """US20 — Se o LLM falhar ao sugerir melhorias, devolve 500."""
    mock_llm.side_effect = Exception("Timeout LLM")
    r = client.post("/api/v1/presentations/improve", json={
        "slides": [{"title": "S1", "bullets": ["B1"]}],
    })
    assert r.status_code == 500


@patch("app.api.routes.presentations.pptx_service.export_to_pptx")
def test_export_pptx_failure(mock_pptx):
    """US2 — Falha na escrita do arquivo no disco deve gerar 500."""
    mock_pptx.side_effect = Exception("Disco cheio")
    r = client.post("/api/v1/presentations/export/pptx", json={
        "title": "Apresentação", "slides": []
    })
    assert r.status_code == 500


@patch("app.api.routes.presentations.get_pull_requests", new_callable=AsyncMock)
def test_pr_summary_github_failure(mock_gh):
    """US18 — Falha de comunicação com GitHub buscando PRs devolve 502."""
    mock_gh.side_effect = Exception("GitHub down")
    r = client.post("/api/v1/presentations/generate/pull-requests", json={"repo": "owner/repo"})
    assert r.status_code == 502

