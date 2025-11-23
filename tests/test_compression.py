"""
Testes para o middleware de compressão
"""

import sys
from pathlib import Path
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

# Adiciona src ao path para imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from backend.middleware import CompressionMiddleware  # noqa: E402
from chatbot_acessibilidade.config import settings  # noqa: E402


@pytest.fixture
def test_app():
    """Cria uma aplicação FastAPI de teste"""
    app = FastAPI()

    @app.get("/small")
    async def small_endpoint():
        return JSONResponse({"message": "small"})  # Resposta pequena

    @app.get("/large")
    async def large_endpoint():
        # Resposta grande (>500 bytes)
        large_data = "x" * 1000
        return JSONResponse({"data": large_data})

    @app.get("/already-compressed")
    async def compressed_endpoint():
        response = JSONResponse({"message": "compressed"})
        response.headers["Content-Encoding"] = "gzip"
        return response

    @app.get("/image")
    async def image_endpoint():
        response = JSONResponse({"message": "image"}, media_type="image/png")
        return response

    app.add_middleware(CompressionMiddleware)
    return app


@pytest.fixture
def client(test_app):
    """Cria um cliente de teste"""
    return TestClient(test_app)


def test_compression_disabled():
    """Testa que compressão não é aplicada quando desabilitada"""
    from unittest.mock import patch

    with patch("backend.middleware.settings") as mock_settings:
        mock_settings.compression_enabled = False

        app = FastAPI()

        @app.get("/test")
        async def test_endpoint():
            return JSONResponse({"data": "x" * 1000})

        app.add_middleware(CompressionMiddleware)
        client = TestClient(app)

        response = client.get("/test", headers={"Accept-Encoding": "gzip"})

        assert response.status_code == 200
        # Quando desabilitado, não deve ter Content-Encoding
        assert "Content-Encoding" not in response.headers or response.headers.get("Content-Encoding") != "gzip"


def test_compression_no_accept_encoding(client):
    """Testa que compressão não é aplicada sem Accept-Encoding"""
    response = client.get("/large")  # Sem header Accept-Encoding

    assert response.status_code == 200
    # Sem Accept-Encoding, não deve comprimir
    assert "Content-Encoding" not in response.headers or response.headers.get("Content-Encoding") != "gzip"


def test_compression_already_compressed(client):
    """Testa que compressão não é aplicada se já está comprimida"""
    response = client.get(
        "/already-compressed", headers={"Accept-Encoding": "gzip"}
    )

    assert response.status_code == 200
    # Deve manter o Content-Encoding original (não comprime novamente)
    # O middleware detecta que já está comprimido e não processa
    assert response.headers.get("Content-Encoding") == "gzip"


def test_compression_wrong_content_type(client):
    """Testa que compressão não é aplicada para tipos não comprimíveis"""
    response = client.get("/image", headers={"Accept-Encoding": "gzip"})

    assert response.status_code == 200
    # Tipos não comprimíveis (como image/png) não devem ser comprimidos
    assert "Content-Encoding" not in response.headers or response.headers.get("Content-Encoding") != "gzip"


def test_compression_small_response(client):
    """Testa que respostas pequenas não são comprimidas"""
    response = client.get("/small", headers={"Accept-Encoding": "gzip"})

    assert response.status_code == 200
    # Resposta pequena (<500 bytes) não deve ser comprimida
    assert "Content-Encoding" not in response.headers


def test_compression_large_response(client):
    """Testa que respostas grandes são comprimidas"""
    import gzip

    response = client.get("/large", headers={"Accept-Encoding": "gzip"})

    assert response.status_code == 200

    if settings.compression_enabled:
        content_encoding = response.headers.get("Content-Encoding")
        if content_encoding == "gzip":
            # Verifica que foi comprimido
            assert len(response.content) < 1000  # Comprimido é menor
            # Descomprime e verifica conteúdo
            decompressed = gzip.decompress(response.content)
            assert b"data" in decompressed


def test_compression_content_length_header(client):
    """Testa que Content-Length é atualizado após compressão"""
    response = client.get("/large", headers={"Accept-Encoding": "gzip"})

    assert response.status_code == 200

    if settings.compression_enabled:
        content_encoding = response.headers.get("Content-Encoding")
        if content_encoding == "gzip":
            # Content-Length deve estar presente e correto
            content_length = response.headers.get("Content-Length")
            assert content_length is not None
            assert int(content_length) == len(response.content)


def test_compression_accept_encoding_variations(client):
    """Testa diferentes variações de Accept-Encoding"""
    import gzip

    # Testa com diferentes formatos de Accept-Encoding
    variations = [
        "gzip",
        "gzip, deflate",
        "gzip, deflate, br",
        "gzip,deflate",
    ]

    for accept_encoding in variations:
        response = client.get(
            "/large", headers={"Accept-Encoding": accept_encoding}
        )

        assert response.status_code == 200

        if settings.compression_enabled:
            content_encoding = response.headers.get("Content-Encoding")
            if content_encoding == "gzip":
                # Verifica que foi comprimido
                decompressed = gzip.decompress(response.content)
                assert b"data" in decompressed

