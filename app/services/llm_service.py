"""
LLM Service — US1, US5, US6, US7, US9
Abstração sobre Anthropic e OpenAI com prompts especializados por tipo de apresentação.
"""
import json
import re
from typing import List

from app.core.config import settings
from app.schemas.presentation import SlideContent, ToneEnum, PresentationTypeEnum


# ── Instruções de tom (US6) ───────────────────────────────────────────────────

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
        "do cotidiano. Nunca use siglas sem explicar. Adequado para stakeholders não-técnicos e clientes."
    ),
}


# ── Instruções por tipo de apresentação (US9 incluso) ────────────────────────

PRESENTATION_TYPE_INSTRUCTIONS: dict[str, str] = {
    PresentationTypeEnum.sprint_review: (
        "Esta é uma Sprint Review. Estruture os slides em: "
        "1) Resumo da Sprint, 2) Funcionalidades Entregues, 3) Demonstração/Destaques Técnicos, "
        "4) Métricas (velocidade, bugs, cobertura), 5) Impedimentos encontrados, 6) Próximos Passos."
    ),
    PresentationTypeEnum.next_steps: (
        "Esta é uma apresentação de PRÓXIMOS PASSOS. Seu objetivo é alinhar expectativas "
        "com o cliente ou time sobre o que vem a seguir. Estruture assim: "
        "1) Contexto atual (onde estamos), 2) Objetivos do próximo ciclo, "
        "3) Lista priorizada de próximas tarefas (máx. 5 por slide), "
        "4) Responsáveis e prazos estimados, 5) Dependências e riscos, "
        "6) Critérios de sucesso. Use verbos de ação nos bullets (Implementar, Validar, Entregar)."
    ),
    PresentationTypeEnum.architecture: (
        "Esta é uma apresentação de Arquitetura de Software. Estruture em: "
        "1) Visão geral do sistema, 2) Componentes e responsabilidades, "
        "3) Fluxo de dados, 4) Decisões de arquitetura (ADRs), "
        "5) Pontos de integração, 6) Escalabilidade e resiliência."
    ),
    PresentationTypeEnum.roadmap: (
        "Esta é uma apresentação de Roadmap de Produto. Organize por trimestres ou sprints: "
        "1) Visão de longo prazo, 2) Prioridades atuais, 3) Próximas entregas planejadas, "
        "4) Itens em análise, 5) O que ficou fora do escopo e por quê."
    ),
    PresentationTypeEnum.post_mortem: (
        "Esta é uma apresentação de Post-Mortem. Seja objetivo e sem apontar culpados. "
        "Estruture em: 1) Linha do tempo do incidente, 2) Causa raiz identificada, "
        "3) Impacto (usuários afetados, tempo de indisponibilidade), "
        "4) O que funcionou bem na resposta, 5) O que pode melhorar, "
        "6) Plano de ação com responsáveis e datas."
    ),
    PresentationTypeEnum.onboarding: (
        "Esta é uma apresentação de Onboarding. Seja didático e acolhedor. "
        "Estruture em: 1) Visão geral do produto/sistema, 2) Stack tecnológica, "
        "3) Como rodar o projeto localmente, 4) Fluxo de trabalho do time (Git, PR, Review), "
        "5) Onde encontrar documentação, 6) Primeiras tarefas sugeridas."
    ),
    PresentationTypeEnum.tech_stack: (
        "Esta é uma apresentação de Tech Stack. Estruture em: "
        "1) Visão geral das tecnologias, 2) Backend (linguagens, frameworks, bancos), "
        "3) Frontend (frameworks, libs de UI), 4) Infraestrutura e Deploy (cloud, containers, CI/CD), "
        "5) Ferramentas de qualidade (testes, lint, monitoramento), "
        "6) Justificativa das escolhas técnicas."
    ),
    PresentationTypeEnum.generic: (
        "Gere uma apresentação clara e bem estruturada. "
        "Comece com um slide de introdução/contexto e termine com conclusões ou próximos passos."
    ),
}


# ── Prompts ───────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "Você é um especialista em comunicação técnica e storytelling para times de engenharia de software. "
    "Sua função é transformar informações técnicas brutas em apresentações claras, bem estruturadas e visualmente organizadas. "
    "Você sempre responde SOMENTE com JSON válido, sem texto adicional, sem markdown, sem blocos de código."
)

SLIDES_PROMPT = """\
Gere uma apresentação de exatamente {num_slides} slides com base no conteúdo abaixo.

REGRAS DE TOM — siga rigorosamente:
{tone_instruction}

ESTRUTURA ESPERADA PARA ESTE TIPO DE APRESENTAÇÃO:
{type_instruction}

CONTEÚDO DE ENTRADA:
---
{content}
---

REGRAS DE FORMATAÇÃO:
- Cada slide deve ter entre 3 e 5 bullets objetivos
- Bullets devem ser frases curtas (máx. 12 palavras)
- O campo "notes" deve conter a explicação detalhada para o apresentador (2-3 frases)
- Se o conteúdo contiver código relevante, preencha "code_snippet" com o trecho principal
- O título da apresentação deve refletir o conteúdo real, não ser genérico

Responda SOMENTE com este JSON (sem markdown, sem texto fora do JSON):
{{
  "title": "Título descritivo da apresentação",
  "slides": [
    {{
      "title": "Título do slide",
      "bullets": ["bullet 1", "bullet 2", "bullet 3"],
      "notes": "Notas detalhadas para o apresentador sobre este slide.",
      "code_snippet": null,
      "code_language": null
    }}
  ]
}}
"""

SUMMARIZE_PROMPT = """\
Sua tarefa é resumir o texto abaixo em tópicos curtos e diretos para uso em slides.

REGRAS DE TOM — siga rigorosamente:
{tone_instruction}

{simplify_block}

TEXTO:
---
{text}
---

REGRAS:
- Gere no máximo {max_bullets} tópicos
- Cada tópico deve ter no máximo 12 palavras
- O resumo de uma frase deve capturar a essência do texto inteiro
- Não invente informações que não estão no texto

Responda SOMENTE com este JSON:
{{
  "bullets": ["tópico 1", "tópico 2"],
  "summary": "Uma frase que resume tudo."
}}
"""

SIMPLIFY_BLOCK = """\
REGRA EXTRA DE SIMPLIFICAÇÃO (obrigatória):
Você está gerando conteúdo para um público NÃO-TÉCNICO.
- Substitua TODOS os termos técnicos por linguagem do cotidiano
- Use analogias simples quando necessário
- Nunca use siglas sem explicar entre parênteses na primeira ocorrência
- Foque em VALOR DE NEGÓCIO, não em detalhes de implementação
Exemplos de substituição: "deploy" → "publicação do sistema", "bug" → "erro", 
"refatoração" → "limpeza e organização do código", "latência" → "tempo de resposta"
"""


# ── Chamada ao LLM ────────────────────────────────────────────────────────────

def _call_llm(user_prompt: str) -> str:
    """Despacha para o provider configurado e retorna o texto bruto da resposta."""
    if settings.LLM_PROVIDER == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model=settings.LLM_MODEL,
            max_tokens=settings.LLM_MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text

    # Fallback: OpenAI-compatible
    import openai
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=settings.LLM_MAX_TOKENS,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


def _parse_json(raw: str) -> dict:
    """Remove cercas de markdown residuais e faz o parse do JSON."""
    clean = re.sub(r"```(?:json)?|```", "", raw).strip()
    # Garante que começa e termina com chaves (descarta texto pré/pós-JSON)
    start = clean.find("{")
    end = clean.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"Resposta do LLM não contém JSON válido: {raw[:200]}")
    return json.loads(clean[start:end])


# ── Funções públicas ──────────────────────────────────────────────────────────

def generate_slides_from_text(
    content: str,
    presentation_type: str,
    tone: ToneEnum,
    num_slides: int,
) -> tuple[str, List[SlideContent]]:
    """
    US1, US4, US9 — Gera slides a partir de texto livre.
    Retorna (título_da_apresentação, lista_de_slides).
    """
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
    """
    US5, US7 — Resume um texto longo em bullets para slides.
    Com simplify_technical=True aplica substituição de jargões (US7).
    """
    simplify_block = SIMPLIFY_BLOCK if simplify_technical else ""

    prompt = SUMMARIZE_PROMPT.format(
        tone_instruction=TONE_INSTRUCTIONS[tone],
        simplify_block=simplify_block,
        max_bullets=max_bullets,
        text=text,
    )

    raw = _call_llm(prompt)
    return _parse_json(raw)
