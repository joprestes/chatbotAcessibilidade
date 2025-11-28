"""
Configuração do Playwright para testes E2E
"""

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright
from typing import Generator
import os
from pathlib import Path
import sys
from datetime import datetime

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
    Configura gravação de vídeo e trace se habilitados via variável de ambiente.
    """
    # Verifica se gravação de vídeo está habilitada
    record_video = os.getenv("PLAYWRIGHT_RECORD_VIDEO", "true").lower() == "true"
    # Verifica se trace está habilitado
    enable_trace = os.getenv("PLAYWRIGHT_ENABLE_TRACE", "true").lower() == "true"

    from typing import Any, Dict

    context_options: Dict[str, Any] = {
        "viewport": {"width": 1280, "height": 720},
        "locale": "pt-BR",
        "timezone_id": "America/Sao_Paulo",
    }

    # Adiciona gravação de vídeo se habilitada
    if record_video:
        video_dir = Path("tests/reports/videos")
        video_dir.mkdir(parents=True, exist_ok=True)
        context_options["record_video_dir"] = str(video_dir)
        context_options["record_video_size"] = {"width": 1280, "height": 720}

    context = browser.new_context(**context_options)

    # Inicia trace se habilitado
    if enable_trace:
        trace_dir = Path("tests/reports/traces")
        trace_dir.mkdir(parents=True, exist_ok=True)
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield context

    # Salva trace se habilitado
    if enable_trace:
        trace_path = trace_dir / f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        try:
            context.tracing.stop(path=str(trace_path))
            print(f"\n🔍 Trace salvo em: {trace_path}")
        except Exception as e:
            print(f"\n⚠️  Erro ao salvar trace: {e}")

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


@pytest.fixture(scope="session")
def base_url() -> str:
    """
    URL base da aplicação para testes.
    Pode ser configurada via variável de ambiente PLAYWRIGHT_BASE_URL.
    """
    return os.getenv("PLAYWRIGHT_BASE_URL", "http://localhost:8000")


@pytest.fixture
def api_context(page: Page, base_url: str):
    """
    Cria um contexto de API para fazer requisições HTTP.
    """
    return page.request


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


# pytest_plugins movido para tests/conftest.py (top-level)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook para capturar screenshots e traces automaticamente quando testes falham.
    """
    outcome = yield
    rep = outcome.get_result()

    # Captura screenshot e trace apenas quando o teste falha na fase de execução
    if rep.when == "call" and rep.failed:
        # Verifica se a fixture 'page' está disponível
        if "page" in item.funcargs:
            try:
                page = item.funcargs["page"]

                # Captura screenshot
                screenshot_dir = Path("tests/reports/screenshots")
                screenshot_dir.mkdir(parents=True, exist_ok=True)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                test_name = item.nodeid.replace("::", "_").replace("/", "_").replace("\\", "_")
                # Remove caracteres inválidos para nome de arquivo
                test_name = "".join(c for c in test_name if c.isalnum() or c in ("_", "-", "."))[
                    :100
                ]
                screenshot_path = screenshot_dir / f"{test_name}_{timestamp}.png"

                # Captura screenshot da página inteira
                page.screenshot(path=str(screenshot_path), full_page=True)
                print(f"\n📸 Screenshot salvo em: {screenshot_path}")
            except Exception as e:
                print(f"\n⚠️  Erro ao capturar screenshot: {e}")

        # Salva trace imediatamente em caso de falha
        if "context" in item.funcargs:
            try:
                context = item.funcargs["context"]
                enable_trace = os.getenv("PLAYWRIGHT_ENABLE_TRACE", "true").lower() == "true"

                if enable_trace:
                    trace_dir = Path("tests/reports/traces")
                    trace_dir.mkdir(parents=True, exist_ok=True)

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    test_name = item.nodeid.replace("::", "_").replace("/", "_").replace("\\", "_")
                    test_name = "".join(
                        c for c in test_name if c.isalnum() or c in ("_", "-", ".")
                    )[:100]
                    trace_path = trace_dir / f"trace_{test_name}_{timestamp}.zip"

                    context.tracing.stop(path=str(trace_path))
                    print(f"\n🔍 Trace de falha salvo em: {trace_path}")
            except Exception as e:
                print(f"\n⚠️  Erro ao salvar trace: {e}")
