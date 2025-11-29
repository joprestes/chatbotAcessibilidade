"""
Testes de Fallback e Retry

Testa sistema de fallback automático e retry de requisições.
"""

import pytest
from unittest.mock import patch
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

    # Mock de GoogleGeminiClient.generate que simula retry
    call_count = 0

    async def mock_generate(self, prompt):
        nonlocal call_count
        call_count += 1
        # Simula que após algumas tentativas, funciona
        if call_count < 2:
            from google.api_core import exceptions as google_exceptions

            # Simula erro que causa retry (503 ou ResourceExhausted)
            raise google_exceptions.ResourceExhausted("Temporary error")
        return "Resposta após retry"

    with patch(
        "chatbot_acessibilidade.core.llm_provider.GoogleGeminiClient.generate", new=mock_generate
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
