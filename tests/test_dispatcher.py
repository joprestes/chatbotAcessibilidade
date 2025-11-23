"""
Testes para o módulo dispatcher.py
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from google.adk.agents import Agent
from google.genai import types
from google.api_core import exceptions as google_exceptions

from chatbot_acessibilidade.agents.dispatcher import (
    rodar_agente,
    get_agent_response,
    AGENTES
)
from chatbot_acessibilidade.core.exceptions import APIError, AgentError


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


@patch('chatbot_acessibilidade.agents.dispatcher.get_genai_client')
@patch('chatbot_acessibilidade.agents.dispatcher.Runner')
@patch('chatbot_acessibilidade.agents.dispatcher.InMemorySessionService')
async def test_rodar_agente_sucesso(mock_session_service, mock_runner_class, mock_client, mock_agent, mock_evento):
    """Testa execução bem-sucedida de um agente"""
    # Setup mocks
    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session
    
    mock_runner = AsyncMock()
    mock_runner.run_async = AsyncMock()
    mock_runner.run_async.return_value = [mock_evento]
    mock_runner_class.return_value = mock_runner
    
    # Executa
    resultado = await rodar_agente(mock_agent, "Teste de prompt")
    
    # Verifica
    assert resultado == "Resposta de teste"
    mock_session.create_session.assert_called_once()


@patch('chatbot_acessibilidade.agents.dispatcher.get_genai_client')
@patch('chatbot_acessibilidade.agents.dispatcher.Runner')
@patch('chatbot_acessibilidade.agents.dispatcher.InMemorySessionService')
async def test_rodar_agente_resposta_vazia(mock_session_service, mock_runner_class, mock_client, mock_agent):
    """Testa quando a resposta vem vazia"""
    # Setup mocks
    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session
    
    mock_runner = AsyncMock()
    evento_vazio = MagicMock()
    evento_vazio.is_final_response.return_value = True
    evento_vazio.content = None
    mock_runner.run_async = AsyncMock(return_value=[evento_vazio])
    mock_runner_class.return_value = mock_runner
    
    # Executa
    resultado = await rodar_agente(mock_agent, "Teste")
    
    # Verifica
    assert "vazia" in resultado.lower()


@patch('chatbot_acessibilidade.agents.dispatcher.get_genai_client')
@patch('chatbot_acessibilidade.agents.dispatcher.Runner')
@patch('chatbot_acessibilidade.agents.dispatcher.InMemorySessionService')
async def test_rodar_agente_rate_limit(mock_session_service, mock_runner_class, mock_client, mock_agent):
    """Testa tratamento de rate limit (429)"""
    # Setup mocks
    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session
    
    mock_runner = AsyncMock()
    mock_runner.run_async = AsyncMock(side_effect=google_exceptions.ResourceExhausted("Rate limit"))
    mock_runner_class.return_value = mock_runner
    
    # Executa e verifica exceção
    with pytest.raises(APIError) as exc_info:
        await rodar_agente(mock_agent, "Teste")
    
    assert "muitas perguntas" in str(exc_info.value).lower()


@patch('chatbot_acessibilidade.agents.dispatcher.get_genai_client')
@patch('chatbot_acessibilidade.agents.dispatcher.Runner')
@patch('chatbot_acessibilidade.agents.dispatcher.InMemorySessionService')
async def test_rodar_agente_permission_denied(mock_session_service, mock_runner_class, mock_client, mock_agent):
    """Testa tratamento de erro de autenticação (403)"""
    # Setup mocks
    mock_session = AsyncMock()
    mock_session_service.return_value = mock_session
    
    mock_runner = AsyncMock()
    mock_runner.run_async = AsyncMock(side_effect=google_exceptions.PermissionDenied("Invalid API key"))
    mock_runner_class.return_value = mock_runner
    
    # Executa e verifica exceção
    with pytest.raises(APIError) as exc_info:
        await rodar_agente(mock_agent, "Teste")
    
    assert "configuração" in str(exc_info.value).lower()


@patch('chatbot_acessibilidade.agents.dispatcher.rodar_agente')
async def test_get_agent_response_sucesso(mock_rodar_agente):
    """Testa get_agent_response com agente válido"""
    mock_rodar_agente.return_value = "Resposta de teste"
    
    resultado = await get_agent_response("assistente", "Teste", "prefixo")
    
    assert resultado == "Resposta de teste"
    mock_rodar_agente.assert_called_once()


async def test_get_agent_response_agente_inexistente():
    """Testa get_agent_response com agente que não existe"""
    resultado = await get_agent_response("agente_inexistente", "Teste", "prefixo")
    
    assert "não encontrado" in resultado.lower()
    assert resultado.startswith("Erro")

