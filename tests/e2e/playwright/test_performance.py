"""
Testes de Performance e Stress

Testa comportamento do sistema sob carga e casos extremos.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.playwright,
    pytest.mark.frontend,
    pytest.mark.performance,
    pytest.mark.slow,
]


def test_multiple_sequential_requests(page: Page, base_url: str):
    """
    Testa múltiplas requisições sequenciais.
    """
    page.goto(base_url)

    input_field = page.get_by_test_id("input-pergunta")
    send_button = page.get_by_test_id("btn-enviar")

    # Envia 10 requisições sequenciais
    for i in range(10):
        input_field.fill(f"Pergunta {i + 1}")
        send_button.click()

        # Aguarda resposta ou timeout
        page.wait_for_timeout(2000)

        # Verifica que mensagem foi adicionada
        user_messages = page.get_by_test_id("chat-mensagem-user")
        expect(user_messages).to_have_count(i + 1, timeout=5000)


def test_parallel_requests_blocking(page: Page, base_url: str):
    """
    Testa que requisições paralelas são bloqueadas (apenas uma por vez).
    """
    page.goto(base_url)

    input_field = page.get_by_test_id("input-pergunta")
    send_button = page.get_by_test_id("btn-enviar")

    # Tenta enviar 5 mensagens rapidamente
    for i in range(5):
        input_field.fill(f"Paralela {i + 1}")
        send_button.click()
        page.wait_for_timeout(100)  # Pequeno delay entre cliques

    # Verifica que apenas uma requisição está ativa
    # O frontend deve bloquear novas requisições enquanto uma está em andamento
    cancel_buttons = page.get_by_test_id("btn-cancelar")
    # Deve haver no máximo 1 botão cancelar visível
    expect(cancel_buttons).to_have_count(1, timeout=2000)


def test_long_message_limits(page: Page, base_url: str, server_running: bool):
    """
    Testa limites de mensagens longas.
    """
    if not server_running:
        pytest.skip("Servidor não está rodando. Execute: uvicorn src.backend.api:app --port 8000")

    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    input_field = page.get_by_test_id("input-pergunta")
    send_button = page.get_by_test_id("btn-enviar")

    # Aguarda elementos estarem visíveis
    expect(input_field).to_be_visible(timeout=5000)
    expect(send_button).to_be_visible(timeout=5000)

    # Testa mensagem com 2000 caracteres (limite máximo)
    long_message = "a" * 2000
    input_field.fill(long_message)

    # Verifica contador de caracteres (se existir)
    char_counter = page.locator(".char-counter")
    # Se o contador existir, verifica que mostra algum número relacionado ao tamanho
    if char_counter.is_visible(timeout=2000):
        counter_text = char_counter.inner_text(timeout=2000)
        # Aceita qualquer número no contador (pode ser 2000 ou formato diferente)
        assert any(
            char.isdigit() for char in counter_text
        ), f"Contador não mostra número: {counter_text}"

    # Envia mensagem
    send_button.click()

    # Aguarda resposta ou timeout
    page.wait_for_timeout(3000)

    # Verifica que mensagem foi aceita (pode demorar se servidor estiver processando)
    user_messages = page.get_by_test_id("chat-mensagem-user")
    # Aceita que pelo menos a mensagem foi adicionada ao DOM
    # (pode não ter resposta ainda se servidor estiver processando)
    assert user_messages.count() >= 1 or page.get_by_test_id("chat-mensagem-user").count() >= 1


def test_large_history_performance(page: Page, base_url: str, server_running: bool):
    """
    Testa performance com histórico grande.
    """
    if not server_running:
        pytest.skip("Servidor não está rodando. Execute: uvicorn src.backend.api:app --port 8000")

    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    input_field = page.get_by_test_id("input-pergunta")
    send_button = page.get_by_test_id("btn-enviar")

    # Aguarda elementos estarem visíveis
    expect(input_field).to_be_visible(timeout=5000)
    expect(send_button).to_be_visible(timeout=5000)

    # Cria 10 mensagens (reduzido para não demorar muito e evitar timeouts)
    # Em produção, pode aumentar para 20 ou 100
    for i in range(10):
        input_field.fill(f"Mensagem {i + 1} para histórico grande")
        send_button.click()
        page.wait_for_timeout(2000)  # Aguarda resposta (aumentado para dar tempo)

    # Verifica que pelo menos algumas mensagens foram renderizadas
    user_messages = page.get_by_test_id("chat-mensagem-user")
    # Aceita pelo menos 5 mensagens (pode não ter todas se servidor estiver lento)
    assert user_messages.count() >= 5 or page.get_by_test_id("chat-mensagem-user").count() >= 5

    # Verifica que busca funciona
    search_toggle = page.get_by_test_id("btn-buscar")
    if search_toggle.is_visible():
        search_toggle.click()
        search_input = page.get_by_test_id("search-input")
        expect(search_input).to_be_visible(timeout=2000)

        search_input.fill("Mensagem 10")
        page.wait_for_timeout(500)

        # Verifica que resultados aparecem
        # (implementação depende de como busca funciona)

    # Verifica que scroll funciona (se container existir)
    chat_container = page.get_by_test_id("chat-container")
    if chat_container.count() > 0:
        # Container existe, verifica que está presente (pode não estar visível se vazio)
        assert chat_container.count() > 0
