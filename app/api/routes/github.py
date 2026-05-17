# app/api/routes/github.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.github_service import fetch_commits, commits_to_text

router = APIRouter()


class GitHubRepoRequest(BaseModel):
    repo: str           # formato: owner/repo
    branch: str = "main"
    limit: int = 30


@router.post("/commits", summary="Buscar commits de um repositório (US8)")
async def get_commits(request: GitHubRepoRequest):
    try:
        commits = await fetch_commits(request.repo, request.branch, request.limit)
        return {
            "repo": request.repo,
            "branch": request.branch,
            "commits": commits,
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao acessar GitHub: {str(e)}")