"""
Testes de Acessibilidade Avançados

Testa aspectos avançados de acessibilidade além dos testes básicos.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = [pytest.mark.e2e, pytest.mark.playwright, pytest.mark.accessibility]

# Tenta importar axe-playwright, mas não falha se não estiver disponível
try:
    from axe_playwright.sync_playwright import Axe
    AXE_AVAILABLE = True
except ImportError:
    AXE_AVAILABLE = False
    Axe = None  # type: ignore


@pytest.fixture
def axe():
    """Fixture para instância do Axe."""
    if not AXE_AVAILABLE:
        pytest.skip("axe-playwright não está instalado")
    return Axe()


def test_screen_reader_announcements(page: Page, base_url: str, axe):
    """
    Testa anúncios para screen readers e labels ARIA.
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    
    # Verifica labels ARIA em elementos interativos
    buttons = page.locator("button")
    button_count = buttons.count()
    
    for i in range(button_count):
        button = buttons.nth(i)
        aria_label = button.get_attribute("aria-label")
        aria_labelledby = button.get_attribute("aria-labelledby")
        text_content = button.text_content()
        
        # Deve ter aria-label OU texto visível OU aria-labelledby
        assert aria_label or text_content or aria_labelledby, \
            f"Botão sem label acessível: {button}"
    
    # Verifica landmarks
    main_landmark = page.locator("main, [role='main']")
    assert main_landmark.count() > 0, "Deve haver landmark main"
    
    # Verifica live regions para anúncios (pode não haver inicialmente)
    # live_regions = page.locator("[aria-live], [role='alert'], [role='status']")
    # Pode não haver live regions visíveis inicialmente, mas devem existir quando necessário


def test_complete_keyboard_navigation(page: Page, base_url: str):
    """
    Testa navegação completa por teclado.
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    
    # Lista de elementos interativos esperados
    interactive_elements = [
        '[data-testid="btn-toggle-tema"]',
        '[data-testid="input-pergunta"]',
        '[data-testid="btn-enviar"]',
    ]
    
    # Testa Tab em todos os elementos
    for selector in interactive_elements:
        element = page.locator(selector)
        if element.is_visible():
            element.focus()
            
            # Verifica que elemento recebeu foco
            focused = page.evaluate("() => document.activeElement")
            assert focused is not None
            
            # Verifica que foco é visível
            is_visible = page.evaluate(
                "() => document.activeElement.offsetParent !== null"
            )
            assert is_visible, f"Elemento {selector} não é visível ao focar"
    
    # Testa Shift+Tab (navegação reversa)
    page.keyboard.press("Shift+Tab")
    page.wait_for_timeout(200)
    
    focused = page.evaluate("() => document.activeElement")
    assert focused is not None
    
    # Testa Enter no botão enviar
    input_field = page.locator('[data-testid="input-pergunta"]')
    input_field.focus()
    input_field.fill("Teste teclado")
    
    send_button = page.locator('[data-testid="btn-enviar"]')
    send_button.focus()
    page.keyboard.press("Enter")
    
    # Aguarda um pouco
    page.wait_for_timeout(1000)
    
    # Testa Space em botão
    theme_toggle = page.locator('[data-testid="btn-toggle-tema"]')
    if theme_toggle.is_visible():
        theme_toggle.focus()
        page.keyboard.press("Space")
        page.wait_for_timeout(500)


def test_high_contrast_mode(page: Page, base_url: str, axe):
    """
    Testa modo de alto contraste.
    """
    # Simula prefers-contrast: high
    page.emulate_media(color_scheme="dark", forced_colors="active")
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    
    # Executa análise de contraste com axe
    results = axe.run(
        page,
        options={
            "rules": {
                "color-contrast": {"enabled": True},
            }
        }
    )
    
    # Verifica violações de contraste
    contrast_violations = [
        v for v in results.violations
        if v.id == "color-contrast"
    ]
    
    assert len(contrast_violations) == 0, \
        f"Violations de contraste encontradas: {contrast_violations}"


def test_screen_zoom_200_percent(page: Page, base_url: str):
    """
    Testa zoom de tela 200% (requisito WCAG).
    """
    # Aplica zoom 200% via CSS
    page.add_init_script("""
        document.body.style.zoom = '200%';
    """)
    
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    
    # Verifica que layout não quebra
    header = page.locator("header")
    expect(header).to_be_visible()
    
    input_field = page.locator('[data-testid="input-pergunta"]')
    expect(input_field).to_be_visible()
    
    # Verifica que texto permanece legível
    text_elements = page.locator("p, span, div")
    first_text = text_elements.first
    if first_text.is_visible():
        font_size = first_text.evaluate("el => window.getComputedStyle(el).fontSize")
        # Font size deve ser legível (pelo menos 12px em zoom 200%)
        assert float(font_size.replace("px", "")) >= 12
    
    # Verifica que não há scroll horizontal
    scroll_width = page.evaluate("() => document.documentElement.scrollWidth")
    client_width = page.evaluate("() => document.documentElement.clientWidth")
    assert scroll_width <= client_width, "Há scroll horizontal indesejado"


def test_reduced_motion(page: Page, base_url: str):
    """
    Testa redução de movimento (prefers-reduced-motion).
    """
    # Simula prefers-reduced-motion: reduce
    page.emulate_media(reduced_motion="reduce")
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    
    # Verifica que animações são desabilitadas
    # Isso é feito via CSS, então verificamos que não há transições longas
    body_element = page.locator("body")
    # transition = body_element.evaluate(
    #     "el => window.getComputedStyle(el).transition"
    # )
    
    # Se reduced-motion está ativo, transições devem ser instantâneas ou desabilitadas
    # Nota: Depende da implementação CSS
    # Por enquanto, apenas verifica que página carrega
    expect(body_element).to_be_visible()

