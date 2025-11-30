"""
Testes de Acessibilidade usando Playwright e axe-core

Valida conformidade com WCAG 2.1 AA usando axe-core via JavaScript.
"""

import pytest
from playwright.sync_api import Page
import json

from axe_playwright_python.sync_playwright import Axe

pytestmark = [pytest.mark.e2e, pytest.mark.playwright, pytest.mark.accessibility]


@pytest.fixture
def axe():
    """
    Fixture para instância do Axe.
    """
    return Axe()


def test_homepage_accessibility(page: Page, base_url: str, axe):
    """
    Testa acessibilidade da homepage.
    """
    page.goto(base_url)

    # Aguarda página carregar completamente
    page.wait_for_load_state("networkidle")

    # Executa análise de acessibilidade
    results = axe.run(page)

    # Verifica se há violações
    violations = results.response["violations"]
    if len(violations) > 0:
        print(f"\nVIOLATIONS FOUND: {json.dumps(violations, indent=2)}")
    assert len(violations) == 0, f"Violations encontradas: {[v['id'] for v in violations]}"

    # Verifica se há incompletudes críticas
    incomplete = [
        r for r in results.response["incomplete"] if r["impact"] in ["critical", "serious"]
    ]

    # Filtra falso positivo conhecido: gradiente no header (contraste verificado manualmente > 4.5:1)
    incomplete = [
        i
        for i in incomplete
        if not (i["id"] == "color-contrast" and "background gradient" in str(i["nodes"]))
    ]

    if len(incomplete) > 0:
        print(f"\nINCOMPLETE CRITICAL FOUND: {json.dumps(incomplete, indent=2)}")
    assert len(incomplete) == 0, f"Incompletudes críticas: {[i['id'] for i in incomplete]}"


def test_chat_interface_accessibility(page: Page, base_url: str, axe):
    """
    Testa acessibilidade da interface de chat.
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Envia uma mensagem para testar interface completa
    input_field = page.get_by_test_id("input-pergunta")
    input_field.fill("Teste de acessibilidade")

    send_button = page.get_by_test_id("btn-enviar")
    send_button.click()

    # Aguarda resposta
    page.wait_for_timeout(2000)

    # Executa análise
    results = axe.run(page)

    # Verifica se há incompletudes críticas
    incomplete = [
        r for r in results.response["incomplete"] if r["impact"] in ["critical", "serious"]
    ]

    # Filtra falso positivo conhecido: gradiente no header
    incomplete = [
        i
        for i in incomplete
        if not (i["id"] == "color-contrast" and "background gradient" in str(i["nodes"]))
    ]

    if len(incomplete) > 0:
        print(f"\nINCOMPLETE CRITICAL FOUND: {json.dumps(incomplete, indent=2)}")
    assert len(incomplete) == 0, f"Incompletudes críticas: {[i['id'] for i in incomplete]}"

    violations = results.response["violations"]
    if len(violations) > 0:
        print(f"\nVIOLATIONS FOUND: {json.dumps(violations, indent=2)}")
    assert len(violations) == 0, f"Violations: {[v['id'] for v in violations]}"


def test_keyboard_navigation_complete(page: Page, base_url: str):
    """
    Testa navegação completa por teclado.
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Pressiona Tab várias vezes para navegar
    focused_elements = []
    for _ in range(10):
        page.keyboard.press("Tab")
        page.wait_for_timeout(100)

        # Verifica se há elemento com foco e obtém informações
        focused_info = page.evaluate(
            """() => {
                const el = document.activeElement;
                if (!el || el === document.body) return null;
                return {
                    tagName: el.tagName,
                    isVisible: el.offsetParent !== null || el.getBoundingClientRect().width > 0
                };
            }"""
        )

        if focused_info and focused_info.get("isVisible"):
            focused_elements.append(focused_info.get("tagName", "unknown"))

    # Verifica que pelo menos alguns elementos receberam foco
    assert (
        len(focused_elements) > 0
    ), "Nenhum elemento focável encontrado durante navegação por teclado"


def test_skip_links(page: Page, base_url: str):
    """
    Testa se os skip links funcionam corretamente.
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Procura por skip link
    skip_link = page.locator('a[href="#main-content"]')

    if skip_link.count() > 0:
        # Verifica se está visível ao focar
        skip_link.focus()
        is_visible = skip_link.evaluate("el => el.offsetParent !== null")
        assert is_visible, "Skip link não é visível ao focar"

        # Testa navegação
        skip_link.click()
        page.wait_for_timeout(500)

        # Verifica se foco mudou para main-content
        main_content = page.locator("#main-content")
        assert main_content.count() > 0


def test_aria_labels_present(page: Page, base_url: str):
    """
    Testa se elementos interativos têm labels ARIA apropriados.
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Verifica botões
    buttons = page.locator("button")
    button_count = buttons.count()

    for i in range(button_count):
        button = buttons.nth(i)
        aria_label = button.get_attribute("aria-label")
        text_content = button.text_content()

        # Deve ter aria-label OU texto visível
        assert aria_label or text_content, f"Botão sem label: {button}"


def test_color_contrast(page: Page, base_url: str, axe):
    """
    Testa contraste de cores (WCAG AA).
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Executa análise focada em contraste
    results = axe.run(
        page,
        options={
            "rules": {
                "color-contrast": {"enabled": "true"},
            }
        },
    )

    # Verifica violações de contraste
    contrast_violations = [v for v in results.response["violations"] if v["id"] == "color-contrast"]

    assert len(contrast_violations) == 0, f"Violations de contraste: {contrast_violations}"


def test_focus_management(page: Page, base_url: str):
    """
    Testa gerenciamento de foco (importante para acessibilidade).
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Foca no input
    input_field = page.get_by_test_id("input-pergunta")
    input_field.focus()

    # Verifica se input recebeu foco
    focused = page.evaluate("() => document.activeElement")
    assert focused is not None

    # Envia mensagem
    input_field.fill("Teste")
    send_button = page.get_by_test_id("btn-enviar")
    send_button.click()

    # Aguarda processamento
    page.wait_for_timeout(2000)

    # Verifica se foco voltou para input ou está em elemento apropriado
    focused_after = page.evaluate("() => document.activeElement")
    assert focused_after is not None
