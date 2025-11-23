# 🧪 Guia de Testes - Cobertura 95%

**Objetivo**: Manter cobertura mínima de 95% em todos os módulos do projeto.

## 📊 Estrutura de Testes

A estrutura de testes segue a **Pirâmide de Testes**, organizando os testes por tipo:

```
tests/
├── conftest.py                    # Configuração global de testes
│
├── unit/                          # 🧪 Testes Unitários (Base da Pirâmide)
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
├── integration/                   # 🔄 Testes de Integração (Meio da Pirâmide)
│   ├── conftest.py               # Fixtures específicas de integração
│   └── test_user_flow.py         # Fluxo completo do usuário
│
└── e2e/                           # 🎭 Testes End-to-End (Topo da Pirâmide)
    └── playwright/                # Testes com Playwright
        ├── conftest.py
        ├── test_api_playwright.py
        ├── test_frontend_playwright.py
        └── test_accessibility.py
```

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
- ✅ Parse de modelos OpenRouter
- ✅ Validação de fallback config

#### 5. `llm_provider.py` - ~95%
- ✅ `GoogleGeminiClient` - Sucesso, erros, timeout, segurança
- ✅ `OpenRouterClient` - Sucesso, rate limit, erros HTTP
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

