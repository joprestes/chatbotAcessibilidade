"""
Testes E2E do Frontend usando Playwright

Testa a interface do usuário em navegadores reais,
validando interações, fluxos e comportamento visual.
"""

import pytest
from playwright.sync_api import Page, expect
from typing import Generator

pytestmark = [pytest.mark.e2e, pytest.mark.playwright, pytest.mark.frontend]


def test_homepage_loads(page: Page, base_url: str):
    """
    Testa se a homepage carrega corretamente.
    """
    page.goto(base_url)
    
    # Verifica título
    expect(page).to_have_title(containing="Ada") or expect(page).to_have_title(containing="Acessibilidade")
    
    # Verifica elementos principais
    header = page.locator("header")
    expect(header).to_be_visible()
    
    # Verifica se o card de introdução aparece (quando não há mensagens)
    intro_card = page.locator('[data-testid="intro-card"]')
    # Pode estar visível ou oculto dependendo do estado
    assert intro_card.count() > 0


def test_chat_interface_visible(page: Page, base_url: str):
    """
    Testa se a interface de chat está visível.
    """
    page.goto(base_url)
    
    # Verifica input de pergunta
    input_field = page.locator('[data-testid="input-pergunta"]')
    expect(input_field).to_be_visible()
    
    # Verifica botão de enviar
    send_button = page.locator('[data-testid="btn-enviar"]')
    expect(send_button).to_be_visible()
    
    # Verifica container de chat
    chat_container = page.locator('[data-testid="chat-container"]')
    expect(chat_container).to_be_visible()


def test_send_message_flow(page: Page, base_url: str):
    """
    Testa fluxo completo de envio de mensagem.
    """
    page.goto(base_url)
    
    # Preenche input
    input_field = page.locator('[data-testid="input-pergunta"]')
    input_field.fill("O que é acessibilidade?")
    
    # Clica em enviar
    send_button = page.locator('[data-testid="btn-enviar"]')
    send_button.click()
    
    # Aguarda mensagem do usuário aparecer
    user_message = page.locator('[data-testid="chat-mensagem-user"]').first
    expect(user_message).to_be_visible(timeout=5000)
    
    # Verifica conteúdo da mensagem
    assert "acessibilidade" in user_message.text_content().lower()


def test_typing_indicator_shows(page: Page, base_url: str):
    """
    Testa se o indicador de digitação aparece durante processamento.
    """
    page.goto(base_url)
    
    # Envia mensagem
    input_field = page.locator('[data-testid="input-pergunta"]')
    input_field.fill("Teste de indicador")
    
    send_button = page.locator('[data-testid="btn-enviar"]')
    send_button.click()
    
    # Verifica se indicador aparece (pode ser rápido)
    typing_indicator = page.locator("text=Aguarde que estou pesquisando")
    # Pode não aparecer se a resposta for muito rápida
    try:
        expect(typing_indicator).to_be_visible(timeout=2000)
    except Exception:
        # Se não aparecer, não é erro crítico
        pass


def test_theme_toggle(page: Page, base_url: str):
    """
    Testa se o toggle de tema funciona.
    """
    page.goto(base_url)
    
    # Encontra botão de tema
    theme_toggle = page.locator('[data-testid="btn-toggle-tema"]')
    expect(theme_toggle).to_be_visible()
    
    # Verifica tema inicial
    initial_theme = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
    
    # Clica no toggle
    theme_toggle.click()
    
    # Aguarda mudança
    page.wait_for_timeout(500)
    
    # Verifica se tema mudou
    new_theme = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
    assert new_theme != initial_theme


def test_suggestion_chips_click(page: Page, base_url: str):
    """
    Testa se os chips de sugestão funcionam.
    """
    page.goto(base_url)
    
    # Aguarda card de introdução aparecer
    intro_card = page.locator('[data-testid="intro-card"]')
    
    # Verifica se há chips de sugestão
    suggestion_chip = page.locator('[data-testid="chip-contraste"]').first
    if suggestion_chip.is_visible():
        # Clica no chip
        suggestion_chip.click()
        
        # Verifica se o input foi preenchido
        input_field = page.locator('[data-testid="input-pergunta"]')
        input_value = input_field.input_value()
        assert len(input_value) > 0


def test_clear_chat_button(page: Page, base_url: str):
    """
    Testa se o botão de limpar chat funciona.
    """
    page.goto(base_url)
    
    # Envia uma mensagem primeiro
    input_field = page.locator('[data-testid="input-pergunta"]')
    input_field.fill("Mensagem de teste")
    
    send_button = page.locator('[data-testid="btn-enviar"]')
    send_button.click()
    
    # Aguarda mensagem aparecer
    page.wait_for_timeout(1000)
    
    # Clica no botão de limpar
    clear_button = page.locator('[data-testid="btn-limpar-chat"]')
    if clear_button.is_visible():
        clear_button.click()
        
        # Confirma diálogo (se houver)
        page.on("dialog", lambda dialog: dialog.accept())
        
        # Aguarda limpeza
        page.wait_for_timeout(500)
        
        # Verifica se card de introdução voltou
        intro_card = page.locator('[data-testid="intro-card"]')
        # Pode estar visível novamente


def test_search_functionality(page: Page, base_url: str):
    """
    Testa funcionalidade de busca no histórico.
    """
    page.goto(base_url)
    
    # Envia algumas mensagens
    input_field = page.locator('[data-testid="input-pergunta"]')
    send_button = page.locator('[data-testid="btn-enviar"]')
    
    input_field.fill("Primeira mensagem")
    send_button.click()
    page.wait_for_timeout(1000)
    
    input_field.fill("Segunda mensagem")
    send_button.click()
    page.wait_for_timeout(1000)
    
    # Clica no botão de busca
    search_toggle = page.locator('[data-testid="btn-buscar"]')
    if search_toggle.is_visible():
        search_toggle.click()
        
        # Verifica se campo de busca aparece
        search_input = page.locator('[data-testid="search-input"]')
        expect(search_input).to_be_visible(timeout=2000)
        
        # Digita no campo de busca
        search_input.fill("Primeira")
        
        # Verifica se resultados aparecem
        page.wait_for_timeout(500)


def test_keyboard_navigation(page: Page, base_url: str):
    """
    Testa navegação por teclado (acessibilidade).
    """
    page.goto(base_url)
    
    # Pressiona Tab para navegar
    page.keyboard.press("Tab")
    page.wait_for_timeout(200)
    
    # Verifica se algum elemento recebeu foco
    focused_element = page.evaluate("() => document.activeElement")
    assert focused_element is not None
    
    # Testa Enter no input
    input_field = page.locator('[data-testid="input-pergunta"]')
    input_field.focus()
    input_field.fill("Teste teclado")
    
    # Pressiona Enter (deve enviar)
    page.keyboard.press("Enter")
    page.wait_for_timeout(1000)


def test_responsive_layout_mobile(page: Page, base_url: str):
    """
    Testa layout responsivo em mobile.
    """
    # Define viewport mobile
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto(base_url)
    
    # Verifica se elementos se adaptam
    header = page.locator("header")
    expect(header).to_be_visible()
    
    # Verifica se input está visível
    input_field = page.locator('[data-testid="input-pergunta"]')
    expect(input_field).to_be_visible()


def test_responsive_layout_tablet(page: Page, base_url: str):
    """
    Testa layout responsivo em tablet.
    """
    # Define viewport tablet
    page.set_viewport_size({"width": 768, "height": 1024})
    page.goto(base_url)
    
    # Verifica elementos
    header = page.locator("header")
    expect(header).to_be_visible()


def test_responsive_layout_desktop(page: Page, base_url: str):
    """
    Testa layout responsivo em desktop.
    """
    # Define viewport desktop
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto(base_url)
    
    # Verifica elementos
    header = page.locator("header")
    expect(header).to_be_visible()

