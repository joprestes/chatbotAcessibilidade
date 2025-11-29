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
    generate_with_fallback,
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
async def test_generate_with_fallback_primary_success(
    mock_session_service, mock_runner_class, mock_client_class, mock_agent, mock_evento
):
    """Testa generate_with_fallback quando o provedor primário funciona"""
    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session

    # Cria um async generator (aceita kwargs)
    async def async_gen(**kwargs):
        yield mock_evento

    mock_runner = AsyncMock()
    mock_runner.run_async = async_gen
    mock_runner_class.return_value = mock_runner

    primary_client = GoogleGeminiClient(mock_agent)

    resposta, provedor = await generate_with_fallback(
        primary_client=primary_client, prompt="Teste", fallback_clients=None, fallback_models=None
    )

    assert resposta == "Resposta de teste"
    assert "Google Gemini" in provedor


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@pytest.mark.asyncio
async def test_generate_with_fallback_generic_fallback_success(
    mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa generate_with_fallback quando precisa usar um cliente de fallback genérico"""
    # Mock Google Gemini falhando
    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session

    # Cria um async generator que levanta exceção durante iteração (aceita kwargs)
    async def async_gen_error(**kwargs):
        # Primeiro yield para iniciar a iteração
        await asyncio.sleep(0.01)
        # Depois levanta a exceção
        raise google_exceptions.ResourceExhausted("Rate limit")
        yield  # nunca chega aqui

    mock_runner = AsyncMock()
    mock_runner.run_async = async_gen_error
    mock_runner_class.return_value = mock_runner

    # Mock Fallback Client funcionando
    mock_fallback_client = MagicMock()
    mock_fallback_client.get_provider_name.return_value = "Generic Fallback"
    mock_fallback_client.generate = AsyncMock(return_value="Resposta do Fallback")
    mock_fallback_client.should_fallback.return_value = True

    with patch("chatbot_acessibilidade.core.llm_provider.settings") as mock_settings:
        mock_settings.fallback_enabled = True
        mock_settings.api_timeout_seconds = 60  # Adiciona timeout para Gemini

        primary_client = GoogleGeminiClient(mock_agent)
        # Força erro para testar fallback externo
        primary_client.generate = AsyncMock(side_effect=QuotaExhaustedError("Forced error"))
        primary_client.should_fallback = MagicMock(return_value=True)

        resposta, provedor = await generate_with_fallback(
            primary_client=primary_client,
            prompt="Teste",
            fallback_clients=[mock_fallback_client],
            fallback_models=["test-model"],
        )

        assert resposta == "Resposta do Fallback"
        assert "Generic Fallback" in provedor


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@pytest.mark.asyncio
async def test_google_gemini_client_timeout(
    mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa GoogleGeminiClient com timeout"""
    import asyncio

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
@pytest.mark.asyncio
async def test_generate_with_fallback_todos_falham(
    mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa generate_with_fallback quando todos os provedores falham"""
    import asyncio

    # Mock Google Gemini falhando
    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session

    # Cria um async generator que levanta exceção durante iteração (aceita kwargs)
    async def async_gen_error(**kwargs):
        # Primeiro yield para iniciar a iteração
        await asyncio.sleep(0.01)
        # Depois levanta a exceção
        raise google_exceptions.ResourceExhausted("Rate limit")
        yield  # nunca chega aqui

    mock_runner = AsyncMock()
    mock_runner.run_async = async_gen_error
    mock_runner_class.return_value = mock_runner

    with patch("chatbot_acessibilidade.core.llm_provider.settings") as mock_settings:
        mock_settings.fallback_enabled = True
        mock_settings.api_timeout_seconds = 60  # Adiciona timeout para Gemini

        primary_client = GoogleGeminiClient(mock_agent)

        # Mock Fallback Client também falhando
        mock_fallback_client = MagicMock()
        mock_fallback_client.get_provider_name.return_value = "Generic Fallback"
        mock_fallback_client.generate = AsyncMock(side_effect=QuotaExhaustedError("test"))
        mock_fallback_client.should_fallback.return_value = True

        from chatbot_acessibilidade.core.constants import ErrorMessages

        # Agora deve retornar a mensagem de manutenção em vez de lançar erro
        # Pois o client interno captura o erro e retorna a mensagem
        # E o generate_with_fallback propaga isso ou tenta outros fallbacks

        # Se o primary_client já retorna a mensagem de manutenção (que é uma string válida),
        # o generate_with_fallback vai considerar como sucesso do primário.

        resposta, provedor = await generate_with_fallback(
            primary_client=primary_client,
            prompt="Teste",
            fallback_clients=[mock_fallback_client],
            fallback_models=["test-model"],
        )

        # O primary client retorna a mensagem de manutenção
        assert resposta == ErrorMessages.MAINTENANCE_MESSAGE


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@pytest.mark.asyncio
async def test_generate_with_fallback_desabilitado(
    mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa generate_with_fallback quando fallback está desabilitado"""
    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session

    # Cria um async generator que levanta exceção durante iteração (aceita kwargs)
    async def async_gen_error(**kwargs):
        # Primeiro yield para iniciar a iteração
        await asyncio.sleep(0.01)
        # Depois levanta a exceção
        raise google_exceptions.ResourceExhausted("Rate limit")
        yield  # nunca chega aqui

    mock_runner = AsyncMock()
    mock_runner.run_async = async_gen_error
    mock_runner_class.return_value = mock_runner

    primary_client = GoogleGeminiClient(mock_agent)

    from chatbot_acessibilidade.core.constants import ErrorMessages

    resposta, provedor = await generate_with_fallback(
        primary_client=primary_client,
        prompt="Teste",
        fallback_clients=None,
        fallback_models=None,
    )

    assert resposta == ErrorMessages.MAINTENANCE_MESSAGE


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@pytest.mark.asyncio
async def test_generate_with_fallback_continue_apos_erro(
    mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa generate_with_fallback quando um cliente de fallback falha mas o próximo funciona"""
    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session

    # Mock erro no Gemini
    async def async_gen_error(**kwargs):
        await asyncio.sleep(0.01)
        raise google_exceptions.ResourceExhausted("Rate limit")
        yield

    mock_runner = AsyncMock()
    mock_runner.run_async = async_gen_error
    mock_runner_class.return_value = mock_runner

    # Mock Fallback Client 1 (falha)
    mock_fallback_client1 = MagicMock()
    mock_fallback_client1.get_provider_name.return_value = "Fallback 1"
    mock_fallback_client1.generate = AsyncMock(side_effect=APIError("Erro temporário"))
    mock_fallback_client1.should_fallback.return_value = True

    # Mock Fallback Client 2 (funciona)
    mock_fallback_client2 = MagicMock()
    mock_fallback_client2.get_provider_name.return_value = "Fallback 2"
    mock_fallback_client2.generate = AsyncMock(return_value="Resposta do Fallback 2")
    mock_fallback_client2.should_fallback.return_value = True

    with patch("chatbot_acessibilidade.core.llm_provider.settings") as mock_settings:
        mock_settings.fallback_enabled = True
        mock_settings.api_timeout_seconds = 60

        primary_client = GoogleGeminiClient(mock_agent)
        # Força erro para testar fallback externo
        primary_client.generate = AsyncMock(side_effect=QuotaExhaustedError("Forced error"))
        # Mock should_fallback do primary para permitir fallback
        primary_client.should_fallback = MagicMock(return_value=True)

        resposta, provedor = await generate_with_fallback(
            primary_client=primary_client,
            prompt="Teste",
            fallback_clients=[mock_fallback_client1, mock_fallback_client2],
            fallback_models=["model1", "model2"],
        )

        assert resposta == "Resposta do Fallback 2"
        assert "Fallback 2" in provedor


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
