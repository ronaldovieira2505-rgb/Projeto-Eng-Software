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
    owner, name = _split_repo(repo)
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

import re

# ── Git Trees & Engenharia Reversa de TODOs (US12) ────────────────────────────

async def fetch_repository_tree(repo: str, branch: str = "main") -> List[str]:
    """Busca a árvore completa de arquivos do repositório de forma recursiva."""
    owner, repo_name = _split_repo(repo)
    url = f"{GITHUB_API}/repos/{owner}/{repo_name}/git/trees/{branch}"
    params = {"recursive": "1"}

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(url, headers=_headers(), params=params)
        if resp.status_code == 404:
            return []
        resp.raise_for_status()

    tree = resp.json().get("tree", [])
    # Retorna apenas caminhos de arquivos válidos (blob) ignorando pastas (tree)
    return [item["path"] for item in tree if item["type"] == "blob"]

async def scan_todos_in_code(repo: str, branch: str = "main") -> List[dict]:
    """
    US12 — Varre arquivos de código do repositório buscando marcações TODO: ou FIXME:.
    Retorna uma lista estruturada para o LLM gerar o Roadmap e mapear Dívida Técnica.
    """
    all_files = await fetch_repository_tree(repo, branch)

    # Filtra por extensões de código (evita arquivos estáticos, binários ou muito pesados)
    valid_extensions = {".py", ".js", ".ts", ".go", ".java", ".cpp", ".cs", ".php"}
    code_files = [f for f in all_files if any(f.endswith(ext) for ext in valid_extensions)]

    # Limitamos a 50 arquivos para não estourar o limite da API durante a demo do MVP
    files_data = await fetch_code_files(repo, branch, code_files[:50])
    todos = []

    # Regex para capturar: # TODO: ..., // FIXME: ..., /* TODO: ...
    todo_pattern = re.compile(r"(?i)(?:#|//|/\*)\s*(TODO|FIXME)[\s:]+(.*)")

    for file_data in files_data:
        content = file_data["content"]
        for i, line in enumerate(content.splitlines(), 1):
            match = todo_pattern.search(line)
            if match:
                todos.append({
                    "file": file_data["path"],
                    "line": i,
                    "type": match.group(1).upper(),
                    "description": match.group(2).strip()
                })
    return todos


# ── Tags e Releases (US11, US19) ──────────────────────────────────────────────

async def fetch_tags(repo: str) -> List[dict]:
    """US19 — Busca tags de versão (ex: v1.0.0) para marcos cronológicos."""
    owner, repo_name = _split_repo(repo)
    url = f"{GITHUB_API}/repos/{owner}/{repo_name}/tags"

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, headers=_headers())
        if resp.status_code == 404:
            return []
        resp.raise_for_status()

    return [{"name": t["name"], "commit": t["commit"]["sha"]} for t in resp.json()]

async def fetch_releases(repo: str) -> List[dict]:
    """US11 — Busca os releases oficiais para compor os slides de Changelog."""
    owner, repo_name = _split_repo(repo)
    url = f"{GITHUB_API}/repos/{owner}/{repo_name}/releases"

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, headers=_headers())
        if resp.status_code == 404:
            return []
        resp.raise_for_status()

    return [
        {
            "tag_name": r["tag_name"],
            "name": r.get("name", ""),
            "body": r.get("body", ""),
            "published_at": r["published_at"]
        }
        for r in resp.json()
    ]


def todos_to_text(todos: List[dict]) -> str:
    """Formata a lista de TODOs para o LLM."""
    if not todos:
        return "Nenhum TODO ou FIXME encontrado no código."

    lines = ["## Dívidas Técnicas e Tarefas Pendentes no Código (TODOs)\n"]
    for t in todos:
        lines.append(f"- [{t['type']}] Arquivo `{t['file']}` (Linha {t['line']}): {t['description']}")
    return "\n".join(lines)


def prs_to_text(prs: List[dict]) -> str:
    """Formata a lista de PRs para o LLM resumir (US18)."""
    if not prs:
        return "Nenhum Pull Request fechado recentemente."

    lines = ["## Pull Requests Recentes\n"]
    for pr in prs[:10]:  # Limita aos 10 mais recentes
        status = "✅ Merged" if pr["merged"] else "❌ Closed"
        lines.append(f"- #{pr['number']} ({status}): {pr['title']}\n  Detalhes: {pr['body'][:200]}...\n")
    return "\n".join(lines)