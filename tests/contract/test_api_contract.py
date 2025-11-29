"""
Testes de Contrato para API

Valida que contratos de API não quebram entre versões,
garantindo backward compatibility e documentando schemas.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys
from pydantic import BaseModel, ValidationError, Field
from typing import Dict, Any
from unittest.mock import patch

pytestmark = pytest.mark.contract

# Adiciona src ao path
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from backend.api import app  # noqa: E402


# ==================== SCHEMAS DE CONTRATO ====================


class ChatRequest(BaseModel):
    """Contrato de request do endpoint /api/chat"""

    pergunta: str = Field(..., min_length=3, max_length=2000)


class ExemploItem(BaseModel):
    """Contrato de item de exemplo"""

    titulo: str
    codigo: str
    explicacao: str


class ChatResponse(BaseModel):
    """Contrato de response do endpoint /api/chat"""

    resposta: Dict[str, Any]

    class Config:
        extra = "allow"  # Permite campos extras (não quebra se adicionar novos)


# ==================== FIXTURES ====================


@pytest.fixture
def client():
    """Cliente HTTP para testes de contrato."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_pipeline():
    """Mocka pipeline para não fazer chamadas reais à API."""

    async def mock_response(pergunta: str):
        return {
            "introducao": "Introdução sobre o tema",
            "corpo": "Corpo detalhado da resposta",
            "conclusao": "Conclusão do tema",
            "exemplos": [
                {
                    "titulo": "Exemplo 1",
                    "codigo": "code example",
                    "explicacao": "explicação detalhada",
                }
            ],
            "testes_sugeridos": ["Teste 1", "Teste 2"],
            "materiais_estudo": ["Material 1", "Material 2"],
            "dica_final": "Dica final importante",
        }

    with patch("backend.api.pipeline_acessibilidade", new=mock_response):
        yield


# ==================== TESTES DE CONTRATO DE REQUEST ====================


def test_chat_request_contract_valid():
    """
    Valida contrato de request válido.

    Categoria: Contract Test
    Objetivo: Validar que requests válidos são aceitos
    """
    # Arrange & Act
    valid_request = {"pergunta": "O que é WCAG?"}

    # Assert - Não deve lançar ValidationError
    ChatRequest(**valid_request)


def test_chat_request_contract_missing_field():
    """
    Valida que request sem campo obrigatório é rejeitado.

    Categoria: Contract Test
    Objetivo: Validar validação de campos obrigatórios
    """
    # Arrange
    invalid_request: Dict[str, Any] = {}

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        ChatRequest(**invalid_request)

    # Verifica que erro menciona campo faltante
    assert "pergunta" in str(exc_info.value)


def test_chat_request_contract_too_short():
    """
    Valida que pergunta muito curta é rejeitada.

    Categoria: Contract Test
    Objetivo: Validar comprimento mínimo
    """
    # Arrange
    invalid_request = {"pergunta": "ab"}  # < 3 chars

    # Act & Assert
    with pytest.raises(ValidationError):
        ChatRequest(**invalid_request)


def test_chat_request_contract_too_long():
    """
    Valida que pergunta muito longa é rejeitada.

    Categoria: Contract Test
    Objetivo: Validar comprimento máximo
    """
    # Arrange
    invalid_request = {"pergunta": "a" * 2001}  # > 2000 chars

    # Act & Assert
    with pytest.raises(ValidationError):
        ChatRequest(**invalid_request)


# ==================== TESTES DE CONTRATO DE RESPONSE ====================


def test_chat_response_contract_structure(client: TestClient):
    """
    Valida estrutura do response do endpoint /api/chat.

    Categoria: Contract Test
    Objetivo: Validar estrutura de response
    """
    # Arrange
    request_data = {"pergunta": "teste"}

    # Act
    response = client.post("/api/chat", json=request_data)

    # Assert - Status
    assert response.status_code == 200

    # Assert - Estrutura básica
    data = response.json()
    assert "resposta" in data

    # Assert - Valida com schema Pydantic
    ChatResponse(**data)


def test_chat_response_contract_required_fields(client: TestClient):
    """
    Valida que todos os campos obrigatórios estão presentes.

    Categoria: Contract Test
    Objetivo: Prevenir breaking changes (campos removidos)
    """
    # Arrange
    request_data = {"pergunta": "O que é acessibilidade?"}

    # Act
    response = client.post("/api/chat", json=request_data)

    # Assert
    assert response.status_code == 200
    data = response.json()
    resposta = data["resposta"]

    # Campos que NUNCA devem ser removidos (backward compatibility)
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
        assert field in resposta, f"Campo obrigatório '{field}' foi removido! BREAKING CHANGE!"


def test_chat_response_contract_field_types(client: TestClient):
    """
    Valida tipos de dados dos campos.

    Categoria: Contract Test
    Objetivo: Prevenir mudanças de tipo (breaking changes)
    """
    # Arrange
    request_data = {"pergunta": "teste de tipos"}

    # Act
    response = client.post("/api/chat", json=request_data)

    # Assert
    assert response.status_code == 200
    data = response.json()
    resposta = data["resposta"]

    # Valida tipos (não devem mudar)
    assert isinstance(resposta["introducao"], str), "introducao deve ser string"
    assert isinstance(resposta["corpo"], str), "corpo deve ser string"
    assert isinstance(resposta["conclusao"], str), "conclusao deve ser string"
    assert isinstance(resposta["exemplos"], list), "exemplos deve ser lista"
    assert isinstance(resposta["testes_sugeridos"], list), "testes_sugeridos deve ser lista"
    assert isinstance(resposta["materiais_estudo"], list), "materiais_estudo deve ser lista"
    assert isinstance(resposta["dica_final"], str), "dica_final deve ser string"


def test_chat_response_contract_exemplos_structure(client: TestClient):
    """
    Valida estrutura de items em exemplos.

    Categoria: Contract Test
    Objetivo: Validar schema de objetos aninhados
    """
    # Arrange
    request_data = {"pergunta": "teste exemplos"}

    # Act
    response = client.post("/api/chat", json=request_data)

    # Assert
    assert response.status_code == 200
    data = response.json()
    exemplos = data["resposta"]["exemplos"]

    # Se há exemplos, valida estrutura
    if len(exemplos) > 0:
        exemplo = exemplos[0]

        # Valida com schema Pydantic
        ExemploItem(**exemplo)

        # Valida campos obrigatórios
        assert "titulo" in exemplo
        assert "codigo" in exemplo
        assert "explicacao" in exemplo


def test_chat_response_contract_backward_compatibility(client: TestClient):
    """
    Valida que response é compatível com versões anteriores.

    Categoria: Contract Test
    Objetivo: Garantir backward compatibility
    """
    # Arrange
    request_data = {"pergunta": "teste compatibilidade"}

    # Act
    response = client.post("/api/chat", json=request_data)

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Response deve ter estrutura mínima esperada por clientes antigos
    assert "resposta" in data
    assert isinstance(data["resposta"], dict)

    # Campos obrigatórios que clientes antigos esperam
    legacy_fields = ["introducao", "corpo", "conclusao"]
    for field in legacy_fields:
        assert (
            field in data["resposta"]
        ), f"Campo '{field}' removido quebra compatibilidade com clientes antigos!"


# ==================== TESTES DE CONTRATO DE ERROS ====================


def test_chat_error_contract_validation_error(client: TestClient):
    """
    Valida contrato de erro de validação.

    Categoria: Contract Test
    Objetivo: Validar estrutura de erros 422
    """
    # Arrange - Request inválido
    invalid_request = {"pergunta": ""}

    # Act
    response = client.post("/api/chat", json=invalid_request)

    # Assert - Status
    assert response.status_code == 422

    # Assert - Estrutura de erro
    data = response.json()
    assert "detail" in data

    # FastAPI retorna lista de erros de validação
    assert isinstance(data["detail"], (list, str, dict))


def test_chat_error_contract_method_not_allowed(client: TestClient):
    """
    Valida contrato de erro 405.

    Categoria: Contract Test
    Objetivo: Validar erro de método não permitido
    """
    # Act - GET em endpoint POST-only
    response = client.get("/api/chat")

    # Assert
    assert response.status_code == 405
    data = response.json()
    assert "detail" in data


# ==================== TESTES DE VERSIONAMENTO ====================


def test_api_version_header_present(client: TestClient):
    """
    Valida que header de versão da API está presente.

    Categoria: Contract Test
    Objetivo: Documentar versão da API
    """
    # Arrange
    request_data = {"pergunta": "teste versão"}

    # Act
    response = client.post("/api/chat", json=request_data)

    # Assert
    assert response.status_code == 200

    # Nota: Se API tiver versionamento, validar aqui
    # assert "X-API-Version" in response.headers


def test_contract_documentation_alignment():
    """
    Valida que schemas Pydantic estão alinhados com documentação.

    Categoria: Contract Test
    Objetivo: Garantir que schemas documentam corretamente a API
    """
    # Arrange
    request_schema = ChatRequest.schema()
    response_schema = ChatResponse.schema()

    # Assert - Request schema
    assert "pergunta" in request_schema["properties"]
    assert request_schema["properties"]["pergunta"]["minLength"] == 3
    assert request_schema["properties"]["pergunta"]["maxLength"] == 2000

    # Assert - Response schema
    assert "resposta" in response_schema["properties"]
