# 📚 Documentação da API

## 🎯 Visão Geral

A API do Chatbot de Acessibilidade Digital é uma API REST desenvolvida com FastAPI que fornece respostas inteligentes sobre acessibilidade digital.

**Base URL**: `http://localhost:8000` (desenvolvimento)

**Versão**: 3.7.0

---

## 📖 Documentação Interativa

A API possui documentação interativa automática:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 🔐 Autenticação

Atualmente a API **não requer autenticação**, mas implementa:

- **Rate Limiting**: 10 requisições/minuto por IP (configurável)
- **Validação Rigorosa**: Sanitização e validação de entrada
- **CORS**: Configurável via variável de ambiente

---

## 📡 Endpoints

### 💬 Chat

#### `POST /api/chat`

Processa uma pergunta sobre acessibilidade digital e retorna resposta formatada.

**Request Body:**
```json
{
    "pergunta": "Como testar contraste de cores?"
}
```

**Response 200:**
```json
{
    "resposta": {
        "📘 **Introdução**": "Testar contraste é essencial para acessibilidade...",
        "🔍 **Conceitos Essenciais**": "WCAG 2.1 define critérios de contraste...",
        "🧪 **Como Testar na Prática**": "1. Use ferramentas como WAVE...",
        "📚 **Quer se Aprofundar?**": "Recomendo ler: [link]..."
    }
}
```

**Erros:**
- `400`: Validação falhou (pergunta muito curta/longa)
- `429`: Rate limit excedido
- `500`: Erro interno do servidor

**Exemplo cURL:**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "O que é WCAG 2.1?"}'
```

**Exemplo Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={"pergunta": "O que é WCAG 2.1?"}
)
data = response.json()
print(data["resposta"])
```

**Exemplo JavaScript:**
```javascript
const response = await fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pergunta: 'O que é WCAG 2.1?' })
});
const data = await response.json();
console.log(data.resposta);
```

---

### 🏥 Health Check

#### `GET /api/health`

Verifica se a API está funcionando corretamente.

**Response 200:**
```json
{
    "status": "ok",
    "message": "API funcionando corretamente",
    "cache": {
        "hits": 10,
        "misses": 5,
        "size": 15
    }
}
```

**Exemplo cURL:**
```bash
curl http://localhost:8000/api/health
```

---

### ⚙️ Configuração

#### `GET /api/config`

Retorna configurações necessárias para o frontend.

**Response 200:**
```json
{
    "request_timeout_ms": 120000,
    "error_announcement_duration_ms": 5000
}
```

**Exemplo cURL:**
```bash
curl http://localhost:8000/api/config
```

---

### 📊 Métricas

#### `GET /api/metrics`

Retorna métricas de performance e uso da API.

**Response 200:**
```json
{
    "total_requests": 100,
    "avg_response_time": 2500,
    "cache_hit_rate": 0.65,
    "fallback_rate": 0.1,
    "agent_times": {
        "assistant": 1500,
        "validator": 200,
        "reviewer": 300,
        "tester": 400,
        "deepener": 100
    }
}
```

**Exemplo cURL:**
```bash
curl http://localhost:8000/api/metrics
```

---

## 🔄 Fluxo de Processamento

1. **Validação**: Valida e sanitiza a entrada do usuário
2. **Cache**: Verifica se a resposta está em cache
3. **Pipeline**: Processa através de 5 agentes especializados
4. **Cache**: Salva resposta no cache para futuras requisições
5. **Resposta**: Retorna resposta formatada em seções

---

## 🛡️ Segurança

### Rate Limiting

- **Padrão**: 10 requisições/minuto por IP
- **Configurável**: Via variável de ambiente `RATE_LIMIT_PER_MINUTE`
- **Resposta 429**: Quando limite é excedido

### Validação de Entrada

- **Tamanho**: 3-2000 caracteres
- **Sanitização**: Remove caracteres de controle
- **Detecção**: Padrões de injeção são detectados

### CORS

- **Configurável**: Via variável de ambiente `CORS_ORIGINS`
- **Padrão**: `*` (todas as origens)
- **Produção**: Configure origens específicas

---

## 📝 Modelos de Dados

### ChatRequest

```json
{
    "pergunta": "string (3-2000 caracteres)"
}
```

### ChatResponse

```json
{
    "resposta": {
        "📘 **Introdução**": "string",
        "🔍 **Conceitos Essenciais**": "string",
        "🧪 **Como Testar na Prática**": "string",
        "📚 **Quer se Aprofundar?**": "string"
    }
}
```

### HealthResponse

```json
{
    "status": "ok",
    "message": "string",
    "cache": {
        "hits": 0,
        "misses": 0,
        "size": 0
    }
}
```

---

## ⚡ Performance

### Cache

- **Hit Rate**: ~65% (respostas em cache)
- **TTL**: 1 hora (configurável)
- **Tamanho Máximo**: 100 itens (configurável)

### Tempos de Resposta

- **Cache Hit**: < 50ms
- **Cache Miss**: 5-30s (dependendo do LLM)
- **Fallback**: Pode adicionar 2-5s

---

## 🔄 Fallback Automático

A API suporta fallback automático entre múltiplos LLMs:

1. **Primário**: Google Gemini 2.0 Flash
2. **Secundário**: OpenRouter (múltiplos modelos gratuitos)

**Modelos OpenRouter Suportados:**
- `meta-llama/llama-3.3-70b-instruct:free`
- `google/gemini-flash-1.5:free`
- `mistralai/mistral-7b-instruct:free`
- `qwen/qwen-2.5-7b-instruct:free`
- `microsoft/phi-3-medium-4k-instruct:free`

---

## 🧪 Testes

A API possui testes automatizados:

```bash
# Testes básicos
pytest tests/test_api.py -v

# Testes E2E
pytest tests/e2e/ -v

# Testes com Playwright
pytest tests/e2e/playwright/test_api_playwright.py -v
```

---

## 📊 Status Codes

| Código | Descrição |
|:------:|:----------|
| `200` | Sucesso |
| `400` | Erro de validação |
| `429` | Rate limit excedido |
| `500` | Erro interno do servidor |

---

## 🔗 Links Úteis

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)

---

**Última atualização**: 2025-11-23

