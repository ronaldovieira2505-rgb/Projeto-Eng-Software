import type {
  GenerateFromCommitsRequest,
  GenerateResponse,
} from "../types";

// @ts-ignore
const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body?.detail ?? `Erro ${res.status}`);
  }

  return res.json() as Promise<T>;
}

// ── Presentations ─────────────────────────────────────────────────────────────

export const presentationsApi = {
  generateFromCommits(data: GenerateFromCommitsRequest): Promise<GenerateResponse> {
    return request("/api/v1/presentations/generate/commits", {
      method: "POST",
      body: JSON.stringify({
        repo: data.repo,
        branch: data.branch,
        presentation_type: data.presentation_type,
        tone: data.tone,
        num_commits: 20,
      }),
    });
  },

  download(filename: string): string {
    return `${API_BASE}/api/v1/presentations/download/${filename}`;
  },

  listTemplates(): Promise<{ templates: string[] }> {
    return request("/api/v1/github/templates");
  },
};

// ── GitHub ────────────────────────────────────────────────────────────────────

export const githubApi = {
  fetchCommits(repo: string, branch: string, limit = 20) {
    return request<{ commits: string[] }>("/api/v1/github/commits", {
      method: "POST",
      body: JSON.stringify({ repo, branch, limit }),
    });
  },
};
