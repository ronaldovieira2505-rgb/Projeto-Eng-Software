"""
Rotas de Apresentações — US1–US20
"""
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse

from app.core.config import settings
from app.schemas.presentation import (
    GenerateFromTextRequest, GenerateFromCommitsRequest,
    SummarizeRequest, SummarizeResponse,
    ExportRequest, ExportResponse,
    PresentationResponse,
    ChangelogRequest, ChangelogResponse, ChangelogEntry,
    FAQRequest, FAQResponse,
    PRSummaryRequest,
    ReleasesRequest,
    TodosRequest, TodosResponse,
    ImproveRequest, ImproveResponse,
    DiagramRequest,
)
from app.services import llm_service, pptx_service
from app.services.github_service import (
    fetch_commits, commits_to_text,
    fetch_commits_detailed, detailed_commits_to_text,
    get_pull_requests, prs_to_text,
    fetch_releases, releases_to_text,
    fetch_todos, todos_to_text,
)

router = APIRouter()


def _dl(filename: str) -> str:
    return f"/api/v1/presentations/download/{filename}"

def _share(pid: str) -> str:
    return f"/api/v1/presentations/{pid}/share"

def _pid() -> str:
    return uuid.uuid4().hex


# ── US5 — Resumir texto ───────────────────────────────────────────────────────

@router.post("/summarize", response_model=SummarizeResponse,
             summary="US5/US7 — Resumir texto em tópicos (com simplificação opcional)")
async def summarize(body: SummarizeRequest):
    try:
        result = llm_service.summarize_text(
            text=body.text, max_bullets=body.max_bullets,
            tone=body.tone, simplify_technical=body.simplify_technical,
        )
        return SummarizeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── US1 — Gerar de texto ──────────────────────────────────────────────────────

@router.post("/generate/text", response_model=PresentationResponse,
             summary="US1/US9/US14–US17 — Gerar apresentação a partir de texto")
async def generate_from_text(body: GenerateFromTextRequest):
    try:
        title, slides = llm_service.generate_slides_from_text(
            content=body.content, presentation_type=body.presentation_type.value,
            tone=body.tone, num_slides=body.num_slides,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro LLM: {e}")

    filepath, filename = pptx_service.export_to_pptx(slides, title, body.template_name)
    pid = _pid()
    return PresentationResponse(
        presentation_id=pid, title=title, slides=slides,
        download_url=_dl(filename), share_url=_share(pid),
    )


# ── US4 — Gerar de commits ────────────────────────────────────────────────────

@router.post("/generate/commits", response_model=PresentationResponse,
             summary="US4 — Gerar apresentação a partir de commits do GitHub")
async def generate_from_commits(body: GenerateFromCommitsRequest):
    try:
        commits = await fetch_commits(body.repo, body.branch, body.num_commits)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro GitHub: {e}")

    try:
        title, slides = llm_service.generate_slides_from_text(
            content=commits_to_text(commits),
            presentation_type=body.presentation_type.value,
            tone=body.tone, num_slides=8,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro LLM: {e}")

    filepath, filename = pptx_service.export_to_pptx(slides, title, body.template_name)
    pid = _pid()
    return PresentationResponse(
        presentation_id=pid, title=title, slides=slides,
        download_url=_dl(filename), share_url=_share(pid),
    )


# ── US2 — Exportar .pptx ─────────────────────────────────────────────────────

@router.post("/export/pptx", response_model=ExportResponse,
             summary="US2 — Exportar slides para .pptx")
async def export_pptx(body: ExportRequest):
    try:
        _, filename = pptx_service.export_to_pptx(
            slides=body.slides, title=body.title, template_name=body.template_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return ExportResponse(download_url=_dl(filename), filename=filename)


# ── Download ──────────────────────────────────────────────────────────────────

@router.get("/download/{filename}", summary="Download do arquivo .pptx gerado")
async def download(filename: str, background_tasks: BackgroundTasks):
    filepath = Path(settings.LOCAL_STORAGE_PATH) / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    background_tasks.add_task(filepath.unlink, missing_ok=True)
    return FileResponse(
        path=str(filepath), filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )


# ── US10 — Share ─────────────────────────────────────────────────────────────

@router.get("/{presentation_id}/share", summary="US10 — Link de compartilhamento")
async def share(presentation_id: str):
    return {
        "presentation_id": presentation_id,
        "view_url": f"{settings.INGEST_SERVICE_URL}/view/{presentation_id}",
        "message": "Compartilhe este link com clientes ou stakeholders.",
    }


# ── US11 — Changelog ─────────────────────────────────────────────────────────

@router.post("/changelog", response_model=ChangelogResponse,
             summary="US11 — Gerar changelog automático a partir de commits")
async def generate_changelog(body: ChangelogRequest):
    try:
        commits = await fetch_commits_detailed(body.repo, body.branch, body.num_commits)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro GitHub: {e}")

    try:
        data = llm_service.generate_changelog(
            commits_text=detailed_commits_to_text(commits),
            tone=body.tone,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro LLM: {e}")

    title  = data.get("title", "Changelog")
    raw_slides = data.get("slides", [])

    from app.schemas.presentation import SlideContent
    slides_obj = [SlideContent(**s) for s in raw_slides]
    entries    = [ChangelogEntry(**e) for e in data.get("entries", [])]

    _, filename = pptx_service.export_to_pptx(slides_obj, title, body.template_name)
    pid = _pid()

    return ChangelogResponse(
        presentation_id=pid, title=title,
        entries=entries, slides=slides_obj,
        download_url=_dl(filename), share_url=_share(pid),
    )


# ── US13 — FAQ ────────────────────────────────────────────────────────────────

@router.post("/faq", response_model=FAQResponse,
             summary="US13 — Gerar FAQ via IA para preparar o apresentador")
async def generate_faq(body: FAQRequest):
    try:
        items = llm_service.generate_faq(
            content=body.content, num_questions=body.num_questions,
            tone=body.tone, audience=body.audience,
        )
        return FAQResponse(audience=body.audience, items=items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── US18 — PR Summary ─────────────────────────────────────────────────────────

@router.post("/generate/pull-requests", response_model=PresentationResponse,
             summary="US18 — Gerar slides de resumo a partir de Pull Requests")
async def generate_from_prs(body: PRSummaryRequest):
    try:
        prs = await get_pull_requests(body.repo, body.state)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro GitHub: {e}")

    if not prs:
        raise HTTPException(status_code=404, detail="Nenhum PR encontrado neste repositório.")

    try:
        title, slides = llm_service.generate_from_pull_requests(
            prs_text=prs_to_text(prs), tone=body.tone,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro LLM: {e}")

    _, filename = pptx_service.export_to_pptx(slides, title, body.template_name)
    pid = _pid()
    return PresentationResponse(
        presentation_id=pid, title=title, slides=slides,
        download_url=_dl(filename), share_url=_share(pid),
    )


# ── US19 — Releases ───────────────────────────────────────────────────────────

@router.post("/generate/releases", response_model=PresentationResponse,
             summary="US19 — Gerar apresentação de marcos a partir de releases/tags do Git")
async def generate_from_releases(body: ReleasesRequest):
    try:
        releases = await fetch_releases(body.repo)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro GitHub: {e}")

    if not releases:
        raise HTTPException(status_code=404, detail="Nenhuma release ou tag encontrada.")

    try:
        title, slides = llm_service.generate_from_releases(
            releases_text=releases_to_text(releases), tone=body.tone,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro LLM: {e}")

    _, filename = pptx_service.export_to_pptx(slides, title, body.template_name)
    pid = _pid()
    return PresentationResponse(
        presentation_id=pid, title=title, slides=slides,
        download_url=_dl(filename), share_url=_share(pid),
    )


# ── US12 — TODOs ─────────────────────────────────────────────────────────────

@router.post("/generate/todos", response_model=TodosResponse,
             summary="US12 — Detectar TODOs no código e gerar slides de roadmap")
async def generate_from_todos(body: TodosRequest):
    try:
        todos = await fetch_todos(body.repo, body.branch, body.extensions)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro GitHub: {e}")

    if not todos:
        return TodosResponse(total=0, items=[], slides=None, download_url=None)

    if not body.generate_slides:
        return TodosResponse(total=len(todos), items=todos)

    try:
        title, slides = llm_service.generate_from_todos(
            todos_text=todos_to_text(todos), tone=body.tone,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro LLM: {e}")

    _, filename = pptx_service.export_to_pptx(slides, title)
    pid = _pid()
    return TodosResponse(
        total=len(todos), items=todos, slides=slides,
        presentation_id=pid, download_url=_dl(filename),
    )


# ── US21 — Diagrama de arquitetura ──────────────────────────────────────────

@router.post("/generate/diagram", response_model=PresentationResponse,
             summary="US21 — Gerar slides explicativos a partir de diagrama de arquitetura")
async def generate_from_diagram(body: DiagramRequest):
    try:
        title, slides = llm_service.generate_from_diagram(
            diagram=body.diagram, tone=body.tone, num_slides=body.num_slides,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro LLM: {e}")

    _, filename = pptx_service.export_to_pptx(slides, title, body.template_name)
    pid = _pid()
    return PresentationResponse(
        presentation_id=pid, title=title, slides=slides,
        download_url=_dl(filename), share_url=_share(pid),
    )


# ── US20 — Improve slides ─────────────────────────────────────────────────────

@router.post("/improve", response_model=ImproveResponse,
             summary="US20 — Sugerir melhorias nos slides existentes via IA")
async def improve_slides(body: ImproveRequest):
    if not body.slides:
        raise HTTPException(status_code=422, detail="Envie pelo menos 1 slide para analisar.")
    try:
        summary, improvements = llm_service.suggest_improvements(
            slides=body.slides, audience=body.audience, tone=body.tone,
        )
        return ImproveResponse(summary=summary, improvements=improvements)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
