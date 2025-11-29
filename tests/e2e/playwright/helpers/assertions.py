"""
Assertions customizadas para testes Playwright.

Fornece assertions reutilizáveis e com mensagens de erro claras
para facilitar debugging quando testes falham.
"""

from playwright.sync_api import Page, expect


def assert_message_contains(page: Page, text: str, role: str = "user", timeout: int = 5000):
    """
    Verifica se mensagem contém texto esperado.

    Args:
        page: Instância do Playwright Page
        text: Texto esperado na mensagem
        role: Papel da mensagem (user ou assistant)
        timeout: Timeout em milissegundos

    Raises:
        AssertionError: Se mensagem não contiver o texto
    """
    message = page.get_by_test_id(f"chat-mensagem-{role}").first
    expect(message).to_be_visible(timeout=timeout)

    content = message.text_content()
    assert (
        text.lower() in (content or "").lower()
    ), f"Esperado '{text}' na mensagem {role}, mas recebeu: {content}"


def assert_url_contains(page: Page, expected: str):
    """
    Verifica se URL contém texto esperado.

    Args:
        page: Instância do Playwright Page
        expected: Texto esperado na URL

    Raises:
        AssertionError: Se URL não contiver o texto
    """
    url = page.url
    assert expected in url, f"Esperado '{expected}' na URL, mas recebeu: {url}"


def assert_element_count(page: Page, selector: str, count: int):
    """
    Verifica quantidade de elementos.

    Args:
        page: Instância do Playwright Page
        selector: Seletor CSS ou test-id
        count: Quantidade esperada

    Raises:
        AssertionError: Se quantidade não corresponder
    """
    elements = page.locator(selector)
    actual_count = elements.count()
    assert (
        actual_count == count
    ), f"Esperado {count} elementos '{selector}', mas encontrou {actual_count}"


def assert_element_visible(page: Page, selector: str, timeout: int = 5000):
    """
    Verifica se elemento está visível.

    Args:
        page: Instância do Playwright Page
        selector: Seletor CSS ou test-id
        timeout: Timeout em milissegundos

    Raises:
        AssertionError: Se elemento não estiver visível
    """
    element = page.locator(selector)
    expect(element).to_be_visible(timeout=timeout)


def assert_element_hidden(page: Page, selector: str, timeout: int = 5000):
    """
    Verifica se elemento está oculto.

    Args:
        page: Instância do Playwright Page
        selector: Seletor CSS ou test-id
        timeout: Timeout em milissegundos

    Raises:
        AssertionError: Se elemento estiver visível
    """
    element = page.locator(selector)
    expect(element).to_be_hidden(timeout=timeout)


def assert_text_equals(page: Page, selector: str, expected_text: str):
    """
    Verifica se texto de elemento é exatamente igual ao esperado.

    Args:
        page: Instância do Playwright Page
        selector: Seletor CSS ou test-id
        expected_text: Texto esperado

    Raises:
        AssertionError: Se texto não for igual
    """
    element = page.locator(selector)
    actual_text = element.text_content() or ""
    assert (
        actual_text == expected_text
    ), f"Esperado texto '{expected_text}', mas recebeu: '{actual_text}'"


def assert_attribute_equals(page: Page, selector: str, attribute: str, expected_value: str):
    """
    Verifica se atributo de elemento tem valor esperado.

    Args:
        page: Instância do Playwright Page
        selector: Seletor CSS ou test-id
        attribute: Nome do atributo
        expected_value: Valor esperado

    Raises:
        AssertionError: Se valor não corresponder
    """
    element = page.locator(selector)
    actual_value = element.get_attribute(attribute)
    assert (
        actual_value == expected_value
    ), f"Esperado atributo '{attribute}' = '{expected_value}', mas recebeu: '{actual_value}'"


def assert_input_value(page: Page, selector: str, expected_value: str):
    """
    Verifica valor de um campo de input.

    Args:
        page: Instância do Playwright Page
        selector: Seletor CSS ou test-id
        expected_value: Valor esperado

    Raises:
        AssertionError: Se valor não corresponder
    """
    element = page.locator(selector)
    actual_value = element.input_value()
    assert (
        actual_value == expected_value
    ), f"Esperado valor do input '{expected_value}', mas recebeu: '{actual_value}'"


def assert_element_enabled(page: Page, selector: str):
    """
    Verifica se elemento está habilitado.

    Args:
        page: Instância do Playwright Page
        selector: Seletor CSS ou test-id

    Raises:
        AssertionError: Se elemento estiver desabilitado
    """
    element = page.locator(selector)
    expect(element).to_be_enabled()


def assert_element_disabled(page: Page, selector: str):
    """
    Verifica se elemento está desabilitado.

    Args:
        page: Instância do Playwright Page
        selector: Seletor CSS ou test-id

    Raises:
        AssertionError: Se elemento estiver habilitado
    """
    element = page.locator(selector)
    expect(element).to_be_disabled()


def assert_focus_on_element(page: Page, expected_id: str):
    """
    Verifica se elemento específico tem foco.

    Args:
        page: Instância do Playwright Page
        expected_id: ID esperado do elemento com foco

    Raises:
        AssertionError: Se elemento não tiver foco
    """
    focused_id = page.evaluate("() => document.activeElement.id")
    assert (
        focused_id == expected_id
    ), f"Esperado foco em '{expected_id}', mas foco está em: '{focused_id}'"
