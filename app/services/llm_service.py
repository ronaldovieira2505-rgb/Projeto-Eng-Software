"""
LLM Service — US1, US5, US6, US7, US9
Suporta Anthropic (Claude) e Google GenAI (Gemini).

Robustez implementada:
  - Retry automático com backoff exponencial (até 3 tentativas)
  - Timeout configurável por chamada
  - Fallback de provider: se Gemini falhar após retries, tenta Anthropic (se configurado)
  - Logging estruturado de todas as chamadas e erros
"""
import json
import re
import time
import logging
from typing import List

from app.core.config import settings
from app.schemas.presentation import SlideContent, ToneEnum, PresentationTypeEnum

logger = logging.getLogger(__name__)


# ── Instruções de tom — US6 ───────────────────────────────────────────────────

TONE_INSTRUCTIONS: dict[ToneEnum, str] = {
    ToneEnum.formal: (
        "Use linguagem formal e profissional. Frases completas, sem gírias. "
        "Adequado para relatórios executivos e apresentações para diretoria."
    ),
    ToneEnum.persuasive: (
        "Use linguagem persuasiva e orientada a valor. Destaque impactos positivos, "
        "benefícios de negócio e conquistas. Adequado para clientes e investidores."
    ),
    ToneEnum.technical: (
        "Use terminologia técnica precisa. Inclua detalhes de implementação, "
        "padrões de arquitetura e métricas. Adequado para equipes de engenharia."
    ),
    ToneEnum.simplified: (
        "Use linguagem simples e acessível. SUBSTITUA todos os termos técnicos por "
        "analogias do cotidiano. Nunca use siglas sem explicar. Adequado para não-técnicos."
    ),
}


# ── Instruções por tipo de apresentação — US9 incluso ─────────────────────────

PRESENTATION_TYPE_INSTRUCTIONS: dict[str, str] = {
    PresentationTypeEnum.sprint_review: (
        "Esta é uma Sprint Review. Estruture em: "
        "1) Resumo da Sprint, 2) Funcionalidades Entregues, 3) Destaques Técnicos, "
        "4) Métricas (velocidade, bugs, cobertura), 5) Impedimentos, 6) Próximos Passos."
    ),
    PresentationTypeEnum.next_steps: (
        "Esta é uma apresentação de PRÓXIMOS PASSOS. Estruture assim: "
        "1) Contexto atual, 2) Objetivos do próximo ciclo, "
        "3) Lista priorizada de tarefas (máx. 5 por slide), "
        "4) Responsáveis e prazos, 5) Dependências e riscos, "
        "6) Critérios de sucesso. Use verbos de ação (Implementar, Validar, Entregar)."
    ),
    PresentationTypeEnum.architecture: (
        "Apresentação de Arquitetura. Estruture em: "
        "1) Visão geral, 2) Componentes e responsabilidades, "
        "3) Fluxo de dados, 4) Decisões de arquitetura (ADRs), "
        "5) Pontos de integração, 6) Escalabilidade e resiliência."
    ),
    PresentationTypeEnum.roadmap: (
        "Apresentação de Roadmap. Organize por trimestres/sprints: "
        "1) Visão de longo prazo, 2) Prioridades atuais, 3) Próximas entregas, "
        "4) Itens em análise, 5) O que ficou fora do escopo e por quê."
    ),
    PresentationTypeEnum.post_mortem: (
        "Apresentação de Post-Mortem. Sem apontar culpados. "
        "Estruture em: 1) Linha do tempo, 2) Causa raiz, "
        "3) Impacto, 4) O que funcionou bem, 5) O que melhorar, "
        "6) Plano de ação com responsáveis e datas."
    ),
    PresentationTypeEnum.onboarding: (
        "Apresentação de Onboarding. Seja didático. "
        "Estruture em: 1) Visão geral do produto, 2) Stack tecnológica, "
        "3) Como rodar localmente, 4) Fluxo de trabalho (Git, PR, Review), "
        "5) Onde encontrar documentação, 6) Primeiras tarefas sugeridas."
    ),
    PresentationTypeEnum.tech_stack: (
        "Apresentação de Tech Stack. Estruture em: "
        "1) Visão geral, 2) Backend, 3) Frontend, "
        "4) Infraestrutura e Deploy, 5) Qualidade (testes, lint, monitoramento), "
        "6) Justificativa das escolhas técnicas."
    ),
    PresentationTypeEnum.generic: (
        "Apresentação genérica. Comece com contexto e termine com conclusões ou próximos passos."
    ),
}


# ── Prompts ───────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "Você é um especialista em comunicação técnica para times de engenharia de software. "
    "Transforma informações técnicas em apresentações claras e bem estruturadas. "
    "Responda SOMENTE com JSON válido, sem texto adicional, sem markdown, sem blocos de código."
)

SLIDES_PROMPT = """\
Gere uma apresentação de exatamente {num_slides} slides com base no conteúdo abaixo.

TOM — siga rigorosamente:
{tone_instruction}

ESTRUTURA PARA ESTE TIPO:
{type_instruction}

CONTEÚDO:
---
{content}
---

REGRAS:
- Cada slide: 3 a 5 bullets (máx. 12 palavras cada)
- "notes": explicação detalhada para o apresentador (2-3 frases)
- Se houver código relevante, preencha "code_snippet"
- Título da apresentação deve ser descritivo

JSON de resposta:
{{
  "title": "Título descritivo",
  "slides": [
    {{
      "title": "Título do slide",
      "bullets": ["bullet 1", "bullet 2", "bullet 3"],
      "notes": "Notas para o apresentador.",
      "code_snippet": null,
      "code_language": null
    }}
  ]
}}
"""

SUMMARIZE_PROMPT = """\
Resuma o texto abaixo em tópicos curtos para slides.

TOM:
{tone_instruction}

{simplify_block}

TEXTO:
---
{text}
---

REGRAS:
- Máx. {max_bullets} tópicos, cada um com máx. 12 palavras
- "summary": essência do texto em uma frase
- Não invente informações

JSON de resposta:
{{
  "bullets": ["tópico 1", "tópico 2"],
  "summary": "Uma frase que resume tudo."
}}
"""

SIMPLIFY_BLOCK = """\
SIMPLIFICAÇÃO OBRIGATÓRIA (público não-técnico):
- Substitua TODOS os termos técnicos por linguagem do cotidiano
- Nunca use siglas sem explicar entre parênteses
- Foque em valor de negócio, não em detalhes técnicos
Exemplos: "deploy" → "publicação do sistema", "bug" → "erro",
"refatoração" → "organização do código", "latência" → "tempo de resposta"
"""


# ── Retry com backoff exponencial ─────────────────────────────────────────────

def _retry_call(fn, *args, max_attempts: int = 3, base_delay: float = 1.5, **kwargs) -> str:
    """
    Executa fn(*args, **kwargs) com retry automático.
    Backoff: 1.5s → 3s → 6s entre tentativas.
    Lança a última exceção se todas as tentativas falharem.
    """
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            result = fn(*args, **kwargs)
            if attempt > 1:
                logger.info("LLM call succeeded on attempt %d", attempt)
            return result
        except Exception as exc:
            last_exc = exc
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(
                "LLM call failed (attempt %d/%d): %s — retrying in %.1fs",
                attempt, max_attempts, exc, delay,
            )
            if attempt < max_attempts:
                time.sleep(delay)

    raise RuntimeError(
        f"LLM call failed after {max_attempts} attempts. Last error: {last_exc}"
    ) from last_exc


# ── Chamadas por provider ─────────────────────────────────────────────────────

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


def _call_llm(user_prompt: str) -> str:
    """
    Despacha para o provider configurado.
    Se o provider principal falhar após retries, tenta o fallback (se configurado).
    """
    primary   = settings.LLM_PROVIDER
    fallback  = settings.LLM_FALLBACK_PROVIDER

    provider_map = {
        "anthropic": _call_anthropic,
        "google":    _call_google,
    }

    if primary not in provider_map:
        raise ValueError(f"LLM_PROVIDER '{primary}' inválido. Use 'anthropic' ou 'google'.")

    logger.info("Calling LLM provider=%s", primary)

    try:
        return _retry_call(provider_map[primary], user_prompt)
    except Exception as primary_exc:
        logger.error("Primary LLM provider '%s' exhausted retries: %s", primary, primary_exc)

        # Tenta fallback se configurado e diferente do primary
        if fallback and fallback != primary and fallback in provider_map:
            logger.warning("Attempting fallback provider='%s'", fallback)
            try:
                return _retry_call(provider_map[fallback], user_prompt)
            except Exception as fallback_exc:
                logger.error("Fallback provider '%s' also failed: %s", fallback, fallback_exc)
                raise RuntimeError(
                    f"Both LLM providers failed. Primary: {primary_exc}. Fallback: {fallback_exc}"
                ) from fallback_exc

        raise


# ── Parser JSON ───────────────────────────────────────────────────────────────

def _parse_json(raw: str) -> dict:
    """Remove cercas de markdown e faz parse do JSON."""
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
    logger.info("Generating slides: type=%s tone=%s num_slides=%d", presentation_type, tone, num_slides)
    raw  = _call_llm(prompt)
    data = _parse_json(raw)
    title  = data.get("title", "Apresentação")
    slides = [SlideContent(**s) for s in data.get("slides", [])]
    logger.info("Slides generated: title='%s' count=%d", title, len(slides))
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
    logger.info("Summarizing text: max_bullets=%d simplify=%s", max_bullets, simplify_technical)
    raw = _call_llm(prompt)
    return _parse_json(raw)
