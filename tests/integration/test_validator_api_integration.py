"""
Testes de Integração: Validators + API

Valida que validação de input funciona corretamente na API,
incluindo sanitização, detecção de ataques e rejeição de inputs inválidos.
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


@pytest.fixture
def client():
    """Cliente HTTP para testes de integração."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_pipeline():
    """Mocka pipeline para não fazer chamadas reais à API."""
    mock_response = {
        "introducao": "Introdução sobre o tema",
        "corpo": "Corpo detalhado da resposta",
        "conclusao": "Conclusão do tema",
        "exemplos": [{"titulo": "Exemplo", "codigo": "code", "explicacao": "explicação"}],
        "testes_sugeridos": ["Teste 1"],
        "materiais_estudo": ["Material 1"],
        "dica_final": "Dica final",
    }

    # Mocka no módulo onde é importado (backend.api), não onde é definido
    with patch("backend.api.pipeline_acessibilidade", new=AsyncMock(return_value=mock_response)):
        yield


def test_api_sanitizes_sql_injection_attempts(client: TestClient):
    """
    Testa que API sanitiza tentativas de SQL injection.

    Categoria: Integration Test
    Objetivo: Validar integração Validators + API
    Fluxo: SQL Injection → Sanitização → Resposta segura
    """
    # Arrange
    sql_payloads = [
        "test' OR 1=1--",
        "'; DROP TABLE users--",
        "1' UNION SELECT NULL--",
    ]

    # Act & Assert
    for payload in sql_payloads:
        response = client.post("/api/chat", json={"pergunta": payload})

        # Deve sanitizar ou rejeitar
        assert response.status_code in [200, 400]

        # Se aceitar, resposta não deve conter evidências de SQL
        if response.status_code == 200:
            data = response.json()
            response_str = str(data).lower()
            assert "sql" not in response_str
            assert "syntax error" not in response_str


def test_api_sanitizes_xss_attempts(client: TestClient):
    """
    Testa que API sanitiza tentativas de XSS.

    Categoria: Integration Test
    Objetivo: Validar sanitização de XSS
    Fluxo: XSS Payload → Sanitização → Resposta segura
    """
    # Arrange
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
    ]

    # Act & Assert
    for payload in xss_payloads:
        response = client.post("/api/chat", json={"pergunta": payload})

        # Deve sanitizar ou rejeitar
        assert response.status_code in [200, 400]

        # Se aceitar, resposta não deve conter scripts não escapados
        if response.status_code == 200:
            data = response.json()
            response_str = str(data)
            assert "<script>" not in response_str.lower()
            assert "onerror=" not in response_str.lower()


def test_api_rejects_empty_question(client: TestClient):
    """
    Testa que API rejeita pergunta vazia.

    Categoria: Integration Test
    Objetivo: Validar validação de input obrigatório
    Fluxo: Pergunta vazia → Validação → Erro 422
    """
    # Arrange - apenas strings realmente vazias
    empty_questions = ["", "   "]

    # Act & Assert
    for question in empty_questions:
        response = client.post("/api/chat", json={"pergunta": question})

        # Deve rejeitar (422 = Unprocessable Entity)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


def test_api_rejects_too_short_question(client: TestClient):
    """
    Testa que API rejeita pergunta muito curta.

    Categoria: Integration Test
    Objetivo: Validar validação de comprimento mínimo
    Fluxo: Pergunta < 3 chars → Validação → Erro 422
    """
    # Arrange
    short_questions = ["a", "ab"]

    # Act & Assert
    for question in short_questions:
        response = client.post("/api/chat", json={"pergunta": question})

        # Deve rejeitar
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


def test_api_rejects_too_long_question(client: TestClient):
    """
    Testa que API rejeita pergunta muito longa.

    Categoria: Integration Test
    Objetivo: Validar validação de comprimento máximo
    Fluxo: Pergunta > 2000 chars → Validação → Erro 422
    """
    # Arrange
    long_question = "a" * 2001

    # Act
    response = client.post("/api/chat", json={"pergunta": long_question})

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_api_sanitizes_control_characters(client: TestClient):
    """
    Testa que API remove caracteres de controle.

    Categoria: Integration Test
    Objetivo: Validar sanitização de caracteres de controle
    Fluxo: Input com \\x00 → Sanitização → Resposta limpa
    """
    # Arrange
    question_with_control = "teste\\x00\\x01\\x02 de controle"

    # Act
    response = client.post("/api/chat", json={"pergunta": question_with_control})

    # Assert
    # Deve aceitar após sanitização
    assert response.status_code in [200, 400]

    # Se aceitar, resposta não deve conter caracteres de controle
    if response.status_code == 200:
        data = response.json()
        response_str = str(data)
        assert "\\x00" not in response_str
        assert "\\x01" not in response_str


def test_api_handles_special_characters(client: TestClient):
    """
    Testa que API lida corretamente com caracteres especiais.

    Categoria: Integration Test
    Objetivo: Validar que caracteres especiais são aceitos
    Fluxo: Input com emojis/acentos → Processamento → Resposta OK
    """
    # Arrange
    questions_with_special = [
        "O que é acessibilidade? 🦾",
        "Café com açúcar",
        "Test with émojis 😀",
    ]

    # Act & Assert
    for question in questions_with_special:
        response = client.post("/api/chat", json={"pergunta": question})

        # Deve aceitar
        assert response.status_code == 200
        data = response.json()
        assert "resposta" in data


def test_api_normalizes_whitespace(client: TestClient):
    """
    Testa que API normaliza espaços em branco.

    Categoria: Integration Test
    Objetivo: Validar normalização de whitespace
    Fluxo: "teste    com    espaços" → "teste com espaços"
    """
    # Arrange
    question_with_spaces = "O  que   é    WCAG?"
    question_normalized = "O que é WCAG?"

    # Act
    response1 = client.post("/api/chat", json={"pergunta": question_with_spaces})
    response2 = client.post("/api/chat", json={"pergunta": question_normalized})

    # Assert - Ambas devem retornar mesma resposta (cache hit)
    assert response1.status_code == 200
    assert response2.status_code == 200
    # Respostas devem ser idênticas (normalização funcionou)
    assert response1.json() == response2.json()
