"""
Exemplo de teste refatorado usando Page Object Model.

Este arquivo demonstra como usar os Page Objects para criar
testes mais limpos, legíveis e manuteníveis.
"""

import pytest
from playwright.sync_api import Page
from pages.chat_page import ChatPage
from helpers.assertions import (
    assert_element_visible,
)

pytestmark = [pytest.mark.e2e, pytest.mark.playwright, pytest.mark.example]


def test_send_message_with_pom(page: Page, base_url: str):
    """
    Exemplo: Testa envio de mensagem usando Page Object Model.
    
    Compare com a versão antiga em test_frontend_playwright.py
    para ver a diferença em legibilidade e manutenibilidade.
    """
    # Arrange - Cria e navega para a página
    chat_page = ChatPage(page, base_url)
    chat_page.navigate()
    
    # Act - Envia mensagem
    message_text = "O que é acessibilidade?"
    chat_page.send_message(message_text)
    
    # Assert - Verifica que mensagem apareceu
    last_message = chat_page.get_last_message_text(role="user")
    assert message_text.lower() in last_message.lower()


def test_clear_chat_with_pom(page: Page, base_url: str):
    """
    Exemplo: Testa limpeza de chat usando Page Object Model.
    """
    # Arrange
    chat_page = ChatPage(page, base_url)
    chat_page.navigate()
    
    # Envia mensagem primeiro
    chat_page.send_message("Mensagem de teste")
    
    # Act - Limpa chat
    chat_page.clear_chat(confirm=True)
    
    # Assert - Verifica que card de introdução voltou
    assert chat_page.is_intro_card_visible()


def test_theme_toggle_with_pom(page: Page, base_url: str):
    """
    Exemplo: Testa alternância de tema usando Page Object Model.
    """
    # Arrange
    chat_page = ChatPage(page, base_url)
    chat_page.navigate()
    
    # Captura tema inicial
    initial_theme = chat_page.get_current_theme()
    
    # Act - Alterna tema
    new_theme = chat_page.toggle_theme()
    
    # Assert - Verifica que tema mudou
    assert new_theme != initial_theme


def test_search_with_pom(page: Page, base_url: str):
    """
    Exemplo: Testa busca usando Page Object Model.
    """
    # Arrange
    chat_page = ChatPage(page, base_url)
    chat_page.navigate()
    
    # Envia algumas mensagens
    chat_page.send_message("Primeira mensagem")
    chat_page.send_message("Segunda mensagem")
    
    # Act - Busca
    chat_page.search("Primeira")
    
    # Assert - Verifica que campo de busca está visível
    assert_element_visible(page, "[data-testid='search-input']")


def test_keyboard_navigation_with_pom(page: Page, base_url: str):
    """
    Exemplo: Testa navegação por teclado usando Page Object Model.
    """
    # Arrange
    chat_page = ChatPage(page, base_url)
    chat_page.navigate()
    
    # Act - Preenche input e pressiona Enter
    chat_page.input.fill("Teste teclado")
    chat_page.press_enter_on_input()
    
    # Assert - Verifica que mensagem foi enviada
    chat_page.wait_for_user_message()
    assert chat_page.get_message_count(role="user") >= 1


def test_suggestion_chip_with_pom(page: Page, base_url: str):
    """
    Exemplo: Testa chip de sugestão usando Page Object Model.
    """
    # Arrange
    chat_page = ChatPage(page, base_url)
    chat_page.navigate()
    
    # Act - Clica em chip de sugestão
    chat_page.click_suggestion_chip("chip-contraste")
    
    # Assert - Verifica que input foi preenchido
    input_value = chat_page.get_input_value()
    assert len(input_value) > 0


# ==========================================
# Comparação: Antes vs Depois
# ==========================================

"""
ANTES (sem Page Object Model):
--------------------------------
def test_send_message_flow(page: Page, base_url: str):
    page.goto(base_url)
    
    input_field = page.get_by_test_id("input-pergunta")
    input_field.fill("O que é acessibilidade?")
    
    send_button = page.get_by_test_id("btn-enviar")
    send_button.click()
    
    user_message = page.get_by_test_id("chat-mensagem-user").first
    expect(user_message).to_be_visible(timeout=5000)
    
    assert "acessibilidade" in user_message.text_content().lower()


DEPOIS (com Page Object Model):
--------------------------------
def test_send_message_with_pom(page: Page, base_url: str):
    chat_page = ChatPage(page, base_url)
    chat_page.navigate()
    
    chat_page.send_message("O que é acessibilidade?")
    
    last_message = chat_page.get_last_message_text(role="user")
    assert "acessibilidade" in last_message.lower()


BENEFÍCIOS:
-----------
1. ✅ Código mais limpo e legível
2. ✅ Reutilização de código (send_message usado em vários testes)
3. ✅ Manutenção centralizada (mudança no seletor = 1 lugar)
4. ✅ Abstração de detalhes de implementação
5. ✅ Testes focam no "O QUE" ao invés do "COMO"
6. ✅ Facilita onboarding de novos desenvolvedores
"""
