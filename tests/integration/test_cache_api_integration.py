"""
Testes de Integração: Cache + API

Valida que cache funciona corretamente com a API,
incluindo hits, misses, TTL e estatísticas.
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
from chatbot_acessibilidade.core.cache import get_cache  # noqa: E402


@pytest.fixture
def client():
    """Cliente HTTP para testes de integração."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_cache_before_test():
    """Limpa cache antes de cada teste."""
    cache = get_cache()
    cache.clear()
    yield
    cache.clear()


@pytest.fixture(autouse=True)
def mock_pipeline():
    """Mocka pipeline para não fazer chamadas reais à API."""

    async def mock_response(pergunta: str):
        # Retorna resposta diferente baseada na pergunta
        return {
            "introducao": f"Introdução sobre {pergunta[:20]}",
            "corpo": f"Corpo detalhado sobre {pergunta[:20]}",
            "conclusao": f"Conclusão sobre {pergunta[:20]}",
            "exemplos": [
                {
                    "titulo": "Exemplo",
                    "codigo": "code",
                    "explicacao": f"explicação de {pergunta[:10]}",
                }
            ],
            "testes_sugeridos": [f"Teste para {pergunta[:10]}"],
            "materiais_estudo": [f"Material sobre {pergunta[:10]}"],
            "dica_final": f"Dica sobre {pergunta[:10]}",
        }

    # Mocka no módulo onde é importado (backend.api), não onde é definido
    with patch("backend.api.pipeline_acessibilidade", new=AsyncMock(side_effect=mock_response)):
        yield


def test_cache_miss_on_first_request(client: TestClient):
    """
    Testa que primeira request resulta em cache miss.

    Categoria: Integration Test
    Objetivo: Validar integração Cache + API
    Fluxo: Request → Cache Miss → Gera Resposta → Armazena
    """
    # Arrange
    cache = get_cache()
    pergunta = "O que é WCAG 2.2?"

    # Act
    response = client.post("/api/chat", json={"pergunta": pergunta})

    # Assert - Response OK
    assert response.status_code == 200
    data = response.json()
    assert "resposta" in data

    # Assert - Cache tem 1 item
    assert len(cache) >= 1


def test_cache_hit_on_duplicate_request(client: TestClient):
    """
    Testa que request duplicada resulta em cache hit.

    Categoria: Integration Test
    Objetivo: Validar que cache retorna resposta armazenada
    Fluxo: Request 1 (miss) → Request 2 (hit) → Respostas idênticas
    """
    # Arrange
    cache = get_cache()
    pergunta = "O que é contraste de cores?"

    # Act - Primeira request (cache miss)
    response1 = client.post("/api/chat", json={"pergunta": pergunta})

    # Act - Segunda request (cache hit)
    response2 = client.post("/api/chat", json={"pergunta": pergunta})

    # Assert - Ambas retornam 200
    assert response1.status_code == 200
    assert response2.status_code == 200

    # Assert - Respostas são idênticas
    assert response1.json() == response2.json()

    # Assert - Cache tem 1 item (mesma pergunta)
    assert len(cache) >= 1


def test_cache_normalization_same_question_different_case(client: TestClient):
    """
    Testa que cache normaliza perguntas (case-insensitive).

    Categoria: Integration Test
    Objetivo: Validar normalização de chaves de cache
    Fluxo: "WCAG" e "wcag" devem usar mesmo cache
    """
    # Arrange
    pergunta1 = "O que é WCAG?"
    pergunta2 = "o que é wcag?"

    # Act
    response1 = client.post("/api/chat", json={"pergunta": pergunta1})
    response2 = client.post("/api/chat", json={"pergunta": pergunta2})

    # Assert - Ambas retornam 200
    assert response1.status_code == 200
    assert response2.status_code == 200

    # Assert - Respostas são idênticas (cache hit)
    assert response1.json() == response2.json()


def test_cache_different_questions_different_responses(client: TestClient):
    """
    Testa que perguntas diferentes geram respostas diferentes.

    Categoria: Integration Test
    Objetivo: Validar que cache não mistura respostas
    Fluxo: Pergunta A → Resposta A, Pergunta B → Resposta B
    """
    # Arrange
    pergunta1 = "O que é WCAG?"
    pergunta2 = "O que é ARIA?"

    # Act
    response1 = client.post("/api/chat", json={"pergunta": pergunta1})
    response2 = client.post("/api/chat", json={"pergunta": pergunta2})

    # Assert - Ambas retornam 200
    assert response1.status_code == 200
    assert response2.status_code == 200

    # Assert - Respostas são diferentes
    assert response1.json() != response2.json()


def test_cache_not_used_for_errors(client: TestClient):
    """
    Testa que erros não são armazenados em cache.

    Categoria: Integration Test
    Objetivo: Validar que apenas respostas válidas são cacheadas
    Fluxo: Request inválida → Erro → Não cacheia
    """
    # Arrange
    cache = get_cache()
    pergunta_invalida = ""  # Pergunta vazia (inválida)

    # Act
    response1 = client.post("/api/chat", json={"pergunta": pergunta_invalida})
    response2 = client.post("/api/chat", json={"pergunta": pergunta_invalida})

    # Assert - Ambas retornam erro (422 Unprocessable Entity)
    assert response1.status_code == 422
    assert response2.status_code == 422

    # Assert - Cache deve estar vazio (não armazenou erros)
    assert len(cache) == 0
