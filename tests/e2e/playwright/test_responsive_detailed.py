"""
Testes de Responsividade Detalhados

Testa layout em diferentes breakpoints e orientações.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = [pytest.mark.e2e, pytest.mark.playwright, pytest.mark.frontend]


@pytest.mark.parametrize(
    "width,height",
    [
        (320, 568),  # Mobile pequeno
        (375, 667),  # Mobile padrão
        (414, 896),  # Mobile grande
    ],
)
def test_mobile_breakpoints(page: Page, base_url: str, width: int, height: int):
    """
    Testa layout em breakpoints mobile.
    """
    page.set_viewport_size({"width": width, "height": height})
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Verifica elementos principais
    header = page.locator("header")
    expect(header).to_be_visible()

    input_field = page.get_by_test_id("input-pergunta")
    expect(input_field).to_be_visible()

    # Verifica que elementos não se sobrepõem
    header_box = header.bounding_box()
    input_box = input_field.bounding_box()

    if header_box and input_box:
        # Header não deve sobrepor input
        assert (
            header_box["y"] + header_box["height"] <= input_box["y"]
            or input_box["y"] + input_box["height"] <= header_box["y"]
        ), "Elementos não devem se sobrepor"


@pytest.mark.parametrize(
    "width,height",
    [
        (768, 1024),  # Tablet portrait
        (1024, 768),  # Tablet landscape
    ],
)
def test_tablet_breakpoints(page: Page, base_url: str, width: int, height: int):
    """
    Testa layout em breakpoints tablet.
    """
    page.set_viewport_size({"width": width, "height": height})
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Verifica elementos
    header = page.locator("header")
    expect(header).to_be_visible()

    input_field = page.get_by_test_id("input-pergunta")
    expect(input_field).to_be_visible()


@pytest.mark.parametrize(
    "width,height",
    [
        (1280, 720),  # Desktop padrão
        (1920, 1080),  # Desktop grande
    ],
)
def test_desktop_breakpoints(page: Page, base_url: str, width: int, height: int):
    """
    Testa layout em breakpoints desktop.
    """
    page.set_viewport_size({"width": width, "height": height})
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Verifica elementos
    header = page.locator("header")
    expect(header).to_be_visible()

    input_field = page.get_by_test_id("input-pergunta")
    expect(input_field).to_be_visible()


def test_orientation_change(page: Page, base_url: str):
    """
    Testa mudança de orientação (portrait/landscape).
    """
    # Começa em portrait
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    header_portrait = page.locator("header")
    expect(header_portrait).to_be_visible()

    # Muda para landscape
    page.set_viewport_size({"width": 667, "height": 375})
    page.wait_for_timeout(500)  # Aguarda adaptação

    header_landscape = page.locator("header")
    expect(header_landscape).to_be_visible()

    # Verifica que funcionalidade não quebrou
    input_field = page.get_by_test_id("input-pergunta")
    expect(input_field).to_be_visible()

    # Testa envio de mensagem
    input_field.fill("Teste orientação")
    send_button = page.get_by_test_id("btn-enviar")
    send_button.click()
    page.wait_for_timeout(2000)

    # Verifica que mensagem foi enviada
    user_message = page.get_by_test_id("chat-mensagem-user").first
    expect(user_message).to_be_visible()
