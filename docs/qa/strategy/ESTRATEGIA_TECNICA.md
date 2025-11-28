# 🧪 Estratégia de Testes - Guia Completo para QAs

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Pirâmide de Testes](#-pirâmide-de-testes)
- [Categorias de Testes](#-categorias-de-testes)
- [Padrões e Convenções](#-padrões-e-convenções)
- [Executando Testes](#-executando-testes)
- [Escrevendo Novos Testes](#-escrevendo-novos-testes)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Visão Geral

Este projeto implementa uma **estratégia de testes abrangente** seguindo as melhores práticas da indústria, com foco em **qualidade, manutenibilidade e confiabilidade**.

### Objetivos da Estratégia

1. **Confiança**: Garantir que mudanças não quebrem funcionalidades existentes
2. **Documentação Viva**: Testes servem como documentação executável
3. **Feedback Rápido**: Detectar problemas o mais cedo possível
4. **Qualidade**: Manter cobertura >= 95% em todo o código
5. **Referência**: Servir como exemplo de boas práticas para QAs

### Métricas Atuais

```
📊 Cobertura:  98.77% (meta: 95%)
✅ Testes:     335 testes (100% passando)
⏱️  Tempo:     ~2.4s (unit + integration)
🎭 E2E:        ~45s (Playwright)
```

---

## 🔺 Pirâmide de Testes

### Distribuição Ideal

```
        /\
       /E2E\      10-15% - Fluxos críticos end-to-end
      /------\
     /  INT  \    20-30% - Integração entre módulos
    /----------\
   /   UNIT    \  60-70% - Lógica de negócio isolada
  /--------------\
```

### Distribuição Atual vs Ideal

| Categoria | Atual | Ideal | Status |
|-----------|-------|-------|--------|
| **Unit** | 75% (~250) | 60-70% | ✅ BOM |
| **Integration** | 4% (~15) | 20-30% | 🔴 BAIXO |
| **E2E** | 21% (~70) | 10-15% | ⚠️ ALTO |

**Plano de Ação**: Rebalancear pirâmide criando mais testes de integração.

---

## 📚 Categorias de Testes

### 1. 🧪 Testes Unitários (`tests/unit/`)

#### Objetivo
Testar **unidades isoladas** de código (funções, classes, métodos) sem dependências externas.

#### Características
- ✅ **Rápidos**: < 100ms por teste
- ✅ **Isolados**: Sem I/O, banco de dados, APIs externas
- ✅ **Determinísticos**: Sempre mesmo resultado
- ✅ **Focados**: Um comportamento por teste

#### Quando Usar
- Validar lógica de negócio
- Testar edge cases e validações
- Testar formatação e transformação de dados
- Testar cálculos e algoritmos

#### Estrutura
```
tests/unit/
├── agents/              # Testes de agentes
│   ├── test_dispatcher.py
│   ├── test_factory.py
│   └── test_pipeline.py
├── backend/             # Testes de API
│   ├── test_api.py
│   ├── test_middleware.py
│   └── test_validation.py
└── core/                # Testes de utilitários
    ├── test_cache.py
    ├── test_config.py
    ├── test_formatter.py
    ├── test_llm_provider.py
    └── test_validators.py
```

#### Exemplo
```python
# tests/unit/core/test_validators.py
def test_sanitize_input_remove_caracteres_controle():
    \"\"\"
    Testa que sanitize_input remove caracteres de controle.
    
    Categoria: Unit Test
    Objetivo: Validar sanitização de input
    Edge Case: Caracteres de controle (\\x00, \\x01, etc)
    \"\"\"
    # Arrange
    input_text = "teste\\x00\\x01\\x02"
    
    # Act
    result = sanitize_input(input_text)
    
    # Assert
    assert "\\x00" not in result
    assert "\\x01" not in result
    assert "\\x02" not in result
    assert "teste" in result
```

#### Padrões
- ✅ Usar **mocks** para dependências externas
- ✅ Seguir padrão **AAA** (Arrange, Act, Assert)
- ✅ Nome descritivo: `test_<funcao>_<cenario>_<resultado_esperado>`
- ✅ Docstring explicando objetivo e edge case

---

### 2. 🔄 Testes de Integração (`tests/integration/`)

#### Objetivo
Testar **interação entre módulos** sem mockar tudo, validando que componentes funcionam juntos.

#### Características
- ⏱️ **Moderados**: 100ms - 1s por teste
- 🔗 **Integrados**: Testa comunicação entre módulos
- 🎯 **Realistas**: Usa dependências reais quando possível
- 📦 **Escopo Médio**: Testa fluxo entre 2-3 componentes

#### Quando Usar
- Validar integração entre agentes e pipeline
- Testar cache com API real
- Validar middleware com endpoints
- Testar LLM provider com dispatcher
- Validar formatters com pipeline

#### Estrutura
```
tests/integration/
├── test_agent_pipeline_integration.py    # Agentes + Pipeline
├── test_cache_api_integration.py         # Cache + API
├── test_cache_advanced.py                # Cache avançado
├── test_fallback.py                      # Fallback entre LLMs
├── test_llm_dispatcher_integration.py    # LLM + Dispatcher
├── test_middleware_endpoints.py          # Middleware + Endpoints
└── test_user_flow.py                     # Fluxo completo
```

#### Exemplo
```python
# tests/integration/test_cache_api_integration.py
@pytest.mark.integration
def test_cache_hit_on_duplicate_request(client: TestClient):
    \"\"\"
    Testa que cache funciona corretamente em requests duplicadas.
    
    Categoria: Integration Test
    Objetivo: Validar integração Cache + API
    Fluxo: Request 1 (miss) → Cache → Request 2 (hit)
    \"\"\"
    # Arrange
    cache = get_cache()
    cache.clear()
    pergunta = "O que é WCAG?"
    
    # Act - Primeira request (cache miss)
    response1 = client.post("/api/chat", json={"pergunta": pergunta})
    
    # Act - Segunda request (cache hit)
    response2 = client.post("/api/chat", json={"pergunta": pergunta})
    
    # Assert - Ambas retornam 200
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    # Assert - Respostas são idênticas
    assert response1.json() == response2.json()
    
    # Assert - Estatísticas de cache
    stats = cache.get_stats()
    assert stats["hits"] >= 1
    assert stats["misses"] >= 1
```

#### Padrões
- ✅ Usar **TestClient** para API
- ✅ Mockar apenas **dependências externas** (APIs de terceiros)
- ✅ Limpar estado entre testes (`cache.clear()`)
- ✅ Validar **efeitos colaterais** (cache, logs, métricas)

---

### 3. 🎭 Testes End-to-End (`tests/e2e/`)

#### Objetivo
Testar **fluxos completos** da perspectiva do usuário, incluindo frontend e backend.

#### Características
- 🐌 **Lentos**: 1s - 10s por teste
- 🌐 **Completos**: Testa sistema inteiro
- 👤 **Perspectiva do Usuário**: Simula interação real
- 🎯 **Críticos**: Apenas fluxos essenciais

#### Quando Usar
- Validar fluxos críticos de usuário
- Testar acessibilidade (WCAG)
- Validar responsividade
- Testar compatibilidade entre navegadores
- Validar segurança (XSS, CSRF)

#### Estrutura
```
tests/e2e/playwright/
├── conftest.py                          # Fixtures Playwright
├── pages/                               # Page Object Model
│   ├── base_page.py
│   ├── chat_page.py
│   └── components/
├── helpers/                             # Helpers
│   └── assertions.py
├── test_accessibility.py                # Testes WCAG
├── test_accessibility_advanced.py       # Testes WCAG avançados
├── test_api_playwright.py               # Testes de API
├── test_browser_compatibility.py        # Compatibilidade
├── test_error_handling.py               # Tratamento de erros
├── test_focus_management.py             # Gerenciamento de foco
├── test_frontend_playwright.py          # Testes de frontend
├── test_performance.py                  # Performance
├── test_responsive_detailed.py          # Responsividade
├── test_security.py                     # Segurança
└── test_ui_interactions.py              # Interações UI
```

#### Exemplo
```python
# tests/e2e/playwright/test_frontend_playwright.py
@pytest.mark.e2e
@pytest.mark.playwright
def test_send_message_flow(page: Page, base_url: str):
    \"\"\"
    Testa fluxo completo de envio de mensagem.
    
    Categoria: E2E Test
    Objetivo: Validar fluxo crítico de usuário
    Fluxo: Abrir app → Digitar → Enviar → Ver resposta
    \"\"\"
    # Arrange
    chat_page = ChatPage(page, base_url)
    chat_page.navigate()
    
    # Act
    chat_page.send_message("O que é acessibilidade digital?")
    
    # Assert
    chat_page.wait_for_user_message()
    chat_page.wait_for_assistant_message()
    
    last_message = chat_page.get_last_message_text(role="assistant")
    assert len(last_message) > 50
    assert "acessibilidade" in last_message.lower()
```

#### Padrões
- ✅ Usar **Page Object Model** (POM)
- ✅ **Waits determinísticos** (`expect()`, não `wait_for_timeout()`)
- ✅ Capturar **screenshots** em falhas
- ✅ Gravar **vídeos** de execução
- ✅ Testar em **múltiplos navegadores**

---

### 4. 📝 Testes de Contrato (`tests/contract/`)

#### Objetivo
Validar que **contratos de API** não quebram entre versões.

#### Características
- ⚡ **Rápidos**: < 500ms por teste
- 📋 **Schemas**: Valida estrutura de request/response
- 🔒 **Backward Compatibility**: Previne breaking changes
- 📚 **Documentação**: Serve como spec da API

#### Quando Usar
- Validar estrutura de requests
- Validar estrutura de responses
- Prevenir breaking changes
- Documentar contratos de API

#### Exemplo
```python
# tests/contract/test_api_contract.py
@pytest.mark.contract
def test_chat_endpoint_response_contract():
    \"\"\"
    Valida contrato de response do endpoint /api/chat.
    
    Categoria: Contract Test
    Objetivo: Prevenir breaking changes na API
    Valida: Estrutura, tipos e campos obrigatórios
    \"\"\"
    # Arrange
    client = TestClient(app)
    
    # Act
    response = client.post("/api/chat", json={"pergunta": "teste"})
    
    # Assert - Status
    assert response.status_code == 200
    
    # Assert - Estrutura
    data = response.json()
    assert "resposta" in data
    
    # Assert - Campos obrigatórios
    resposta = data["resposta"]
    required_fields = [
        "introducao", "corpo", "conclusao",
        "exemplos", "testes_sugeridos", 
        "materiais_estudo", "dica_final"
    ]
    for field in required_fields:
        assert field in resposta, f"Campo obrigatório '{field}' ausente!"
    
    # Assert - Tipos
    assert isinstance(resposta["introducao"], str)
    assert isinstance(resposta["exemplos"], list)
```

---

### 5. ⚡ Testes de Performance (`tests/performance/`)

#### Objetivo
Validar **performance** e **escalabilidade** sob carga.

#### Características
- 🐌 **Lentos**: 10s - 60s por teste
- 📊 **Métricas**: Latência, throughput, recursos
- 🎯 **SLAs**: Valida requisitos de performance
- 🔥 **Carga**: Simula múltiplos usuários

#### Quando Usar
- Validar tempo de resposta
- Testar rate limiting
- Validar escalabilidade
- Detectar memory leaks
- Testar sob carga

#### Exemplo
```python
# tests/performance/test_load.py
@pytest.mark.performance
def test_response_time_sla(client: TestClient):
    \"\"\"
    Valida que 95% das requests respondem em < 2s.
    
    Categoria: Performance Test
    Objetivo: Validar SLA de latência
    SLA: P95 < 2000ms
    \"\"\"
    # Arrange
    num_requests = 100
    times = []
    
    # Act
    for _ in range(num_requests):
        start = time.time()
        client.post("/api/chat", json={"pergunta": "teste"})
        end = time.time()
        times.append(end - start)
    
    # Assert
    times.sort()
    p95 = times[int(len(times) * 0.95)]
    assert p95 < 2.0, f"P95 latency {p95}s excede SLA de 2s"
```

---

### 6. 🔒 Testes de Segurança (`tests/security/`)

#### Objetivo
Validar **segurança** contra vetores de ataque conhecidos.

#### Características
- ⏱️ **Moderados**: 500ms - 2s por teste
- 🛡️ **OWASP Top 10**: Cobre principais vulnerabilidades
- 🎯 **Vetores**: Testa múltiplos payloads maliciosos
- 🔍 **Detecção**: Valida que ataques são bloqueados

#### Quando Usar
- Validar sanitização de input
- Testar proteção contra XSS
- Testar proteção contra SQL injection
- Validar CSRF protection
- Testar rate limiting

#### Exemplo
```python
# tests/security/test_security_advanced.py
@pytest.mark.security
def test_sql_injection_protection(client: TestClient):
    \"\"\"
    Valida proteção contra SQL injection.
    
    Categoria: Security Test
    Objetivo: Validar sanitização de input
    Vetores: OWASP SQL Injection payloads
    \"\"\"
    # Arrange
    sql_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE users--",
        "1' UNION SELECT NULL--",
    ]
    
    # Act & Assert
    for payload in sql_payloads:
        response = client.post("/api/chat", json={"pergunta": payload})
        
        # Deve sanitizar ou rejeitar
        assert response.status_code in [200, 400]
        
        # Resposta não deve conter evidências de SQL
        if response.status_code == 200:
            data = response.json()
            response_str = str(data).lower()
            assert "sql" not in response_str
            assert "syntax error" not in response_str
```

---

## 🎨 Padrões e Convenções

### Nomenclatura de Testes

```python
# ✅ BOM: Descritivo e claro
def test_sanitize_input_remove_caracteres_controle():
    pass

# ❌ RUIM: Vago e não descritivo
def test_sanitize():
    pass
```

### Padrão AAA (Arrange, Act, Assert)

```python
def test_exemplo():
    # Arrange - Preparar dados e mocks
    input_data = "teste"
    expected = "TESTE"
    
    # Act - Executar função sob teste
    result = funcao_sob_teste(input_data)
    
    # Assert - Verificar resultado
    assert result == expected
```

### Docstrings

```python
def test_exemplo():
    \"\"\"
    Descrição do que o teste valida.
    
    Categoria: Unit/Integration/E2E/Contract/Performance/Security
    Objetivo: O que está sendo testado
    Edge Case: Caso específico sendo validado (opcional)
    \"\"\"
    pass
```

### Fixtures

```python
# conftest.py
@pytest.fixture
def client():
    \"\"\"Cliente HTTP para testes de API.\"\"\"
    return TestClient(app)

@pytest.fixture(autouse=True)
def clear_cache():
    \"\"\"Limpa cache antes de cada teste.\"\"\"
    cache = get_cache()
    cache.clear()
    yield
    cache.clear()
```

---

## 🚀 Executando Testes

### Comandos Básicos

```bash
# Todos os testes
pytest -v

# Apenas unit tests
pytest tests/unit/ -v

# Apenas integration tests
pytest tests/integration/ -v

# Apenas E2E tests
pytest tests/e2e/ -v

# Por categoria (marker)
pytest -m unit -v
pytest -m integration -v
pytest -m e2e -v
```

### Com Cobertura

```bash
# Cobertura completa
pytest --cov=src --cov-report=html --cov-report=term

# Cobertura de módulo específico
pytest --cov=src.chatbot_acessibilidade.core --cov-report=term-missing
```

### Testes Específicos

```bash
# Arquivo específico
pytest tests/unit/core/test_validators.py -v

# Teste específico
pytest tests/unit/core/test_validators.py::test_sanitize_input_basico -v

# Testes que contêm palavra
pytest -k "sanitize" -v
```

### Makefile

```bash
# Instalar dependências
make install

# Executar testes
make test
make test-unit
make test-integration
make test-e2e

# Com cobertura
make test-cov

# Testes Playwright
make test-playwright
make test-playwright-ui  # Com UI visível
```

---

## ✍️ Escrevendo Novos Testes

### 1. Escolher Categoria

**Pergunte-se**:
- Testa uma função isolada? → **Unit**
- Testa integração entre módulos? → **Integration**
- Testa fluxo completo de usuário? → **E2E**
- Valida contrato de API? → **Contract**
- Testa performance? → **Performance**
- Testa segurança? → **Security**

### 2. Criar Arquivo

```bash
# Unit test
touch tests/unit/core/test_novo_modulo.py

# Integration test
touch tests/integration/test_nova_integracao.py

# E2E test
touch tests/e2e/playwright/test_novo_fluxo.py
```

### 3. Template Base

```python
\"\"\"
Descrição do módulo de testes.
\"\"\"
import pytest

pytestmark = pytest.mark.unit  # ou integration, e2e, etc


def test_cenario_basico():
    \"\"\"
    Testa cenário básico.
    
    Categoria: Unit Test
    Objetivo: Validar comportamento padrão
    \"\"\"
    # Arrange
    input_data = "teste"
    
    # Act
    result = funcao_sob_teste(input_data)
    
    # Assert
    assert result == "esperado"


def test_edge_case_entrada_vazia():
    \"\"\"
    Testa edge case: entrada vazia.
    
    Categoria: Unit Test
    Objetivo: Validar tratamento de entrada vazia
    Edge Case: Input vazio ou None
    \"\"\"
    # Arrange
    input_data = ""
    
    # Act
    result = funcao_sob_teste(input_data)
    
    # Assert
    assert result == ""  # ou comportamento esperado
```

---

## 🔧 Troubleshooting

### Testes Falhando

```bash
# Ver traceback completo
pytest -v --tb=long

# Ver apenas primeira falha
pytest -x

# Ver output de print
pytest -s

# Modo debug
pytest --pdb
```

### Testes Lentos

```bash
# Ver duração de cada teste
pytest --durations=10

# Executar apenas testes rápidos
pytest -m "not slow"
```

### Cache de Testes

```bash
# Limpar cache
pytest --cache-clear

# Ver cache
pytest --cache-show
```

---

## 📊 Métricas e Relatórios

### Cobertura

```bash
# Gerar relatório HTML
pytest --cov=src --cov-report=html

# Abrir relatório
open htmlcov/index.html
```

### Relatórios HTML

```bash
# Gerar relatório de testes
pytest --html=report.html --self-contained-html
```

### CI/CD

Testes são executados automaticamente no GitHub Actions:
- ✅ Em cada push
- ✅ Em cada pull request
- ✅ Diariamente (testes de acessibilidade)

---

## 🎯 Checklist de Qualidade

### Antes de Commitar
- [ ] Todos os testes passam
- [ ] Cobertura >= 95%
- [ ] Linters sem erros
- [ ] Testes seguem padrões
- [ ] Docstrings completas

### Antes de PR
- [ ] Testes de integração passam
- [ ] Testes E2E passam
- [ ] Sem testes skipped sem justificativa
- [ ] Documentação atualizada

---

## 📚 Referências

- [Pytest Documentation](https://docs.pytest.org/)
- [Playwright Documentation](https://playwright.dev/python/)
- [Testing Best Practices](https://testingjavascript.com/)
- [WCAG 2.2](https://www.w3.org/WAI/WCAG22/quickref/)

---

**Última atualização**: 2025-11-26
**Versão**: 2.0
**Autor**: Equipe de QA
