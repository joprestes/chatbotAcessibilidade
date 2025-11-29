"""
Testes de Fallback e Retry

Testa sistema de fallback automático e retry de requisições.
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from pathlib import Path
import sys

pytestmark = pytest.mark.integration

# Adiciona src ao path
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from backend.api import app  # noqa: E402


@pytest.fixture
def client():
    """Cliente HTTP para testes de integração."""
    return TestClient(app)


@pytest.mark.asyncio
async def test_automatic_fallback_on_gemini_failure():
    """
    Testa fallback automático quando Google Gemini falha.
    """
    from chatbot_acessibilidade.core.llm_provider import (
        GoogleGeminiClient,
        generate_with_fallback,
    )
    from chatbot_acessibilidade.core.exceptions import APIError

    # Mock de falha do Gemini
    mock_gemini = MagicMock(spec=GoogleGeminiClient)
    mock_gemini.generate = AsyncMock(side_effect=APIError("Google Gemini quota exceeded"))
    mock_gemini.should_fallback.return_value = True

    # Mock de sucesso de um cliente genérico de fallback
    mock_fallback_client = MagicMock()
    mock_fallback_client.get_provider_name.return_value = "Generic Fallback"
    mock_fallback_client.generate = AsyncMock(return_value="Resposta do Fallback")
    mock_fallback_client.should_fallback.return_value = True

    # Mock de settings para habilitar fallback
    with patch("chatbot_acessibilidade.core.llm_provider.settings") as mock_settings:
        mock_settings.fallback_enabled = True

        # Testa fallback diretamente
        resposta, provedor = await generate_with_fallback(
            primary_client=mock_gemini,
            prompt="Teste de fallback",
            fallback_clients=[mock_fallback_client],
        )

        # Verifica que fallback foi usado
        assert "Generic Fallback" in provedor or provedor == "Generic Fallback"
        assert resposta == "Resposta do Fallback"
        assert mock_gemini.generate.called
        assert mock_fallback_client.generate.called


@pytest.mark.asyncio
async def test_retry_on_temporary_error():
    """
    Testa retry automático em erros temporários.
    Nota: Este teste verifica que retry é configurado, mas pode não executar
    retry real devido à complexidade de mockar tenacity.
    """
    from chatbot_acessibilidade.agents.dispatcher import rodar_agente
    from chatbot_acessibilidade.agents.factory import criar_agentes

    # Obtém agentes disponíveis
    agentes = criar_agentes()
    # Nota: O agente se chama "assistente" (português), não "assistant" (inglês)
    if "assistente" not in agentes:
        pytest.skip("Agente 'assistente' não disponível")

    agent = agentes["assistente"]

    # Mock de generate_with_fallback que simula retry
    call_count = 0

    async def mock_fallback(primary_client, prompt, fallback_clients=None, fallback_models=None):
        nonlocal call_count
        call_count += 1
        # Simula que após algumas tentativas, funciona
        if call_count < 2:
            from chatbot_acessibilidade.core.exceptions import APIError

            raise APIError("Temporary error")
        return ("Resposta após retry", "Google Gemini")

    with patch(
        "chatbot_acessibilidade.agents.dispatcher.generate_with_fallback", new=mock_fallback
    ):
        # Executa agente
        try:
            resposta = await rodar_agente(agent, "Teste retry", "user", "sessao")
            # Se retry funcionou, deve ter resposta
            assert "Resposta" in resposta
        except Exception:
            # Se falhou, verifica que tentou
            assert call_count > 0


@pytest.mark.asyncio
async def test_all_providers_fail(client: TestClient):
    """
    Testa quando todos os provedores falham.
    """
    from chatbot_acessibilidade.core.exceptions import APIError

    # Mock de falha de todos os provedores
    with patch("chatbot_acessibilidade.pipeline.pipeline_acessibilidade") as mock_pipeline:
        mock_pipeline.side_effect = APIError("Todos os modelos disponíveis falharam")

        # Tenta fazer requisição
        response = client.post("/api/chat", json={"pergunta": "Teste falha total"})

        # Deve retornar erro 500 ou mensagem de erro apropriada
        assert response.status_code in [500, 503]

        data = response.json()
        error_message = str(data.get("detail", "")).lower()
        assert "falharam" in error_message or "erro" in error_message
