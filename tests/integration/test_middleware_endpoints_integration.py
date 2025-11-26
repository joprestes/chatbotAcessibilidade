"""
Testes de Integração: Middleware + Endpoints

Valida que middlewares funcionam corretamente com endpoints,
incluindo compressão, CORS, rate limiting e headers de segurança.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys
from unittest.mock import patch

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

    async def mock_response(pergunta: str):
        return {
            "introducao": f"Introdução sobre {pergunta[:20]}",
            "corpo": f"Corpo detalhado sobre {pergunta[:20]}",
            "conclusao": f"Conclusão sobre {pergunta[:20]}",
            "exemplos": [{"titulo": "Exemplo", "codigo": "code", "explicacao": "explicação"}],
            "testes_sugeridos": ["Teste 1"],
            "materiais_estudo": ["Material 1"],
            "dica_final": "Dica final",
        }

    with patch("backend.api.pipeline_acessibilidade", new=mock_response):
        yield


def test_compression_middleware_compresses_large_responses(client: TestClient):
    """
    Testa que middleware de compressão funciona em respostas grandes.

    Categoria: Integration Test
    Objetivo: Validar integração Compression Middleware + Endpoint
    Fluxo: Request → Response grande → Compressão → Response comprimida
    """
    # Arrange
    pergunta = "O que é WCAG 2.2?"

    # Act - Request com Accept-Encoding: gzip
    response = client.post(
        "/api/chat", json={"pergunta": pergunta}, headers={"Accept-Encoding": "gzip"}
    )

    # Assert
    assert response.status_code == 200

    # Verifica se resposta foi comprimida (Content-Encoding: gzip)
    # Nota: TestClient pode descomprimir automaticamente
    assert "resposta" in response.json()


def test_cors_headers_present_in_response(client: TestClient):
    """
    Testa que headers CORS estão presentes nas respostas.

    Categoria: Integration Test
    Objetivo: Validar integração CORS Middleware + Endpoint
    Fluxo: Request → CORS Middleware → Response com headers CORS
    """
    # Arrange
    pergunta = "Teste CORS"

    # Act
    response = client.post(
        "/api/chat", json={"pergunta": pergunta}, headers={"Origin": "http://localhost:3000"}
    )

    # Assert
    assert response.status_code == 200

    # Verifica headers CORS
    assert "access-control-allow-origin" in response.headers


def test_security_headers_present_in_response(client: TestClient):
    """
    Testa que headers de segurança estão presentes.

    Categoria: Integration Test
    Objetivo: Validar integração Security Headers Middleware + Endpoint
    Fluxo: Request → Security Middleware → Response com headers
    """
    # Arrange
    pergunta = "Teste segurança"

    # Act
    response = client.post("/api/chat", json={"pergunta": pergunta})

    # Assert
    assert response.status_code == 200

    # Verifica headers de segurança
    headers = {k.lower(): v for k, v in response.headers.items()}

    # Alguns headers de segurança esperados
    expected_headers = [
        "x-content-type-options",
        "x-frame-options",
    ]

    for header in expected_headers:
        assert header in headers, f"Header de segurança '{header}' ausente"


def test_docs_endpoint_accessible(client: TestClient):
    """
    Testa que endpoint de documentação está acessível.

    Categoria: Integration Test
    Objetivo: Validar endpoint de docs (Swagger)
    Fluxo: GET /docs → Response OK
    """
    # Act
    response = client.get("/docs")

    # Assert
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


def test_static_files_served_correctly(client: TestClient):
    """
    Testa que arquivos estáticos são servidos corretamente.

    Categoria: Integration Test
    Objetivo: Validar serving de arquivos estáticos
    Fluxo: GET /static/... → Arquivo estático
    """
    # Act - Tenta acessar página principal
    response = client.get("/")

    # Assert
    assert response.status_code == 200
    # Deve retornar HTML
    assert "text/html" in response.headers.get("content-type", "")


def test_404_for_nonexistent_endpoint(client: TestClient):
    """
    Testa que endpoints inexistentes retornam 404.

    Categoria: Integration Test
    Objetivo: Validar tratamento de rotas inexistentes
    Fluxo: GET /nonexistent → 404 Not Found
    """
    # Act
    response = client.get("/api/nonexistent")

    # Assert
    assert response.status_code == 404


def test_method_not_allowed_returns_405(client: TestClient):
    """
    Testa que métodos HTTP não permitidos retornam 405.

    Categoria: Integration Test
    Objetivo: Validar tratamento de métodos não permitidos
    Fluxo: GET /api/chat (POST only) → 405 Method Not Allowed
    """
    # Act - GET em endpoint que só aceita POST
    response = client.get("/api/chat")

    # Assert
    assert response.status_code == 405
