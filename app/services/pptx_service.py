import uuid
from pathlib import Path
from typing import List, Optional

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

from app.core.config import settings
from app.schemas.presentation import SlideContent

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"
STORAGE_PATH = Path(settings.LOCAL_STORAGE_PATH)


def _ensure_storage():
    STORAGE_PATH.mkdir(parents=True, exist_ok=True)


def _get_template_path(template_name: Optional[str]) -> Optional[Path]:
    if not template_name:
        return None
    p = TEMPLATES_DIR / f"{template_name}.pptx"
    return p if p.exists() else None


def _add_title_slide(prs: Presentation, title: str):
    layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(layout)
    slide.shapes.title.text = title
    if len(slide.placeholders) > 1:
        slide.placeholders[1].text = "Gerado automaticamente — Plataforma de Documentação Inteligente"


def _add_content_slide(prs: Presentation, slide_data: SlideContent):
    layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(layout)
    slide.shapes.title.text = slide_data.title

    tf = slide.placeholders[1].text_frame
    tf.clear()
    for i, bullet in enumerate(slide_data.bullets):
        p = tf.add_paragraph() if i > 0 else tf.paragraphs[0]
        p.text = bullet
        p.level = 0

    if slide_data.code_snippet:
        txBox = slide.shapes.add_textbox(Inches(0.5), Inches(4.5), Inches(9), Inches(2.5))
        tf2 = txBox.text_frame
        tf2.word_wrap = True
        p = tf2.paragraphs[0]
        p.text = slide_data.code_snippet
        p.font.size = Pt(10)
        p.font.name = "Courier New"
        p.font.color.rgb = RGBColor(0x00, 0xFF, 0x7F)
        txBox.fill.solid()
        txBox.fill.fore_color.rgb = RGBColor(0x1E, 0x1E, 0x1E)

    if slide_data.notes:
        slide.notes_slide.notes_text_frame.text = slide_data.notes


def export_to_pptx(
    slides: List[SlideContent],
    title: str,
    template_name: Optional[str] = "default",
) -> tuple[str, str]:
    _ensure_storage()
    template_path = _get_template_path(template_name)
    prs = Presentation(str(template_path)) if template_path else Presentation()

    if not template_path:
        prs.slide_width = Inches(13.33)
        prs.slide_height = Inches(7.5)

    _add_title_slide(prs, title)
    for slide_data in slides:
        _add_content_slide(prs, slide_data)

    filename = f"{uuid.uuid4().hex}.pptx"
    filepath = STORAGE_PATH / filename
    prs.save(str(filepath))
    return str(filepath), filename