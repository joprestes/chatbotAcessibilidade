"""
Testes para a API FastAPI
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from backend.api import app
from chatbot_acessibilidade.core.exceptions import ValidationError, APIError


@pytest.fixture
def client():
    """Cria um cliente de teste para a API"""
    return TestClient(app)


def test_health_check(client):
    """Testa o endpoint de health check"""
    response = client.get("/api/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "funcionando" in data["message"].lower()


@patch('backend.api.pipeline_acessibilidade', new_callable=AsyncMock)
def test_chat_endpoint_sucesso(mock_pipeline, client):
    """Testa o endpoint de chat com sucesso"""
    # Mock da resposta do pipeline
    mock_pipeline.return_value = {
        "📘 **Introdução**": "Introdução teste",
        "🔍 **Conceitos Essenciais**": "Conceitos teste",
        "🧪 **Como Testar na Prática**": "Testes teste",
        "📚 **Quer se Aprofundar?**": "Aprofundar teste",
        "👋 **Dica Final**": "Dica teste"
    }
    
    response = client.post(
        "/api/chat",
        json={"pergunta": "O que é WCAG?"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "resposta" in data
    assert "📘 **Introdução**" in data["resposta"]


@patch('backend.api.pipeline_acessibilidade', new_callable=AsyncMock)
def test_chat_endpoint_pergunta_vazia(mock_pipeline, client):
    """Testa o endpoint de chat com pergunta vazia"""
    response = client.post(
        "/api/chat",
        json={"pergunta": "  "}
    )
    
    assert response.status_code == 422  # Validation error do Pydantic


def test_chat_endpoint_pergunta_muito_curta(client):
    """Testa o endpoint com pergunta muito curta"""
    response = client.post(
        "/api/chat",
        json={"pergunta": "ab"}
    )
    
    assert response.status_code == 422


def test_chat_endpoint_pergunta_muito_longa(client):
    """Testa o endpoint com pergunta muito longa"""
    pergunta_longa = "a" * 2001
    response = client.post(
        "/api/chat",
        json={"pergunta": pergunta_longa}
    )
    
    assert response.status_code == 422


@patch('backend.api.pipeline_acessibilidade', new_callable=AsyncMock)
def test_chat_endpoint_erro_no_pipeline(mock_pipeline, client):
    """Testa o endpoint quando o pipeline retorna erro"""
    mock_pipeline.return_value = {"erro": "Erro de teste"}
    
    response = client.post(
        "/api/chat",
        json={"pergunta": "Teste"}
    )
    
    assert response.status_code == 500
    data = response.json()
    assert "erro" in data["detail"].lower() or "Erro de teste" in data["detail"]


@patch('backend.api.pipeline_acessibilidade', new_callable=AsyncMock)
def test_chat_endpoint_excecao_inesperada(mock_pipeline, client):
    """Testa o endpoint quando ocorre exceção inesperada"""
    mock_pipeline.side_effect = Exception("Erro inesperado")
    
    response = client.post(
        "/api/chat",
        json={"pergunta": "Teste"}
    )
    
    assert response.status_code == 500
    data = response.json()
    assert "erro" in data["detail"].lower()


def test_chat_endpoint_sem_body(client):
    """Testa o endpoint sem body"""
    response = client.post("/api/chat")
    
    assert response.status_code == 422


def test_chat_endpoint_metodo_errado(client):
    """Testa usar método errado no endpoint"""
    response = client.get("/api/chat")
    
    assert response.status_code == 405  # Method not allowed

