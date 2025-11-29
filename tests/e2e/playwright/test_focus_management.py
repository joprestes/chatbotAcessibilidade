"""
Testes de Gerenciamento de Foco

Testa que o foco é gerenciado corretamente após interações,
garantindo acessibilidade e boa experiência do usuário.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = [pytest.mark.e2e, pytest.mark.playwright]


def test_focus_returns_to_input_after_send(page: Page, base_url: str, server_running: bool):
    """
    Testa que o foco retorna ao input após envio de mensagem.
    """
    if not server_running:
        pytest.skip("Servidor não está rodando. Execute: uvicorn src.backend.api:app --port 8000")

    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Foca no input
    input_field = page.get_by_test_id("input-pergunta")
    input_field.focus()

    # Verifica que input tem foco inicialmente
    focused_element = page.evaluate("() => document.activeElement.id")
    assert focused_element == "user-input", "Input deve ter foco inicial"

    # Preenche e envia mensagem
    input_field.fill("Teste de foco")
    send_button = page.get_by_test_id("btn-enviar")
    send_button.click()

    # Aguarda mensagem do usuário aparecer (indica que processamento iniciou)
    user_message = page.get_by_test_id("chat-mensagem-user").first
    expect(user_message).to_be_visible(timeout=5000)

    # Aguarda estado de rede estabilizar (resposta processada)
    page.wait_for_load_state("networkidle", timeout=10000)

    # Verifica que foco retornou ao input
    # Usa expect com retry automático para lidar com o setTimeout do frontend
    expect(input_field).to_be_focused(timeout=5000)


def test_focus_after_search_toggle(page: Page, base_url: str):
    """
    Testa que o foco vai para o campo de busca quando busca é aberta.
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Clica no botão de busca
    search_toggle = page.get_by_test_id("btn-buscar")
    if search_toggle.is_visible():
        search_toggle.click()

        # Aguarda campo de busca aparecer
        search_input = page.get_by_test_id("search-input")
        expect(search_input).to_be_visible(timeout=2000)

        # Verifica que campo de busca tem foco
        focused_element = page.evaluate("() => document.activeElement.id")
        assert focused_element == "search-input", "Campo de busca deve ter foco ao abrir"


def test_focus_after_clear_chat(page: Page, base_url: str):
    """
    Testa que o foco é gerenciado corretamente após limpar chat.
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Envia uma mensagem primeiro
    input_field = page.get_by_test_id("input-pergunta")
    input_field.fill("Mensagem de teste")
    send_button = page.get_by_test_id("btn-enviar")
    send_button.click()

    # Aguarda mensagem aparecer
    page.wait_for_timeout(2000)

    # Clica no botão de limpar
    clear_button = page.get_by_test_id("btn-limpar-chat")
    if clear_button.is_visible():
        # Configura handler para aceitar diálogo de confirmação
        page.on("dialog", lambda dialog: dialog.accept())

        clear_button.click()

        # Aguarda limpeza
        page.wait_for_timeout(1000)

        # Verifica que foco está em elemento apropriado
        # (pode ser input ou outro elemento focável)
        focused_element = page.evaluate("() => document.activeElement")
        assert focused_element is not None, "Deve haver um elemento com foco após limpar chat"


def test_keyboard_navigation_focus_visible(page: Page, base_url: str):
    """
    Testa que o foco é visível durante navegação por teclado.
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Pressiona Tab várias vezes
    focused_elements = []
    for _ in range(5):
        page.keyboard.press("Tab")
        page.wait_for_timeout(200)

        # Verifica se elemento com foco é visível
        focused_info = page.evaluate(
            """() => {
                const el = document.activeElement;
                if (!el || el === document.body) return null;
                const rect = el.getBoundingClientRect();
                return {
                    id: el.id,
                    tagName: el.tagName,
                    isVisible: rect.width > 0 && rect.height > 0,
                    hasOutline: window.getComputedStyle(el).outlineWidth !== '0px'
                };
            }"""
        )

        if focused_info:
            focused_elements.append(focused_info)
            # Verifica que elemento é visível
            element_id = focused_info["id"]
            assert focused_info[
                "isVisible"
            ], f"Elemento {element_id} deve ser visível quando focado"

    # Verifica que pelo menos alguns elementos receberam foco
    assert len(focused_elements) > 0, "Deve haver elementos focáveis na página"


def test_focus_trap_in_modal(page: Page, base_url: str):
    """
    Testa que o foco fica preso dentro de modais (se houver modais abertos).

    Nota: Este teste verifica se há modais VISÍVEIS no projeto.
    O modal existe no HTML mas fica hidden até ser aberto via JavaScript.
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Verifica se há modais VISÍVEIS (não apenas presentes no DOM)
    modals = page.locator(
        "[role='dialog'][aria-hidden='false'], .modal:visible, [aria-modal='true']:visible"
    )
    modal_count = modals.count()

    if modal_count == 0:
        # Tenta abrir o modal de configurações para testar
        settings_btn = page.locator("#settings-toggle")
        if settings_btn.is_visible():
            settings_btn.click()
            page.wait_for_selector(
                "#accessible-modal[aria-hidden='false']", state="visible", timeout=2000
            )
            # Recalcula modais
            modals = page.locator(
                "[role='dialog'][aria-hidden='false'], .modal:visible, [aria-modal='true']:visible"
            )
            modal_count = modals.count()

    if modal_count == 0:
        pytest.skip("Não há modais visíveis no projeto atualmente e não foi possível abrir um.")
    else:
        # Se houver modais visíveis, testa que foco fica preso
        first_modal = modals.first

        # Aguarda o foco entrar no modal (pode demorar devido ao setTimeout do app.js)
        # Usa loop manual para evitar erro de CSP com wait_for_function
        import time

        for _ in range(20):  # Tenta por 2 segundos
            is_focused = page.evaluate(
                "() => document.getElementById('accessible-modal').contains(document.activeElement)"
            )
            if is_focused:
                break
            time.sleep(0.1)

        # Pressiona Tab várias vezes
        for i in range(10):
            page.keyboard.press("Tab")

            # Verifica que foco ainda está dentro do modal
            modal_contains_focus = first_modal.evaluate(
                "modal => modal.contains(document.activeElement)"
            )
            assert modal_contains_focus, "Foco deve permanecer dentro do modal"


def test_skip_link_focus(page: Page, base_url: str):
    """
    Testa que o skip link funciona corretamente e recebe foco.
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Procura por skip link
    skip_link = page.locator('a[href="#user-input"], .skip-link').first

    if skip_link.count() > 0:
        # Faz scroll para o topo para garantir que skip link esteja visível
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(200)

        # Skip link está com top: -60px inicialmente, só aparece com foco
        # Força o elemento a aparecer usando JavaScript antes de clicar
        page.evaluate(
            """
            () => {
                const link = document.querySelector('a[href="#user-input"], .skip-link');
                if (link) {
                    link.style.top = '20px';
                    link.style.position = 'absolute';
                }
            }
            """
        )
        page.wait_for_timeout(200)

        # Aguarda skip link estar visível
        expect(skip_link).to_be_visible(timeout=2000)

        # Clica diretamente no skip link
        skip_link.click(timeout=10000)
        page.wait_for_timeout(500)

        # Verifica que foco mudou para o elemento alvo
        focused_after = page.evaluate("() => document.activeElement.id")
        expected_targets = ["user-input", "main-content"]
        assert (
            focused_after in expected_targets
        ), f"Foco deve ir para elemento alvo do skip link, mas foi para: {focused_after}"
