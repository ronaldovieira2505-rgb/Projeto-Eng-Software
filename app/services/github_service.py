"""
GitHub Service — US1, US4, US8
Lê commits, PRs e README de repositórios.
Todas as funções recebem `repo` no formato "owner/repo".
"""
import base64
from typing import List, Optional

import httpx

from app.core.config import settings

GITHUB_API = "https://api.github.com"


def _headers() -> dict:
    h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if settings.GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"
    return h


def _split_repo(repo: str) -> tuple[str, str]:
    """Separa 'owner/repo' em (owner, repo_name). Lança ValueError se mal formatado."""
    parts = repo.strip().split("/", 1)
    if len(parts) != 2 or not all(parts):
        raise ValueError(
            f"Formato inválido: '{repo}'. Use o formato 'owner/repo' (ex: octocat/hello-world)."
        )
    return parts[0], parts[1]


# ── Commits ───────────────────────────────────────────────────────────────────

async def fetch_commits(
    repo: str,
    branch: str = "main",
    limit: int = 30,
) -> List[str]:
    """
    US4, US8 — Retorna lista de mensagens de commit (primeira linha de cada).

    Args:
        repo:   Repositório no formato "owner/repo".
        branch: Branch a consultar (default: main).
        limit:  Número máximo de commits (1–100).
    """
    owner, repo_name = _split_repo(repo)
    url = f"{GITHUB_API}/repos/{owner}/{repo_name}/commits"
    params = {"sha": branch, "per_page": min(limit, 100)}

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, headers=_headers(), params=params)
        resp.raise_for_status()

    return [c["commit"]["message"].split("\n")[0] for c in resp.json()]


def commits_to_text(commits: List[str]) -> str:
    """Converte lista de commits em bloco de texto para o LLM processar."""
    if not commits:
        return "Nenhum commit encontrado."
    lines = ["## Commits recentes\n"]
    lines += [f"- {msg}" for msg in commits]
    return "\n".join(lines)


# ── README ────────────────────────────────────────────────────────────────────

async def get_readme(repo: str) -> Optional[str]:
    """
    US8 — Retorna conteúdo do README decodificado (base64 → UTF-8).
    Retorna None se não existir.
    """
    owner, repo_name = _split_repo(repo)
    url = f"{GITHUB_API}/repos/{owner}/{repo_name}/readme"

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, headers=_headers())
        if resp.status_code == 404:
            return None
        resp.raise_for_status()

    data = resp.json()
    return base64.b64decode(data["content"]).decode("utf-8")


# ── Pull Requests ─────────────────────────────────────────────────────────────

async def get_pull_requests(repo: str, state: str = "closed") -> List[dict]:
    """
    US8 — Retorna lista de PRs com título, body e status de merge.

    Args:
        repo:  Repositório no formato "owner/repo".
        state: "open", "closed" ou "all".
    """
    owner, repo_name = _split_repo(repo)
    url = f"{GITHUB_API}/repos/{owner}/{repo_name}/pulls"
    params = {"state": state, "per_page": 20}

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, headers=_headers(), params=params)
        resp.raise_for_status()

    return [
        {
            "title": pr["title"],
            "body": pr.get("body") or "",
            "merged": pr.get("merged_at") is not None,
            "number": pr["number"],
        }
        for pr in resp.json()
    ]


async def fetch_file_content(repo: str, path: str, branch: str = "main") -> Optional[str]:
    """Busca o conteúdo de um arquivo específico no repositório."""
    owner, name = _split(repo)
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(
            f"{GITHUB_API}/repos/{owner}/{name}/contents/{path}",
            headers=_headers(),
            params={"ref": branch},
        )
        if r.status_code == 404:
            return None
        r.raise_for_status()
        data = r.json()

        # A API do GitHub retorna o conteúdo em Base64 para arquivos válidos
        if "content" in data:
            return base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
        return None


async def fetch_code_files(repo: str, branch: str, paths: List[str]) -> List[dict]:
    """Busca o conteúdo de múltiplos arquivos a partir de uma lista de caminhos."""
    files_data = []
    for path in paths:
        content = await fetch_file_content(repo, path, branch)
        if content:
            files_data.append({"path": path, "content": content})
    return files_data