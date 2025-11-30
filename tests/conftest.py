import webbrowser
import os
import sys
import warnings
from pathlib import Path

# Configura variáveis de ambiente para testes ANTES de importar qualquer módulo
# Isso garante que Settings() possa ser inicializado corretamente
os.environ.setdefault("GOOGLE_API_KEY", "test_key_for_pytest")

# Desabilita rate limiting durante testes para evitar falhas por 429
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

# Suprime warnings de dependências externas e ambiente
try:
    from urllib3.exceptions import NotOpenSSLWarning

    warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
except ImportError:
    pass
warnings.filterwarnings("ignore", category=FutureWarning, module="google.api_core")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="google.genai")

import asyncio  # noqa: E402
import pytest  # noqa: E402
import nest_asyncio  # noqa: E402

# Aplica nest_asyncio para permitir loops aninhados (necessário para testes com pytest-asyncio + playwright)
nest_asyncio.apply()

# Configura plugins do pytest
# pytest_plugins = ("pytest_asyncio", "pytest_playwright")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_teardown(item):
    """
    Hook executado após cada teste.
    
    Suprime RuntimeError de event loop que ocorre durante teardown
    de testes async quando exceções são lançadas.
    """
    outcome = yield
    if outcome.excinfo:
        exc_type, exc_value, traceback = outcome.excinfo
        # Verifica se é o erro de event loop específico
        if isinstance(exc_value, RuntimeError) and "Cannot close a running event loop" in str(exc_value):
            outcome.force_result(None)
        # Verifica se é um ExceptionGroup contendo o erro (comum em pytest 8+)
        elif hasattr(exc_value, "exceptions"):
            # Se for o único erro no grupo, suprime tudo
            is_only_loop_error = all(
                isinstance(e, RuntimeError) and "Cannot close a running event loop" in str(e)
                for e in exc_value.exceptions
            )
            if is_only_loop_error:
                outcome.force_result(None)


def pytest_configure(config):
    """Configuração executada uma vez no início da sessão de testes."""
    # Suprime warnings específicos de event loop
    warnings.filterwarnings(
        "ignore",
        message=".*Cannot close a running event loop.*",
        category=RuntimeWarning,
    )


# Adiciona src ao path para imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def pytest_sessionfinish(session):
    """
    Este hook é chamado após toda a sessão de testes terminar.
    Ele verifica se um relatório HTML foi gerado e tenta abri-lo.
    """
    # A opção --html salva o caminho do relatório em session.config.option.htmlpath
    # Usamos getattr para evitar um erro caso a opção --html não seja usada.
    html_report_path = getattr(session.config.option, "htmlpath", None)

    if html_report_path:
        # Constrói o caminho absoluto para o arquivo (melhor para webbrowser)
        absolute_html_path = os.path.abspath(html_report_path)
        print(f"\nFim da sessão de testes. Tentando abrir o relatório HTML: {absolute_html_path}")
        try:
            # file_uri garante que funcione bem em diferentes sistemas, especialmente no Windows
            file_uri = f"file://{absolute_html_path}"
            webbrowser.open_new_tab(file_uri)
            print(f"Relatório solicitado para abertura em: {file_uri}")
        except Exception as e:
            print(f"Não foi possível abrir o relatório HTML no navegador: {e}")
    else:
        print("\nFim da sessão de testes. Nenhum caminho de relatório HTML configurado para abrir.")
