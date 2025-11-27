"""
Testes de Integração Profunda (Deep Integration) para o fluxo de Chat.

Estes testes verificam a integração entre a API, o Orquestrador e os Agentes,
mockando apenas a chamada externa ao LLM (get_agent_response).
Diferente dos testes E2E que mockam o pipeline inteiro, estes testes
exercitam a lógica do PipelineOrquestrador.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from src.backend.api import app

pytestmark = pytest.mark.integration


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_chat_flow_deep_integration_success(client):
    """
    Verifica o fluxo completo de sucesso:
    API -> Pipeline -> Orquestrador -> Agentes (Mockados) -> Formatador -> Resposta
    """

    # Mock para simular as respostas dos agentes
    async def mock_get_agent_response(agent_name, prompt, model_type):
        responses = {
            "assistente": "Resposta inicial do assistente sobre acessibilidade.",
            "validador": "OK",  # Validador aprova
            "revisor": "Resposta revisada e simplificada.",
            "testador": "Plano de testes sugerido.",
            "aprofundador": "Links para estudo.",
        }
        return responses.get(agent_name, "Resposta padrão")

    with patch(
        "chatbot_acessibilidade.pipeline.orquestrador.get_agent_response",
        side_effect=mock_get_agent_response,
    ) as mock_agent:

        # Executa a requisição
        response = client.post("/api/chat", json={"pergunta": "Como testar contraste?"})

        # Verificações
        assert response.status_code == 200
        data = response.json()

        # Verifica se o orquestrador chamou todos os agentes
        assert mock_agent.call_count == 5

        # Verifica se a resposta está formatada corretamente
        resposta = data["resposta"]
        assert "📘 **Introdução**" in resposta
        assert "🔍 **Conceitos Essenciais**" in resposta
        assert "🧪 **Como Testar na Prática**" in resposta
        assert "📚 **Quer se Aprofundar?**" in resposta

        # Verifica conteúdo específico vindo dos mocks
        assert "Resposta revisada" in resposta["🔍 **Conceitos Essenciais**"]
        assert "Plano de testes" in resposta["🧪 **Como Testar na Prática**"]


@pytest.mark.asyncio
async def test_chat_flow_deep_integration_validator_correction(client):
    """
    Verifica o fluxo onde o Validador corrige a resposta do Assistente.
    """

    async def mock_get_agent_response(agent_name, prompt, model_type):
        if agent_name == "assistente":
            return "Resposta incorreta."
        if agent_name == "validador":
            return "Resposta corrigida pelo validador."
        if agent_name == "revisor":
            # Revisor deve receber a resposta corrigida
            assert "Resposta corrigida" in prompt
            return "Resposta final revisada."
        return "Conteúdo extra"

    with patch(
        "chatbot_acessibilidade.pipeline.orquestrador.get_agent_response",
        side_effect=mock_get_agent_response,
    ):
        response = client.post("/api/chat", json={"pergunta": "Pergunta complexa"})
        assert response.status_code == 200
        data = response.json()
        assert "Resposta final revisada" in data["resposta"]["🔍 **Conceitos Essenciais**"]


@pytest.mark.asyncio
async def test_chat_flow_deep_integration_parallel_failure(client):
    """
    Verifica se o pipeline continua funcionando mesmo se um agente paralelo falhar.
    """

    async def mock_get_agent_response(agent_name, prompt, model_type):
        if agent_name == "testador":
            raise Exception("Erro no agente testador")
        return "Conteúdo válido"

    with patch(
        "chatbot_acessibilidade.pipeline.orquestrador.get_agent_response",
        side_effect=mock_get_agent_response,
    ):
        response = client.post("/api/chat", json={"pergunta": "Pergunta teste erro"})

        assert response.status_code == 200
        data = response.json()

        # O campo de testes deve conter a mensagem de fallback
        assert (
            "Não foi possível gerar sugestões de testes"
            in data["resposta"]["🧪 **Como Testar na Prática**"]
        )
        # O resto deve estar normal
        assert "Conteúdo válido" in data["resposta"]["🔍 **Conceitos Essenciais**"]
