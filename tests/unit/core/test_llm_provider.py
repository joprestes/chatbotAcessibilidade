"""
Testes para o módulo llm_provider.py
"""

import asyncio

import pytest
from google.adk.agents import Agent
from google.api_core import exceptions as google_exceptions
from unittest.mock import AsyncMock, MagicMock, patch

from chatbot_acessibilidade.core.exceptions import (
    APIError,
    ModelUnavailableError,
    QuotaExhaustedError,
)
from chatbot_acessibilidade.core.llm_provider import (
    GoogleGeminiClient,

)

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


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@pytest.mark.asyncio
async def test_google_gemini_client_sucesso(
    mock_session_service, mock_runner_class, mock_client_class, mock_agent, mock_evento
):
    """Testa GoogleGeminiClient com sucesso"""
    # Setup mocks
    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session

    # Cria um async generator para simular run_async (aceita kwargs)
    async def async_gen(**kwargs):
        yield mock_evento

    mock_runner = AsyncMock()
    mock_runner.run_async = async_gen
    mock_runner_class.return_value = mock_runner

    client = GoogleGeminiClient(mock_agent)
    resultado = await client.generate("Teste")

    assert resultado == "Resposta de teste"
    assert client.get_provider_name() == "Google Gemini"


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@pytest.mark.asyncio
async def test_google_gemini_client_quota_exhausted(
    mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa GoogleGeminiClient com quota esgotada"""
    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session

    # Cria um async generator que levanta exceção (aceita kwargs)
    async def async_gen_error(**kwargs):
        # Levanta a exceção imediatamente quando o generator é iterado
        raise google_exceptions.ResourceExhausted("Rate limit")
        yield  # nunca chega aqui

    mock_runner = AsyncMock()
    mock_runner.run_async = async_gen_error
    mock_runner_class.return_value = mock_runner

    client = GoogleGeminiClient(mock_agent)

    from chatbot_acessibilidade.core.constants import ErrorMessages

    resultado = await client.generate("Teste")
    assert resultado == ErrorMessages.MAINTENANCE_MESSAGE








@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@pytest.mark.asyncio
async def test_google_gemini_client_timeout(
    mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa GoogleGeminiClient com timeout"""

    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session

    # Cria um async generator que demora muito (para triggerar timeout do asyncio.wait_for)
    async def async_gen_timeout(**kwargs):
        await asyncio.sleep(100)  # Delay longo para triggerar timeout
        yield  # nunca chega aqui

    mock_runner = AsyncMock()
    mock_runner.run_async = async_gen_timeout
    mock_runner_class.return_value = mock_runner

    # Mock settings para timeout curto - precisa ser feito antes de criar o client
    with patch("chatbot_acessibilidade.core.llm_provider.settings") as mock_settings:
        mock_settings.api_timeout_seconds = 0.01  # Timeout muito curto para teste

        # Cria o client após mockar settings
        client = GoogleGeminiClient(mock_agent)

        with pytest.raises(APIError) as exc_info:
            await client.generate("Teste")

        assert "timeout" in str(exc_info.value).lower()


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@pytest.mark.asyncio
async def test_google_gemini_client_safety_block(
    mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa GoogleGeminiClient com bloqueio por segurança"""
    from google.genai import types

    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session

    evento = MagicMock()
    evento.is_final_response.return_value = True
    evento.content = MagicMock()
    parte = MagicMock()
    parte.finish_reason = types.FinishReason.SAFETY
    parte.text = None
    evento.content.parts = [parte]

    # Cria um async generator (aceita kwargs)
    async def async_gen(**kwargs):
        yield evento

    mock_runner = AsyncMock()
    mock_runner.run_async = async_gen
    mock_runner_class.return_value = mock_runner

    client = GoogleGeminiClient(mock_agent)

    with pytest.raises(APIError) as exc_info:
        await client.generate("Teste")

    assert "segurança" in str(exc_info.value).lower()


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@pytest.mark.asyncio
async def test_google_gemini_client_should_fallback(
    mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa should_fallback do GoogleGeminiClient"""
    client = GoogleGeminiClient(mock_agent)

    assert client.should_fallback(QuotaExhaustedError("test")) is True
    assert client.should_fallback(ModelUnavailableError("test")) is True
    assert client.should_fallback(google_exceptions.ResourceExhausted("test")) is True

    # Erros que não devem acionar fallback
    assert client.should_fallback(Exception("teste genérico")) is False












@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_google_gemini_client_resposta_vazia(
    mock_settings, mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa GoogleGeminiClient quando resposta está vazia"""
    from chatbot_acessibilidade.core.llm_provider import GoogleGeminiClient

    mock_settings.api_timeout_seconds = 60

    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session

    evento = MagicMock()
    evento.is_final_response.return_value = True
    evento.content = MagicMock()
    evento.content.parts = []  # Resposta vazia

    async def async_gen(**kwargs):
        yield evento

    mock_runner = AsyncMock()
    mock_runner.run_async = async_gen
    mock_runner_class.return_value = mock_runner

    client = GoogleGeminiClient(mock_agent)

    with pytest.raises(APIError) as exc_info:
        await client.generate("Teste")

    assert "vazia" in str(exc_info.value).lower()
