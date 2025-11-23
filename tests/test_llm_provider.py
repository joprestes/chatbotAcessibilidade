"""
Testes para o módulo llm_provider.py
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from google.adk.agents import Agent
from google.api_core import exceptions as google_exceptions

from chatbot_acessibilidade.core.llm_provider import (
    GoogleGeminiClient,
    OpenRouterClient,
    generate_with_fallback,
    LLMProvider,
)
from chatbot_acessibilidade.core.exceptions import (
    APIError,
    QuotaExhaustedError,
    ModelUnavailableError,
)


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
    evento.content.parts = [
        MagicMock(text="Resposta de teste", finish_reason=None)
    ]
    return evento


@patch('chatbot_acessibilidade.core.llm_provider.genai.Client')
@patch('chatbot_acessibilidade.core.llm_provider.Runner')
@patch('chatbot_acessibilidade.core.llm_provider.InMemorySessionService')
async def test_google_gemini_client_sucesso(
    mock_session_service, mock_runner_class, mock_client_class, mock_agent, mock_evento
):
    """Testa GoogleGeminiClient com sucesso"""
    # Setup mocks
    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session
    
    mock_runner = AsyncMock()
    mock_runner.run_async = AsyncMock(return_value=[mock_evento])
    mock_runner_class.return_value = mock_runner
    
    client = GoogleGeminiClient(mock_agent)
    resultado = await client.generate("Teste")
    
    assert resultado == "Resposta de teste"
    assert client.get_provider_name() == "Google Gemini"


@patch('chatbot_acessibilidade.core.llm_provider.genai.Client')
@patch('chatbot_acessibilidade.core.llm_provider.Runner')
@patch('chatbot_acessibilidade.core.llm_provider.InMemorySessionService')
async def test_google_gemini_client_quota_exhausted(
    mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa GoogleGeminiClient com quota esgotada"""
    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session
    
    mock_runner = AsyncMock()
    mock_runner.run_async = AsyncMock(side_effect=google_exceptions.ResourceExhausted("Rate limit"))
    mock_runner_class.return_value = mock_runner
    
    client = GoogleGeminiClient(mock_agent)
    
    with pytest.raises(QuotaExhaustedError):
        await client.generate("Teste")
    
    assert client.should_fallback(QuotaExhaustedError("test")) is True


@patch('chatbot_acessibilidade.core.llm_provider.httpx.AsyncClient')
async def test_openrouter_client_sucesso(mock_client_class):
    """Testa OpenRouterClient com sucesso"""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "Resposta do OpenRouter"
                }
            }
        ]
    }
    mock_response.raise_for_status = MagicMock()
    
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client_class.return_value = mock_client
    
    with patch('chatbot_acessibilidade.core.llm_provider.settings') as mock_settings:
        mock_settings.openrouter_api_key = "test_key"
        mock_settings.openrouter_timeout_seconds = 60
        
        client = OpenRouterClient()
        resultado = await client.generate("Teste", model="test-model")
        
        assert resultado == "Resposta do OpenRouter"
        assert client.get_provider_name() == "OpenRouter"


@patch('chatbot_acessibilidade.core.llm_provider.httpx.AsyncClient')
async def test_openrouter_client_rate_limit(mock_client_class):
    """Testa OpenRouterClient com rate limit"""
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_error = httpx.HTTPStatusError("Rate limit", request=MagicMock(), response=mock_response)
    
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=mock_error)
    mock_client_class.return_value = mock_client
    
    with patch('chatbot_acessibilidade.core.llm_provider.settings') as mock_settings:
        mock_settings.openrouter_api_key = "test_key"
        mock_settings.openrouter_timeout_seconds = 60
        
        client = OpenRouterClient()
        
        with pytest.raises(QuotaExhaustedError):
            await client.generate("Teste", model="test-model")
        
        assert client.should_fallback(QuotaExhaustedError("test")) is True


@patch('chatbot_acessibilidade.core.llm_provider.genai.Client')
@patch('chatbot_acessibilidade.core.llm_provider.Runner')
@patch('chatbot_acessibilidade.core.llm_provider.InMemorySessionService')
async def test_generate_with_fallback_primary_success(
    mock_session_service, mock_runner_class, mock_client_class, mock_agent, mock_evento
):
    """Testa generate_with_fallback quando o provedor primário funciona"""
    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session
    
    mock_runner = AsyncMock()
    mock_runner.run_async = AsyncMock(return_value=[mock_evento])
    mock_runner_class.return_value = mock_runner
    
    primary_client = GoogleGeminiClient(mock_agent)
    
    resposta, provedor = await generate_with_fallback(
        primary_client=primary_client,
        prompt="Teste",
        fallback_clients=None,
        fallback_models=None
    )
    
    assert resposta == "Resposta de teste"
    assert "Google Gemini" in provedor


@patch('chatbot_acessibilidade.core.llm_provider.genai.Client')
@patch('chatbot_acessibilidade.core.llm_provider.Runner')
@patch('chatbot_acessibilidade.core.llm_provider.InMemorySessionService')
@patch('chatbot_acessibilidade.core.llm_provider.httpx.AsyncClient')
async def test_generate_with_fallback_openrouter_success(
    mock_httpx_client, mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa generate_with_fallback quando precisa usar OpenRouter"""
    # Mock Google Gemini falhando
    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session
    
    mock_runner = AsyncMock()
    mock_runner.run_async = AsyncMock(side_effect=google_exceptions.ResourceExhausted("Rate limit"))
    mock_runner_class.return_value = mock_runner
    
    # Mock OpenRouter funcionando
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Resposta do OpenRouter"}}]
    }
    mock_response.raise_for_status = MagicMock()
    
    mock_httpx = AsyncMock()
    mock_httpx.post = AsyncMock(return_value=mock_response)
    mock_httpx_client.return_value = mock_httpx
    
    with patch('chatbot_acessibilidade.core.llm_provider.settings') as mock_settings:
        mock_settings.fallback_enabled = True
        mock_settings.openrouter_api_key = "test_key"
        mock_settings.openrouter_timeout_seconds = 60
        
        primary_client = GoogleGeminiClient(mock_agent)
        openrouter_client = OpenRouterClient()
        
        resposta, provedor = await generate_with_fallback(
            primary_client=primary_client,
            prompt="Teste",
            fallback_clients=[openrouter_client],
            fallback_models=["test-model"]
        )
        
        assert resposta == "Resposta do OpenRouter"
        assert "OpenRouter" in provedor

