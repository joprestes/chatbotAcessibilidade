"""
Fixtures específicas para Page Objects.

Fornece fixtures prontas para uso nos testes, com páginas já navegadas
e configuradas.
"""

import pytest
from playwright.sync_api import Page
from pages.chat_page import ChatPage


@pytest.fixture
def chat_page(page: Page, base_url: str) -> ChatPage:
    """
    Fixture que retorna ChatPage já navegada.

    Args:
        page: Fixture do Playwright (page)
        base_url: Fixture com URL base

    Returns:
        Instância de ChatPage pronta para uso
    """
    chat = ChatPage(page, base_url)
    chat.navigate()
    return chat


@pytest.fixture
def chat_page_with_message(chat_page: ChatPage) -> ChatPage:
    """
    Fixture que retorna ChatPage com uma mensagem já enviada.

    Args:
        chat_page: Fixture de ChatPage

    Returns:
        Instância de ChatPage com mensagem enviada
    """
    chat_page.send_message("Mensagem de teste")
    return chat_page
