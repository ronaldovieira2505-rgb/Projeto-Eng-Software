# Contrato de Integração — Presentation Service

**Base URL (local):** `http://localhost:8000`  
**Base URL (Docker / rede interna):** `http://presentation-service:8000`

---

## Como outros microsserviços chamam este serviço

### 1. Gerar apresentação a partir de texto
**Caso de uso:** o módulo de Ingestão ou o módulo de Consulta manda conteúdo bruto (resumo de sprint, README, lista de tarefas) e recebe slides prontos + link para download do `.pptx`.

```http
POST /api/v1/presentations/generate/text
```

**Body:**
```json
{
  "content": "Conteúdo base...",
  "presentation_type": "sprint_review",
  "tone": "formal",
  "num_slides": 8,
  "template_name": "default"
}
```

**Valores aceitos para `presentation_type`:**
`sprint_review` · `next_steps` · `architecture` · `roadmap` · `post_mortem` · `onboarding` · `tech_stack` · `generic`· `risks` · `lessons_learned` · `technical_debt` · `architecture_evolution`

**Valores aceitos para `tone`:**
`formal` · `persuasive` · `technical` · `simplified`

**Resposta 200:**
```json
{
  "presentation_id": "a3f9c1...",
  "title": "Sprint 42 Review — Autenticação e Módulo de Usuários",
  "slides": [
    {
      "title": "Resumo da Sprint",
      "bullets": ["Entregamos JWT", "Refatoramos módulo de usuários"],
      "notes": "Explicar ao PM o impacto no roadmap.",
      "code_snippet": null,
      "code_language": null
    }
  ],
  "download_url": "/api/v1/presentations/download/abc123.pptx",
  "share_url": "/api/v1/presentations/a3f9c1.../share"
}
```

---

### 2. Resumir texto em tópicos para slides
**Caso de uso:** módulo de Consulta quer transformar uma resposta longa da IA em bullets para um slide.

```http
POST /api/v1/presentations/summarize
```

**Body:**
```json
{
  "text": "Texto longo...",
  "max_bullets": 5,
  "tone": "formal",
  "simplify_technical": false
}
```

**Resposta 200:**
```json
{
  "bullets": ["Ponto principal 1", "Ponto principal 2"],
  "summary": "Uma frase resumindo tudo."
}
```

> Passe `"simplify_technical": true` para substituir jargões técnicos por linguagem acessível (útil para apresentações a clientes não-técnicos).

---

### 3. Gerar apresentação a partir de commits do GitHub
**Caso de uso:** módulo de Ingestão já leu os commits e quer gerar slides de Sprint Review.

```http
POST /api/v1/presentations/generate/commits
```

**Body:**
```json
{
  "repo": "owner/nome-do-repo",
  "branch": "main",
  "num_commits": 20,
  "presentation_type": "sprint_review",
  "tone": "formal"
}
```

---

### 4. Exportar slides para .pptx
**Caso de uso:** outro módulo já tem uma lista de slides montada e quer só o arquivo.

```http
POST /api/v1/presentations/export/pptx
```

**Body:**
```json
{
  "title": "Minha Apresentação",
  "slides": [
    { "title": "Slide 1", "bullets": ["A", "B"], "notes": null, "code_snippet": null, "code_language": null }
  ],
  "template_name": "default"
}
```

**Resposta 200:**
```json
{
  "download_url": "/api/v1/presentations/download/abc123.pptx",
  "filename": "abc123.pptx"
}
```

---

### 5. Listar templates de marca disponíveis
```
GET /api/v1/presentations/templates
```
**Resposta:** `{ "templates": ["mackenzie", "cliente_x"] }`

---

## Códigos de erro

| Código | Significado |
|--------|-------------|
| 422 | Campo obrigatório ausente ou formato inválido (ex: `repo` sem `owner/repo`) |
| 500 | Erro interno — LLM falhou após retries |
| 502 | Serviço externo indisponível — GitHub inacessível |
| 404 | Arquivo de download não encontrado (expirou ou nunca gerado) |

---

## Health check (para monitoramento e Docker)

```
GET /health/        → { "status": "ok", "service": "presentation-service" }
GET /health/ready   → { "ready": true, "checks": { "llm_key_configured": true } }
```

---

## Exemplo de chamada com Python (requests)

```python
import requests

resp = requests.post(
    "http://presentation-service:8000/api/v1/presentations/generate/text",
    json={
        "content": "Sprint 5: entregamos login, cadastro e dashboard.",
        "presentation_type": "sprint_review",
        "tone": "formal",
        "num_slides": 6,
    }
)
data = resp.json()
print(data["download_url"])   # /api/v1/presentations/download/abc123.pptx
```

---

## Exemplo de chamada com JavaScript (fetch)

```javascript
const resp = await fetch("http://presentation-service:8000/api/v1/presentations/summarize", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    text: "Conteúdo longo aqui...",
    max_bullets: 4,
    simplify_technical: true,
  }),
});
const data = await resp.json();
console.log(data.bullets);
```
### 6. Atualização: Novos Tipos de Apresentação Aceitos
No endpoint `/generate/text`, além dos tipos básicos, você agora pode enviar:
`risks` (Mapeamento de Riscos) · `lessons_learned` (Lições Aprendidas) · `technical_debt` (Dívida Técnica) · `architecture_evolution` (Evolução da Arquitetura)

---

### 7. Gerar Roadmap Técnico via TODOs no Código (US12)
**Caso de uso:** Lê a árvore de arquivos de código no GitHub e extrai comentários `TODO:` ou `FIXME:` transformando em slides de Dívida Técnica/Roadmap.

```http
POST /api/v1/presentations/generate/todos
```

```json
{
  "repo": "owner/repo",
  "branch": "main",
  "extensions": [".py", ".ts", ".js", ".java", ".go"],
  "generate_slides": true,
  "tone": "formal"
}
```

```http
POST /api/v1/presentations/generate/releases
```

```json
{
  "repo": "owner/repo",
  "tone": "persuasive"
}
```

```http
POST /api/v1/presentations/changelog
```

```json
{
  "repo": "owner/repo",
  "num_commits": 30,
  "tone": "formal"
}
```

```http
POST /api/v1/presentations/generate/pull-requests
```

```json
{
  "repo": "owner/repo",
  "state": "closed",
  "tone": "technical"
}
```

```http
POST /api/v1/presentations/faq
```

```json
{
  "content": "Conteúdo da apresentação...",
  "num_questions": 5,
  "audience": "diretoria"
}
```

```http
POST /api/v1/presentations/improve
```

```json
{
  "slides": [ { "title": "...", "bullets": ["..."] }],
  "audience": "stakeholders",
  "tone": "persuasive"
}
```