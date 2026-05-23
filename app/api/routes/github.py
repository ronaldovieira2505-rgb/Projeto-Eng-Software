# app/api/routes/github.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.services.github_service import (
    fetch_commits, get_readme, get_pull_requests,
    fetch_todos, fetch_releases,
)
from app.services.pptx_service import list_templates

router = APIRouter()


class GitHubRepoRequest(BaseModel):
    repo:   str            # owner/repo
    branch: str  = "main"
    limit:  int  = 30


class TodosQueryRequest(BaseModel):
    repo:       str
    branch:     str       = "main"
    extensions: List[str] = [".py", ".ts", ".js", ".java", ".go"]


# ── US8 — Commits ────────────────────────────────────────────────────────────

@router.post("/commits", summary="US8 — Buscar commits de um repositório")
async def route_commits(req: GitHubRepoRequest):
    try:
        commits = await fetch_commits(req.repo, req.branch, req.limit)
        return {"repo": req.repo, "branch": req.branch, "count": len(commits), "commits": commits}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro GitHub: {e}")


# ── US8 — README ─────────────────────────────────────────────────────────────

@router.post("/readme", summary="US8 — Buscar README de um repositório")
async def route_readme(req: GitHubRepoRequest):
    try:
        readme = await get_readme(req.repo)
        if readme is None:
            raise HTTPException(status_code=404, detail="README não encontrado.")
        return {"repo": req.repo, "readme": readme}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro GitHub: {e}")


# ── US8 — Pull Requests ───────────────────────────────────────────────────────

@router.post("/pull-requests", summary="US8/US18 — Buscar Pull Requests")
async def route_prs(req: GitHubRepoRequest):
    try:
        prs = await get_pull_requests(req.repo)
        return {"repo": req.repo, "count": len(prs), "pull_requests": prs}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro GitHub: {e}")


# ── US12 — TODOs ─────────────────────────────────────────────────────────────

@router.post("/todos", summary="US12 — Detectar comentários TODO/FIXME no código")
async def route_todos(req: TodosQueryRequest):
    try:
        todos = await fetch_todos(req.repo, req.branch, req.extensions)
        return {
            "repo":  req.repo,
            "total": len(todos),
            "todos": [t.model_dump() for t in todos],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro GitHub: {e}")


# ── US19 — Releases / Tags ────────────────────────────────────────────────────

@router.post("/releases", summary="US19 — Buscar releases e tags de versão")
async def route_releases(req: GitHubRepoRequest):
    try:
        releases = await fetch_releases(req.repo)
        return {"repo": req.repo, "count": len(releases), "releases": releases}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro GitHub: {e}")


# ── US3 — Templates disponíveis ──────────────────────────────────────────────

@router.get("/templates", summary="US3 — Listar templates de marca disponíveis")
async def route_templates():
    return {"templates": list_templates()}
