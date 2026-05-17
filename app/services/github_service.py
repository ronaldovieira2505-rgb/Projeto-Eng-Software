"""
Integração com GitHub — US1, US4, US8
Lê commits, PRs e README de repositórios.
"""
from typing import List, Optional
import httpx
from app.core.config import settings

GITHUB_API = "https://api.github.com"

def _headers() -> dict:
    h = {"Accept": "application/vnd.github+json"}
    if settings.GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"
    return h

# Renomeado de get_commits para fetch_commits para bater com a rota
async def fetch_commits(owner: str, repo: str, branch: str = "main", limit: int = 30) -> List[str]:
    """Retorna lista de mensagens de commit."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/commits"
    params = {"sha": branch, "per_page": limit}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, headers=_headers(), params=params)
        resp.raise_for_status()
        data = resp.json()
        return [c["commit"]["message"].split("\n")[0] for c in data]

# Função adicionada que o Claude esqueceu de gerar
def commits_to_text(commits: List[str]) -> str:
    """Converte a lista de commits em um bloco de texto para a IA processar."""
    if not commits:
        return "Nenhum commit encontrado."
    return "\n".join(f"- {commit}" for commit in commits)

async def get_readme(owner: str, repo: str) -> Optional[str]:
    """Retorna conteúdo do README decodificado."""
    import base64
    url = f"{GITHUB_API}/repos/{owner}/{repo}/readme"
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, headers=_headers())
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        data = resp.json()
        return base64.b64decode(data["content"]).decode("utf-8")

async def get_pull_requests(owner: str, repo: str, state: str = "closed") -> List[dict]:
    """Retorna lista de PRs para geração de resumos."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls"
    params = {"state": state, "per_page": 20}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, headers=_headers(), params=params)
        resp.raise_for_status()
        return [{"title": pr["title"], "body": pr.get("body", ""), "merged": pr.get("merged_at") is not None}
                for pr in resp.json()]