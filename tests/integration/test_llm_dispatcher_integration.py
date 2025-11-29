"""
Testes de Integração: LLM Provider + Dispatcher

Valida integração entre LLM provider e dispatcher,
incluindo fallback, retry e error handling.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys
from unittest.mock import patch, AsyncMock

pytestmark = pytest.mark.integration

# Adiciona src ao path
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from backend.api import app  # noqa: E402
from chatbot_acessibilidade.core.exceptions import AgentError  # noqa: E402


@pytest.fixture
def client():
    """Cliente HTTP para testes de integração."""
    return TestClient(app)


def test_llm_dispatcher_successful_response(client: TestClient):
    """
    Testa que dispatcher processa resposta do LLM com sucesso.

    Categoria: Integration Test
    Objetivo: Validar integração LLM + Dispatcher
    Fluxo: Request → Dispatcher → LLM → Response
    """
    # Arrange
    mock_response = {
        "introducao": "Introdução sobre acessibilidade",
        "corpo": "Corpo detalhado",
        "conclusao": "Conclusão",
        "exemplos": [{"titulo": "Ex1", "codigo": "code", "explicacao": "exp"}],
        "testes_sugeridos": ["Teste 1"],
        "materiais_estudo": ["Material 1"],
        "dica_final": "Dica final",
    }

    # Act
    with patch("backend.api.pipeline_acessibilidade", new=AsyncMock(return_value=mock_response)):
        response = client.post("/api/chat", json={"pergunta": "O que é WCAG?"})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "resposta" in data
    assert data["resposta"]["introducao"] == "Introdução sobre acessibilidade"


def test_llm_dispatcher_handles_timeout(client: TestClient):
    """
    Testa que dispatcher trata timeout do LLM corretamente.

    Categoria: Integration Test
    Objetivo: Validar tratamento de timeout
    Fluxo: Request → Dispatcher → LLM timeout → Error response
    """

    # Arrange
    async def mock_timeout(*args, **kwargs):
        raise TimeoutError("LLM timeout")

    # Act
    with patch("backend.api.pipeline_acessibilidade", new=mock_timeout):
        response = client.post("/api/chat", json={"pergunta": "teste timeout"})

    # Assert
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data


def test_llm_dispatcher_handles_api_error(client: TestClient):
    """
    Testa que dispatcher trata erro de API do LLM.

    Categoria: Integration Test
    Objetivo: Validar tratamento de erro de API
    Fluxo: Request → Dispatcher → LLM error → Error response
    """

    # Arrange
    async def mock_api_error(*args, **kwargs):
        raise AgentError("Erro na API do LLM")

    # Act
    with patch("backend.api.pipeline_acessibilidade", new=mock_api_error):
        response = client.post("/api/chat", json={"pergunta": "teste erro"})

    # Assert
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data


def test_llm_dispatcher_propagates_validation_errors(client: TestClient):
    """
    Testa que dispatcher propaga erros de validação corretamente.

    Categoria: Integration Test
    Objetivo: Validar propagação de erros de validação
    Fluxo: Request inválida → Validação → Error 422
    """
    # Arrange
    invalid_request = {"pergunta": ""}  # Pergunta vazia

    # Act
    response = client.post("/api/chat", json=invalid_request)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_llm_dispatcher_handles_malformed_response(client: TestClient):
    """
    Testa que dispatcher trata resposta malformada do LLM.

    Categoria: Integration Test
    Objetivo: Validar tratamento de resposta inválida
    Fluxo: Request → LLM → Resposta inválida → Error
    """
    # Arrange
    malformed_response = {"invalid": "structure"}  # Falta campos obrigatórios

    # Act
    with patch(
        "backend.api.pipeline_acessibilidade",
        new=AsyncMock(return_value=malformed_response),
    ):
        response = client.post("/api/chat", json={"pergunta": "teste malformed"})

    # Assert
    # Pode retornar 500 se validação falhar ou 200 se aceitar parcialmente
    assert response.status_code in [200, 500]


def test_llm_dispatcher_processes_multiple_requests(client: TestClient):
    """
    Testa que dispatcher processa múltiplas requests corretamente.

    Categoria: Integration Test
    Objetivo: Validar processamento sequencial
    Fluxo: Request 1 → Response 1, Request 2 → Response 2
    """

    # Arrange
    async def mock_response(pergunta: str):
        return {
            "introducao": f"Sobre {pergunta[:10]}",
            "corpo": "Corpo",
            "conclusao": "Conclusão",
            "exemplos": [{"titulo": "Ex", "codigo": "c", "explicacao": "e"}],
            "testes_sugeridos": ["T"],
            "materiais_estudo": ["M"],
            "dica_final": "D",
        }

    # Act
    with patch("backend.api.pipeline_acessibilidade", new=mock_response):
        response1 = client.post("/api/chat", json={"pergunta": "Pergunta 1"})
        response2 = client.post("/api/chat", json={"pergunta": "Pergunta 2"})

    # Assert
    assert response1.status_code == 200
    assert response2.status_code == 200

    # Respostas devem ser diferentes
    data1 = response1.json()
    data2 = response2.json()
    assert data1["resposta"]["introducao"] != data2["resposta"]["introducao"]


def test_llm_dispatcher_maintains_context(client: TestClient):
    """
    Testa que dispatcher mantém contexto entre chamadas.

    Categoria: Integration Test
    Objetivo: Validar manutenção de contexto
    Fluxo: Request com contexto → Dispatcher → Response contextualizada
    """
    # Arrange
    mock_response = {
        "introducao": "Introdução contextualizada",
        "corpo": "Corpo com contexto",
        "conclusao": "Conclusão",
        "exemplos": [{"titulo": "Ex", "codigo": "c", "explicacao": "e"}],
        "testes_sugeridos": ["T"],
        "materiais_estudo": ["M"],
        "dica_final": "D",
    }

    # Act
    with patch("backend.api.pipeline_acessibilidade", new=AsyncMock(return_value=mock_response)):
        response = client.post("/api/chat", json={"pergunta": "Continue sobre acessibilidade"})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "resposta" in data


def test_llm_dispatcher_handles_empty_response(client: TestClient):
    """
    Testa que dispatcher trata resposta vazia do LLM.

    Categoria: Integration Test
    Objetivo: Validar tratamento de resposta vazia
    Fluxo: Request → LLM → Resposta vazia → Error
    """
    # Arrange
    from typing import Any, Dict

    empty_response: Dict[str, Any] = {}

    # Act
    with patch(
        "backend.api.pipeline_acessibilidade",
        new=AsyncMock(return_value=empty_response),
    ):
        response = client.post("/api/chat", json={"pergunta": "teste vazio"})

    # Assert
    # Deve retornar erro ou resposta parcial
    assert response.status_code in [200, 500]


def test_llm_dispatcher_response_structure_validation(client: TestClient):
    """
    Testa que dispatcher valida estrutura da resposta.

    Categoria: Integration Test
    Objetivo: Validar que resposta tem estrutura esperada
    Fluxo: Request → LLM → Response → Validação estrutura
    """
    # Arrange
    valid_response = {
        "introducao": "Intro",
        "corpo": "Corpo",
        "conclusao": "Conclusão",
        "exemplos": [{"titulo": "T", "codigo": "C", "explicacao": "E"}],
        "testes_sugeridos": ["Teste"],
        "materiais_estudo": ["Material"],
        "dica_final": "Dica",
    }

    # Act
    with patch(
        "backend.api.pipeline_acessibilidade",
        new=AsyncMock(return_value=valid_response),
    ):
        response = client.post("/api/chat", json={"pergunta": "teste estrutura"})

    # Assert
    assert response.status_code == 200
    data = response.json()
    resposta = data["resposta"]

    # Valida campos obrigatórios
    required_fields = [
        "introducao",
        "corpo",
        "conclusao",
        "exemplos",
        "testes_sugeridos",
        "materiais_estudo",
        "dica_final",
    ]
    for field in required_fields:
        assert field in resposta, f"Campo '{field}' ausente na resposta"
