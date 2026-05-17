# app/api/routes/github.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.github_service import fetch_commits, get_readme, get_pull_requests

router = APIRouter()


class GitHubRepoRequest(BaseModel):
    repo: str            # formato: owner/repo  ex: "octocat/hello-world"
    branch: str = "main"
    limit: int = 30


@router.post("/commits", summary="Buscar commits de um repositório (US8)")
async def route_fetch_commits(request: GitHubRepoRequest):
    try:
        commits = await fetch_commits(request.repo, request.branch, request.limit)
        return {"repo": request.repo, "branch": request.branch, "commits": commits}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao acessar GitHub: {str(e)}")


@router.post("/readme", summary="Buscar README de um repositório (US8)")
async def route_fetch_readme(request: GitHubRepoRequest):
    try:
        readme = await get_readme(request.repo)
        if readme is None:
            raise HTTPException(status_code=404, detail="README não encontrado.")
        return {"repo": request.repo, "readme": readme}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao acessar GitHub: {str(e)}")


@router.post("/pull-requests", summary="Buscar Pull Requests (US8)")
async def route_fetch_prs(request: GitHubRepoRequest):
    try:
        prs = await get_pull_requests(request.repo)
        return {"repo": request.repo, "pull_requests": prs}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao acessar GitHub: {str(e)}")


@router.get("/templates", summary="Listar templates de marca disponíveis (US3)")
async def list_templates():
    from app.services.pptx_service import list_templates
    return {"templates": list_templates()}
