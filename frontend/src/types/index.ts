// ── Enums ─────────────────────────────────────────────────────────────────────

export type PresentationType =
  | "sprint_review"
  | "architecture"
  | "roadmap"
  | "live_demo"
  | "post_mortem"
  | "onboarding"
  | "tech_stack"
  | "generic";

export type ToneType =
  | "formal"
  | "persuasive"
  | "technical"
  | "simplified";

export type PresentationStatus = "Publicada" | "Pronta" | "Rascunho" | "Gerando";

// ── Domain models ─────────────────────────────────────────────────────────────

export interface SlideContent {
  title: string;
  bullets: string[];
  notes?: string;
  code_snippet?: string;
  code_language?: string;
}

export interface Presentation {
  id: string;
  title: string;
  type: string;
  audience: string;
  status: PresentationStatus;
  createdAt: string;
  downloadUrl?: string;
  shareUrl?: string;
  slides?: SlideContent[];
}

export interface DashboardStats {
  presentationsCreated: number;
  commitsAnalyzed: number;
  hoursSaved: number;
  approvalRate: number;
}

// ── API request/response types ────────────────────────────────────────────────

export interface GenerateFromCommitsRequest {
  title: string;
  repo: string;
  branch: string;
  audience: string;
  tone: ToneType;
  presentation_type: PresentationType;
  exportSnippets: boolean;
  analyzeCommits: boolean;
  detectTodos: boolean;
}

export interface GenerateResponse {
  presentation_id: string;
  title: string;
  slides: SlideContent[];
  download_url: string;
  share_url: string;
}

// ── Settings ──────────────────────────────────────────────────────────────────

export interface AppSettings {
  githubToken: string;
  openaiApiKey: string;
  defaultTone: ToneType;
  autoAnalyzeCommits: boolean;
  includeCodeSnippets: boolean;
  emailNotifications: boolean;
  slackWebhook: string;
}

export const DEFAULT_SETTINGS: AppSettings = {
  githubToken: "",
  openaiApiKey: "",
  defaultTone: "formal",
  autoAnalyzeCommits: true,
  includeCodeSnippets: true,
  emailNotifications: false,
  slackWebhook: "",
};
