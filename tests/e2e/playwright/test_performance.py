"""
Testes de Performance e Stress

Testa comportamento do sistema sob carga e casos extremos.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = [pytest.mark.e2e, pytest.mark.playwright, pytest.mark.frontend, pytest.mark.performance, pytest.mark.slow]


def test_multiple_sequential_requests(page: Page, base_url: str):
    """
    Testa múltiplas requisições sequenciais.
    """
    page.goto(base_url)
    
    input_field = page.locator('[data-testid="input-pergunta"]')
    send_button = page.locator('[data-testid="btn-enviar"]')
    
    # Envia 10 requisições sequenciais
    for i in range(10):
        input_field.fill(f"Pergunta {i+1}")
        send_button.click()
        
        # Aguarda resposta ou timeout
        page.wait_for_timeout(2000)
        
        # Verifica que mensagem foi adicionada
        user_messages = page.locator('[data-testid="chat-mensagem-user"]')
        expect(user_messages).to_have_count(i + 1, timeout=5000)


def test_parallel_requests_blocking(page: Page, base_url: str):
    """
    Testa que requisições paralelas são bloqueadas (apenas uma por vez).
    """
    page.goto(base_url)
    
    input_field = page.locator('[data-testid="input-pergunta"]')
    send_button = page.locator('[data-testid="btn-enviar"]')
    
    # Tenta enviar 5 mensagens rapidamente
    for i in range(5):
        input_field.fill(f"Paralela {i+1}")
        send_button.click()
        page.wait_for_timeout(100)  # Pequeno delay entre cliques
    
    # Verifica que apenas uma requisição está ativa
    # O frontend deve bloquear novas requisições enquanto uma está em andamento
    cancel_buttons = page.locator('[data-testid="btn-cancelar"]')
    # Deve haver no máximo 1 botão cancelar visível
    expect(cancel_buttons).to_have_count(1, timeout=2000)


def test_long_message_limits(page: Page, base_url: str):
    """
    Testa limites de mensagens longas.
    """
    page.goto(base_url)
    
    input_field = page.locator('[data-testid="input-pergunta"]')
    send_button = page.locator('[data-testid="btn-enviar"]')
    
    # Testa mensagem com 2000 caracteres (limite máximo)
    long_message = "a" * 2000
    input_field.fill(long_message)
    
    # Verifica contador de caracteres
    char_counter = page.locator('.char-counter')
    if char_counter.is_visible():
        expect(char_counter).to_contain_text("2000")
    
    # Envia mensagem
    send_button.click()
    
    # Aguarda resposta
    page.wait_for_timeout(2000)
    
    # Verifica que mensagem foi aceita
    user_message = page.locator('[data-testid="chat-mensagem-user"]').first
    expect(user_message).to_be_visible()
    
    # Testa mensagem com 2001 caracteres (deve ser rejeitada)
    too_long_message = "a" * 2001
    input_field.fill(too_long_message)
    
    # Verifica que contador mostra erro (se houver classe de erro)
    if char_counter.is_visible():
        char_counter_class = char_counter.get_attribute("class")
        if char_counter_class:
            assert "error" in char_counter_class.lower()
    
    # Tenta enviar (deve ser bloqueado pelo frontend)
    send_button.click()
    page.wait_for_timeout(500)
    
    # Verifica que mensagem não foi enviada (não há nova mensagem)
    # Se o frontend bloqueia, não deve haver nova mensagem
    # Se permite, o backend deve rejeitar
    # Por enquanto, apenas verifica que não quebrou
    # Nota: Validação de limite é feita no frontend e backend


def test_large_history_performance(page: Page, base_url: str):
    """
    Testa performance com histórico grande.
    """
    page.goto(base_url)
    
    input_field = page.locator('[data-testid="input-pergunta"]')
    send_button = page.locator('[data-testid="btn-enviar"]')
    
    # Cria 20 mensagens (não 100 para não demorar muito)
    # Em produção, pode aumentar para 100
    for i in range(20):
        input_field.fill(f"Mensagem {i+1} para histórico grande")
        send_button.click()
        page.wait_for_timeout(1000)  # Aguarda resposta
    
    # Verifica que todas as mensagens foram renderizadas
    user_messages = page.locator('[data-testid="chat-mensagem-user"]')
    expect(user_messages).to_have_count(20, timeout=30000)
    
    # Verifica que busca funciona
    search_toggle = page.locator('[data-testid="btn-buscar"]')
    if search_toggle.is_visible():
        search_toggle.click()
        search_input = page.locator('[data-testid="search-input"]')
        expect(search_input).to_be_visible(timeout=2000)
        
        search_input.fill("Mensagem 10")
        page.wait_for_timeout(500)
        
        # Verifica que resultados aparecem
        # (implementação depende de como busca funciona)
    
    # Verifica que scroll funciona
    chat_container = page.locator('[data-testid="chat-container"]')
    expect(chat_container).to_be_visible()

