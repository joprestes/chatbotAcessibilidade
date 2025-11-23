"""
Configuração do Playwright para testes E2E
"""

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright
from typing import Generator
import os
from pathlib import Path
import sys

# Adiciona src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def browser() -> Generator[Browser, None, None]:
    """
    Inicia navegador uma vez por sessão de testes.
    Usa Chromium por padrão, mas pode ser configurado via variável de ambiente.
    """
    browser_type = os.getenv("PLAYWRIGHT_BROWSER", "chromium")
    headless = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
    
    with sync_playwright() as p:
        if browser_type == "firefox":
            browser = p.firefox.launch(headless=headless)
        elif browser_type == "webkit":
            browser = p.webkit.launch(headless=headless)
        else:
            browser = p.chromium.launch(headless=headless)
        
        yield browser
        browser.close()


@pytest.fixture
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """
    Cria um novo contexto de navegador para cada teste.
    Isola cookies, localStorage, etc.
    """
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        locale="pt-BR",
        timezone_id="America/Sao_Paulo",
    )
    yield context
    context.close()


@pytest.fixture
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """
    Cria uma nova página para cada teste.
    """
    page = context.new_page()
    
    # Configura timeout padrão
    page.set_default_timeout(30000)  # 30 segundos
    
    yield page
    
    # Fecha a página ao final do teste
    page.close()


@pytest.fixture
def base_url() -> str:
    """
    URL base da aplicação para testes.
    Pode ser configurada via variável de ambiente PLAYWRIGHT_BASE_URL.
    """
    return os.getenv("PLAYWRIGHT_BASE_URL", "http://localhost:8000")


@pytest.fixture
def server_running(base_url: str) -> bool:
    """
    Verifica se o servidor está rodando.
    Retorna True se conseguir acessar /api/health.
    """
    import httpx
    
    try:
        response = httpx.get(f"{base_url}/api/health", timeout=2.0)
        return response.status_code == 200
    except Exception:
        return False


# Markers para pytest
pytest_plugins = ["pytest_playwright"]

