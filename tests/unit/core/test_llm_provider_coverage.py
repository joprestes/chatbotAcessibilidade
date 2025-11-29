"""
Testes adicionais para aumentar cobertura de llm_provider.py
Focando nas linhas não cobertas
"""

import asyncio

import pytest
from google.adk.agents import Agent
from unittest.mock import AsyncMock, MagicMock, patch

from chatbot_acessibilidade.core.exceptions import APIError
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



