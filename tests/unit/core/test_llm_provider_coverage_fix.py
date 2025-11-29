"""
Testes adicionais para cobrir linhas não testadas em llm_provider.py
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from google.api_core import exceptions as google_exceptions
from chatbot_acessibilidade.core.llm_provider import GoogleGeminiClient
from chatbot_acessibilidade.core.exceptions import APIError, ModelUnavailableError, AgentError
from chatbot_acessibilidade.core.constants import ErrorMessages

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_agent():
    return MagicMock()


@patch("chatbot_acessibilidade.core.llm_provider.settings")
def test_get_genai_client_missing_api_key(mock_settings, mock_agent):
    """Testa erro quando API key não está configurada (linhas 103-104)"""
    mock_settings.google_api_key = ""
    client = GoogleGeminiClient(mock_agent)

    with pytest.raises(ValueError, match="GOOGLE_API_KEY não configurada"):
        client._get_genai_client()


@patch("chatbot_acessibilidade.core.llm_provider.settings")
@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
def test_get_genai_client_init_error(mock_genai_client, mock_settings, mock_agent):
    """Testa erro na inicialização do genai.Client (linhas 113-115)"""
    mock_settings.google_api_key = "test_key"
    mock_genai_client.side_effect = Exception("Init Error")
    client = GoogleGeminiClient(mock_agent)

    with pytest.raises(Exception, match="Init Error"):
        client._get_genai_client()


@patch("chatbot_acessibilidade.core.llm_provider.settings")
def test_switch_to_secondary_key_already_using(mock_settings, mock_agent):
    """Testa switch quando já está usando a chave secundária (linhas 129-131)"""
    mock_settings.google_api_key_second = "key2"
    client = GoogleGeminiClient(mock_agent)
    client._using_secondary_key = True

    assert client._switch_to_secondary_key() is False


@patch("chatbot_acessibilidade.core.llm_provider.settings")
@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
def test_switch_to_secondary_key_error(mock_genai_client, mock_settings, mock_agent):
    """Testa erro ao trocar para chave secundária (linhas 140-142)"""
    mock_settings.google_api_key_second = "key2"
    mock_genai_client.side_effect = Exception("Switch Error")
    client = GoogleGeminiClient(mock_agent)

    assert client._switch_to_secondary_key() is False


@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_generate_google_api_call_error_429(mock_settings, mock_agent):
    """Testa GoogleAPICallError com código 429 (linhas 214-217)"""
    mock_settings.google_api_key = "key1"
    mock_settings.google_api_key_second = ""  # Sem chave secundária para forçar manutenção

    client = GoogleGeminiClient(mock_agent)
    client._execute_runner_with_retry = AsyncMock()

    # Simula erro 429
    error = google_exceptions.GoogleAPICallError("Rate limit")
    error.code = 429
    client._execute_runner_with_retry.side_effect = error

    resultado = await client.generate("test")
    assert resultado == ErrorMessages.MAINTENANCE_MESSAGE


@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_generate_retry_with_secondary_key_success(mock_settings, mock_agent):
    """Testa retry com sucesso usando chave secundária (linhas 223-227)"""
    mock_settings.google_api_key = "key1"
    mock_settings.google_api_key_second = "key2"

    client = GoogleGeminiClient(mock_agent)

    # Primeiro falha com ResourceExhausted, depois sucesso
    client._execute_runner_with_retry = AsyncMock(
        side_effect=[google_exceptions.ResourceExhausted("Quota"), "Success Response"]
    )

    resultado = await client.generate("test")
    assert resultado == "Success Response"
    assert client._using_secondary_key is True


@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_generate_retry_with_secondary_key_failure(mock_settings, mock_agent):
    """Testa falha no retry mesmo com chave secundária (linhas 228-231)"""
    mock_settings.google_api_key = "key1"
    mock_settings.google_api_key_second = "key2"

    client = GoogleGeminiClient(mock_agent)

    # Falha na primeira e na segunda tentativa
    client._execute_runner_with_retry = AsyncMock(
        side_effect=[google_exceptions.ResourceExhausted("Quota 1"), Exception("Error 2")]
    )

    resultado = await client.generate("test")
    assert resultado == ErrorMessages.MAINTENANCE_MESSAGE


@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_generate_permission_denied(mock_settings, mock_agent):
    """Testa PermissionDenied (linhas 237-239)"""
    mock_settings.google_api_key = "key1"
    client = GoogleGeminiClient(mock_agent)
    client._execute_runner_with_retry = AsyncMock(
        side_effect=google_exceptions.PermissionDenied("Auth error")
    )

    with pytest.raises(APIError) as exc:
        await client.generate("test")
    assert str(exc.value) == ErrorMessages.API_ERROR_SERVER_CONFIG


@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_generate_503_unavailable(mock_settings, mock_agent):
    """Testa erro 503 (linhas 241-244)"""
    mock_settings.google_api_key = "key1"
    client = GoogleGeminiClient(mock_agent)

    error = google_exceptions.GoogleAPICallError("Unavailable")
    error.code = 503
    client._execute_runner_with_retry = AsyncMock(side_effect=error)

    with pytest.raises(ModelUnavailableError) as exc:
        await client.generate("test")
    assert str(exc.value) == ErrorMessages.MODEL_UNAVAILABLE_GEMINI


@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_generate_generic_google_api_error(mock_settings, mock_agent):
    """Testa erro genérico da API Google (linhas 246-247)"""
    mock_settings.google_api_key = "key1"
    client = GoogleGeminiClient(mock_agent)

    error = google_exceptions.GoogleAPICallError("Generic Error")
    error.code = 500
    client._execute_runner_with_retry = AsyncMock(side_effect=error)

    with pytest.raises(APIError) as exc:
        await client.generate("test")
    assert "Erro na API do Google" in str(exc.value)


@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_generate_generic_exception_quota(mock_settings, mock_agent):
    """Testa Exception genérica contendo 'quota' (linhas 257-269)"""
    mock_settings.google_api_key = "key1"
    mock_settings.google_api_key_second = ""

    client = GoogleGeminiClient(mock_agent)
    client._execute_runner_with_retry = AsyncMock(side_effect=Exception("Error: quota exceeded"))

    resultado = await client.generate("test")
    assert resultado == ErrorMessages.MAINTENANCE_MESSAGE


@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_generate_generic_exception_unexpected(mock_settings, mock_agent):
    """Testa Exception genérica inesperada (linha 271)"""
    mock_settings.google_api_key = "key1"
    client = GoogleGeminiClient(mock_agent)
    client._execute_runner_with_retry = AsyncMock(side_effect=Exception("Unexpected boom"))

    with pytest.raises(AgentError) as exc:
        await client.generate("test")
    assert "Unexpected boom" in str(exc.value)


def test_should_fallback_google_api_call_error_503(mock_agent):
    """Testa should_fallback com GoogleAPICallError 503 (linhas 281-284)"""
    client = GoogleGeminiClient(mock_agent)
    error = google_exceptions.GoogleAPICallError("503 Service Unavailable")
    assert client.should_fallback(error) is True


def test_should_fallback_google_api_call_error_overloaded(mock_agent):
    """Testa should_fallback com GoogleAPICallError overloaded (linhas 281-284)"""
    client = GoogleGeminiClient(mock_agent)
    error = google_exceptions.GoogleAPICallError("Service overloaded")
    assert client.should_fallback(error) is True
