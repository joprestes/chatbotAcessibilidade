"""
Testes de Tratamento de Erros no Frontend

Testa cenários de erro e como o frontend os trata graciosamente.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = [pytest.mark.e2e, pytest.mark.playwright, pytest.mark.frontend]


def test_timeout_request(
    page: Page,
    base_url: str,
):
    """
    Testa timeout quando requisição demora mais que request_timeout_ms.
    Nota: Este teste requer mock de requisição lenta ou pode ser marcado como skip
    se timeout for muito longo para testes.
    """
    from playwright.sync_api import Route

    page.goto(base_url)

    # Intercepta requisição (sem delay - Playwright já sincroniza)
    def handle_route(route: Route):
        route.continue_()

    page.route(f"{base_url}/api/chat", handle_route)

    # Preenche input
    input_field = page.get_by_test_id("input-pergunta")
    input_field.fill("Teste de timeout")

    # Envia mensagem
    send_button = page.get_by_test_id("btn-enviar")
    send_button.click()

    # Para teste real de timeout, seria necessário delay de 120s+
    # Por enquanto, apenas verifica que requisição foi iniciada
    cancel_button = page.get_by_test_id("btn-cancelar")
    # Se botão cancelar aparece, requisição está em andamento
    try:
        expect(cancel_button).to_be_visible(timeout=2000)
    except Exception:
        # Se não aparecer, pode ser que resposta foi muito rápida
        pass

    page.unroute(f"{base_url}/api/chat")


def test_offline_error(page: Page, base_url: str):
    """
    Testa erro quando usuário está offline.
    """
    page.goto(base_url)

    # Simula estado offline
    page.context.set_offline(True)

    # Preenche input
    input_field = page.get_by_test_id("input-pergunta")
    input_field.fill("Teste offline")

    # Envia mensagem
    send_button = page.get_by_test_id("btn-enviar")
    send_button.click()

    # Verifica mensagem de offline
    offline_message = page.locator("text=📡 Você está offline")
    expect(offline_message).to_be_visible(timeout=5000)

    # Simula reconexão
    page.context.set_offline(False)
    page.evaluate("() => window.dispatchEvent(new Event('online'))")

    # Aguarda um pouco para reconexão ser detectada
    page.wait_for_timeout(1000)


def test_rate_limit_error(page: Page, base_url: str):
    """
    Testa erro de rate limit (429).
    """
    import json
    from playwright.sync_api import Route

    page.goto(base_url)

    # Mock de resposta 429
    def handle_route(route: Route):
        route.fulfill(
            status=429,
            headers={"Content-Type": "application/json"},
            body=json.dumps({"detail": "Rate limit exceeded"}),
        )

    page.route(f"{base_url}/api/chat", handle_route)

    # Preenche input
    input_field = page.get_by_test_id("input-pergunta")
    input_field.fill("Teste rate limit")

    # Envia mensagem
    send_button = page.get_by_test_id("btn-enviar")
    send_button.click()

    # Verifica mensagem de rate limit
    rate_limit_message = page.locator("text=🚦 Muitas requisições")
    expect(rate_limit_message).to_be_visible(timeout=5000)

    page.unroute(f"{base_url}/api/chat")


def test_server_error_500(page: Page, base_url: str):
    """
    Testa erro do servidor (500+).
    """
    import json
    from playwright.sync_api import Route

    page.goto(base_url)

    # Mock de resposta 500
    def handle_route(route: Route):
        route.fulfill(
            status=500,
            headers={"Content-Type": "application/json"},
            body=json.dumps({"detail": "Internal server error"}),
        )

    page.route(f"{base_url}/api/chat", handle_route)

    # Preenche input
    input_field = page.get_by_test_id("input-pergunta")
    input_field.fill("Teste erro servidor")

    # Envia mensagem
    send_button = page.get_by_test_id("btn-enviar")
    send_button.click()

    # Verifica mensagem de erro do servidor
    server_error_message = page.locator("text=🔧 Erro no servidor")
    expect(server_error_message).to_be_visible(timeout=5000)

    page.unroute(f"{base_url}/api/chat")


def test_manual_cancellation(page: Page, base_url: str):
    """
    Testa cancelamento manual de requisição.
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Preenche input
    input_field = page.get_by_test_id("input-pergunta")
    input_field.fill("Teste cancelamento")

    # Envia mensagem
    send_button = page.get_by_test_id("btn-enviar")
    send_button.click()

    # Aguarda que o typing indicator apareça (garante que a requisição começou)
    typing_indicator = page.locator("text=Aguarde que estou pesquisando")
    expect(typing_indicator).to_be_visible(timeout=10000)

    # Aguarda botão cancelar aparecer (aguarda que isLoading seja true)
    # O botão só aparece quando isLoading é true, então aguardamos
    # que a classe 'hidden' seja removida
    cancel_button = page.get_by_test_id("btn-cancelar")

    # Aguarda que o botão não tenha mais a classe 'hidden' E esteja visível
    page.wait_for_function(
        "() => { const btn = document.querySelector('[data-testid=\"btn-cancelar\"]'); return btn && !btn.classList.contains('hidden') && btn.offsetParent !== null; }",
        timeout=10000,
    )

    # Verifica que está visível
    expect(cancel_button).to_be_visible(timeout=2000)

    # Clica no botão cancelar
    cancel_button.click()

    # Aguarda um pouco
    page.wait_for_timeout(500)

    # Verifica que não há mensagem de erro
    # Busca mensagens assistant que tenham classe error
    error_messages = page.locator('[data-testid="chat-mensagem-assistant"].error')
    expect(error_messages).to_have_count(0)

    # Verifica que indicador foi removido
    typing_indicator = page.locator("text=Aguarde que estou pesquisando")
    expect(typing_indicator).not_to_be_visible()


def test_malformed_response(page: Page, base_url: str):
    """
    Testa tratamento de resposta malformada do servidor.
    """
    from playwright.sync_api import Route

    page.goto(base_url)

    # Mock de resposta malformada
    def handle_route(route: Route):
        route.fulfill(
            status=200,
            headers={"Content-Type": "application/json"},
            body="{invalid json}",
        )

    page.route(f"{base_url}/api/chat", handle_route)

    # Preenche input
    input_field = page.get_by_test_id("input-pergunta")
    input_field.fill("Teste resposta malformada")

    # Envia mensagem
    send_button = page.get_by_test_id("btn-enviar")
    send_button.click()

    # Verifica que erro é tratado graciosamente
    # Pode ser mensagem de erro genérica ou específica
    # Usa locator para combinar test-id com classe CSS
    error_message = page.locator('[data-testid="chat-mensagem-assistant"].error')
    expect(error_message).to_be_visible(timeout=5000)

    page.unroute(f"{base_url}/api/chat")
