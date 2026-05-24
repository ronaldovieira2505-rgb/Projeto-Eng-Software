"""
GitHub Service — US1, US4, US8, US12, US19
Commits, PRs, README, TODOs no código e tags de versão.
"""
import base64
import re
from typing import List, Optional

import httpx

from app.core.config import settings
from app.schemas.presentation import TodoItem

GITHUB_API = "https://api.github.com"
TODO_PATTERN = re.compile(r"#\s*(TODO|FIXME|HACK|NOTE)[:\s]+(.*)", re.IGNORECASE)


def _headers() -> dict:
    h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if settings.GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"
    return h


def _split(repo: str) -> tuple[str, str]:
    parts = repo.strip().split("/", 1)
    if len(parts) != 2 or not all(parts):
        raise ValueError(f"Formato inválido: '{repo}'. Use 'owner/repo'.")
    return parts[0], parts[1]


# ── Commits ───────────────────────────────────────────────────────────────────

async def fetch_commits(repo: str, branch: str = "main", limit: int = 30) -> List[str]:
    """Retorna lista de mensagens de commit (primeira linha)."""
    owner, name = _split(repo)
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(
            f"{GITHUB_API}/repos/{owner}/{name}/commits",
            headers=_headers(),
            params={"sha": branch, "per_page": min(limit, 100)},
        )
        r.raise_for_status()
    return [c["commit"]["message"].split("\n")[0] for c in r.json()]


async def fetch_commits_detailed(repo: str, branch: str = "main", limit: int = 30) -> List[dict]:
    """Retorna commits com sha, message, author, date — para changelog."""
    owner, name = _split(repo)
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(
            f"{GITHUB_API}/repos/{owner}/{name}/commits",
            headers=_headers(),
            params={"sha": branch, "per_page": min(limit, 100)},
        )
        r.raise_for_status()
    return [
        {
            "sha":     item["sha"][:7],
            "message": item["commit"]["message"].split("\n")[0],
            "author":  item["commit"]["author"]["name"],
            "date":    item["commit"]["author"]["date"][:10],
        }
        for item in r.json()
    ]


def commits_to_text(commits: List[str]) -> str:
    if not commits:
        return "Nenhum commit encontrado."
    return "## Commits\n" + "\n".join(f"- {m}" for m in commits)


def detailed_commits_to_text(commits: List[dict]) -> str:
    if not commits:
        return "Nenhum commit encontrado."
    lines = ["## Commits detalhados\n"]
    for c in commits:
        lines.append(f"- [{c['sha']}] {c['date']} — {c['author']}: {c['message']}")
    return "\n".join(lines)


# ── README ────────────────────────────────────────────────────────────────────

async def get_readme(repo: str) -> Optional[str]:
    owner, name = _split(repo)
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(f"{GITHUB_API}/repos/{owner}/{name}/readme", headers=_headers())
        if r.status_code == 404:
            return None
        r.raise_for_status()
    return base64.b64decode(r.json()["content"]).decode("utf-8")


# ── Pull Requests ─────────────────────────────────────────────────────────────

async def get_pull_requests(repo: str, state: str = "closed") -> List[dict]:
    owner, name = _split(repo)
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(
            f"{GITHUB_API}/repos/{owner}/{name}/pulls",
            headers=_headers(),
            params={"state": state, "per_page": 20},
        )
        r.raise_for_status()
    return [
        {
            "number": pr["number"],
            "title":  pr["title"],
            "body":   pr.get("body") or "",
            "merged": pr.get("merged_at") is not None,
            "user":   pr["user"]["login"],
        }
        for pr in r.json()
    ]


def prs_to_text(prs: List[dict]) -> str:
    if not prs:
        return "Nenhum PR encontrado."
    lines = ["## Pull Requests\n"]
    for pr in prs:
        status = "✅ merged" if pr["merged"] else "🔄 open"
        body   = pr["body"][:200].replace("\n", " ") if pr["body"] else "sem descrição"
        lines.append(f"- #{pr['number']} [{status}] {pr['title']} (@{pr['user']})\n  {body}")
    return "\n".join(lines)


# ── US12 — TODOs no código ────────────────────────────────────────────────────

async def fetch_todos(
    repo: str,
    branch: str = "main",
    extensions: Optional[List[str]] = None,
) -> List[TodoItem]:
    """
    US12 — Percorre a árvore de arquivos do repositório, baixa os que
    batem com as extensões e extrai comentários TODO/FIXME/HACK/NOTE.
    """
    if extensions is None:
        extensions = [".py", ".ts", ".js", ".java", ".go"]

    owner, name = _split(repo)

    # 1. Busca a árvore recursiva de arquivos
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(
            f"{GITHUB_API}/repos/{owner}/{name}/git/trees/{branch}",
            headers=_headers(),
            params={"recursive": "1"},
        )
        r.raise_for_status()
        tree = r.json().get("tree", [])

    # Filtra apenas arquivos com extensões desejadas (máx. 30 para não estourar rate limit)
    files = [
        item for item in tree
        if item["type"] == "blob"
        and any(item["path"].endswith(ext) for ext in extensions)
    ][:30]

    todos: List[TodoItem] = []

    async with httpx.AsyncClient(timeout=30) as c:
        for file in files:
            try:
                r = await c.get(file["url"], headers=_headers())
                if r.status_code != 200:
                    continue
                content_b64 = r.json().get("content", "")
                content = base64.b64decode(content_b64).decode("utf-8", errors="ignore")

                for line_num, line in enumerate(content.splitlines(), start=1):
                    match = TODO_PATTERN.search(line)
                    if match:
                        todos.append(TodoItem(
                            file=file["path"],
                            line=line_num,
                            tag=match.group(1).upper(),
                            message=match.group(2).strip(),
                        ))
            except Exception:
                continue  # arquivo ilegível, pula

    return todos


def todos_to_text(todos: List[TodoItem]) -> str:
    if not todos:
        return "Nenhum TODO/FIXME encontrado."
    lines = [f"Total: {len(todos)} itens\n"]
    for t in todos:
        lines.append(f"[{t.tag}] {t.file}:{t.line} — {t.message}")
    return "\n".join(lines)


# ── US19 — Tags / Releases ────────────────────────────────────────────────────

async def fetch_releases(repo: str) -> List[dict]:
    """US19 — Retorna releases publicadas (ou tags se não houver releases)."""
    owner, name = _split(repo)

    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(
            f"{GITHUB_API}/repos/{owner}/{name}/releases",
            headers=_headers(),
            params={"per_page": 20},
        )
        r.raise_for_status()
        releases = r.json()

    if releases:
        return [
            {
                "tag":  rel["tag_name"],
                "name": rel["name"] or rel["tag_name"],
                "date": (rel.get("published_at") or "")[:10],
                "body": (rel.get("body") or "")[:400],
            }
            for rel in releases
        ]

    # Fallback: usa tags simples se não houver releases formais
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(
            f"{GITHUB_API}/repos/{owner}/{name}/tags",
            headers=_headers(),
            params={"per_page": 20},
        )
        r.raise_for_status()

    return [
        {"tag": t["name"], "name": t["name"], "date": None, "body": None}
        for t in r.json()
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
