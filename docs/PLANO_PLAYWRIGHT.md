# 🎭 Plano de Implementação - Playwright

## 📋 Objetivo

Implementar testes E2E automatizados com Playwright para validar tanto a API quanto o frontend em navegadores reais, garantindo qualidade e acessibilidade.

---

## 🎯 Benefícios do Playwright

1. **Navegadores Reais**: Testa em Chrome, Firefox, Safari (WebKit)
2. **Testes de API**: Pode testar endpoints REST diretamente
3. **Acessibilidade**: Integração com axe-core para testes automatizados
4. **Screenshots/Vídeos**: Captura automática de evidências
5. **Auto-wait**: Aguarda elementos automaticamente (mais robusto)
6. **Trace Viewer**: Debug visual de testes
7. **CI/CD Ready**: Funciona perfeitamente em pipelines

---

## 📦 Dependências

```txt
# Adicionar ao requirements.txt
pytest-playwright>=0.4.0
playwright>=1.40.0
axe-playwright>=1.0.0  # Para testes de acessibilidade
```

---

## 🏗️ Estrutura de Testes

```
tests/
├── e2e/
│   ├── playwright/
│   │   ├── __init__.py
│   │   ├── conftest.py              # Configuração Playwright
│   │   ├── test_api_playwright.py   # Testes de API com Playwright
│   │   ├── test_frontend_playwright.py  # Testes de UI
│   │   ├── test_accessibility.py    # Testes de acessibilidade
│   │   └── fixtures/
│   │       └── page_fixtures.py     # Fixtures reutilizáveis
│   └── test_user_flow.py            # Testes E2E existentes (manter)
```

---

## 🧪 Cenários de Teste

### 1. Testes de API com Playwright

#### `test_api_playwright.py`

```python
# Exemplos de testes:
- test_api_health_check()
- test_api_chat_endpoint_success()
- test_api_chat_endpoint_validation_error()
- test_api_config_endpoint()
- test_api_metrics_endpoint()
- test_api_cors_headers()
- test_api_rate_limiting()
- test_api_static_files()
```

**Vantagens sobre TestClient:**
- Testa HTTP real (não bypass do FastAPI)
- Pode testar headers, cookies, redirects
- Melhor para testes de CORS e segurança

### 2. Testes de Frontend

#### `test_frontend_playwright.py`

```python
# Exemplos de testes:
- test_homepage_loads()
- test_chat_interface_visible()
- test_send_message_flow()
- test_message_appears_in_chat()
- test_typing_indicator_shows()
- test_error_message_display()
- test_theme_toggle()
- test_search_functionality()
- test_clear_chat_button()
- test_suggestion_chips_click()
- test_responsive_layout()
- test_keyboard_navigation()
```

### 3. Testes de Acessibilidade

#### `test_accessibility.py`

```python
# Exemplos de testes:
- test_homepage_accessibility()
- test_chat_interface_accessibility()
- test_keyboard_navigation()
- test_screen_reader_compatibility()
- test_color_contrast()
- test_aria_labels()
- test_focus_management()
- test_skip_links()
```

---

## ⚙️ Configuração

### 1. `conftest.py` (Playwright)

```python
import pytest
from playwright.sync_api import Page, Browser, BrowserContext
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    """Inicia navegador uma vez por sessão"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture
def page(browser: Browser):
    """Cria nova página para cada teste"""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()

@pytest.fixture
def base_url():
    """URL base da aplicação"""
    return "http://localhost:8000"
```

### 2. `pytest.ini` ou `pyproject.toml`

```toml
[tool.pytest.ini_options]
markers = [
    "playwright: marca testes que usam Playwright",
    "api: marca testes de API",
    "frontend: marca testes de frontend",
    "accessibility: marca testes de acessibilidade",
    "slow: marca testes lentos",
]
```

---

## 🚀 Execução

### Instalar Playwright

```bash
# Instalar dependências Python
pip install pytest-playwright playwright axe-playwright

# Instalar navegadores
playwright install chromium firefox webkit
```

### Executar Testes

```bash
# Todos os testes Playwright
pytest tests/e2e/playwright/ -v

# Apenas testes de API
pytest tests/e2e/playwright/test_api_playwright.py -v

# Apenas testes de frontend
pytest tests/e2e/playwright/test_frontend_playwright.py -v

# Apenas testes de acessibilidade
pytest tests/e2e/playwright/test_accessibility.py -v

# Com UI (modo headed)
pytest tests/e2e/playwright/ --headed

# Com trace (para debug)
pytest tests/e2e/playwright/ --tracing on
```

---

## 📊 Integração com CI/CD

### GitHub Actions

```yaml
- name: Install Playwright Browsers
  run: playwright install --with-deps chromium

- name: Run Playwright tests
  run: pytest tests/e2e/playwright/ --html=report.html
```

---

## 🎯 Ordem de Implementação

1. ✅ **Setup Inicial** (Dependências e configuração)
2. ✅ **Testes de API** (Substituir/complementar TestClient)
3. ✅ **Testes de Frontend Básicos** (Carregamento, elementos visíveis)
4. ✅ **Testes de Interação** (Clicks, formulários, navegação)
5. ✅ **Testes de Acessibilidade** (axe-core)
6. ✅ **Testes de Responsividade** (Mobile, tablet, desktop)
7. ✅ **CI/CD Integration** (GitHub Actions)

---

## 📝 Exemplos de Testes

### Exemplo 1: Teste de API

```python
def test_api_chat_endpoint(page: Page, base_url: str):
    """Testa endpoint de chat via Playwright"""
    response = page.request.post(
        f"{base_url}/api/chat",
        data={"pergunta": "O que é WCAG?"}
    )
    
    assert response.status == 200
    data = response.json()
    assert "resposta" in data
```

### Exemplo 2: Teste de Frontend

```python
def test_send_message_flow(page: Page, base_url: str):
    """Testa fluxo completo de envio de mensagem"""
    page.goto(base_url)
    
    # Espera input aparecer
    input_field = page.locator('[data-testid="input-pergunta"]')
    input_field.fill("O que é acessibilidade?")
    
    # Clica em enviar
    send_button = page.locator('[data-testid="btn-enviar"]')
    send_button.click()
    
    # Verifica que mensagem aparece
    message = page.locator('[data-testid="chat-mensagem-user"]')
    assert message.is_visible()
    assert "acessibilidade" in message.text_content().lower()
```

### Exemplo 3: Teste de Acessibilidade

```python
from axe_playwright_python.sync_playwright import Axe

def test_homepage_accessibility(page: Page, base_url: str):
    """Testa acessibilidade da homepage"""
    page.goto(base_url)
    
    axe = Axe()
    results = axe.run(page)
    
    assert len(results.violations) == 0, f"Violations: {results.violations}"
```

---

## 🔄 Migração Gradual

1. **Fase 1**: Adicionar Playwright sem remover TestClient
2. **Fase 2**: Migrar testes críticos para Playwright
3. **Fase 3**: Adicionar novos testes apenas em Playwright
4. **Fase 4**: (Opcional) Remover TestClient se não for mais necessário

---

## 📈 Métricas Esperadas

- **Cobertura E2E**: 100% dos fluxos críticos
- **Testes de Acessibilidade**: 0 violações WCAG AA
- **Tempo de Execução**: < 5 minutos para suite completa
- **Estabilidade**: > 95% de taxa de sucesso

---

## 🎓 Recursos

- [Playwright Python Docs](https://playwright.dev/python/)
- [pytest-playwright](https://github.com/microsoft/playwright-python)
- [axe-playwright](https://github.com/abhinaba-ghosh/axe-playwright-python)
- [Best Practices](https://playwright.dev/python/docs/best-practices)

---

**Status**: 📋 Planejado | 🚧 Em Implementação | ✅ Concluído

