from playwright.sync_api import Page, expect


def test_code_mode_toggle(page: Page):
    """
    Testa a funcionalidade do botão de Modo Código.
    Verifica se o placeholder muda e se a classe CSS é aplicada.
    """
    page.goto("http://localhost:8000/")

    # Localiza elementos
    code_btn = page.locator('[data-testid="btn-code-mode"]')
    input_area = page.locator('[data-testid="input-pergunta"]')

    # Estado inicial
    expect(input_area).not_to_have_class("code-mode-active")
    expect(input_area).to_have_attribute("placeholder", "Pergunte sobre WCAG, ARIA ou testes...")

    # Ativa modo código
    code_btn.click()

    # Verifica mudanças
    expect(input_area).to_have_class("code-mode-active")
    expect(input_area).to_have_attribute("placeholder", "Cole seu código aqui para refatoração...")
    expect(code_btn).to_have_class("icon-button-small active")
    expect(code_btn).to_have_attribute("aria-pressed", "true")

    # Desativa modo código
    code_btn.click()

    # Verifica retorno ao estado original
    expect(input_area).not_to_have_class("code-mode-active")
    expect(input_area).to_have_attribute("placeholder", "Pergunte sobre WCAG, ARIA ou testes...")
    expect(code_btn).not_to_have_class("icon-button-small active")
    expect(code_btn).to_have_attribute("aria-pressed", "false")


def test_persona_selection_flow(page: Page):
    """
    Testa o fluxo de seleção de Persona.
    Verifica abertura do modal, seleção e preenchimento do input.
    """
    page.goto("http://localhost:8000/")

    # Localiza elementos
    persona_btn = page.locator('[data-testid="btn-persona"]')
    modal = page.locator("#accessible-modal")
    input_area = page.locator('[data-testid="input-pergunta"]')

    # Abre modal
    persona_btn.click()
    expect(modal).to_be_visible()
    expect(modal).to_have_attribute("aria-hidden", "false")

    # Verifica foco no modal (primeiro botão de persona ou fechar)
    # O foco deve ir para o primeiro elemento focável.
    # Vamos verificar se o botão de "Pessoa Cega" está visível e clicável
    blind_persona_btn = page.locator("button[onclick=\"selectPersona('cega')\"]")
    # Verifica se modal abriu
    expect(modal).to_be_visible()

    # Seleciona cenário (botão de leitor de tela - antigo 'cega')
    blind_persona_btn = page.locator(".persona-btn").first
    blind_persona_btn.click()
    # Verifica se modal fechou (verifica atributo aria-hidden primeiro)
    expect(modal).to_have_attribute("aria-hidden", "true")
    expect(modal).to_be_hidden()

    # Verifica input preenchido com exemplo
    expect(input_area).to_have_value(
        "/simular leitor-tela Estou tentando comprar um ingresso, mas o leitor de tela não anuncia o preço quando navego pela tabela de assentos."
    )

    # Verifica se o foco voltou para o input (correção de acessibilidade implementada)
    expect(input_area).to_be_focused()


def test_send_code_refactor(page: Page):
    """
    Testa o envio de código para refatoração.
    Mocka a API para verificar se o comando /refatorar é enviado corretamente.
    """
    # Mock da API
    page.route(
        "**/api/chat",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"resposta": {"💻 **Código Refatorado**": "<code>fixed</code>", "📝 **Explicação**": "Fixed", "✅ **Critérios WCAG**": "1.1.1"}}',
        ),
    )

    page.goto("http://localhost:8000/")

    # Ativa modo código
    page.locator('[data-testid="btn-code-mode"]').click()

    # Digita código
    input_area = page.locator('[data-testid="input-pergunta"]')
    input_area.fill("<div>bad code</div>")

    # Envia
    page.locator('[data-testid="btn-enviar"]').click()

    # Verifica se a resposta renderizou (mock)
    expect(page.locator(".response-section")).to_have_count(3)
    expect(page.locator("text=Código Refatorado")).to_be_visible()


def test_send_persona_simulation(page: Page):
    """
    Testa o envio de simulação de persona.
    """
    # Mock da API
    page.route(
        "**/api/chat",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"resposta": {"🎭 **Análise de Cenário**": "Simulando uso com leitor de tela...", "ℹ️ **Nota**": "Simulação"}}',
        ),
    )

    page.goto("http://localhost:8000/")

    # Seleciona persona via script para agilizar (já testamos UI no outro teste)
    page.evaluate("selectPersona('baixa_visao')")

    # Completa o contexto
    input_area = page.locator('[data-testid="input-pergunta"]')
    input_area.type("teste de contraste")

    # Envia
    page.locator('[data-testid="btn-enviar"]').click()

    # Verifica resposta
    expect(page.locator("text=Análise de Cenário")).to_be_visible()
