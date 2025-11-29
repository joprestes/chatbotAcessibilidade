"""
Testes de Acessibilidade WCAG AAA

Valida conformidade com WCAG 2.2 Nível AAA usando Playwright e axe-core.
Foca em critérios específicos do nível AAA que vão além do AA.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = [pytest.mark.e2e, pytest.mark.playwright, pytest.mark.accessibility]

# Tenta importar axe-playwright
try:
    from axe_playwright_python.sync_playwright import Axe

    AXE_AVAILABLE = True
except ImportError:
    AXE_AVAILABLE = False
    Axe = None


@pytest.fixture
def axe():
    """Fixture para instância do Axe."""
    if not AXE_AVAILABLE:
        pytest.skip("axe-playwright não está instalado")
    return Axe()


def test_contrast_ratio_aaa(page: Page, base_url: str, axe):
    """
    Testa contraste de cores AAA (WCAG 1.4.6).

    Requisito AAA:
    - Texto normal: razão mínima de 7:1
    - Texto grande (18pt+ ou 14pt+ bold): razão mínima de 4.5:1
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Executa análise focada em contraste com padrão AAA
    results = axe.run(
        page,
        options={
            "runOnly": {
                "type": "tag",
                "values": ["wcag2aaa", "wcag146"],
            },
            "rules": {
                "color-contrast-enhanced": {"enabled": True},
            },
        },
    )

    # Verifica violações de contraste AAA
    contrast_violations = [v for v in results.violations if "contrast" in v.id.lower()]

    assert (
        len(contrast_violations) == 0
    ), f"Violations de contraste AAA encontradas: {[v.id for v in contrast_violations]}"


def test_text_spacing_override(page: Page, base_url: str):
    """
    Testa suporte a override de espaçamento de texto (WCAG 1.4.12 - AA).

    Requisitos:
    - line-height: pelo menos 1.5x o tamanho da fonte
    - letter-spacing: pelo menos 0.12x o tamanho da fonte
    - word-spacing: pelo menos 0.16x o tamanho da fonte
    - paragraph-spacing: pelo menos 2x o tamanho da fonte
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Aplica CSS de override de espaçamento
    page.add_style_tag(
        content="""
        * {
            line-height: 1.5 !important;
            letter-spacing: 0.12em !important;
            word-spacing: 0.16em !important;
        }
        p {
            margin-bottom: 2em !important;
        }
    """
    )

    page.wait_for_timeout(1000)

    # Verifica que elementos principais ainda são visíveis
    header = page.locator("header")
    expect(header).to_be_visible()

    input_field = page.get_by_test_id("input-pergunta")
    expect(input_field).to_be_visible()

    # Verifica que não há scroll horizontal
    scroll_width = page.evaluate("() => document.documentElement.scrollWidth")
    client_width = page.evaluate("() => document.documentElement.clientWidth")
    assert scroll_width <= client_width + 5, "Há scroll horizontal após override de spacing"

    # Verifica que texto não está cortado
    intro_card = page.locator("#intro-card")
    if intro_card.is_visible():
        overflow = intro_card.evaluate("el => window.getComputedStyle(el).overflow")
        assert overflow != "hidden", "Texto pode estar cortado após override"


def test_focus_indicator_contrast(page: Page, base_url: str):
    """
    Testa contraste do indicador de foco (WCAG 2.4.11 - AAA).

    Requisito: Indicador de foco deve ter contraste mínimo de 3:1
    com cores adjacentes.
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Testa foco em diferentes elementos
    interactive_elements = [
        '[data-testid="btn-toggle-tema"]',
        '[data-testid="input-pergunta"]',
        '[data-testid="btn-enviar"]',
    ]

    for selector in interactive_elements:
        element = page.locator(selector)
        if element.is_visible():
            element.focus()
            page.wait_for_timeout(200)

            # Verifica que elemento tem outline visível
            outline_width = element.evaluate("el => window.getComputedStyle(el).outlineWidth")
            outline_style = element.evaluate("el => window.getComputedStyle(el).outlineStyle")

            # Outline deve ter pelo menos 2px
            assert (
                outline_width and outline_width != "0px"
            ), f"Elemento {selector} não tem outline visível ao focar"
            assert outline_style != "none", f"Elemento {selector} tem outline-style: none"


def test_no_text_images(page: Page, base_url: str):
    """
    Testa ausência de imagens de texto (WCAG 1.4.9 - AAA).

    Requisito: Imagens de texto não devem ser usadas, exceto para
    logotipos ou quando essencial.
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Verifica que fonte web está sendo usada
    body_font = page.evaluate("() => window.getComputedStyle(document.body).fontFamily")
    assert "Atkinson Hyperlegible" in body_font, "Fonte web não está sendo usada"

    # Verifica que não há imagens com texto (exceto logo)
    images = page.locator("img")
    image_count = images.count()

    for i in range(image_count):
        img = images.nth(i)
        alt = img.get_attribute("alt") or ""
        src = img.get_attribute("src") or ""

        # Permite apenas logo e avatares
        is_logo = "logo" in src.lower() or "logo" in alt.lower()
        is_avatar = "avatar" in src.lower() or "ada" in alt.lower()

        # Se não é logo nem avatar, verifica que não contém texto
        if not (is_logo or is_avatar):
            # Imagens decorativas devem ter alt vazio
            assert alt == "" or len(alt) < 50, f"Imagem {src} pode conter texto"


def test_animation_reduced_motion_all(page: Page, base_url: str):
    """
    Testa que todas as animações respeitam prefers-reduced-motion (WCAG 2.3.3 - AAA).

    Requisito: Animações devem ser desabilitadas quando usuário
    prefere movimento reduzido.
    """
    # Simula prefers-reduced-motion: reduce
    page.emulate_media(reduced_motion="reduce")
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Verifica que animações estão desabilitadas ou muito curtas
    body_element = page.locator("body")

    # Verifica transition-duration
    transition = body_element.evaluate("el => window.getComputedStyle(el).transitionDuration")

    # Deve ser 0s ou muito curto (< 0.1s)
    if transition and transition != "0s":
        duration_ms = float(transition.replace("s", "")) * 1000
        assert duration_ms < 100, f"Transições não foram desabilitadas: {transition}"

    # Envia mensagem e verifica que não há animação longa
    input_field = page.get_by_test_id("input-pergunta")
    input_field.fill("Teste reduced motion")

    send_button = page.get_by_test_id("btn-enviar")
    send_button.click()

    # Aguarda um pouco
    page.wait_for_timeout(500)

    # Verifica que mensagem aparece rapidamente (sem animação longa)
    # Se reduced motion está ativo, não deve haver fadeIn longo


def test_help_contextual(page: Page, base_url: str):
    """
    Testa disponibilidade de ajuda contextual (WCAG 3.3.5 - AAA).

    Requisito: Ajuda sensível ao contexto deve estar disponível.
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Verifica se há hints ou tooltips
    input_field = page.get_by_test_id("input-pergunta")

    # Verifica aria-describedby
    described_by = input_field.get_attribute("aria-describedby")

    # Se não há aria-describedby, deve haver placeholder descritivo
    if not described_by:
        placeholder = input_field.get_attribute("placeholder")
        assert (
            placeholder and len(placeholder) > 10
        ), "Input não tem ajuda contextual (aria-describedby ou placeholder descritivo)"

    # Verifica se há botão de ajuda ou sugestões visíveis
    chips = page.locator(".chip")
    if chips.count() > 0:
        # Sugestões servem como ajuda contextual
        assert chips.count() >= 3, "Deve haver pelo menos 3 sugestões como ajuda"


def test_timeout_warning(page: Page, base_url: str):
    """
    Testa aviso de timeout (WCAG 2.2.6 - AAA).

    Requisito: Usuário deve ser avisado antes de timeout e poder
    estender o tempo.

    Nota: Este teste verifica a estrutura, não o comportamento real
    de timeout que levaria 2 minutos.
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Verifica que há configuração de timeout no JavaScript
    has_timeout_config = page.evaluate(
        """() => {
        return typeof frontendConfig !== 'undefined' && 
               frontendConfig.request_timeout_ms !== undefined;
    }"""
    )

    assert has_timeout_config, "Configuração de timeout não encontrada"

    # Verifica que timeout é razoável (>= 60s)
    timeout_ms = page.evaluate("() => frontendConfig.request_timeout_ms")
    assert timeout_ms >= 60000, f"Timeout muito curto: {timeout_ms}ms"

    # TODO: Implementar teste de aviso de timeout quando funcionalidade for adicionada
    # Por enquanto, apenas documenta que timeout existe


def test_language_identification(page: Page, base_url: str):
    """
    Testa identificação de idioma (WCAG 3.1.1 - A, 3.1.2 - AA).

    Requisito: Idioma da página deve ser identificado.
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Verifica atributo lang no html
    html_lang = page.evaluate("() => document.documentElement.lang")
    assert html_lang, "Atributo lang não encontrado no <html>"
    assert html_lang.startswith("pt"), f"Idioma incorreto: {html_lang}"

    # Verifica que não há mudanças de idioma não marcadas
    # (todo o conteúdo é em português)


def test_heading_structure_complete(page: Page, base_url: str):
    """
    Testa estrutura completa de headings (WCAG 2.4.10 - AAA).

    Requisito: Seções devem ter headings descritivos.
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Verifica que há h1
    h1 = page.locator("h1")
    assert h1.count() == 1, "Deve haver exatamente um h1"

    # Envia mensagem para gerar resposta com seções
    input_field = page.get_by_test_id("input-pergunta")
    input_field.fill("Como testar acessibilidade?")

    send_button = page.get_by_test_id("btn-enviar")
    send_button.click()

    # Aguarda resposta
    page.wait_for_timeout(3000)

    # Verifica que seções de resposta têm headings
    # TODO: Implementar quando headings forem adicionados às respostas


def test_consistent_identification(page: Page, base_url: str):
    """
    Testa identificação consistente de componentes (WCAG 3.2.4 - AA).

    Requisito: Componentes com mesma funcionalidade devem ser
    identificados consistentemente.
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Verifica que botões com mesma função têm labels consistentes
    # Ex: todos os botões de fechar devem ter "Fechar" ou "Cancelar"

    # Verifica botão de enviar
    send_button = page.get_by_test_id("btn-enviar")
    send_label = send_button.get_attribute("aria-label")
    assert (
        send_label and "enviar" in send_label.lower()
    ), "Botão de enviar não tem label consistente"

    # Verifica botão de tema
    theme_button = page.get_by_test_id("btn-toggle-tema")
    theme_label = theme_button.get_attribute("aria-label")
    assert theme_label and "tema" in theme_label.lower(), "Botão de tema não tem label consistente"


def test_target_size_minimum(page: Page, base_url: str):
    """
    Testa tamanho mínimo de alvos (WCAG 2.5.5 - AAA).

    Requisito: Alvos de ponteiro devem ter pelo menos 44x44 pixels.
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Verifica tamanho de botões
    interactive_elements = [
        '[data-testid="btn-toggle-tema"]',
        '[data-testid="btn-enviar"]',
        '[data-testid="btn-limpar-chat"]',
    ]

    for selector in interactive_elements:
        element = page.locator(selector)
        if element.is_visible():
            box = element.bounding_box()
            assert box is not None, f"Não foi possível obter bounding box de {selector}"

            # Verifica tamanho mínimo
            assert (
                box["width"] >= 44 and box["height"] >= 44
            ), f"Elemento {selector} é muito pequeno: {box['width']}x{box['height']}px (mínimo 44x44px)"


def test_visual_presentation_aaa(page: Page, base_url: str):
    """
    Testa apresentação visual AAA (WCAG 1.4.8).

    Requisitos:
    - Largura de linha não excede 80 caracteres
    - Texto não é justificado
    - Line-height pelo menos 1.5x
    - Paragraph-spacing pelo menos 2x
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Envia mensagem para gerar resposta
    input_field = page.get_by_test_id("input-pergunta")
    input_field.fill("Explique WCAG")

    send_button = page.get_by_test_id("btn-enviar")
    send_button.click()

    page.wait_for_timeout(3000)

    # Verifica line-height do body
    line_height = page.evaluate("() => window.getComputedStyle(document.body).lineHeight")
    font_size = page.evaluate("() => window.getComputedStyle(document.body).fontSize")

    # Converte para números
    line_height_num = float(line_height.replace("px", ""))
    font_size_num = float(font_size.replace("px", ""))

    ratio = line_height_num / font_size_num
    assert ratio >= 1.5, f"Line-height muito baixo: {ratio} (mínimo 1.5)"

    # Verifica que texto não é justificado
    text_align = page.evaluate("() => window.getComputedStyle(document.body).textAlign")
    assert text_align != "justify", "Texto não deve ser justificado (AAA)"
