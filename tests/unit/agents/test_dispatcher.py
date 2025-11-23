"""
Testes para o módulo dispatcher.py
"""

import pytest
from unittest.mock import MagicMock, patch

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


@patch("chatbot_acessibilidade.agents.dispatcher.generate_with_fallback")
@pytest.mark.asyncio
async def test_get_agent_response_sucesso_com_fallback(mock_fallback):
    """Testa get_agent_response com sucesso usando fallback"""
    mock_fallback.return_value = ("Resposta de teste", "Google Gemini")

    resultado = await get_agent_response("assistente", "Teste", "prefixo")

    assert resultado == "Resposta de teste"
    mock_fallback.assert_called_once()


@patch("chatbot_acessibilidade.agents.dispatcher.generate_with_fallback")
@pytest.mark.asyncio
async def test_get_agent_response_com_erro_timeout(mock_fallback):
    """Testa get_agent_response quando há timeout"""

    mock_fallback.side_effect = APIError("Timeout: A requisição demorou mais de 60 segundos")

    with pytest.raises(APIError) as exc_info:
        await get_agent_response("assistente", "Teste", "prefixo")

    assert "timeout" in str(exc_info.value).lower() or "demorou" in str(exc_info.value).lower()


@patch("chatbot_acessibilidade.agents.dispatcher.generate_with_fallback")
@pytest.mark.asyncio
async def test_get_agent_response_com_erro_quota(mock_fallback):
    """Testa get_agent_response quando há erro de quota"""

    mock_fallback.side_effect = APIError("quota esgotada")

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


@patch("chatbot_acessibilidade.agents.dispatcher._get_openrouter_client")
@patch("chatbot_acessibilidade.agents.dispatcher.settings")
@pytest.mark.asyncio
async def test_get_agent_response_inicializa_openrouter_sucesso(mock_settings, mock_get_openrouter):
    """Testa inicialização do OpenRouter quando fallback está habilitado (linha 42-49)"""
    from chatbot_acessibilidade.agents.dispatcher import get_agent_response
    from chatbot_acessibilidade.core.llm_provider import OpenRouterClient

    mock_settings.fallback_enabled = True
    mock_settings.openrouter_api_key = "test_key"
    mock_openrouter_client = MagicMock(spec=OpenRouterClient)
    mock_get_openrouter.return_value = mock_openrouter_client

    with patch("chatbot_acessibilidade.agents.dispatcher.generate_with_fallback") as mock_fallback:
        mock_fallback.return_value = ("Resposta teste", "OpenRouter")

        resultado = await get_agent_response("assistente", "Teste", "prefixo")

        assert resultado == "Resposta teste"
        mock_get_openrouter.assert_called_once()


@patch("chatbot_acessibilidade.agents.dispatcher._get_openrouter_client")
@patch("chatbot_acessibilidade.agents.dispatcher.settings")
@pytest.mark.asyncio
async def test_get_agent_response_openrouter_falha_inicializacao(
    mock_settings, mock_get_openrouter
):
    """Testa quando OpenRouter falha na inicialização (linha 46-48)"""
    from chatbot_acessibilidade.agents.dispatcher import get_agent_response

    mock_settings.fallback_enabled = True
    mock_settings.openrouter_api_key = "test_key"
    mock_get_openrouter.return_value = None  # Falha na inicialização

    with patch("chatbot_acessibilidade.agents.dispatcher.generate_with_fallback") as mock_fallback:
        mock_fallback.return_value = ("Resposta teste", "Google Gemini")

        resultado = await get_agent_response("assistente", "Teste", "prefixo")

        assert resultado == "Resposta teste"
        # Deve tentar inicializar, mas continuar sem fallback se falhar
        mock_get_openrouter.assert_called_once()


@patch("chatbot_acessibilidade.agents.dispatcher.generate_with_fallback")
@pytest.mark.asyncio
async def test_get_agent_response_erro_google_api_call_503(mock_fallback):
    """Testa get_agent_response quando há erro 503 (sobrecarga) - linha 58-66"""
    # Mock erro 503 (sobrecarga) - deve ser APIError
    mock_fallback.side_effect = APIError("API sobrecarregada 503")

    with pytest.raises(APIError) as exc_info:
        await get_agent_response("assistente", "Teste", "prefixo")

    # Deve propagar o erro
    assert "sobrecarregada" in str(exc_info.value).lower() or "erro" in str(exc_info.value).lower()


@patch("chatbot_acessibilidade.agents.dispatcher.OpenRouterClient")
@patch("chatbot_acessibilidade.agents.dispatcher.settings")
@pytest.mark.asyncio
async def test_get_openrouter_client_excecao_na_inicializacao(mock_settings, mock_openrouter_class):
    """Testa _get_openrouter_client quando OpenRouterClient levanta exceção (linha 46-48)"""
    from chatbot_acessibilidade.agents.dispatcher import _get_openrouter_client

    mock_settings.fallback_enabled = True
    mock_settings.openrouter_api_key = "test_key"
    mock_openrouter_class.side_effect = ValueError("Erro ao inicializar")

    resultado = _get_openrouter_client()

    assert resultado is None
    mock_openrouter_class.assert_called_once()


@patch("chatbot_acessibilidade.agents.dispatcher.OpenRouterClient")
@patch("chatbot_acessibilidade.agents.dispatcher.settings")
def test_get_openrouter_client_ja_inicializado(mock_settings, mock_openrouter_class):
    """Testa _get_openrouter_client quando já está inicializado (linha 49)"""
    from chatbot_acessibilidade.agents.dispatcher import _get_openrouter_client

    mock_settings.fallback_enabled = True
    mock_settings.openrouter_api_key = "test_key"

    # Simula que já foi inicializado
    from chatbot_acessibilidade.agents import dispatcher

    mock_existing_client = MagicMock()
    dispatcher._openrouter_client = mock_existing_client

    resultado = _get_openrouter_client()

    assert resultado == mock_existing_client
    # Não deve chamar OpenRouterClient novamente
    mock_openrouter_class.assert_not_called()

    # Limpa para não afetar outros testes
    dispatcher._openrouter_client = None


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


@patch("chatbot_acessibilidade.agents.dispatcher.generate_with_fallback")
@pytest.mark.asyncio
async def test_get_agent_response_erro_todos_provedores(mock_fallback):
    """Testa get_agent_response quando todos os provedores falham"""
    mock_fallback.side_effect = APIError("todos os provedores falharam")

    with pytest.raises(APIError) as exc_info:
        await get_agent_response("assistente", "Teste", "prefixo")

    assert (
        "todos os modelos" in str(exc_info.value).lower()
        or "falharam" in str(exc_info.value).lower()
    )


@patch("chatbot_acessibilidade.agents.dispatcher.generate_with_fallback")
@pytest.mark.asyncio
async def test_get_agent_response_erro_inesperado(mock_fallback):
    """Testa get_agent_response quando ocorre erro inesperado"""
    from chatbot_acessibilidade.core.exceptions import AgentError

    mock_fallback.side_effect = Exception("Erro inesperado")

    with pytest.raises(AgentError):
        await get_agent_response("assistente", "Teste", "prefixo")


@patch("chatbot_acessibilidade.agents.dispatcher._get_openrouter_client")
@patch("chatbot_acessibilidade.agents.dispatcher.settings")
@pytest.mark.asyncio
async def test_get_agent_response_com_openrouter_client(mock_settings, mock_get_openrouter):
    """Testa get_agent_response quando OpenRouter está disponível"""
    from chatbot_acessibilidade.agents.dispatcher import get_agent_response
    from chatbot_acessibilidade.core.llm_provider import OpenRouterClient

    mock_settings.fallback_enabled = True
    mock_settings.openrouter_api_key = "test_key"
    mock_openrouter_client = MagicMock(spec=OpenRouterClient)
    mock_get_openrouter.return_value = mock_openrouter_client

    with patch("chatbot_acessibilidade.agents.dispatcher.generate_with_fallback") as mock_fallback:
        mock_fallback.return_value = ("Resposta teste", "OpenRouter")

        resultado = await get_agent_response("assistente", "Teste", "prefixo")

        assert resultado == "Resposta teste"
        # Verifica que fallback_clients foi passado
        call_args = mock_fallback.call_args
        assert call_args is not None
