"""
Page Object para a página principal de chat.

Encapsula todos os elementos e ações relacionadas à interface de chat,
incluindo envio de mensagens, limpeza, busca e alternância de tema.
"""

from playwright.sync_api import Page, expect
from .base_page import BasePage
from typing import Optional


class ChatPage(BasePage):
    """Page Object para a página de chat"""

    def __init__(self, page: Page, base_url: str):
        """
        Inicializa a página de chat.

        Args:
            page: Instância do Playwright Page
            base_url: URL base da aplicação
        """
        super().__init__(page, base_url)

        # Locators - elementos principais da interface
        self.input = page.get_by_test_id("input-pergunta")
        self.send_button = page.get_by_test_id("btn-enviar")
        self.clear_button = page.get_by_test_id("btn-limpar-chat")
        self.search_button = page.get_by_test_id("btn-buscar")
        self.theme_toggle = page.get_by_test_id("btn-toggle-tema")
        self.intro_card = page.get_by_test_id("intro-card")
        self.header = page.locator("header")

    # ==========================================
    # Ações de Mensagem
    # ==========================================

    def send_message(self, text: str, wait_for_response: bool = True):
        """
        Envia uma mensagem no chat.

        Args:
            text: Texto da mensagem
            wait_for_response: Se True, aguarda mensagem do usuário aparecer
        """
        self.input.fill(text)
        self.send_button.click()

        if wait_for_response:
            self.wait_for_user_message()

    def wait_for_user_message(self, timeout: int = 5000):
        """
        Aguarda mensagem do usuário aparecer.

        Args:
            timeout: Timeout em milissegundos
        """
        user_message = self.page.get_by_test_id("chat-mensagem-user").first
        expect(user_message).to_be_visible(timeout=timeout)

    def wait_for_assistant_message(self, timeout: int = 10000):
        """
        Aguarda mensagem do assistente aparecer.

        Args:
            timeout: Timeout em milissegundos
        """
        assistant_message = self.page.get_by_test_id("chat-mensagem-assistant").first
        expect(assistant_message).to_be_visible(timeout=timeout)

    def get_last_message_text(self, role: str = "user") -> str:
        """
        Retorna texto da última mensagem.

        Args:
            role: Papel da mensagem (user ou assistant)

        Returns:
            Texto da mensagem ou string vazia
        """
        message = self.page.get_by_test_id(f"chat-mensagem-{role}").last
        return message.text_content() or ""

    def get_message_count(self, role: Optional[str] = None) -> int:
        """
        Retorna quantidade de mensagens.

        Args:
            role: Se especificado, conta apenas mensagens desse papel

        Returns:
            Número de mensagens
        """
        if role:
            messages = self.page.get_by_test_id(f"chat-mensagem-{role}")
        else:
            messages = self.page.locator("[data-testid^='chat-mensagem-']")
        return messages.count()

    # ==========================================
    # Ações de Interface
    # ==========================================

    def clear_chat(self, confirm: bool = True):
        """
        Limpa o chat.

        Args:
            confirm: Se True, confirma o diálogo de confirmação
        """
        if confirm:
            # Configura handler para aceitar diálogo
            self.page.on("dialog", lambda dialog: dialog.accept())

        self.clear_button.click()

        if confirm:
            # Aguarda card de introdução aparecer
            expect(self.intro_card).to_be_visible(timeout=2000)

    def toggle_theme(self) -> str:
        """
        Alterna o tema da interface.

        Returns:
            Novo tema aplicado (light ou dark)
        """
        self.theme_toggle.click()
        # Aguarda animação de transição
        self.page.wait_for_timeout(500)

        theme = self.page.evaluate("() => document.documentElement.getAttribute('data-theme')")
        return theme or "light"

    def get_current_theme(self) -> str:
        """
        Retorna tema atual.

        Returns:
            Tema atual (light ou dark)
        """
        theme = self.page.evaluate("() => document.documentElement.getAttribute('data-theme')")
        return theme or "light"

    def open_search(self):
        """Abre o campo de busca"""
        self.search_button.click()
        search_input = self.page.get_by_test_id("search-input")
        expect(search_input).to_be_visible(timeout=2000)

    def search(self, query: str):
        """
        Busca no histórico.

        Args:
            query: Texto a buscar
        """
        self.open_search()
        search_input = self.page.get_by_test_id("search-input")
        search_input.fill(query)
        # Aguarda resultados aparecerem
        self.page.wait_for_timeout(500)

    def click_suggestion_chip(self, chip_id: str):
        """
        Clica em um chip de sugestão.

        Args:
            chip_id: ID do chip (ex: 'chip-contraste')
        """
        chip = self.page.get_by_test_id(chip_id).first
        if chip.is_visible():
            chip.click()

    # ==========================================
    # Verificações
    # ==========================================

    def is_intro_card_visible(self) -> bool:
        """Verifica se card de introdução está visível"""
        return self.intro_card.is_visible()

    def is_typing_indicator_visible(self) -> bool:
        """Verifica se indicador de digitação está visível"""
        typing_indicator = self.page.locator("text=Aguarde que estou pesquisando")
        try:
            typing_indicator.wait_for(state="visible", timeout=2000)
            return True
        except Exception:
            return False

    def get_input_value(self) -> str:
        """Retorna valor atual do input"""
        return self.input.input_value()

    def is_send_button_enabled(self) -> bool:
        """Verifica se botão de enviar está habilitado"""
        return self.send_button.is_enabled()

    # ==========================================
    # Navegação por Teclado
    # ==========================================

    def press_enter_on_input(self):
        """Pressiona Enter no input (envia mensagem)"""
        self.input.focus()
        self.page.keyboard.press("Enter")

    def get_focused_element_id(self) -> str:
        """
        Retorna ID do elemento com foco.

        Returns:
            ID do elemento focado ou string vazia
        """
        return self.page.evaluate("() => document.activeElement.id") or ""

    def tab_navigate(self, times: int = 1):
        """
        Navega por Tab.

        Args:
            times: Número de vezes para pressionar Tab
        """
        for _ in range(times):
            self.page.keyboard.press("Tab")
            self.page.wait_for_timeout(200)
