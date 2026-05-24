"""
Schemas Pydantic — Presentation Service
Cobre todas as US implementadas (US1–US20).
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


# ── Enums ─────────────────────────────────────────────────────────────────────

class ToneEnum(str, Enum):
    formal     = "formal"
    persuasive = "persuasive"
    technical  = "technical"
    simplified = "simplified"


class PresentationTypeEnum(str, Enum):
    # US originais
    sprint_review        = "sprint_review"
    architecture         = "architecture"
    roadmap              = "roadmap"
    post_mortem          = "post_mortem"
    onboarding           = "onboarding"
    next_steps           = "next_steps"
    tech_stack           = "tech_stack"
    generic              = "generic"
    # Novos — US14–US17
    risks                = "risks"
    lessons_learned      = "lessons_learned"
    technical_debt       = "technical_debt"
    architecture_evolution = "architecture_evolution"


# ── Slide base ────────────────────────────────────────────────────────────────

class SlideContent(BaseModel):
    title:        str
    bullets:      List[str]      = []
    notes:        Optional[str]  = None
    code_snippet: Optional[str]  = None
    code_language: Optional[str] = None


# ── Requests existentes ───────────────────────────────────────────────────────

class GenerateFromTextRequest(BaseModel):
    content:           str               = Field(..., description="Texto de entrada")
    presentation_type: PresentationTypeEnum = PresentationTypeEnum.generic
    tone:              ToneEnum          = ToneEnum.formal
    num_slides:        int               = Field(default=8, ge=3, le=20)
    template_name:     Optional[str]     = "default"
    project_id:        Optional[str]     = None


class GenerateFromCommitsRequest(BaseModel):
    repo:              str               = Field(..., description="owner/repo")
    branch:            str               = "main"
    num_commits:       int               = Field(default=20, ge=1, le=100)
    presentation_type: PresentationTypeEnum = PresentationTypeEnum.sprint_review
    tone:              ToneEnum          = ToneEnum.formal
    template_name:     Optional[str]     = "default"
    project_id:        Optional[str]     = None


class SummarizeRequest(BaseModel):
    text:               str
    max_bullets:        int      = Field(default=5, ge=2, le=10)
    tone:               ToneEnum = ToneEnum.formal
    simplify_technical: bool     = False


class SummarizeResponse(BaseModel):
    bullets: List[str]
    summary: str


class ExportRequest(BaseModel):
    slides:        List[SlideContent]
    title:         str           = "Apresentação"
    template_name: Optional[str] = "default"


class ExportResponse(BaseModel):
    download_url: str
    filename:     str


class PresentationResponse(BaseModel):
    presentation_id: str
    title:           str
    slides:          List[SlideContent]
    download_url:    str
    share_url:       str


# ── US11 — Changelog ─────────────────────────────────────────────────────────

class ChangelogRequest(BaseModel):
    repo:        str           = Field(..., description="owner/repo")
    branch:      str           = "main"
    num_commits: int           = Field(default=30, ge=1, le=100)
    tone:        ToneEnum      = ToneEnum.formal
    template_name: Optional[str] = "default"


class ChangelogEntry(BaseModel):
    type:    str        # feat | fix | refactor | docs | test | chore | other
    message: str
    sha:     str


class ChangelogResponse(BaseModel):
    presentation_id: str
    title:           str
    entries:         List[ChangelogEntry]
    slides:          List[SlideContent]
    download_url:    str
    share_url:       str


# ── US12 — TODOs ──────────────────────────────────────────────────────────────

class TodosRequest(BaseModel):
    repo:       str   = Field(..., description="owner/repo")
    branch:     str   = "main"
    extensions: List[str] = Field(
        default=[".py", ".ts", ".js", ".java", ".go"],
        description="Extensões de arquivo para buscar TODOs"
    )
    generate_slides: bool = True
    tone:       ToneEnum  = ToneEnum.formal


class TodoItem(BaseModel):
    file:    str
    line:    int
    tag:     str    # TODO | FIXME | HACK | NOTE
    message: str


class TodosResponse(BaseModel):
    total:           int
    items:           List[TodoItem]
    presentation_id: Optional[str] = None
    slides:          Optional[List[SlideContent]] = None
    download_url:    Optional[str] = None


# ── US13 — FAQ ────────────────────────────────────────────────────────────────

class FAQRequest(BaseModel):
    content:    str            = Field(..., description="Conteúdo da apresentação ou documento")
    num_questions: int         = Field(default=7, ge=3, le=15)
    tone:       ToneEnum       = ToneEnum.formal
    audience:   str            = Field(default="stakeholders", description="Perfil do público (ex: clientes, diretoria, engenheiros)")


class FAQItem(BaseModel):
    question: str
    answer:   str


class FAQResponse(BaseModel):
    audience: str
    items:    List[FAQItem]


# ── US18 — Pull Requests summary ──────────────────────────────────────────────

class PRSummaryRequest(BaseModel):
    repo:          str      = Field(..., description="owner/repo")
    state:         str      = Field(default="closed", description="open | closed | all")
    tone:          ToneEnum = ToneEnum.formal
    template_name: Optional[str] = "default"


# ── US19 — Releases / tags ────────────────────────────────────────────────────

class ReleasesRequest(BaseModel):
    repo:          str      = Field(..., description="owner/repo")
    tone:          ToneEnum = ToneEnum.formal
    template_name: Optional[str] = "default"


class ReleaseItem(BaseModel):
    tag:     str
    name:    str
    date:    Optional[str] = None
    body:    Optional[str] = None


# ── US21 — Diagrama de arquitetura ──────────────────────────────────────────

class DiagramRequest(BaseModel):
    diagram:       str      = Field(..., description="Descrição textual ou DSL do diagrama de arquitetura (ex: PlantUML, Mermaid, texto livre)")
    tone:          ToneEnum = ToneEnum.technical
    num_slides:    int      = Field(default=6, ge=3, le=15)
    template_name: Optional[str] = "default"


# ── US21 — Diagrama de arquitetura ──────────────────────────────────────────

class DiagramRequest(BaseModel):
    diagram:       str      = Field(..., description="Descrição textual ou DSL do diagrama de arquitetura (ex: PlantUML, Mermaid, texto livre)")
    tone:          ToneEnum = ToneEnum.technical
    num_slides:    int      = Field(default=6, ge=3, le=15)
    template_name: Optional[str] = "default"


# ── US20 — Improve slides ─────────────────────────────────────────────────────

class ImproveRequest(BaseModel):
    slides:   List[SlideContent]
    audience: str      = Field(default="stakeholders", description="Perfil do público-alvo")
    tone:     ToneEnum = ToneEnum.formal


class SlideImprovement(BaseModel):
    slide_index: int
    original_title: str
    suggestions:    List[str]
    improved_bullets: Optional[List[str]] = None


class ImproveResponse(BaseModel):
    summary:      str
    improvements: List[SlideImprovement]
