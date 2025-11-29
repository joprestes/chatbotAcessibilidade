"""
Classe base para Page Objects.

Fornece métodos comuns para todas as páginas, como navegação,
waits inteligentes e interações básicas.
"""

from playwright.sync_api import Page
from typing import Optional, Literal


class BasePage:
    """Classe base para todos os Page Objects"""

    def __init__(self, page: Page, base_url: str):
        """
        Inicializa a página base.

        Args:
            page: Instância do Playwright Page
            base_url: URL base da aplicação
        """
        self.page = page
        self.base_url = base_url

    def navigate(self, path: str = ""):
        """
        Navega para uma URL.

        Args:
            path: Caminho relativo à base_url (opcional)
        """
        url = f"{self.base_url}{path}"
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")

    def wait_for_element(self, selector: str, timeout: int = 5000, state: Literal["attached", "detached", "hidden", "visible"] = "visible"):
        """
        Aguarda elemento estar em determinado estado.

        Args:
            selector: Seletor CSS ou test-id
            timeout: Timeout em milissegundos
            state: Estado esperado (visible, hidden, attached, detached)
        """
        self.page.wait_for_selector(selector, state=state, timeout=timeout)

    def get_text(self, selector: str) -> str:
        """
        Retorna texto de um elemento.

        Args:
            selector: Seletor CSS ou test-id

        Returns:
            Texto do elemento ou string vazia
        """
        element = self.page.locator(selector)
        return element.text_content() or ""

    def click(self, selector: str, timeout: int = 5000):
        """
        Clica em um elemento.

        Args:
            selector: Seletor CSS ou test-id
            timeout: Timeout em milissegundos
        """
        element = self.page.locator(selector)
        element.click(timeout=timeout)

    def fill(self, selector: str, text: str, timeout: int = 5000):
        """
        Preenche um campo de texto.

        Args:
            selector: Seletor CSS ou test-id
            text: Texto a preencher
            timeout: Timeout em milissegundos
        """
        element = self.page.locator(selector)
        element.fill(text, timeout=timeout)

    def is_visible(self, selector: str, timeout: int = 1000) -> bool:
        """
        Verifica se elemento está visível.

        Args:
            selector: Seletor CSS ou test-id
            timeout: Timeout em milissegundos

        Returns:
            True se visível, False caso contrário
        """
        try:
            element = self.page.locator(selector)
            element.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """
        Retorna atributo de um elemento.

        Args:
            selector: Seletor CSS ou test-id
            attribute: Nome do atributo

        Returns:
            Valor do atributo ou None
        """
        element = self.page.locator(selector)
        return element.get_attribute(attribute)

    def evaluate_script(self, script: str):
        """
        Executa JavaScript na página.

        Args:
            script: Código JavaScript a executar

        Returns:
            Resultado da execução
        """
        return self.page.evaluate(script)

    def get_current_url(self) -> str:
        """Retorna URL atual da página"""
        return self.page.url

    def get_title(self) -> str:
        """Retorna título da página"""
        return self.page.title()

    def take_screenshot(self, path: str, full_page: bool = True):
        """
        Captura screenshot da página.

        Args:
            path: Caminho onde salvar o screenshot
            full_page: Se True, captura página inteira
        """
        self.page.screenshot(path=path, full_page=full_page)
