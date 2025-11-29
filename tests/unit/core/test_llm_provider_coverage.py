"""
Testes adicionais para aumentar cobertura de llm_provider.py
Focando nas linhas não cobertas
"""

import asyncio

import pytest
from google.adk.agents import Agent
from google.api_core import exceptions as google_exceptions
from unittest.mock import AsyncMock, MagicMock, patch

from chatbot_acessibilidade.core.exceptions import APIError, QuotaExhaustedError
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


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_google_gemini_client_timeout_linha_191(
    mock_settings, mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """
    Testa linha 191: TimeoutError durante wait_for(coletar_resposta)
    Esta linha é executada quando o timeout ocorre durante a coleta da resposta
    """
    mock_settings.google_api_key = "test_key"
    mock_settings.api_timeout_seconds = 0.01  # Timeout muito curto

    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session

    # Mock que demora mais que o timeout
    async def async_gen_slow(**kwargs):
        await asyncio.sleep(0.1)  # Mais que o timeout de 0.01s
        yield MagicMock(
            is_final_response=lambda: True,
            content=MagicMock(parts=[MagicMock(text="Resposta", finish_reason=None)]),
        )

    mock_runner = AsyncMock()
    mock_runner.run_async = async_gen_slow
    mock_runner_class.return_value = mock_runner

    client = GoogleGeminiClient(mock_agent)

    with pytest.raises(APIError) as exc_info:
        await client.generate("Teste")

    # Verifica que o erro é de timeout (linha 191-193)
    assert "timeout" in str(exc_info.value).lower() or "demorou mais" in str(exc_info.value).lower()


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_generate_with_fallback_continue_linhas_435_439(
    mock_settings, mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """
    Testa linhas 435-439: quando should_fallback retorna True para outros clientes
    e o código faz continue para tentar o próximo cliente
    """
    from chatbot_acessibilidade.core.llm_provider import GoogleGeminiClient

    mock_settings.fallback_enabled = True
    mock_settings.google_api_key = "test_key"
    mock_settings.api_timeout_seconds = 60

    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session

    # Mock erro no Gemini primário
    async def async_gen_error(**kwargs):
        await asyncio.sleep(0.01)
        raise google_exceptions.ResourceExhausted("Rate limit")
        yield

    mock_runner = AsyncMock()
    mock_runner.run_async = async_gen_error
    mock_runner_class.return_value = mock_runner

    # Cria dois clientes de fallback: primeiro falha, segundo funciona
    class CustomFallbackClient1:
        """Primeiro cliente de fallback - falha"""

        async def generate(self, prompt: str, model=None):
            raise QuotaExhaustedError("Quota esgotada")

        def should_fallback(self, exception: Exception) -> bool:
            # Retorna True para acionar continue (linha 434-439)
            return isinstance(exception, QuotaExhaustedError)

        def get_provider_name(self) -> str:
            return "Custom Fallback 1"

    class CustomFallbackClient2:
        """Segundo cliente de fallback - funciona"""

        async def generate(self, prompt: str, model=None):
            return "Resposta do fallback 2"

        def should_fallback(self, exception: Exception) -> bool:
            return False

        def get_provider_name(self) -> str:
            return "Custom Fallback 2"

    primary_client = GoogleGeminiClient(mock_agent)
    fallback_client1 = CustomFallbackClient1()
    fallback_client2 = CustomFallbackClient2()

    # Primeiro cliente falha, primeiro fallback falha (continue), segundo fallback funciona
    resposta, provedor = await generate_with_fallback(
        primary_client=primary_client,
        prompt="Teste",
        fallback_clients=[fallback_client1, fallback_client2],
        fallback_models=None,
    )

    # Verifica que o fallback funcionou
    assert resposta == "Resposta do fallback 2"
    assert provedor == "Custom Fallback 2"
