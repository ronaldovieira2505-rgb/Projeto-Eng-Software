import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse

from app.core.config import settings
from app.schemas.presentation import (
    GenerateFromTextRequest,
    GenerateFromCommitsRequest,
    SummarizeRequest,
    SummarizeResponse,
    ExportRequest,
    ExportResponse,
    PresentationResponse,
)
from app.services import llm_service, pptx_service
from app.services.github_service import fetch_commits, commits_to_text

router = APIRouter()


def _download_url(filename: str) -> str:
    return f"/api/v1/presentations/download/{filename}"


def _share_url(pid: str) -> str:
    return f"/api/v1/presentations/{pid}/share"


@router.post("/summarize", response_model=SummarizeResponse, summary="US5 — Resumir texto em tópicos")
async def summarize(body: SummarizeRequest):
    try:
        result = llm_service.summarize_text(
            text=body.text,
            max_bullets=body.max_bullets,
            tone=body.tone,
            simplify_technical=body.simplify_technical,
        )
        return SummarizeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/text", response_model=PresentationResponse, summary="US1 — Gerar apresentação a partir de texto")
async def generate_from_text(body: GenerateFromTextRequest):
    try:
        title, slides = llm_service.generate_slides_from_text(
            content=body.content,
            presentation_type=body.presentation_type.value,
            tone=body.tone,
            num_slides=body.num_slides,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro LLM: {e}")

    filepath, filename = pptx_service.export_to_pptx(slides, title, body.template_name)
    pid = uuid.uuid4().hex

    return PresentationResponse(
        presentation_id=pid,
        title=title,
        slides=slides,
        download_url=_download_url(filename),
        share_url=_share_url(pid),
    )


@router.post("/generate/commits", response_model=PresentationResponse, summary="US4 — Gerar apresentação a partir de commits do GitHub")
async def generate_from_commits(body: GenerateFromCommitsRequest):
    try:
        commits = await fetch_commits(body.repo, body.branch, body.num_commits)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro GitHub: {e}")

    content = commits_to_text(commits)

    try:
        title, slides = llm_service.generate_slides_from_text(
            content=content,
            presentation_type=body.presentation_type.value,
            tone=body.tone,
            num_slides=8,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro LLM: {e}")

    filepath, filename = pptx_service.export_to_pptx(slides, title, body.template_name)
    pid = uuid.uuid4().hex

    return PresentationResponse(
        presentation_id=pid,
        title=title,
        slides=slides,
        download_url=_download_url(filename),
        share_url=_share_url(pid),
    )


@router.post("/export/pptx", response_model=ExportResponse, summary="US2 — Exportar slides para .pptx")
async def export_pptx(body: ExportRequest):
    try:
        filepath, filename = pptx_service.export_to_pptx(
            slides=body.slides, title=body.title, template_name=body.template_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return ExportResponse(download_url=_download_url(filename), filename=filename)


@router.get("/download/{filename}")
async def download(filename: str, background_tasks: BackgroundTasks):
    filepath = Path(settings.LOCAL_STORAGE_PATH) / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    background_tasks.add_task(filepath.unlink, missing_ok=True)
    return FileResponse(
        path=str(filepath),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )


@router.get("/{presentation_id}/share", summary="US10 — Link de compartilhamento")
async def share(presentation_id: str):
    return {
        "presentation_id": presentation_id,
        "view_url": f"{settings.INGEST_SERVICE_URL}/view/{presentation_id}",
        "message": "Compartilhe este link com clientes ou stakeholders.",
    }