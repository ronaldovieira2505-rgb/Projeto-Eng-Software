"""
LLM Service — US1, US5, US6, US7, US9
Suporta dois providers: Anthropic (Claude) e Google GenAI (Gemini).
Controlado pela variável LLM_PROVIDER no .env
"""
import json
import re
from typing import List

from app.core.config import settings
from app.schemas.presentation import SlideContent, ToneEnum, PresentationTypeEnum


# ── Instruções de tom — US6 ───────────────────────────────────────────────────

TONE_INSTRUCTIONS: dict[ToneEnum, str] = {
    ToneEnum.formal: (
        "Use linguagem formal e profissional. Frases completas, sem gírias. "
        "Adequado para relatórios executivos e apresentações para diretoria."
    ),
    ToneEnum.persuasive: (
        "Use linguagem persuasiva e orientada a valor. Destaque impactos positivos, "
        "benefícios de negócio e conquistas. Adequado para apresentações a clientes e investidores."
    ),
    ToneEnum.technical: (
        "Use terminologia técnica precisa. Inclua detalhes de implementação, "
        "padrões de arquitetura e métricas quando relevante. Adequado para equipes de engenharia."
    ),
    ToneEnum.simplified: (
        "Use linguagem simples e acessível. SUBSTITUA todos os termos técnicos por analogias "
        "do cotidiano. Nunca use siglas sem explicar. Adequado para stakeholders não-técnicos."
    ),
}


# ── Instruções por tipo de apresentação — US9 incluso ─────────────────────────

PRESENTATION_TYPE_INSTRUCTIONS: dict[str, str] = {
    PresentationTypeEnum.sprint_review: (
        "Esta é uma Sprint Review. Estruture os slides em: "
        "1) Resumo da Sprint, 2) Funcionalidades Entregues, 3) Destaques Técnicos, "
        "4) Métricas (velocidade, bugs, cobertura), 5) Impedimentos encontrados, 6) Próximos Passos."
    ),
    PresentationTypeEnum.next_steps: (
        "Esta é uma apresentação de PRÓXIMOS PASSOS. Objetivo: alinhar expectativas "
        "sobre o que vem a seguir. Estruture assim: "
        "1) Contexto atual (onde estamos), 2) Objetivos do próximo ciclo, "
        "3) Lista priorizada de próximas tarefas (máx. 5 por slide), "
        "4) Responsáveis e prazos estimados, 5) Dependências e riscos, "
        "6) Critérios de sucesso. Use verbos de ação nos bullets (Implementar, Validar, Entregar)."
    ),
    PresentationTypeEnum.architecture: (
        "Esta é uma apresentação de Arquitetura. Estruture em: "
        "1) Visão geral do sistema, 2) Componentes e responsabilidades, "
        "3) Fluxo de dados, 4) Decisões de arquitetura (ADRs), "
        "5) Pontos de integração, 6) Escalabilidade e resiliência."
    ),
    PresentationTypeEnum.roadmap: (
        "Esta é uma apresentação de Roadmap. Organize por trimestres ou sprints: "
        "1) Visão de longo prazo, 2) Prioridades atuais, 3) Próximas entregas, "
        "4) Itens em análise, 5) O que ficou fora do escopo e por quê."
    ),
    PresentationTypeEnum.post_mortem: (
        "Esta é uma apresentação de Post-Mortem. Sem apontar culpados. "
        "Estruture em: 1) Linha do tempo do incidente, 2) Causa raiz, "
        "3) Impacto (usuários afetados, tempo de indisponibilidade), "
        "4) O que funcionou bem, 5) O que melhorar, "
        "6) Plano de ação com responsáveis e datas."
    ),
    PresentationTypeEnum.onboarding: (
        "Esta é uma apresentação de Onboarding. Seja didático e acolhedor. "
        "Estruture em: 1) Visão geral do produto, 2) Stack tecnológica, "
        "3) Como rodar localmente, 4) Fluxo de trabalho do time (Git, PR, Review), "
        "5) Onde encontrar documentação, 6) Primeiras tarefas sugeridas."
    ),
    PresentationTypeEnum.tech_stack: (
        "Esta é uma apresentação de Tech Stack. Estruture em: "
        "1) Visão geral das tecnologias, 2) Backend, 3) Frontend, "
        "4) Infraestrutura e Deploy, 5) Ferramentas de qualidade, "
        "6) Justificativa das escolhas técnicas."
    ),
    PresentationTypeEnum.generic: (
        "Gere uma apresentação clara e bem estruturada. "
        "Comece com introdução/contexto e termine com conclusões ou próximos passos."
    ),
}


# ── Prompts ───────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "Você é um especialista em comunicação técnica e storytelling para times de engenharia de software. "
    "Transforma informações técnicas brutas em apresentações claras e bem estruturadas. "
    "Responda SOMENTE com JSON válido, sem texto adicional, sem markdown, sem blocos de código."
)

SLIDES_PROMPT = """\
Gere uma apresentação de exatamente {num_slides} slides com base no conteúdo abaixo.

REGRAS DE TOM — siga rigorosamente:
{tone_instruction}

ESTRUTURA ESPERADA PARA ESTE TIPO:
{type_instruction}

CONTEÚDO DE ENTRADA:
---
{content}
---

REGRAS DE FORMATAÇÃO:
- Cada slide deve ter entre 3 e 5 bullets objetivos (máx. 12 palavras cada)
- O campo "notes" deve conter explicação detalhada para o apresentador (2-3 frases)
- Se o conteúdo contiver código relevante, preencha "code_snippet" com o trecho principal
- O título da apresentação deve ser descritivo, não genérico

Responda SOMENTE com este JSON:
{{
  "title": "Título descritivo da apresentação",
  "slides": [
    {{
      "title": "Título do slide",
      "bullets": ["bullet 1", "bullet 2", "bullet 3"],
      "notes": "Notas detalhadas para o apresentador.",
      "code_snippet": null,
      "code_language": null
    }}
  ]
}}
"""

SUMMARIZE_PROMPT = """\
Resuma o texto abaixo em tópicos curtos para uso em slides.

REGRAS DE TOM:
{tone_instruction}

{simplify_block}

TEXTO:
---
{text}
---

REGRAS:
- Gere no máximo {max_bullets} tópicos
- Cada tópico: máx. 12 palavras
- O resumo deve capturar a essência do texto inteiro em uma frase
- Não invente informações

Responda SOMENTE com este JSON:
{{
  "bullets": ["tópico 1", "tópico 2"],
  "summary": "Uma frase que resume tudo."
}}
"""

SIMPLIFY_BLOCK = """\
REGRA EXTRA — SIMPLIFICAÇÃO OBRIGATÓRIA (público não-técnico):
- Substitua TODOS os termos técnicos por linguagem do cotidiano
- Nunca use siglas sem explicar entre parênteses na primeira ocorrência
- Foque em valor de negócio, não em detalhes de implementação
Exemplos: "deploy" → "publicação do sistema", "bug" → "erro",
"refatoração" → "limpeza e organização do código", "latência" → "tempo de resposta"
"""


# ── Chamada ao LLM ────────────────────────────────────────────────────────────

def _call_llm(user_prompt: str) -> str:
    """
    Despacha para o provider configurado no .env via LLM_PROVIDER:
      - "anthropic" → Claude
      - "google"    → Gemini
    """
    if settings.LLM_PROVIDER == "anthropic":
        return _call_anthropic(user_prompt)
    if settings.LLM_PROVIDER == "google":
        return _call_google(user_prompt)
    raise ValueError(
        f"LLM_PROVIDER '{settings.LLM_PROVIDER}' não suportado. Use 'anthropic' ou 'google'."
    )


def _call_anthropic(user_prompt: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=settings.LLM_MODEL,
        max_tokens=settings.LLM_MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text


def _call_google(user_prompt: str) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=settings.LLM_MAX_TOKENS,
            temperature=0.4,
        ),
    )
    return response.text


# ── Parser JSON ───────────────────────────────────────────────────────────────

def _parse_json(raw: str) -> dict:
    """Remove cercas de markdown e faz parse do JSON. Tolera texto antes/depois."""
    clean = re.sub(r"```(?:json)?|```", "", raw).strip()
    start = clean.find("{")
    end   = clean.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"Resposta do LLM não contém JSON válido:\n{raw[:300]}")
    return json.loads(clean[start:end])


# ── Funções públicas ──────────────────────────────────────────────────────────

def generate_slides_from_text(
    content: str,
    presentation_type: str,
    tone: ToneEnum,
    num_slides: int,
) -> tuple[str, List[SlideContent]]:
    """US1, US4, US9 — Gera slides a partir de texto livre."""
    type_instruction = PRESENTATION_TYPE_INSTRUCTIONS.get(
        presentation_type,
        PRESENTATION_TYPE_INSTRUCTIONS[PresentationTypeEnum.generic],
    )
    prompt = SLIDES_PROMPT.format(
        num_slides=num_slides,
        tone_instruction=TONE_INSTRUCTIONS[tone],
        type_instruction=type_instruction,
        content=content,
    )
    raw  = _call_llm(prompt)
    data = _parse_json(raw)
    title  = data.get("title", "Apresentação")
    slides = [SlideContent(**s) for s in data.get("slides", [])]
    return title, slides


def summarize_text(
    text: str,
    max_bullets: int,
    tone: ToneEnum,
    simplify_technical: bool,
) -> dict:
    """US5, US7 — Resume texto em bullets. simplify_technical=True ativa US7."""
    prompt = SUMMARIZE_PROMPT.format(
        tone_instruction=TONE_INSTRUCTIONS[tone],
        simplify_block=SIMPLIFY_BLOCK if simplify_technical else "",
        max_bullets=max_bullets,
        text=text,
    )
    raw = _call_llm(prompt)
    return _parse_json(raw)
