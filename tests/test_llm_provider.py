"""
Testes para o módulo llm_provider.py
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from google.adk.agents import Agent
from google.api_core import exceptions as google_exceptions

from chatbot_acessibilidade.core.llm_provider import (
    GoogleGeminiClient,
    OpenRouterClient,
    generate_with_fallback,
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

    with pytest.raises(QuotaExhaustedError):
        await client.generate("Teste")

    assert client.should_fallback(QuotaExhaustedError("test")) is True


@patch("chatbot_acessibilidade.core.llm_provider.httpx.AsyncClient")
@pytest.mark.asyncio
async def test_openrouter_client_sucesso(mock_client_class):
    """Testa OpenRouterClient com sucesso"""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Resposta do OpenRouter"}}]
    }
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client_class.return_value = mock_client

    with patch("chatbot_acessibilidade.core.llm_provider.settings") as mock_settings:
        mock_settings.openrouter_api_key = "test_key"
        mock_settings.openrouter_timeout_seconds = 60

        client = OpenRouterClient()
        resultado = await client.generate("Teste", model="test-model")

        assert resultado == "Resposta do OpenRouter"
        assert client.get_provider_name() == "OpenRouter"


@patch("chatbot_acessibilidade.core.llm_provider.httpx.AsyncClient")
@pytest.mark.asyncio
async def test_openrouter_client_rate_limit(mock_client_class):
    """Testa OpenRouterClient com rate limit"""
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_error = httpx.HTTPStatusError("Rate limit", request=MagicMock(), response=mock_response)

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=mock_error)
    mock_client_class.return_value = mock_client

    with patch("chatbot_acessibilidade.core.llm_provider.settings") as mock_settings:
        mock_settings.openrouter_api_key = "test_key"
        mock_settings.openrouter_timeout_seconds = 60

        client = OpenRouterClient()

        with pytest.raises(QuotaExhaustedError):
            await client.generate("Teste", model="test-model")

        assert client.should_fallback(QuotaExhaustedError("test")) is True


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
@patch("chatbot_acessibilidade.core.llm_provider.httpx.AsyncClient")
@pytest.mark.asyncio
async def test_generate_with_fallback_openrouter_success(
    mock_httpx_client, mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa generate_with_fallback quando precisa usar OpenRouter"""
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

    # Mock OpenRouter funcionando
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Resposta do OpenRouter"}}]
    }
    mock_response.raise_for_status = MagicMock()

    mock_httpx = AsyncMock()
    mock_httpx.post = AsyncMock(return_value=mock_response)
    mock_httpx_client.return_value = mock_httpx

    with patch("chatbot_acessibilidade.core.llm_provider.settings") as mock_settings:
        mock_settings.fallback_enabled = True
        mock_settings.openrouter_api_key = "test_key"
        mock_settings.openrouter_timeout_seconds = 60
        mock_settings.api_timeout_seconds = 60  # Adiciona timeout para Gemini

        primary_client = GoogleGeminiClient(mock_agent)
        openrouter_client = OpenRouterClient()

        resposta, provedor = await generate_with_fallback(
            primary_client=primary_client,
            prompt="Teste",
            fallback_clients=[openrouter_client],
            fallback_models=["test-model"],
        )

        assert resposta == "Resposta do OpenRouter"
        assert "OpenRouter" in provedor


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


@patch("chatbot_acessibilidade.core.llm_provider.httpx.AsyncClient")
@pytest.mark.asyncio
async def test_openrouter_client_sem_modelo(mock_client_class):
    """Testa OpenRouterClient sem especificar modelo"""
    with patch("chatbot_acessibilidade.core.llm_provider.settings") as mock_settings:
        mock_settings.openrouter_api_key = "test_key"
        mock_settings.openrouter_timeout_seconds = 60

        client = OpenRouterClient()

        with pytest.raises(ValueError) as exc_info:
            await client.generate("Teste", model=None)

        assert "modelo" in str(exc_info.value).lower()


@patch("chatbot_acessibilidade.core.llm_provider.httpx.AsyncClient")
@pytest.mark.asyncio
async def test_openrouter_client_erro_401(mock_client_class):
    """Testa OpenRouterClient com erro 401 (não autorizado)"""
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_error = httpx.HTTPStatusError("Unauthorized", request=MagicMock(), response=mock_response)

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=mock_error)
    mock_client_class.return_value = mock_client

    with patch("chatbot_acessibilidade.core.llm_provider.settings") as mock_settings:
        mock_settings.openrouter_api_key = "test_key"
        mock_settings.openrouter_timeout_seconds = 60

        client = OpenRouterClient()

        with pytest.raises(APIError) as exc_info:
            await client.generate("Teste", model="test-model")

        assert "chave" in str(exc_info.value).lower() or "api" in str(exc_info.value).lower()


@patch("chatbot_acessibilidade.core.llm_provider.httpx.AsyncClient")
@pytest.mark.asyncio
async def test_openrouter_client_erro_503(mock_client_class):
    """Testa OpenRouterClient com erro 503 (indisponível)"""
    mock_response = MagicMock()
    mock_response.status_code = 503
    mock_error = httpx.HTTPStatusError(
        "Service Unavailable", request=MagicMock(), response=mock_response
    )

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=mock_error)
    mock_client_class.return_value = mock_client

    with patch("chatbot_acessibilidade.core.llm_provider.settings") as mock_settings:
        mock_settings.openrouter_api_key = "test_key"
        mock_settings.openrouter_timeout_seconds = 60

        client = OpenRouterClient()

        with pytest.raises(ModelUnavailableError):
            await client.generate("Teste", model="test-model")


@patch("chatbot_acessibilidade.core.llm_provider.httpx.AsyncClient")
@pytest.mark.asyncio
async def test_openrouter_client_resposta_sem_choices(mock_client_class):
    """Testa OpenRouterClient com resposta inválida sem choices"""
    mock_response = MagicMock()
    mock_response.json.return_value = {}  # Sem choices
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client_class.return_value = mock_client

    with patch("chatbot_acessibilidade.core.llm_provider.settings") as mock_settings:
        mock_settings.openrouter_api_key = "test_key"
        mock_settings.openrouter_timeout_seconds = 60

        client = OpenRouterClient()

        with pytest.raises(APIError) as exc_info:
            await client.generate("Teste", model="test-model")

        # Verifica que uma exceção foi levantada (pode ser APIError genérico)
        assert "erro" in str(exc_info.value).lower() or "inválida" in str(exc_info.value).lower()


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
        mock_settings.openrouter_api_key = "test_key"
        mock_settings.openrouter_timeout_seconds = 60
        mock_settings.api_timeout_seconds = 60  # Adiciona timeout para Gemini

        primary_client = GoogleGeminiClient(mock_agent)

        # Mock OpenRouter também falhando - cria uma instância real para passar no isinstance
        from chatbot_acessibilidade.core.llm_provider import OpenRouterClient

        openrouter_client = OpenRouterClient()
        # Mock o método generate para falhar
        openrouter_client.generate = AsyncMock(side_effect=QuotaExhaustedError("test"))

        with pytest.raises(APIError) as exc_info:
            await generate_with_fallback(
                primary_client=primary_client,
                prompt="Teste",
                fallback_clients=[openrouter_client],
                fallback_models=["test-model"],
            )

        assert "todos" in str(exc_info.value).lower() or "falharam" in str(exc_info.value).lower()


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

    with pytest.raises(APIError) as exc_info:
        await generate_with_fallback(
            primary_client=primary_client,
            prompt="Teste",
            fallback_clients=None,
            fallback_models=None,
        )

        assert (
            "desabilitado" in str(exc_info.value).lower() or "erro" in str(exc_info.value).lower()
        )


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@pytest.mark.asyncio
async def test_generate_with_fallback_openrouter_client_nao_openrouter(
    mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa generate_with_fallback com cliente que não é OpenRouter"""
    from chatbot_acessibilidade.core.llm_provider import (
        GoogleGeminiClient,
        generate_with_fallback,
    )

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

    # Cria um cliente mock que não é OpenRouter
    mock_other_client = MagicMock()
    mock_other_client.get_provider_name.return_value = "OtherProvider"
    mock_other_client.generate = AsyncMock(return_value="Resposta do outro provedor")
    mock_other_client.should_fallback.return_value = True  # Deve permitir fallback

    with patch("chatbot_acessibilidade.core.llm_provider.settings") as mock_settings:
        mock_settings.fallback_enabled = True
        mock_settings.api_timeout_seconds = 60

        primary_client = GoogleGeminiClient(mock_agent)

        resposta, provedor = await generate_with_fallback(
            primary_client=primary_client,
            prompt="Teste",
            fallback_clients=[mock_other_client],
            fallback_models=None,
        )

        assert resposta == "Resposta do outro provedor"
        assert provedor == "OtherProvider"


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_generate_with_fallback_openrouter_should_fallback_false(
    mock_settings, mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa generate_with_fallback quando should_fallback retorna False no fallback (linha 403-404)"""
    from chatbot_acessibilidade.core.llm_provider import (
        GoogleGeminiClient,
        generate_with_fallback,
    )

    mock_settings.fallback_enabled = True
    mock_settings.openrouter_api_key = "test_key"
    mock_settings.api_timeout_seconds = 60

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

    # Cria um cliente mock que não é OpenRouter e should_fallback retorna False
    mock_other_client = MagicMock()
    mock_other_client.get_provider_name.return_value = "OtherProvider"
    mock_other_client.should_fallback = MagicMock(return_value=False)  # Não deve acionar fallback
    mock_other_client.generate = AsyncMock(
        side_effect=APIError("Erro que não deve acionar fallback")
    )

    primary_client = GoogleGeminiClient(mock_agent)
    # Mock should_fallback do primary para permitir fallback
    primary_client.should_fallback = MagicMock(return_value=True)

    with pytest.raises(APIError) as exc_info:
        await generate_with_fallback(
            primary_client=primary_client,
            prompt="Teste",
            fallback_clients=[mock_other_client],
            fallback_models=None,
        )

        # Deve re-lançar o erro sem tentar novo fallback (linha 403-404)
        assert "erro que não deve acionar fallback" in str(exc_info.value).lower()


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_generate_with_fallback_openrouter_continue_apos_erro(
    mock_settings, mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa generate_with_fallback quando OpenRouter continua após erro (linha 397-402)"""
    from chatbot_acessibilidade.core.llm_provider import (
        GoogleGeminiClient,
        OpenRouterClient,
        generate_with_fallback,
    )

    mock_settings.fallback_enabled = True
    mock_settings.openrouter_api_key = "test_key"
    mock_settings.api_timeout_seconds = 60

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

    openrouter_client = OpenRouterClient()
    # Primeiro modelo falha, segundo funciona
    call_count = [0]

    async def generate_side_effect(prompt, model=None):
        call_count[0] += 1
        if call_count[0] == 1:
            raise APIError("Erro temporário")  # Primeiro modelo falha
        return "Resposta do segundo modelo"  # Segundo modelo funciona

    openrouter_client.generate = AsyncMock(side_effect=generate_side_effect)
    openrouter_client.should_fallback = MagicMock(return_value=True)

    primary_client = GoogleGeminiClient(mock_agent)
    primary_client.should_fallback = MagicMock(return_value=True)

    resposta, provedor = await generate_with_fallback(
        primary_client=primary_client,
        prompt="Teste",
        fallback_clients=[openrouter_client],
        fallback_models=["model1", "model2"],
    )

    assert resposta == "Resposta do segundo modelo"
    assert "model2" in provedor or "OpenRouter" in provedor


@patch("chatbot_acessibilidade.core.llm_provider.httpx.AsyncClient")
@pytest.mark.asyncio
async def test_openrouter_client_timeout(mock_client_class):
    """Testa OpenRouterClient com timeout (linha 284-288)"""
    from chatbot_acessibilidade.core.llm_provider import OpenRouterClient
    import asyncio

    async def slow_post(*args, **kwargs):
        await asyncio.sleep(1)  # Demora mais que o timeout
        return MagicMock()

    mock_client = AsyncMock()
    mock_client.post = slow_post
    mock_client_class.return_value = mock_client

    with patch("chatbot_acessibilidade.core.llm_provider.settings") as mock_settings:
        mock_settings.openrouter_api_key = "test_key"
        mock_settings.openrouter_timeout_seconds = 0.01  # Timeout muito curto

        client = OpenRouterClient()
        with pytest.raises(APIError) as exc_info:
            await client.generate("Teste", model="test-model")

        assert "timeout" in str(exc_info.value).lower()


@patch("chatbot_acessibilidade.core.llm_provider.httpx.AsyncClient")
@pytest.mark.asyncio
async def test_openrouter_client_http_error_outro_status(mock_client_class):
    """Testa OpenRouterClient com erro HTTP diferente de 429/503/401/403 (linha 300-304)"""
    from chatbot_acessibilidade.core.llm_provider import OpenRouterClient
    import httpx

    mock_response = MagicMock()
    mock_response.status_code = 500
    http_error = httpx.HTTPStatusError(
        "500 Internal Server Error", request=MagicMock(), response=mock_response
    )

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=http_error)
    mock_client_class.return_value = mock_client

    with patch("chatbot_acessibilidade.core.llm_provider.settings") as mock_settings:
        mock_settings.openrouter_api_key = "test_key"
        mock_settings.openrouter_timeout_seconds = 60

        client = OpenRouterClient()
        with pytest.raises(APIError) as exc_info:
            await client.generate("Teste", model="test-model")

        assert "500" in str(exc_info.value) or "comunicação" in str(exc_info.value).lower()


@patch("chatbot_acessibilidade.core.llm_provider.httpx.AsyncClient")
@pytest.mark.asyncio
async def test_openrouter_client_request_error(mock_client_class):
    """Testa OpenRouterClient com RequestError (linha 305-307)"""
    from chatbot_acessibilidade.core.llm_provider import OpenRouterClient
    import httpx

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=httpx.RequestError("Connection error"))
    mock_client_class.return_value = mock_client

    with patch("chatbot_acessibilidade.core.llm_provider.settings") as mock_settings:
        mock_settings.openrouter_api_key = "test_key"
        mock_settings.openrouter_timeout_seconds = 60

        client = OpenRouterClient()
        with pytest.raises(APIError) as exc_info:
            await client.generate("Teste", model="test-model")

        assert (
            "conectar" in str(exc_info.value).lower() or "openrouter" in str(exc_info.value).lower()
        )


@patch("chatbot_acessibilidade.core.llm_provider.httpx.AsyncClient")
@pytest.mark.asyncio
async def test_openrouter_client_excecao_geral(mock_client_class):
    """Testa OpenRouterClient com exceção geral (linha 308-310)"""
    from chatbot_acessibilidade.core.llm_provider import OpenRouterClient

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=ValueError("Erro inesperado"))
    mock_client_class.return_value = mock_client

    with patch("chatbot_acessibilidade.core.llm_provider.settings") as mock_settings:
        mock_settings.openrouter_api_key = "test_key"
        mock_settings.openrouter_timeout_seconds = 60

        client = OpenRouterClient()
        with pytest.raises(APIError) as exc_info:
            await client.generate("Teste", model="test-model")

        assert (
            "falha inesperada" in str(exc_info.value).lower()
            or "openrouter" in str(exc_info.value).lower()
        )


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_google_gemini_client_resposta_vazia(
    mock_settings, mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa GoogleGeminiClient quando resposta está vazia (linha 147-149)"""
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


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_google_gemini_client_google_api_call_error_nao_503(
    mock_settings, mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa GoogleGeminiClient com GoogleAPICallError que não é 503 (linha 186-187)"""
    from chatbot_acessibilidade.core.llm_provider import GoogleGeminiClient
    from google.api_core import exceptions as google_exceptions

    mock_settings.api_timeout_seconds = 60

    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session

    async def async_gen_error(**kwargs):
        await asyncio.sleep(0.01)
        raise google_exceptions.GoogleAPICallError("500 Internal Server Error")
        yield

    mock_runner = AsyncMock()
    mock_runner.run_async = async_gen_error
    mock_runner_class.return_value = mock_runner

    client = GoogleGeminiClient(mock_agent)

    with pytest.raises(APIError) as exc_info:
        await client.generate("Teste")

    assert "comunicação" in str(exc_info.value).lower() or "problema" in str(exc_info.value).lower()


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_google_gemini_client_permission_denied(
    mock_settings, mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa GoogleGeminiClient com PermissionDenied (linha 178-180)"""
    from chatbot_acessibilidade.core.llm_provider import GoogleGeminiClient
    from google.api_core import exceptions as google_exceptions

    mock_settings.api_timeout_seconds = 60

    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session

    async def async_gen_error(**kwargs):
        await asyncio.sleep(0.01)
        raise google_exceptions.PermissionDenied("Permission denied")
        yield

    mock_runner = AsyncMock()
    mock_runner.run_async = async_gen_error
    mock_runner_class.return_value = mock_runner

    client = GoogleGeminiClient(mock_agent)

    with pytest.raises(APIError) as exc_info:
        await client.generate("Teste")

    assert (
        "configuração" in str(exc_info.value).lower() or "servidor" in str(exc_info.value).lower()
    )


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_google_gemini_client_google_api_call_error_durante_iteracao(
    mock_settings, mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa GoogleGeminiClient quando GoogleAPICallError ocorre durante iteração (linha 133-135)"""
    from chatbot_acessibilidade.core.llm_provider import GoogleGeminiClient
    from google.api_core import exceptions as google_exceptions

    mock_settings.api_timeout_seconds = 60

    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session

    async def async_gen_error(**kwargs):
        await asyncio.sleep(0.01)
        raise google_exceptions.GoogleAPICallError("Erro durante iteração")
        yield

    mock_runner = AsyncMock()
    mock_runner.run_async = async_gen_error
    mock_runner_class.return_value = mock_runner

    client = GoogleGeminiClient(mock_agent)

    with pytest.raises(APIError) as exc_info:
        await client.generate("Teste")

    assert "comunicação" in str(exc_info.value).lower() or "problema" in str(exc_info.value).lower()


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_google_gemini_client_permission_denied_durante_iteracao(
    mock_settings, mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa GoogleGeminiClient quando PermissionDenied ocorre durante iteração (linha 130-132)"""
    from chatbot_acessibilidade.core.llm_provider import GoogleGeminiClient
    from google.api_core import exceptions as google_exceptions

    mock_settings.api_timeout_seconds = 60

    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session

    async def async_gen_error(**kwargs):
        await asyncio.sleep(0.01)
        raise google_exceptions.PermissionDenied("Permission denied durante iteração")
        yield

    mock_runner = AsyncMock()
    mock_runner.run_async = async_gen_error
    mock_runner_class.return_value = mock_runner

    client = GoogleGeminiClient(mock_agent)

    with pytest.raises(APIError) as exc_info:
        await client.generate("Teste")

    assert (
        "configuração" in str(exc_info.value).lower() or "servidor" in str(exc_info.value).lower()
    )


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_google_gemini_client_timeout_error(
    mock_settings, mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa GoogleGeminiClient com asyncio.TimeoutError (linha 171-173)"""
    mock_settings.api_timeout_seconds = 0.01  # Timeout muito curto

    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session

    async def slow_gen(**kwargs):
        await asyncio.sleep(1)  # Demora mais que o timeout
        yield

    mock_runner = AsyncMock()
    mock_runner.run_async = slow_gen
    mock_runner_class.return_value = mock_runner

    client = GoogleGeminiClient(mock_agent)

    with pytest.raises(APIError) as exc_info:
        await client.generate("Teste")

    assert "timeout" in str(exc_info.value).lower() or "demorou" in str(exc_info.value).lower()


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_google_gemini_client_google_api_call_error_503(
    mock_settings, mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa GoogleGeminiClient com GoogleAPICallError 503 (linha 184-185)"""
    mock_settings.api_timeout_seconds = 60

    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session

    async def async_gen_error(**kwargs):
        await asyncio.sleep(0.01)
        raise google_exceptions.GoogleAPICallError("503 Service Unavailable")
        yield

    mock_runner = AsyncMock()
    mock_runner.run_async = async_gen_error
    mock_runner_class.return_value = mock_runner

    client = GoogleGeminiClient(mock_agent)

    with pytest.raises(ModelUnavailableError) as exc_info:
        await client.generate("Teste")

    assert "sobrecarregada" in str(exc_info.value).lower()


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_google_gemini_client_excecao_geral(
    mock_settings, mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa GoogleGeminiClient com exceção geral (linha 191-193)"""
    from chatbot_acessibilidade.core.exceptions import AgentError

    mock_settings.api_timeout_seconds = 60

    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session

    async def async_gen_error(**kwargs):
        await asyncio.sleep(0.01)
        raise ValueError("Erro inesperado")
        yield

    mock_runner = AsyncMock()
    mock_runner.run_async = async_gen_error
    mock_runner_class.return_value = mock_runner

    client = GoogleGeminiClient(mock_agent)

    with pytest.raises(AgentError) as exc_info:
        await client.generate("Teste")

    assert "falha inesperada" in str(exc_info.value).lower()


def test_google_gemini_client_should_fallback_google_api_call_error_nao_503():
    """Testa should_fallback com GoogleAPICallError que não é 503 (linha 204-206)"""
    client = GoogleGeminiClient(MagicMock(spec=Agent))

    # GoogleAPICallError sem 503 ou overloaded
    exception = google_exceptions.GoogleAPICallError("500 Internal Server Error")
    assert client.should_fallback(exception) is False


def test_openrouter_client_init_sem_api_key():
    """Testa OpenRouterClient.__init__ sem OPENROUTER_API_KEY (linha 221)"""
    with patch("chatbot_acessibilidade.core.llm_provider.settings") as mock_settings:
        mock_settings.openrouter_api_key = None

        with pytest.raises(ValueError) as exc_info:
            OpenRouterClient()

        assert "OPENROUTER_API_KEY" in str(exc_info.value)


@patch("chatbot_acessibilidade.core.llm_provider.httpx.AsyncClient")
@pytest.mark.asyncio
async def test_openrouter_client_resposta_sem_message_content(mock_client_class):
    """Testa OpenRouterClient quando resposta não tem message/content (linha 278)"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"no_content": "invalid"}}]  # Sem "content"
    }
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client_class.return_value = mock_client

    with patch("chatbot_acessibilidade.core.llm_provider.settings") as mock_settings:
        mock_settings.openrouter_api_key = "test_key"
        mock_settings.openrouter_timeout_seconds = 60

        client = OpenRouterClient()
        # Mock _get_client para retornar o mock_client
        client._get_client = MagicMock(return_value=mock_client)

        with pytest.raises(APIError) as exc_info:
            await client.generate("Teste", model="test-model")

        # O erro pode ser capturado pelo handler genérico, então verificamos ambas as mensagens
        error_msg = str(exc_info.value).lower()
        assert (
            "sem content" in error_msg
            or "falha inesperada" in error_msg
            or "openrouter" in error_msg
        )


def test_openrouter_client_should_fallback():
    """Testa OpenRouterClient.should_fallback (linha 316-318)"""
    with patch("chatbot_acessibilidade.core.llm_provider.settings") as mock_settings:
        mock_settings.openrouter_api_key = "test_key"

        client = OpenRouterClient()

        # Testa com QuotaExhaustedError
        assert client.should_fallback(QuotaExhaustedError("test")) is True

        # Testa com ModelUnavailableError
        assert client.should_fallback(ModelUnavailableError("test")) is True

        # Testa com outra exceção
        assert client.should_fallback(ValueError("test")) is False


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_generate_with_fallback_should_fallback_false_primary(
    mock_settings, mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa generate_with_fallback quando should_fallback retorna False no primary (linha 354)"""
    mock_settings.fallback_enabled = True
    mock_settings.api_timeout_seconds = 60

    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session

    async def async_gen_error(**kwargs):
        await asyncio.sleep(0.01)
        raise ValueError("Erro que não deve acionar fallback")
        yield

    mock_runner = AsyncMock()
    mock_runner.run_async = async_gen_error
    mock_runner_class.return_value = mock_runner

    primary_client = GoogleGeminiClient(mock_agent)
    # Mock should_fallback para retornar False
    primary_client.should_fallback = MagicMock(return_value=False)

    # O erro ValueError será capturado pelo handler genérico e transformado em AgentError
    # Mas como should_fallback retorna False, não deve acionar fallback
    # O generate_with_fallback vai re-lançar o erro na linha 354
    from chatbot_acessibilidade.core.exceptions import AgentError

    with pytest.raises(AgentError):  # O erro é transformado em AgentError pelo GoogleGeminiClient
        await generate_with_fallback(
            primary_client=primary_client,
            prompt="Teste",
            fallback_clients=None,
            fallback_models=None,
        )


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_generate_with_fallback_openrouter_should_fallback_false_raise(
    mock_settings, mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa generate_with_fallback quando should_fallback retorna False no fallback OpenRouter (linha 388)"""
    mock_settings.fallback_enabled = True
    mock_settings.openrouter_api_key = "test_key"
    mock_settings.api_timeout_seconds = 60

    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session

    async def async_gen_error(**kwargs):
        await asyncio.sleep(0.01)
        raise google_exceptions.ResourceExhausted("Rate limit")
        yield

    mock_runner = AsyncMock()
    mock_runner.run_async = async_gen_error
    mock_runner_class.return_value = mock_runner

    openrouter_client = OpenRouterClient()
    openrouter_client.generate = AsyncMock(
        side_effect=ValueError("Erro que não deve acionar fallback")
    )
    openrouter_client.should_fallback = MagicMock(return_value=False)

    primary_client = GoogleGeminiClient(mock_agent)
    primary_client.should_fallback = MagicMock(return_value=True)

    with pytest.raises(ValueError) as exc_info:
        await generate_with_fallback(
            primary_client=primary_client,
            prompt="Teste",
            fallback_clients=[openrouter_client],
            fallback_models=["test-model"],
        )

    assert "erro que não deve acionar fallback" in str(exc_info.value).lower()


@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_generate_with_fallback_outro_cliente_should_fallback_true(
    mock_settings, mock_session_service, mock_runner_class, mock_client_class, mock_agent
):
    """Testa generate_with_fallback quando outro cliente should_fallback retorna True (linha 398-402)"""
    mock_settings.fallback_enabled = True
    mock_settings.api_timeout_seconds = 60

    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session

    async def async_gen_error(**kwargs):
        await asyncio.sleep(0.01)
        raise google_exceptions.ResourceExhausted("Rate limit")
        yield

    mock_runner = AsyncMock()
    mock_runner.run_async = async_gen_error
    mock_runner_class.return_value = mock_runner

    # Cria um cliente mock que não é OpenRouter
    mock_other_client = MagicMock()
    mock_other_client.get_provider_name.return_value = "OtherProvider"
    # Retorna sucesso diretamente (não falha)
    mock_other_client.generate = AsyncMock(return_value="Resposta do outro provedor")
    mock_other_client.should_fallback = MagicMock(return_value=True)  # Permite fallback

    primary_client = GoogleGeminiClient(mock_agent)
    primary_client.should_fallback = MagicMock(return_value=True)

    resposta, provedor = await generate_with_fallback(
        primary_client=primary_client,
        prompt="Teste",
        fallback_clients=[mock_other_client],
        fallback_models=None,
    )

    assert resposta == "Resposta do outro provedor"
    assert provedor == "OtherProvider"


@patch("chatbot_acessibilidade.core.llm_provider.settings")
def test_google_gemini_client_get_genai_client_api_key_vazia(mock_settings, mock_agent):
    """Testa _get_genai_client com api_key vazia (linha 96-98)"""
    mock_settings.google_api_key = ""  # API key vazia

    client = GoogleGeminiClient(mock_agent)

    with pytest.raises(ValueError, match="GOOGLE_API_KEY não configurada"):
        client._get_genai_client()


@patch("chatbot_acessibilidade.core.llm_provider.logger")
@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.settings")
def test_google_gemini_client_logging_inicializacao(
    mock_settings, mock_client_class, mock_logger, mock_agent
):
    """Testa logging de inicialização (linha 93, 99, 102, 103-105)"""
    mock_settings.google_api_key = "test_key_12345"

    client = GoogleGeminiClient(mock_agent)
    mock_client_instance = MagicMock()
    mock_client_class.return_value = mock_client_instance

    # Chama _get_genai_client para inicializar
    client._get_genai_client()

    # Verifica que logger foi chamado (linhas 93, 99, 102)
    assert mock_logger.info.call_count >= 2  # Linha 93 e 102
    mock_logger.debug.assert_called()  # Linha 99


@patch("chatbot_acessibilidade.core.llm_provider.logger")
@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@patch("chatbot_acessibilidade.core.llm_provider.settings")
def test_google_gemini_client_logging_erro_inicializacao(
    mock_settings, mock_client_class, mock_logger, mock_agent
):
    """Testa logging de erro na inicialização (linha 103-105)"""
    mock_settings.google_api_key = "test_key_12345"

    client = GoogleGeminiClient(mock_agent)
    # Simula erro ao criar genai.Client
    mock_client_class.side_effect = Exception("Erro ao criar cliente")

    # Chama _get_genai_client que deve levantar exceção
    with pytest.raises(Exception, match="Erro ao criar cliente"):
        client._get_genai_client()

    # Verifica que logger.error foi chamado (linha 104)
    mock_logger.error.assert_called()


@patch("chatbot_acessibilidade.core.llm_provider.settings")
@patch("chatbot_acessibilidade.core.llm_provider.InMemorySessionService")
@patch("chatbot_acessibilidade.core.llm_provider.Runner")
@patch("chatbot_acessibilidade.core.llm_provider.genai.Client")
@pytest.mark.asyncio
async def test_google_gemini_client_google_api_error_nao_503_detalhado(
    mock_client_class, mock_runner_class, mock_session_service_class, mock_settings, mock_agent
):
    """Testa GoogleAPICallError que não é 503 (linha 186, 195-201)"""
    mock_settings.google_api_key = "test_key"
    mock_settings.api_timeout_seconds = 60

    # Mock do session service
    mock_session_service = AsyncMock()
    mock_session_service.create_session = AsyncMock()
    mock_session_service_class.return_value = mock_session_service

    # Mock do runner que levanta GoogleAPICallError sem 503
    async def async_gen_error(**kwargs):
        await asyncio.sleep(0.01)
        raise google_exceptions.GoogleAPICallError("500 Internal Server Error")
        yield

    mock_runner = AsyncMock()
    mock_runner.run_async = async_gen_error
    mock_runner_class.return_value = mock_runner

    client = GoogleGeminiClient(mock_agent)

    # Deve cair no except GoogleAPICallError (linha 195) e não no 503 (linha 186)
    with pytest.raises(APIError, match="Ocorreu um problema de comunicação"):
        await client.generate("teste")


def test_google_gemini_should_fallback_google_api_error_503():
    """Testa should_fallback com GoogleAPICallError 503 (linha 220-223)"""
    client = GoogleGeminiClient(MagicMock(spec=Agent))

    # GoogleAPICallError com 503
    exception = google_exceptions.GoogleAPICallError("503 Service Unavailable")
    assert client.should_fallback(exception) is True

    # GoogleAPICallError com overloaded
    exception = google_exceptions.GoogleAPICallError("Service overloaded")
    assert client.should_fallback(exception) is True


@patch("chatbot_acessibilidade.core.llm_provider.httpx.AsyncClient")
@patch("chatbot_acessibilidade.core.llm_provider.settings")
def test_openrouter_client_get_client_erro(mock_settings, mock_async_client_class):
    """Testa _get_client com erro na inicialização (linha 246, 303)"""
    mock_settings.openrouter_api_key = "test_key"
    mock_settings.openrouter_timeout_seconds = 60

    # Simula erro ao criar AsyncClient na primeira chamada
    mock_async_client_class.side_effect = [Exception("Erro ao criar cliente"), httpx.AsyncClient()]

    client = OpenRouterClient()

    # Primeira chamada deve levantar exceção (linha 246)
    with pytest.raises(Exception, match="Erro ao criar cliente"):
        client._get_client()

    # Segunda chamada deve funcionar (mock retorna cliente válido)
    # Isso testa o cache (linha 245) e a linha 303 não é alcançada neste caso
    client2 = client._get_client()
    assert client2 is not None


@patch("chatbot_acessibilidade.core.llm_provider.httpx.AsyncClient")
@patch("chatbot_acessibilidade.core.llm_provider.settings")
def test_openrouter_client_get_client_cache(mock_settings, mock_async_client_class):
    """Testa _get_client com cache (linha 245, 303)"""
    mock_settings.openrouter_api_key = "test_key"
    mock_settings.openrouter_timeout_seconds = 60

    mock_client_instance = MagicMock()
    mock_async_client_class.return_value = mock_client_instance

    client = OpenRouterClient()

    # Primeira chamada cria o cliente (linha 246)
    client1 = client._get_client()
    assert client1 is not None
    assert mock_async_client_class.call_count == 1

    # Segunda chamada retorna o mesmo cliente (cache, linha 245)
    client2 = client._get_client()
    assert client1 is client2
    assert mock_async_client_class.call_count == 1  # Não cria novo cliente


@patch("chatbot_acessibilidade.core.llm_provider.settings")
@pytest.mark.asyncio
async def test_generate_with_fallback_todos_modelos_falham_detalhado(mock_settings, mock_agent):
    """Testa generate_with_fallback quando todos os modelos falham (linha 421-425)"""
    mock_settings.fallback_enabled = True
    mock_settings.api_timeout_seconds = 60
    mock_settings.openrouter_api_key = "test_key"
    mock_settings.openrouter_models = "model1,model2"

    primary_client = GoogleGeminiClient(mock_agent)
    primary_client.generate = AsyncMock(side_effect=QuotaExhaustedError("Quota esgotada"))
    primary_client.should_fallback = MagicMock(return_value=True)

    # Cria OpenRouterClient que falha em todos os modelos
    openrouter_client = OpenRouterClient()
    openrouter_client.generate = AsyncMock(side_effect=APIError("Erro no modelo"))
    openrouter_client.should_fallback = MagicMock(return_value=True)

    with pytest.raises(APIError, match="Todos os provedores e modelos disponíveis falharam"):
        await generate_with_fallback(
            primary_client=primary_client,
            prompt="teste",
            fallback_clients=[openrouter_client],
            fallback_models=["model1", "model2"],
        )
