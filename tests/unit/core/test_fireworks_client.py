import pytest
from unittest.mock import Mock, patch, AsyncMock
from chatbot_acessibilidade.core.llm_provider import FireworksAIClient, QuotaExhaustedError, ModelUnavailableError, APIError
from chatbot_acessibilidade.core.constants import ErrorMessages

@pytest.fixture
def mock_settings():
    with patch("chatbot_acessibilidade.core.llm_provider.settings") as mock:
        mock.huggingface_api_key = "fake_key"
        mock.huggingface_timeout_seconds = 30
        yield mock

@pytest.fixture
def client(mock_settings):
    return FireworksAIClient()

@pytest.mark.asyncio
async def test_fireworks_client_initialization(client):
    assert client.api_key == "fake_key"
    assert client.timeout == 30
    assert client._client is None

@pytest.mark.asyncio
async def test_fireworks_client_get_client(client):
    with patch("openai.OpenAI") as mock_openai:
        openai_instance = Mock()
        mock_openai.return_value = openai_instance
        
        c = client._get_client()
        assert c == openai_instance
        assert client._client == openai_instance
        
        # Deve retornar a mesma instância na segunda chamada
        c2 = client._get_client()
        assert c2 == c
        mock_openai.assert_called_once()

@pytest.mark.asyncio
async def test_generate_success(client):
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Resposta gerada"))]
    
    with patch.object(client, "_get_client") as mock_get_client:
        mock_openai = Mock()
        mock_openai.chat.completions.create = Mock(return_value=mock_response)
        mock_get_client.return_value = mock_openai
        
        response = await client.generate("Teste", model="accounts/fireworks/models/llama-v3-70b-instruct")
        assert response == "Resposta gerada"

@pytest.mark.asyncio
async def test_generate_no_model(client):
    with pytest.raises(ValueError, match="Modelo deve ser especificado"):
        await client.generate("Teste")

@pytest.mark.asyncio
async def test_generate_timeout(client):
    with patch.object(client, "_get_client") as mock_get_client:
        mock_openai = Mock()
        # Simula timeout usando side_effect com sleep se necessário, mas aqui vamos mockar o wait_for
        mock_get_client.return_value = mock_openai
        
        with patch("asyncio.wait_for", side_effect=TimeoutError):
            with pytest.raises(APIError, match="Timeout"):
                await client.generate("Teste", model="modelo")

@pytest.mark.asyncio
async def test_generate_rate_limit(client):
    with patch.object(client, "_get_client") as mock_get_client:
        mock_openai = Mock()
        mock_openai.chat.completions.create.side_effect = Exception("429 Rate limit exceeded")
        mock_get_client.return_value = mock_openai
        
        with pytest.raises(QuotaExhaustedError):
            await client.generate("Teste", model="modelo")

@pytest.mark.asyncio
async def test_generate_model_unavailable(client):
    with patch.object(client, "_get_client") as mock_get_client:
        mock_openai = Mock()
        mock_openai.chat.completions.create.side_effect = Exception("503 Service Unavailable")
        mock_get_client.return_value = mock_openai
        
        with pytest.raises(ModelUnavailableError):
            await client.generate("Teste", model="modelo")

@pytest.mark.asyncio
async def test_generate_auth_error(client):
    with patch.object(client, "_get_client") as mock_get_client:
        mock_openai = Mock()
        mock_openai.chat.completions.create.side_effect = Exception("401 Unauthorized")
        mock_get_client.return_value = mock_openai
        
        with pytest.raises(APIError, match="API key inválida"):
            await client.generate("Teste", model="modelo")

@pytest.mark.asyncio
async def test_should_fallback(client):
    assert client.should_fallback(QuotaExhaustedError("erro")) is True
    assert client.should_fallback(ModelUnavailableError("erro")) is True
    assert client.should_fallback(Exception("outro erro")) is False

@pytest.mark.asyncio
async def test_get_provider_name(client):
    assert client.get_provider_name() == "Fireworks AI"
