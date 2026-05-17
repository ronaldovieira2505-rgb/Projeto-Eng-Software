import json
import re
from typing import List

from app.core.config import settings
from app.schemas.presentation import SlideContent, ToneEnum


TONE_INSTRUCTIONS = {
    ToneEnum.formal: "Use linguagem formal e profissional.",
    ToneEnum.persuasive: "Use linguagem persuasiva, destacando benefícios e impactos positivos.",
    ToneEnum.technical: "Use terminologia técnica precisa, adequada para engenheiros.",
    ToneEnum.simplified: (
        "Simplifique termos técnicos. Substitua jargões por analogias do cotidiano."
    ),
}

SLIDES_PROMPT = """
Você é um especialista em comunicação técnica. Gere uma apresentação de {num_slides} slides
com base no conteúdo abaixo.

Tom: {tone_instruction}
Tipo: {ptype}

Conteúdo:
---
{content}
---

Responda SOMENTE com JSON válido, sem markdown:
{{
  "title": "Título da apresentação",
  "slides": [
    {{
      "title": "Título do slide",
      "bullets": ["ponto 1", "ponto 2"],
      "notes": "Notas do apresentador",
      "code_snippet": null,
      "code_language": null
    }}
  ]
}}
"""

SUMMARIZE_PROMPT = """
Resuma o texto abaixo em no máximo {max_bullets} tópicos curtos.
{simplify_instruction}
Tom: {tone_instruction}

Texto:
---
{text}
---

Responda SOMENTE com JSON válido:
{{
  "bullets": ["tópico 1", "tópico 2"],
  "summary": "Resumo de uma frase"
}}
"""


def _call_llm(prompt: str) -> str:
    if settings.LLM_PROVIDER == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model=settings.LLM_MODEL,
            max_tokens=settings.LLM_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    import openai
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=settings.LLM_MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def _parse_json(raw: str) -> dict:
    clean = re.sub(r"```(?:json)?|```", "", raw).strip()
    return json.loads(clean)


def generate_slides_from_text(
    content: str,
    presentation_type: str,
    tone: ToneEnum,
    num_slides: int,
) -> tuple[str, List[SlideContent]]:
    prompt = SLIDES_PROMPT.format(
        num_slides=num_slides,
        tone_instruction=TONE_INSTRUCTIONS[tone],
        ptype=presentation_type,
        content=content,
    )
    raw = _call_llm(prompt)
    data = _parse_json(raw)
    title = data.get("title", "Apresentação")
    slides = [SlideContent(**s) for s in data.get("slides", [])]
    return title, slides


def summarize_text(
    text: str,
    max_bullets: int,
    tone: ToneEnum,
    simplify_technical: bool,
) -> dict:
    simplify_instruction = (
        "Substitua todos os termos técnicos por linguagem acessível ao público geral."
        if simplify_technical else ""
    )
    prompt = SUMMARIZE_PROMPT.format(
        max_bullets=max_bullets,
        simplify_instruction=simplify_instruction,
        tone_instruction=TONE_INSTRUCTIONS[tone],
        text=text,
    )
    raw = _call_llm(prompt)
    return _parse_json(raw)
