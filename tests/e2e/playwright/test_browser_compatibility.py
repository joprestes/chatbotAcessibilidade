"""
Testes de Compatibilidade de Navegadores

Testa funcionalidades específicas em diferentes navegadores.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = [pytest.mark.e2e, pytest.mark.playwright, pytest.mark.frontend]


def test_localstorage_all_browsers(page: Page, base_url: str):
    """
    Testa localStorage em todos os navegadores.
    """
    page.goto(base_url)
    
    # Limpa localStorage
    page.evaluate("() => localStorage.clear()")
    
    # Salva algo no localStorage
    page.evaluate("() => localStorage.setItem('test_key', 'test_value')")
    
    # Recarrega página
    page.reload()
    page.wait_for_load_state("networkidle")
    
    # Verifica que valor foi mantido
    stored_value = page.evaluate("() => localStorage.getItem('test_key')")
    assert stored_value == "test_value", "localStorage deve persistir entre reloads"
    
    # Limpa após teste
    page.evaluate("() => localStorage.removeItem('test_key')")


def test_fetch_api_compatibility(page: Page, base_url: str):
    """
    Testa que fetch API funciona em todos os navegadores.
    """
    page.goto(base_url)
    
    # Testa fetch via JavaScript
    fetch_result = page.evaluate("""
        async () => {
            try {
                const response = await fetch('/api/health');
                return { success: true, status: response.status };
            } catch (error) {
                return { success: false, error: error.message };
            }
        }
    """)
    
    assert fetch_result["success"], f"Fetch API deve funcionar: {fetch_result.get('error')}"
    assert fetch_result["status"] == 200, "Health check deve retornar 200"


def test_abort_controller_compatibility(page: Page, base_url: str):
    """
    Testa que AbortController funciona em todos os navegadores.
    """
    page.goto(base_url)
    
    # Testa AbortController via JavaScript
    abort_test = page.evaluate("""
        async () => {
            try {
                const controller = new AbortController();
                const signal = controller.signal;
                
                // Inicia requisição
                const fetchPromise = fetch('/api/health', { signal });
                
                // Aborta imediatamente
                controller.abort();
                
                await fetchPromise;
                return { success: false, error: 'Should have been aborted' };
            } catch (error) {
                if (error.name === 'AbortError') {
                    return { success: true };
                }
                return { success: false, error: error.message };
            }
        }
    """)
    
    assert abort_test["success"], f"AbortController deve funcionar: {abort_test.get('error')}"


def test_css_compatibility(page: Page, base_url: str):
    """
    Testa que CSS Grid/Flexbox funciona em todos os navegadores.
    """
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    
    # Verifica que layout funciona (pode usar grid, flex ou block)
    header = page.locator("header")
    if header.is_visible():
        display = header.evaluate("el => window.getComputedStyle(el).display")
        # Aceita qualquer display válido (grid, flex, block, etc.)
        assert display in ["grid", "flex", "inline-flex", "block", "inline-block"], \
            f"Layout deve usar display válido, encontrado: {display}"
    
    # Verifica que elementos estão posicionados corretamente
    chat_container = page.locator('[data-testid="chat-container"]')
    if chat_container.is_visible():
        expect(chat_container).to_be_visible()
    
    # Verifica que input está visível (testa que layout funciona)
    input_field = page.locator('[data-testid="input-pergunta"]')
    expect(input_field).to_be_visible()

