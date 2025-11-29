# 🧪 Guia de Testes - Cobertura 95%

**Objetivo**: Manter cobertura mínima de 95% em todos os módulos do projeto.

## 📊 Estrutura de Testes

A estrutura de testes segue a **Pirâmide de Testes**, organizando os testes por tipo:

```
tests/
├── conftest.py                    # Configuração global de testes
│
├── unit/                          # 🧪 Testes Unitários (Base da Pirâmide - 70%)
│   ├── conftest.py               # Fixtures específicas de unitários
│   ├── core/                     # Testes dos módulos core
│   │   ├── test_cache.py
│   │   ├── test_config.py
│   │   ├── test_formatter.py
│   │   ├── test_validators.py
│   │   └── test_llm_provider.py
│   ├── agents/                   # Testes dos agentes
│   │   ├── test_dispatcher.py
│   │   ├── test_factory.py
│   │   └── test_pipeline.py
│   └── backend/                  # Testes do backend
│       ├── test_api.py
│       ├── test_security_headers.py
│       └── test_compression.py
│
├── integration/                   # 🔄 Testes de Integração (Meio da Pirâmide - 20%)
│   ├── conftest.py               # Fixtures específicas de integração
│   ├── test_user_flow.py         # Fluxo completo do usuário
│   └── test_deep_integration.py  # 🆕 Integração profunda (API -> Pipeline -> Agentes)
│
└── e2e/                           # 🎭 Testes End-to-End (Topo da Pirâmide - 10%)
    └── playwright/                # Testes com Playwright
        ├── conftest.py
        ├── test_api_playwright.py
        ├── test_frontend_playwright.py
        └── test_accessibility.py
```

### 🆕 Rebalanceamento da Pirâmide (Novembro 2025)

Para otimizar a velocidade e estabilidade da suite, adotamos uma estratégia de **Deep Integration Testing**:
- **Unitários**: Focam em lógica isolada de classes e funções.
- **Integração**: Validam o fluxo completo (API + Pipeline) usando mocks apenas para chamadas externas (LLM). Isso permite testar a orquestração sem a lentidão do browser.
- **E2E**: Focam exclusivamente em fluxos que exigem interação visual ou comportamento do navegador (JavaScript, CSS, Acessibilidade).

### Execução Seletiva

```bash
# Apenas testes unitários (rápido)
make test-unit
# ou
pytest tests/unit/ -v -m "unit"

# Apenas testes de integração
make test-integration
# ou
pytest tests/integration/ -v -m "integration"

# Apenas testes E2E
make test-e2e
# ou
pytest tests/e2e/ -v -m "e2e"

# Testes rápidos (unit + integration)
make test-fast

# Todos os testes
make test
```

## 🎯 Cobertura por Módulo

### ✅ Módulos com Testes Completos

#### 1. `formatter.py` - 100%
- ✅ `eh_erro()` - Detecção de erros
- ✅ `gerar_dica_final()` - Geração de dicas específicas e genéricas
- ✅ `extrair_primeiro_paragrafo()` - Extração com múltiplos cenários
- ✅ `formatar_resposta_final()` - Formatação de resposta

#### 2. `cache.py` - 100%
- ✅ `get_cache()` - Criação e reutilização de instância
- ✅ `get_cache_key()` - Normalização de chaves
- ✅ `get_cached_response()` - Cache hit/miss
- ✅ `set_cached_response()` - Armazenamento
- ✅ `clear_cache()` - Limpeza
- ✅ `get_cache_stats()` - Estatísticas
- ✅ Edge cases: cache desabilitado, TTL, tamanho máximo

#### 3. `factory.py` - 100%
- ✅ Criação de todos os 5 agentes
- ✅ Verificação de tipos e nomes
- ✅ Configuração de ferramentas
- ✅ Validação de instruções

#### 4. `config.py` - 100%
- ✅ Validação de variáveis de ambiente
- ✅ Valores padrão
- ✅ Parse de CORS origins
- ✅ Validação de log_level
- ✅ Validação de fallback config

#### 5. `llm_provider.py` - ~95%
- ✅ `GoogleGeminiClient` - Sucesso, erros, timeout, segurança
- ✅ `generate_with_fallback()` - Múltiplos cenários
- ✅ Edge cases: todos falham, fallback desabilitado

#### 6. `dispatcher.py` - ~90%
- ✅ `get_agent_response()` - Sucesso e erros
- ✅ Tratamento de agentes inexistentes
- ✅ Integração com fallback

#### 7. `pipeline.py` - ~95%
- ✅ Caminho feliz completo
- ✅ Validação de entrada (vazia, curta, longa)
- ✅ Falhas em agentes individuais
- ✅ Fallbacks para agentes paralelos
- ✅ Tratamento de introdução igual ao corpo

#### 8. `api.py` - ~90%
- ✅ Health check
- ✅ Chat endpoint - sucesso e erros
- ✅ Cache hit/miss
- ✅ Validação de entrada
- ✅ Rate limiting (testado indiretamente)
- ✅ Sanitização de entrada

## 🚀 Executando Testes

### Testes por Tipo

```bash
# Todos os testes
make test
# ou
pytest tests/ -v

# Apenas testes unitários (rápido)
make test-unit
# ou
pytest tests/unit/ -v -m "unit"

# Apenas testes de integração
make test-integration
# ou
pytest tests/integration/ -v -m "integration"

# Apenas testes E2E
make test-e2e
# ou
pytest tests/e2e/ -v -m "e2e"

# Testes rápidos (unit + integration)
make test-fast
```

### Com Cobertura
```bash
make test-cov
# ou
pytest --cov=src.chatbot_acessibilidade --cov=src.backend --cov-report=term-missing --cov-report=html tests/
```

### Teste Específico
```bash
# Teste unitário específico
pytest tests/unit/core/test_formatter.py -v

# Teste de integração
pytest tests/integration/test_user_flow.py -v

# Teste E2E específico
pytest tests/e2e/playwright/test_frontend_playwright.py -v
```

## 🎭 Testes Playwright - Funcionalidades Avançadas

### Screenshots Automáticos

Screenshots são capturados automaticamente quando testes falham:
- Localização: `tests/reports/screenshots/`
- Formato: PNG (página inteira)
- Nome: `{test_name}_{timestamp}.png`

### Vídeos de Execução

Vídeos são gravados para cada teste:
- Localização: `tests/reports/videos/`
- Formato: WebM
- Configuração: Habilitado por padrão, pode ser desabilitado via `PLAYWRIGHT_RECORD_VIDEO=false`

### Trace Viewer

Traces são salvos para debug detalhado:
- Localização: `tests/reports/traces/`
- Formato: ZIP (contém screenshots, snapshots e sources)
- Visualização: `make playwright-trace` ou `playwright show-trace tests/reports/traces/*.zip`
- Configuração: Habilitado por padrão, pode ser desabilitado via `PLAYWRIGHT_ENABLE_TRACE=false`

### Relatórios HTML

Gere relatórios HTML completos dos testes:
```bash
make test-playwright-report
# ou
pytest tests/e2e/playwright/ -v -m "playwright" --html=tests/reports/html/report.html --self-contained-html
```

### Testes em Múltiplos Navegadores

Execute testes em diferentes navegadores:

```bash
# Chromium (padrão)
make test-playwright-chromium
# ou
PLAYWRIGHT_BROWSER=chromium pytest tests/e2e/playwright/ -v -m "playwright"

# Firefox
make test-playwright-firefox
# ou
PLAYWRIGHT_BROWSER=firefox pytest tests/e2e/playwright/ -v -m "playwright"

# WebKit (Safari)
make test-playwright-webkit
# ou
PLAYWRIGHT_BROWSER=webkit pytest tests/e2e/playwright/ -v -m "playwright"

# Todos os navegadores
make test-playwright-all-browsers
```

**No CI/CD**: Os testes são executados automaticamente em todos os navegadores (Chromium, Firefox, WebKit) via matriz no GitHub Actions.

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|:---|:---|:---|
| `PLAYWRIGHT_BROWSER` | Navegador a usar (`chromium`, `firefox`, `webkit`) | `chromium` |
| `PLAYWRIGHT_HEADLESS` | Executar em modo headless | `true` |
| `PLAYWRIGHT_BASE_URL` | URL base da aplicação | `http://localhost:8000` |
| `PLAYWRIGHT_RECORD_VIDEO` | Gravar vídeos dos testes | `true` |
| `PLAYWRIGHT_ENABLE_TRACE` | Habilitar trace para debug | `true` |

## 🆕 Novos Testes Implementados

### Testes de Tratamento de Erros (Frontend)
- `test_error_handling.py` - 6 testes
  - Timeout de requisição
  - Erro offline
  - Rate limit (429)
  - Erro do servidor (500)
  - Cancelamento manual
  - Resposta malformada

### Testes de Performance
- `test_performance.py` - 4 testes
  - Múltiplas requisições sequenciais
  - Requisições paralelas bloqueadas
  - Mensagens longas (limites)
  - Histórico grande

### Testes de Segurança
- `test_security.py` - 4 testes
  - Prevenção XSS
  - Prevenção SQL Injection
  - Proteção CSRF
  - Rate limiting real

### Testes de Acessibilidade Avançados
- `test_accessibility_advanced.py` - 5 testes
  - Screen reader compatibility
  - Navegação por teclado completa
  - Modo de alto contraste
  - Zoom 200%
  - Redução de movimento

### Testes de UI/UX
- `test_ui_interactions.py` - 5 testes
  - Interação com expanders
  - Toast notifications
  - Auto-resize do textarea
  - Persistência de tema
  - Histórico de mensagens

### Testes de Responsividade
- `test_responsive_detailed.py` - 4 testes parametrizados
  - Breakpoints mobile (320px, 375px, 414px)
  - Breakpoints tablet (768px, 1024px)
  - Breakpoints desktop (1280px, 1920px)
  - Mudança de orientação

### Testes de Compatibilidade
- `test_browser_compatibility.py` - 4 testes
  - localStorage em todos os navegadores
  - Fetch API
  - AbortController
  - CSS Grid/Flexbox

### Testes de Fallback e Retry
- `test_fallback.py` - 3 testes
  - Fallback automático
  - Retry em erros temporários
  - Falha de todos os provedores

### Testes de Cache Avançado
- `test_cache_advanced.py` - 3 testes
  - Cache com TTL
  - Métricas detalhadas
  - Pipeline com falhas parciais

### Testes de Validação
- `test_validation.py` - 7 testes
  - Pergunta muito curta
  - Pergunta muito longa
  - Apenas espaços
  - Caracteres especiais
  - Emojis
  - HTML
  - Sanitização de padrões de injeção

**Total**: ~45 novos testes implementados

## 📈 Verificando Cobertura

### Relatório HTML
Após executar com `--cov-report=html`, abra:
```
htmlcov/index.html
```

### Cobertura por Arquivo
```bash
pytest --cov=src.chatbot_acessibilidade --cov=src.backend --cov-report=term-missing | grep -E "TOTAL|src/"
```

## 🎯 Meta de Cobertura

- **Mínimo**: 95% em todos os módulos
- **Ideal**: 98%+ em módulos críticos (pipeline, dispatcher, api)

## 📝 Adicionando Novos Testes

### Estrutura de um Teste
```python
def test_nome_descritivo():
    """Docstring explicando o que o teste verifica"""
    # Arrange (preparar)
    dado = "valor de teste"
    
    # Act (executar)
    resultado = funcao_sob_teste(dado)
    
    # Assert (verificar)
    assert resultado == "valor esperado"
```

### Testes Assíncronos
```python
async def test_funcao_async():
    resultado = await funcao_async()
    assert resultado == "esperado"
```

### Mocks
```python
from unittest.mock import patch, AsyncMock

@patch('modulo.funcao')
def test_com_mock(mock_funcao):
    mock_funcao.return_value = "valor mockado"
    # ...
```

## 🔍 Áreas que Precisam de Mais Testes

1. **Edge Cases de Erro**: Mais cenários de falha
2. **Integração**: Testes end-to-end
3. **Performance**: Testes de carga (futuro)
4. **Concorrência**: Múltiplas requisições simultâneas

## ✅ Checklist de Qualidade

Antes de fazer commit, verifique:
- [ ] Todos os testes passam: `pytest -v`
- [ ] Cobertura >= 95%: `pytest --cov=...`
- [ ] Sem erros de lint: `make lint`
- [ ] Testes são descritivos e bem documentados
- [ ] Edge cases estão cobertos

---

**Última atualização**: 2025-11-22

