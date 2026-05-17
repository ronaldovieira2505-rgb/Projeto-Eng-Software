from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class ToneEnum(str, Enum):
    formal = "formal"
    persuasive = "persuasive"
    technical = "technical"
    simplified = "simplified"


class PresentationTypeEnum(str, Enum):
    sprint_review = "sprint_review"
    architecture = "architecture"
    roadmap = "roadmap"
    post_mortem = "post_mortem"
    onboarding = "onboarding"
    next_steps = "next_steps"
    tech_stack = "tech_stack"
    generic = "generic"


class SlideContent(BaseModel):
    title: str
    bullets: List[str] = []
    notes: Optional[str] = None
    code_snippet: Optional[str] = None
    code_language: Optional[str] = None


class GenerateFromTextRequest(BaseModel):
    content: str = Field(..., description="Texto de entrada")
    presentation_type: PresentationTypeEnum = PresentationTypeEnum.generic
    tone: ToneEnum = ToneEnum.formal
    num_slides: int = Field(default=8, ge=3, le=20)
    template_name: Optional[str] = Field(default="default")
    project_id: Optional[str] = None


class GenerateFromCommitsRequest(BaseModel):
    repo: str = Field(..., description="owner/repo")
    branch: str = "main"
    num_commits: int = Field(default=20, ge=1, le=100)
    presentation_type: PresentationTypeEnum = PresentationTypeEnum.sprint_review
    tone: ToneEnum = ToneEnum.formal
    template_name: Optional[str] = "default"
    project_id: Optional[str] = None


class SummarizeRequest(BaseModel):
    text: str
    max_bullets: int = Field(default=5, ge=2, le=10)
    tone: ToneEnum = ToneEnum.formal
    simplify_technical: bool = False


class SummarizeResponse(BaseModel):
    bullets: List[str]
    summary: str


class ExportRequest(BaseModel):
    slides: List[SlideContent]
    title: str = "Apresentação"
    template_name: Optional[str] = "default"


class ExportResponse(BaseModel):
    download_url: str
    filename: str


class PresentationResponse(BaseModel):
    presentation_id: str
    title: str
    slides: List[SlideContent]
    download_url: str
    share_url: str
