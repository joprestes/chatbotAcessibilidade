# 🧪 Guia de Testes - Cobertura 95%

**Objetivo**: Manter cobertura mínima de 95% em todos os módulos do projeto.

## 📊 Estrutura de Testes

```
tests/
├── conftest.py              # Configuração global de testes
├── test_api.py              # Testes da API FastAPI
├── test_cache.py            # Testes do módulo de cache
├── test_config.py           # Testes de configuração
├── test_dispatcher.py       # Testes do dispatcher de agentes
├── test_factory.py          # Testes da factory de agentes
├── test_formatter.py        # Testes de formatação
├── test_llm_provider.py     # Testes de provedores LLM
├── test_pipeline.py         # Testes do pipeline principal
├── unit/                    # Testes unitários (futuro)
└── integration/            # Testes de integração (futuro)
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

### Testes Básicos
```bash
pytest -v
```

### Com Cobertura
```bash
pytest --cov=src.chatbot_acessibilidade --cov=src.backend --cov-report=term-missing --cov-report=html
```

### Apenas Testes Rápidos
```bash
pytest -v -m "not slow"
```

### Teste Específico
```bash
pytest tests/test_formatter.py -v
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

