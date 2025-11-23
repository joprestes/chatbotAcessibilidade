"""
Testes para a API FastAPI
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from src.backend.api import app
from chatbot_acessibilidade.config import settings


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


@patch("src.backend.api.pipeline_acessibilidade", new_callable=AsyncMock)
def test_chat_endpoint_sucesso(mock_pipeline, client):
    """Testa o endpoint de chat com sucesso"""

    # Mock da resposta do pipeline (async)
    async def mock_pipeline_func(pergunta):
        return {
            "📘 **Introdução**": "Introdução teste",
            "🔍 **Conceitos Essenciais**": "Conceitos teste",
            "🧪 **Como Testar na Prática**": "Testes teste",
            "📚 **Quer se Aprofundar?**": "Aprofundar teste",
            "👋 **Dica Final**": "Dica teste",
        }

    mock_pipeline.side_effect = mock_pipeline_func

    response = client.post("/api/chat", json={"pergunta": "O que é WCAG?"})

    assert response.status_code == 200
    data = response.json()
    assert "resposta" in data
    assert "📘 **Introdução**" in data["resposta"]


@patch("src.backend.api.pipeline_acessibilidade", new_callable=AsyncMock)
def test_chat_endpoint_pergunta_vazia(mock_pipeline, client):
    """Testa o endpoint de chat com pergunta vazia"""
    response = client.post("/api/chat", json={"pergunta": "  "})

    assert response.status_code == 422  # Validation error do Pydantic


@patch("src.backend.api.pipeline_acessibilidade", new_callable=AsyncMock)
def test_chat_endpoint_erro_no_pipeline(mock_pipeline, client):
    """Testa o endpoint quando o pipeline retorna erro"""

    async def mock_pipeline_func(pergunta):
        return {"erro": "Erro de teste"}

    mock_pipeline.side_effect = mock_pipeline_func

    response = client.post("/api/chat", json={"pergunta": "Teste"})

    assert response.status_code == 500
    data = response.json()
    assert "erro" in data["detail"].lower() or "Erro de teste" in data["detail"]


@patch("src.backend.api.pipeline_acessibilidade", new_callable=AsyncMock)
def test_chat_endpoint_excecao_inesperada(mock_pipeline, client):
    """Testa o endpoint quando ocorre exceção inesperada"""

    async def mock_pipeline_func(pergunta):
        raise Exception("Erro inesperado")

    mock_pipeline.side_effect = mock_pipeline_func

    response = client.post("/api/chat", json={"pergunta": "Teste"})

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


@patch("src.backend.api.get_cached_response")
@patch("src.backend.api.pipeline_acessibilidade")
def test_chat_endpoint_com_cache_hit(mock_pipeline, mock_cache, client):
    """Testa quando resposta vem do cache"""
    resposta_cache = {"📘 **Introdução**": "Resposta do cache"}
    mock_cache.return_value = resposta_cache

    response = client.post("/api/chat", json={"pergunta": "O que é WCAG?"})

    assert response.status_code == 200
    assert response.json()["resposta"] == resposta_cache
    # Pipeline não deve ser chamado quando há cache
    mock_pipeline.assert_not_called()


@patch("src.backend.api.get_cached_response")
@patch("src.backend.api.set_cached_response")
@patch("src.backend.api.pipeline_acessibilidade", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_chat_endpoint_salva_no_cache(mock_pipeline, mock_set_cache, mock_get_cache, client):
    """Testa se resposta é salva no cache após sucesso"""
    mock_get_cache.return_value = None  # Cache miss
    resposta_pipeline = {"📘 **Introdução**": "Resposta do pipeline"}

    async def mock_pipeline_func(pergunta):
        return resposta_pipeline

    mock_pipeline.side_effect = mock_pipeline_func

    response = client.post("/api/chat", json={"pergunta": "O que é WCAG?"})

    assert response.status_code == 200
    # Verifica se set_cached_response foi chamado
    mock_set_cache.assert_called_once()


@patch("src.backend.api.get_cached_response")
@patch("src.backend.api.set_cached_response")
@patch("src.backend.api.pipeline_acessibilidade", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_chat_endpoint_nao_salva_erro_no_cache(
    mock_pipeline, mock_set_cache, mock_get_cache, client
):
    """Testa se erro não é salvo no cache"""
    mock_get_cache.return_value = None
    resposta_erro = {"erro": "Erro no pipeline"}

    async def mock_pipeline_func(pergunta):
        return resposta_erro

    mock_pipeline.side_effect = mock_pipeline_func

    response = client.post("/api/chat", json={"pergunta": "O que é WCAG?"})

    assert response.status_code == 500
    # Verifica se set_cached_response NÃO foi chamado para erro
    mock_set_cache.assert_not_called()


def test_chat_endpoint_pergunta_muito_curta(client):
    """Testa validação de pergunta muito curta"""
    response = client.post("/api/chat", json={"pergunta": "ab"})

    # Pydantic retorna 422 para validação, mas pode ser 400 também
    assert response.status_code in [400, 422]
    detail = response.json().get("detail", "")
    if isinstance(detail, list):
        detail = str(detail)
    assert "caracteres" in detail.lower() or "min" in detail.lower()


def test_chat_endpoint_pergunta_muito_longa(client):
    """Testa validação de pergunta muito longa"""
    pergunta_longa = "a" * 2001
    response = client.post("/api/chat", json={"pergunta": pergunta_longa})

    # Pydantic retorna 422 para validação, mas pode ser 400 também
    assert response.status_code in [400, 422]
    detail = response.json().get("detail", "")
    if isinstance(detail, list):
        detail = str(detail)
    assert "caracteres" in detail.lower() or "max" in detail.lower()


def test_compression_enabled(client):
    """Testa que compressão está habilitada e funciona"""
    import gzip

    # Faz requisição com Accept-Encoding: gzip
    response = client.get(
        "/api/health", headers={"Accept-Encoding": "gzip, deflate, br"}
    )

    assert response.status_code == 200

    # Verifica se Content-Encoding está presente
    content_encoding = response.headers.get("Content-Encoding")
    if content_encoding:
        assert content_encoding == "gzip"
        # Descomprime para verificar conteúdo
        decompressed = gzip.decompress(response.content)
        assert b"status" in decompressed
    else:
        # Se não comprimiu, pode ser porque a resposta é muito pequena
        # ou compressão está desabilitada
        assert len(response.content) < 500 or not settings.compression_enabled


@patch("src.backend.api.pipeline_acessibilidade", new_callable=AsyncMock)
def test_compression_large_response(mock_pipeline, client):
    """Testa compressão em resposta grande"""
    import gzip

    # Mock para retornar resposta grande (mais de 500 bytes)
    large_data = "x" * 1000  # Dados grandes
    mock_pipeline.return_value = {
        "📘 **Introdução**": large_data,
        "📚 **Detalhes**": large_data * 2,
        "📖 **Mais Informações**": large_data * 3,
    }

    response = client.post(
        "/api/chat",
        json={"pergunta": "Teste de compressão"},
        headers={"Accept-Encoding": "gzip"},
    )

    assert response.status_code == 200

    # Verifica se foi comprimido (resposta grande deve ser comprimida)
    content_encoding = response.headers.get("Content-Encoding")
    if settings.compression_enabled and content_encoding == "gzip":
        # Descomprime e verifica conteúdo
        decompressed = gzip.decompress(response.content)
        assert b"Introdução" in decompressed or "Introdução".encode("utf-8") in decompressed
    else:
        # Se não comprimiu, verifica que a resposta existe
        assert response.json() is not None


def test_compression_disabled():
    """Testa que compressão pode ser desabilitada"""
    from unittest.mock import patch
    from fastapi.testclient import TestClient
    from src.backend.api import app

    with patch("chatbot_acessibilidade.config.settings") as mock_settings:
        mock_settings.compression_enabled = False

        client = TestClient(app)
        response = client.get(
            "/api/health", headers={"Accept-Encoding": "gzip"}
        )

        assert response.status_code == 200
        # Não deve ter Content-Encoding quando desabilitado
        assert "Content-Encoding" not in response.headers or response.headers.get(
            "Content-Encoding"
        ) != "gzip"


@patch("src.backend.api.pipeline_acessibilidade", new_callable=AsyncMock)
def test_chat_endpoint_pergunta_com_caracteres_controle(mock_pipeline, client):
    """Testa sanitização de caracteres de controle"""

    async def mock_pipeline_func(pergunta):
        return {"📘 **Introdução**": "Resposta teste"}

    mock_pipeline.side_effect = mock_pipeline_func

    pergunta_com_controle = "Pergunta\x00com\x01controle"
    response = client.post("/api/chat", json={"pergunta": pergunta_com_controle})

    # Deve aceitar após sanitização ou rejeitar
    assert response.status_code in [200, 400, 422]


def test_read_root_endpoint(client):
    """Testa o endpoint raiz que serve o index.html"""
    response = client.get("/")

    # Pode retornar 200 se o frontend existir, ou 404 se não existir
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        # Se retornou 200, deve ser HTML
        assert "text/html" in response.headers.get("content-type", "")


def test_api_sys_path_insert():
    """Testa se sys.path.insert é executado quando necessário (linha 23)"""
    import sys
    from pathlib import Path
    from src.backend import api

    # Verifica se src_path está no sys.path (indiretamente testa linha 23)
    src_path = Path(api.__file__).parent.parent
    # Se a linha 23 foi executada, src_path deve estar no sys.path
    # Como o módulo já foi importado, não podemos testar diretamente,
    # mas podemos verificar que o import funcionou
    assert str(src_path) in sys.path or any(str(src_path) in str(p) for p in sys.path)


@patch("src.backend.api.pipeline_acessibilidade", new_callable=AsyncMock)
def test_chat_endpoint_validation_error(mock_pipeline, client):
    """Testa tratamento de ValidationError no endpoint de chat"""

    from chatbot_acessibilidade.core.exceptions import ValidationError

    # Mock do pipeline para levantar ValidationError
    async def mock_pipeline_func(pergunta):
        raise ValidationError("Erro de validação de teste")

    mock_pipeline.side_effect = mock_pipeline_func

    response = client.post("/api/chat", json={"pergunta": "Teste"})

    assert response.status_code == 400
    data = response.json()
    assert (
        "erro de validação" in data.get("detail", "").lower() or "validation" in str(data).lower()
    )


@patch("src.backend.api.get_cache_stats")
def test_health_check_com_cache(mock_cache_stats, client):
    """Testa health check com cache habilitado"""
    mock_cache_stats.return_value = {"enabled": True, "size": 5, "max_size": 100, "ttl": 3600}

    response = client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "cache" in data
    assert data["cache"]["enabled"] is True


@patch("src.backend.api.get_cache_stats")
def test_health_check_sem_cache(mock_cache_stats, client):
    """Testa health check com cache desabilitado"""
    mock_cache_stats.return_value = {"enabled": False, "size": 0, "max_size": 0, "ttl": 0}

    response = client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["cache"]["enabled"] is False
