"""
LLM Service — US1–US20
Anthropic (Claude) e Google GenAI (Gemini) com retry + fallback.
"""
import json
import re
import time
import logging
from typing import List, Optional

from app.core.config import settings
from app.schemas.presentation import (
    SlideContent, ToneEnum, PresentationTypeEnum,
    FAQItem, SlideImprovement,
)

logger = logging.getLogger(__name__)

# ── Tom de voz ────────────────────────────────────────────────────────────────

TONE_INSTRUCTIONS: dict[ToneEnum, str] = {
    ToneEnum.formal: (
        "Use linguagem formal e profissional. Frases completas, sem gírias. "
        "Adequado para diretoria e relatórios executivos."
    ),
    ToneEnum.persuasive: (
        "Use linguagem persuasiva e orientada a valor. Destaque benefícios e conquistas. "
        "Adequado para clientes e investidores."
    ),
    ToneEnum.technical: (
        "Use terminologia técnica precisa com métricas e padrões de arquitetura. "
        "Adequado para equipes de engenharia."
    ),
    ToneEnum.simplified: (
        "Linguagem simples e acessível. Substitua TODOS os jargões por analogias do cotidiano. "
        "Nunca use siglas sem explicar. Adequado para não-técnicos."
    ),
}

# ── Tipos de apresentação ─────────────────────────────────────────────────────

PRESENTATION_TYPE_INSTRUCTIONS: dict[str, str] = {
    PresentationTypeEnum.sprint_review: (
        "Sprint Review. Estruture: 1) Resumo da Sprint, 2) Funcionalidades Entregues, "
        "3) Destaques Técnicos, 4) Métricas, 5) Impedimentos, 6) Próximos Passos."
    ),
    PresentationTypeEnum.next_steps: (
        "Próximos Passos. Estruture: 1) Contexto atual, 2) Objetivos do próximo ciclo, "
        "3) Tarefas priorizadas (máx. 5/slide), 4) Responsáveis e prazos, "
        "5) Riscos e dependências, 6) Critérios de sucesso. Use verbos de ação."
    ),
    PresentationTypeEnum.architecture: (
        "Arquitetura de Software. Estruture: 1) Visão geral, 2) Componentes, "
        "3) Fluxo de dados, 4) Decisões (ADRs), 5) Integrações, 6) Escalabilidade."
    ),
    PresentationTypeEnum.roadmap: (
        "Roadmap de Produto. Organize por trimestres: 1) Visão de longo prazo, "
        "2) Prioridades atuais, 3) Próximas entregas, 4) Em análise, 5) Fora do escopo."
    ),
    PresentationTypeEnum.post_mortem: (
        "Post-Mortem. Sem culpados. Estruture: 1) Linha do tempo, 2) Causa raiz, "
        "3) Impacto, 4) O que funcionou, 5) O que melhorar, 6) Plano de ação."
    ),
    PresentationTypeEnum.onboarding: (
        "Onboarding. Didático e acolhedor. Estruture: 1) Visão do produto, 2) Stack, "
        "3) Rodar localmente, 4) Fluxo Git/PR/Review, 5) Exemplos práticos de uso de código "
        "(OBRIGATÓRIO: gere os exemplos na chave 'code_snippet' do JSON e defina 'code_language'), 6) Primeiras tarefas."
    ),
    PresentationTypeEnum.tech_stack: (
        "Tech Stack. Estruture: 1) Visão geral, 2) Backend, 3) Frontend, "
        "4) Infra e Deploy, 5) Qualidade, 6) Justificativas técnicas."
    ),
    PresentationTypeEnum.risks: (
        "Mapeamento de Riscos. Estruture: 1) Contexto e escopo, "
        "2) Riscos críticos (probabilidade alta + impacto alto), "
        "3) Riscos moderados, 4) Riscos baixos/monitorados, "
        "5) Planos de mitigação por risco, 6) Responsáveis e datas de revisão. "
        "Classifique cada risco como: Técnico / Negócio / Externo / Processo."
    ),
    PresentationTypeEnum.lessons_learned: (
        "Lições Aprendidas. Encerre ciclos com foco em melhoria contínua. Estruture: "
        "1) Contexto do projeto/sprint, 2) O que foi bem (keep doing), "
        "3) O que pode melhorar (stop doing), 4) O que tentar (start doing), "
        "5) Ações concretas com responsáveis, 6) Como aplicar no próximo ciclo."
    ),
    PresentationTypeEnum.technical_debt: (
        "Dívida Técnica. Objetivo: negociar tempo de refatoração com o PM. Estruture: "
        "1) O que é dívida técnica (linguagem acessível), "
        "2) Inventário da dívida atual (agrupado por área), "
        "3) Impacto no negócio (lentidão, bugs, onboarding), "
        "4) Custo de não agir (tendência de crescimento), "
        "5) Proposta de refatoração priorizada, 6) ROI esperado com prazo estimado."
    ),
    PresentationTypeEnum.architecture_evolution: (
        "Evolução da Arquitetura. Mostre como o sistema cresceu. Estruture: "
        "1) Arquitetura inicial (v0), 2) Principais mudanças e motivações, "
        "3) Estado atual com diagrama textual, 4) Problemas resolvidos em cada iteração, "
        "5) Desafios que surgiram com o crescimento, 6) Próxima evolução planejada."
    ),
    PresentationTypeEnum.generic: (
        "Apresentação genérica. Comece com contexto e termine com conclusões."
    ),
    PresentationTypeEnum.monthly_retrospective: (
        "Retrospectiva Mensal. Estruture: 1) Resumo da evolução no mês, 2) Principais entregas, "
        "3) Desafios superados, 4) Evolução de métricas, 5) Próximos passos."
    ),
    PresentationTypeEnum.cicd_strategy: (
        "Estratégia de CI/CD. Mostre a eficiência do processo para stakeholders. Estruture: 1) Visão do pipeline, "
        "2) Automação de testes, 3) Processo de deploy, 4) Métricas (frequência, tempo de build), 5) Benefícios e ROI."
    ),
    PresentationTypeEnum.frontend_backend_progress: (
        "Progresso Backend e Frontend. OBRIGATÓRIO: Crie slides separados exclusivamente para o progresso do Backend "
        "e slides separados para o Frontend. Detalhe as entregas, esforço técnico e integrações de cada área."
    ),
}

# ── Prompts ───────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "Você é um especialista em comunicação técnica para times de engenharia de software. "
    "Transforma informações técnicas em apresentações claras e bem estruturadas. "
    "Responda SOMENTE com JSON válido, sem texto adicional, sem markdown, sem blocos de código."
)

SLIDES_PROMPT = """\
Gere uma apresentação de exatamente {num_slides} slides.

TOM: {tone_instruction}
ESTRUTURA: {type_instruction}

CONTEÚDO:
---
{content}
---

REGRAS:
- 3–5 bullets por slide (máx. 12 palavras cada)
- "notes": 2-3 frases para o apresentador
- Preencha "code_snippet" se houver código relevante
- Título descritivo (não genérico)

JSON:
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
Resuma em tópicos curtos para slides.

TOM: {tone_instruction}
{simplify_block}

TEXTO:
---
{text}
---

REGRAS: máx. {max_bullets} tópicos, máx. 12 palavras cada. Não invente informações.

JSON:
{{
  "bullets": ["tópico 1", "tópico 2"],
  "summary": "Uma frase que resume tudo."
}}
"""

SIMPLIFY_BLOCK = """\
SIMPLIFICAÇÃO (público não-técnico): substitua TODOS os jargões por linguagem do cotidiano.
Exemplos: "deploy"→"publicação", "bug"→"erro", "refatoração"→"organização do código".
"""

CHANGELOG_PROMPT = """\
Analise os commits abaixo e gere um changelog profissional.

TOM: {tone_instruction}

COMMITS:
---
{commits_text}
---

Classifique cada commit em: feat | fix | refactor | docs | test | chore | other.
Gere também slides de apresentação do changelog.

JSON:
{{
  "title": "Changelog — [período ou versão]",
  "entries": [
    {{"type": "feat", "message": "Descrição clara da mudança", "sha": "abc1234"}}
  ],
  "slides": [
    {{
      "title": "Título do slide",
      "bullets": ["bullet 1", "bullet 2"],
      "notes": "Notas.",
      "code_snippet": null,
      "code_language": null
    }}
  ]
}}
"""

FAQ_PROMPT = """\
Com base no conteúdo abaixo, gere {num_questions} perguntas frequentes que o público "{audience}" faria.
Para cada pergunta, gere uma resposta clara e objetiva.

TOM: {tone_instruction}

CONTEÚDO:
---
{content}
---

JSON:
{{
  "items": [
    {{"question": "Pergunta?", "answer": "Resposta objetiva."}}
  ]
}}
"""

PR_SUMMARY_PROMPT = """\
Analise os Pull Requests abaixo e gere slides de resumo executivo.

TOM: {tone_instruction}

PULL REQUESTS:
---
{prs_text}
---

Estruture os slides em: 1) Visão geral dos PRs, 2) Principais funcionalidades mescladas,
3) Bugs corrigidos, 4) Melhorias de qualidade, 5) Impacto no produto.

JSON:
{{
  "title": "Resumo de Pull Requests",
  "slides": [
    {{
      "title": "Título",
      "bullets": ["bullet 1", "bullet 2"],
      "notes": "Notas.",
      "code_snippet": null,
      "code_language": null
    }}
  ]
}}
"""

RELEASES_PROMPT = """\
Analise as releases/tags abaixo e gere uma apresentação de marcos do projeto.

TOM: {tone_instruction}

RELEASES:
---
{releases_text}
---

Estruture os slides para mostrar a evolução cronológica do projeto,
destacando o valor entregue em cada versão.

JSON:
{{
  "title": "Marcos e Releases do Projeto",
  "slides": [
    {{
      "title": "Título",
      "bullets": ["bullet 1", "bullet 2"],
      "notes": "Notas.",
      "code_snippet": null,
      "code_language": null
    }}
  ]
}}
"""

TODOS_SLIDE_PROMPT = """\
Com base na lista de TODOs/FIXMEs encontrados no código, gere slides de Roadmap Técnico.

TOM: {tone_instruction}

TODOS ENCONTRADOS:
---
{todos_text}
---

Agrupe por prioridade e área. Transforme cada grupo em um slide de "Próximos Passos Técnicos".

JSON:
{{
  "title": "Roadmap Técnico — TODOs e Débitos Identificados",
  "slides": [
    {{
      "title": "Título",
      "bullets": ["bullet 1", "bullet 2"],
      "notes": "Notas.",
      "code_snippet": null,
      "code_language": null
    }}
  ]
}}
"""

IMPROVE_PROMPT = """\
Analise os slides abaixo e sugira melhorias para o público "{audience}".

TOM DESEJADO: {tone_instruction}

SLIDES ATUAIS:
---
{slides_text}
---

Para cada slide, sugira:
1. Melhorias nos bullets (clareza, impacto, concisão)
2. Bullets melhorados (reescritos)

JSON:
{{
  "summary": "Avaliação geral em 1-2 frases.",
  "improvements": [
    {{
      "slide_index": 0,
      "original_title": "Título original",
      "suggestions": ["Sugestão 1", "Sugestão 2"],
      "improved_bullets": ["bullet melhorado 1", "bullet melhorado 2"]
    }}
  ]
}}
"""

REVIEW_PROMPT = """\
Você é um Arquiteto de Software Sênior revisando slides gerados por IA. 
Sua missão é garantir que NENHUM conceito técnico foi deturpado ou simplificado demais a ponto de ficar incorreto.

SLIDES ATUAIS:
---
{slides_text}
---

Para cada erro técnico grave, aponte o problema e sugira a correção. Se tudo estiver correto, retorne a lista vazia.

JSON:
{{
  "summary": "Avaliação geral da precisão técnica em 1-2 frases.",
  "corrections": [
    {{
      "slide_index": 0,
      "issue": "O conceito X foi simplificado de forma incorreta.",
      "suggestion": "Reescrever o bullet para: ..."
    }}
  ]
}}
"""

DIAGRAM_PROMPT = """\
Você recebeu um diagrama de arquitetura abaixo (pode estar em formato textual, Mermaid, PlantUML ou descrição livre).
Gere uma apresentação de exatamente {num_slides} slides explicando o fluxo de dados e os componentes.

TOM: {tone_instruction}

ESTRUTURA SUGERIDA:
1) Visão geral da arquitetura
2) Componentes principais e responsabilidades
3) Fluxo de dados (passo a passo)
4) Integrações e dependências externas
5) Decisões de design e trade-offs
6) Pontos de atenção e próximos passos

DIAGRAMA:
---
{diagram}
---

REGRAS:
- 3–5 bullets por slide (máx. 12 palavras cada)
- "notes": 2-3 frases explicando o fluxo para o apresentador
- Preencha "code_snippet" com trecho relevante do diagrama se aplicável
- Título descritivo (não genérico)

JSON:
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


# ── Retry ─────────────────────────────────────────────────────────────────────

def _retry_call(fn, *args, max_attempts: int = 3, base_delay: float = 1.5, **kwargs) -> str:
    last_exc = None
    for attempt in range(1, max_attempts + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            last_exc = exc
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning("LLM attempt %d/%d failed: %s — retry in %.1fs", attempt, max_attempts, exc, delay)
            if attempt < max_attempts:
                time.sleep(delay)
    raise RuntimeError(f"LLM failed after {max_attempts} attempts. Last: {last_exc}") from last_exc


# ── Providers ─────────────────────────────────────────────────────────────────

def _call_anthropic(prompt: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    msg = client.messages.create(
        model=settings.LLM_MODEL,
        max_tokens=settings.LLM_MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def _call_google(prompt: str) -> str:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=settings.LLM_MAX_TOKENS,
            temperature=0.4,
        ),
    )
    return response.text


def _call_llm(prompt: str) -> str:
    provider_map = {"anthropic": _call_anthropic, "google": _call_google}
    primary = settings.LLM_PROVIDER
    fallback = settings.LLM_FALLBACK_PROVIDER

    if primary not in provider_map:
        raise ValueError(f"LLM_PROVIDER '{primary}' inválido.")

    logger.info("LLM call: provider=%s", primary)
    try:
        return _retry_call(provider_map[primary], prompt)
    except Exception as primary_exc:
        logger.error("Primary LLM '%s' failed: %s", primary, primary_exc)
        if fallback and fallback != primary and fallback in provider_map:
            logger.warning("Trying fallback provider='%s'", fallback)
            return _retry_call(provider_map[fallback], prompt)
        raise


# ── JSON parser ───────────────────────────────────────────────────────────────

def _parse_json(raw: str) -> dict:
    clean = re.sub(r"```(?:json)?|```", "", raw).strip()
    start = clean.find("{")
    end = clean.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"LLM não retornou JSON válido:\n{raw[:300]}")
    return json.loads(clean[start:end])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _tone(tone: ToneEnum) -> str:
    return TONE_INSTRUCTIONS[tone]


def _type_instruction(ptype: str) -> str:
    return PRESENTATION_TYPE_INSTRUCTIONS.get(
        ptype, PRESENTATION_TYPE_INSTRUCTIONS[PresentationTypeEnum.generic]
    )


def _parse_slides(data: dict) -> tuple[str, List[SlideContent]]:
    title = data.get("title", "Apresentação")
    slides = [SlideContent(**s) for s in data.get("slides", [])]
    return title, slides


# ── Funções públicas — US originais ───────────────────────────────────────────

def generate_slides_from_text(
        content: str, presentation_type: str, tone: ToneEnum, num_slides: int, swagger_url: Optional[str] = None
) -> tuple[str, List[SlideContent]]:
    """US1, US4, US9, US14–US17, US025 — Gera slides a partir de texto."""

    type_instruction = _type_instruction(presentation_type)
    if swagger_url:
        type_instruction += f"\n- OBRIGATÓRIO: Inclua o link da doc/Swagger ({swagger_url}) no campo 'notes' ou 'bullets' dos slides relevantes."

    prompt = SLIDES_PROMPT.format(
        num_slides=num_slides,
        tone_instruction=_tone(tone),
        type_instruction=type_instruction,
        content=content,
    )
    logger.info("generate_slides: type=%s tone=%s n=%d", presentation_type, tone, num_slides)
    return _parse_slides(_parse_json(_call_llm(prompt)))


def summarize_text(
        text: str, max_bullets: int, tone: ToneEnum, simplify_technical: bool,
) -> dict:
    """US5, US7 — Resume texto em bullets."""
    prompt = SUMMARIZE_PROMPT.format(
        tone_instruction=_tone(tone),
        simplify_block=SIMPLIFY_BLOCK if simplify_technical else "",
        max_bullets=max_bullets,
        text=text,
    )
    return _parse_json(_call_llm(prompt))


# ── US11 — Changelog ─────────────────────────────────────────────────────────

def generate_changelog(commits_text: str, tone: ToneEnum) -> dict:
    """
    US11 — Analisa commits, classifica por tipo e gera changelog + slides.
    Retorna dict com keys: title, entries, slides.
    """
    prompt = CHANGELOG_PROMPT.format(
        tone_instruction=_tone(tone),
        commits_text=commits_text,
    )
    logger.info("generate_changelog: tone=%s", tone)
    data = _parse_json(_call_llm(prompt))
    return data


# ── US13 — FAQ ────────────────────────────────────────────────────────────────

def generate_faq(
        content: str, num_questions: int, tone: ToneEnum, audience: str,
) -> List[FAQItem]:
    """US13 — Gera perguntas frequentes com respostas para preparar o apresentador."""
    prompt = FAQ_PROMPT.format(
        num_questions=num_questions,
        audience=audience,
        tone_instruction=_tone(tone),
        content=content,
    )
    logger.info("generate_faq: audience=%s n=%d", audience, num_questions)
    data = _parse_json(_call_llm(prompt))
    return [FAQItem(**item) for item in data.get("items", [])]


# ── US18 — PR Summary ─────────────────────────────────────────────────────────

def generate_from_pull_requests(prs_text: str, tone: ToneEnum) -> tuple[str, List[SlideContent]]:
    """US18 — Gera slides de resumo a partir de Pull Requests."""
    prompt = PR_SUMMARY_PROMPT.format(
        tone_instruction=_tone(tone),
        prs_text=prs_text,
    )
    logger.info("generate_from_pull_requests: tone=%s", tone)
    return _parse_slides(_parse_json(_call_llm(prompt)))


# ── US19 — Releases ───────────────────────────────────────────────────────────

def generate_from_releases(releases_text: str, tone: ToneEnum) -> tuple[str, List[SlideContent]]:
    """US19 — Gera apresentação de marcos a partir de releases/tags do Git."""
    prompt = RELEASES_PROMPT.format(
        tone_instruction=_tone(tone),
        releases_text=releases_text,
    )
    logger.info("generate_from_releases: tone=%s", tone)
    return _parse_slides(_parse_json(_call_llm(prompt)))


# ── US12 — TODOs → slides ─────────────────────────────────────────────────────

def generate_from_todos(todos_text: str, tone: ToneEnum) -> tuple[str, List[SlideContent]]:
    """US12 — Transforma lista de TODOs em slides de roadmap técnico."""
    prompt = TODOS_SLIDE_PROMPT.format(
        tone_instruction=_tone(tone),
        todos_text=todos_text,
    )
    logger.info("generate_from_todos: tone=%s", tone)
    return _parse_slides(_parse_json(_call_llm(prompt)))


# ── US21 — Diagrama de arquitetura ───────────────────────────────────────────

def generate_from_diagram(
        diagram: str, tone: ToneEnum, num_slides: int,
) -> tuple[str, List[SlideContent]]:
    """US21 — Gera slides explicativos sobre fluxo de dados a partir de diagrama de arquitetura."""
    prompt = DIAGRAM_PROMPT.format(
        num_slides=num_slides,
        tone_instruction=_tone(tone),
        diagram=diagram,
    )
    logger.info("generate_from_diagram: tone=%s n=%d", tone, num_slides)
    return _parse_slides(_parse_json(_call_llm(prompt)))


# ── US20 — Improve slides ─────────────────────────────────────────────────────

def suggest_improvements(
        slides: List[SlideContent], audience: str, tone: ToneEnum,
) -> tuple[str, List[SlideImprovement]]:
    """US20 — Analisa slides existentes e sugere melhorias via IA."""
    slides_text = "\n".join(
        f"[Slide {i}] {s.title}\n" + "\n".join(f"  - {b}" for b in s.bullets)
        for i, s in enumerate(slides)
    )
    prompt = IMPROVE_PROMPT.format(
        audience=audience,
        tone_instruction=_tone(tone),
        slides_text=slides_text,
    )
    logger.info("suggest_improvements: audience=%s tone=%s slides=%d", audience, tone, len(slides))
    data = _parse_json(_call_llm(prompt))
    summary = data.get("summary", "")
    improvements = [SlideImprovement(**item) for item in data.get("improvements", [])]
    return summary, improvements

# ── US — Revisão Técnica ──────────────────────────────────────────────────────

def review_technical_accuracy(slides: List[SlideContent]) -> dict:
    """US: Revisa descrições técnicas para evitar deturpação de conceitos."""
    slides_text = "\n".join(
        f"[Slide {i}] {s.title}\n" + "\n".join(f"  - {b}" for b in s.bullets)
        for i, s in enumerate(slides)
    )
    prompt = REVIEW_PROMPT.format(slides_text=slides_text)
    logger.info("review_technical_accuracy: slides=%d", len(slides))
    data = _parse_json(_call_llm(prompt))
    return data