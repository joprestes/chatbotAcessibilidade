"""
Testes para o módulo dispatcher.py
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from google.adk.agents import Agent

from chatbot_acessibilidade.agents.dispatcher import get_agent_response
from chatbot_acessibilidade.core.exceptions import APIError

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_agent():
    """Cria um agente mock para testes"""
    agent = MagicMock(spec=Agent)
    agent.name = "test_agent"
    return agent


@pytest.fixture
def mock_evento():
    """Cria um evento mock com resposta final"""
    evento = MagicMock()
    evento.is_final_response.return_value = True
    evento.content = MagicMock()
    evento.content.parts = [MagicMock(text="Resposta de teste", finish_reason=None)]
    return evento


@patch("chatbot_acessibilidade.agents.dispatcher.GoogleGeminiClient")
@pytest.mark.asyncio
async def test_get_agent_response_sucesso_com_fallback(mock_client_class):
    """Testa get_agent_response com sucesso"""
    # Setup mock instance
    mock_client = MagicMock()
    mock_client.generate = AsyncMock(return_value="Resposta de teste")
    mock_client.get_provider_name.return_value = "Google Gemini"
    mock_client_class.return_value = mock_client

    resultado = await get_agent_response("assistente", "Teste", "prefixo")

    assert resultado == "Resposta de teste"
    mock_client.generate.assert_called_once()


@patch("chatbot_acessibilidade.agents.dispatcher.GoogleGeminiClient")
@pytest.mark.asyncio
async def test_get_agent_response_com_erro_timeout(mock_client_class):
    """Testa get_agent_response quando há timeout"""
    mock_client = MagicMock()
    mock_client.generate = AsyncMock(
        side_effect=APIError("Timeout: A requisição demorou mais de 60 segundos")
    )
    mock_client_class.return_value = mock_client

    with pytest.raises(APIError) as exc_info:
        await get_agent_response("assistente", "Teste", "prefixo")

    assert "timeout" in str(exc_info.value).lower() or "demorou" in str(exc_info.value).lower()


@patch("chatbot_acessibilidade.agents.dispatcher.GoogleGeminiClient")
@pytest.mark.asyncio
async def test_get_agent_response_com_erro_quota(mock_client_class):
    """Testa get_agent_response quando há erro de quota"""
    mock_client = MagicMock()
    mock_client.generate = AsyncMock(side_effect=APIError("quota esgotada"))
    mock_client_class.return_value = mock_client

    with pytest.raises(APIError) as exc_info:
        await get_agent_response("assistente", "Teste", "prefixo")

    assert (
        "muitas perguntas" in str(exc_info.value).lower() or "quota" in str(exc_info.value).lower()
    )


@pytest.mark.asyncio
async def test_get_agent_response_agente_inexistente():
    """Testa get_agent_response com agente que não existe"""
    resultado = await get_agent_response("agente_inexistente", "Teste", "prefixo")

    assert "não encontrado" in resultado.lower()
    assert resultado.startswith("Erro")


@patch("chatbot_acessibilidade.agents.dispatcher.GoogleGeminiClient")
@pytest.mark.asyncio
async def test_get_agent_response_erro_google_api_call_503(mock_client_class):
    """Testa get_agent_response quando há erro 503 (sobrecarga) - linha 58-66"""
    # Mock erro 503 (sobrecarga) - deve ser APIError
    mock_client = MagicMock()
    mock_client.generate = AsyncMock(side_effect=APIError("API sobrecarregada 503"))
    mock_client_class.return_value = mock_client

    with pytest.raises(APIError) as exc_info:
        await get_agent_response("assistente", "Teste", "prefixo")

    # Deve propagar o erro
    assert "sobrecarregada" in str(exc_info.value).lower() or "erro" in str(exc_info.value).lower()


def test_should_retry_resource_exhausted():
    """Testa _should_retry com ResourceExhausted (linha 58-59)"""
    from chatbot_acessibilidade.agents.dispatcher import _should_retry
    from google.api_core import exceptions as google_exceptions

    exception = google_exceptions.ResourceExhausted("Rate limit")
    assert _should_retry(exception) is True


def test_should_retry_google_api_call_error_503():
    """Testa _should_retry com GoogleAPICallError 503 (linha 60-64)"""
    from chatbot_acessibilidade.agents.dispatcher import _should_retry
    from google.api_core import exceptions as google_exceptions

    exception = google_exceptions.GoogleAPICallError("503 Service Unavailable")
    assert _should_retry(exception) is True

    exception_overloaded = google_exceptions.GoogleAPICallError("Service overloaded")
    assert _should_retry(exception_overloaded) is True


def test_should_retry_google_api_call_error_outro():
    """Testa _should_retry com GoogleAPICallError que não é 503 (linha 65-66)"""
    from chatbot_acessibilidade.agents.dispatcher import _should_retry
    from google.api_core import exceptions as google_exceptions

    exception = google_exceptions.GoogleAPICallError("500 Internal Server Error")
    assert _should_retry(exception) is False


def test_should_retry_outra_excecao():
    """Testa _should_retry com exceção que não deve ser retentada (linha 66)"""
    from chatbot_acessibilidade.agents.dispatcher import _should_retry

    exception = ValueError("Erro de validação")
    assert _should_retry(exception) is False


@patch("chatbot_acessibilidade.agents.dispatcher.GoogleGeminiClient")
@pytest.mark.asyncio
async def test_get_agent_response_erro_todos_provedores(mock_client_class):
    """Testa get_agent_response quando todos os provedores falham"""
    mock_client = MagicMock()
    mock_client.generate = AsyncMock(side_effect=APIError("todos os provedores falharam"))
    mock_client_class.return_value = mock_client

    with pytest.raises(APIError) as exc_info:
        await get_agent_response("assistente", "Teste", "prefixo")

    assert (
        "todos os modelos" in str(exc_info.value).lower()
        or "falharam" in str(exc_info.value).lower()
    )


@patch("chatbot_acessibilidade.agents.dispatcher.GoogleGeminiClient")
@pytest.mark.asyncio
async def test_get_agent_response_erro_inesperado(mock_client_class):
    """Testa get_agent_response quando ocorre erro inesperado"""
    from chatbot_acessibilidade.core.exceptions import AgentError

    mock_client = MagicMock()
    mock_client.generate = AsyncMock(side_effect=Exception("Erro inesperado"))
    mock_client_class.return_value = mock_client

    with pytest.raises(AgentError):
        await get_agent_response("assistente", "Teste", "prefixo")
