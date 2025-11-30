"""
Testes de Contrato para APIs Externas

Estes testes validam que as bibliotecas externas funcionam conforme esperado,
detectando mudanças de API que podem quebrar nosso código.
"""

import pytest
from playwright.sync_api import sync_playwright
from axe_playwright_python.sync_playwright import Axe
from google import genai

pytestmark = pytest.mark.contract


class TestAxePlaywrightContract:
    """Testa contrato da biblioteca axe-playwright-python"""

    def test_axe_run_returns_response_dict(self):
        """Valida que axe.run() retorna objeto com atributo 'response' contendo dict"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content("<html><body><h1>Test</h1></body></html>")

            axe = Axe()
            results = axe.run(page)

            # Contrato: results deve ter atributo 'response'
            assert hasattr(results, "response"), "AxeResults deve ter atributo 'response'"

            # Contrato: response deve ser um dict
            assert isinstance(results.response, dict), "results.response deve ser um dict"

            # Contrato: response deve ter chave 'violations'
            assert "violations" in results.response, "results.response deve ter chave 'violations'"

            # Contrato: violations deve ser uma lista
            assert isinstance(results.response["violations"], list), "violations deve ser uma lista"

            browser.close()

    def test_axe_accepts_options_with_integer_values(self):
        """Valida que axe.run() aceita opções com valores inteiros (workaround para booleanos)"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content("<html><body><h1>Test</h1></body></html>")

            axe = Axe()

            # Contrato: deve aceitar inteiros em vez de booleanos
            try:
                axe.run(
                    page,
                    options={
                        "rules": {
                            "color-contrast": {"enabled": 1},  # 1 em vez de True
                        }
                    },
                )
                # Se chegou aqui, aceitou as opções
                assert True
            except Exception as e:
                pytest.fail(f"axe.run() não aceitou opções com valores inteiros: {str(e)}")

            browser.close()

    def test_axe_response_structure(self):
        """Valida estrutura completa do response do axe"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content("<html><body><h1>Test</h1></body></html>")

            axe = Axe()
            results = axe.run(page)

            # Contrato: response deve ter chaves esperadas
            expected_keys = ["violations", "passes", "incomplete", "inapplicable"]
            for key in expected_keys:
                assert key in results.response, f"results.response deve ter chave '{key}'"

            # Contrato: cada violation deve ter estrutura esperada
            if results.response["violations"]:
                violation = results.response["violations"][0]
                assert "id" in violation, "violation deve ter 'id'"
                assert "impact" in violation, "violation deve ter 'impact'"
                assert "nodes" in violation, "violation deve ter 'nodes'"

            browser.close()


class TestGoogleGenerativeAIContract:
    """Testa contrato da biblioteca google-generativeai"""

    def test_genai_client_initialization(self):
        """Valida que genai.Client pode ser inicializado com API key"""
        # Contrato: genai.Client deve aceitar api_key como parâmetro
        try:
            # Usa uma chave fake para testar apenas a inicialização
            client = genai.Client(api_key="fake_key_for_testing")
            assert client is not None, "genai.Client deve retornar uma instância"
        except (TypeError, ValueError) as e:
            # ValueError é esperado com chave fake, mas valida que aceita o parâmetro
            if "api_key" in str(e).lower():
                pytest.fail(f"genai.Client não aceita api_key como parâmetro: {str(e)}")
            # Se o erro for sobre chave inválida, está OK (aceita o parâmetro)
            assert True

    def test_genai_exceptions_exist(self):
        """Valida que exceções esperadas existem no módulo"""
        from google.api_core import exceptions as google_exceptions

        # Contrato: exceções devem existir
        assert hasattr(
            google_exceptions, "GoogleAPICallError"
        ), "google_exceptions deve ter GoogleAPICallError"
        assert hasattr(
            google_exceptions, "ResourceExhausted"
        ), "google_exceptions deve ter ResourceExhausted"
        assert hasattr(
            google_exceptions, "PermissionDenied"
        ), "google_exceptions deve ter PermissionDenied"

    def test_genai_error_has_code_attribute(self):
        """Valida que GoogleAPICallError tem atributo 'code'"""
        from google.api_core import exceptions as google_exceptions

        # Contrato: GoogleAPICallError deve ter atributo 'code'
        error = google_exceptions.GoogleAPICallError("Test error")
        assert hasattr(error, "code"), "GoogleAPICallError deve ter atributo 'code'"


class TestPlaywrightContract:
    """Testa contrato da biblioteca playwright"""

    def test_playwright_page_evaluate_accepts_js(self):
        """Valida que page.evaluate() aceita código JavaScript"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content("<html><body><h1>Test</h1></body></html>")

            # Contrato: page.evaluate() deve executar JavaScript
            result = page.evaluate("() => document.title")
            assert result == "", "page.evaluate() deve retornar resultado do JS"

            browser.close()

    def test_playwright_emulate_media_accepts_forced_colors(self):
        """Valida que page.emulate_media() aceita parâmetro forced_colors"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            # Contrato: deve aceitar forced_colors='active'
            try:
                page.emulate_media(forced_colors="active")
                assert True, "page.emulate_media() aceitou forced_colors"
            except TypeError as e:
                pytest.fail(f"page.emulate_media() não aceita forced_colors: {str(e)}")

            browser.close()


# Fixture para pular testes de contrato se bibliotecas não estiverem instaladas
@pytest.fixture(autouse=True)
def skip_if_missing_dependencies():
    """Pula testes se dependências não estiverem instaladas"""
    import importlib.util

    dependencies = ["playwright", "axe_playwright_python", "google.genai"]
    for dep in dependencies:
        spec = importlib.util.find_spec(dep.replace(".", "/"))
        if spec is None:
            pytest.skip(f"Dependência não instalada: {dep}")
