"""
Testes para o middleware de cache de assets estáticos
"""

import pytest

pytestmark = pytest.mark.unit
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from backend.middleware import StaticCacheMiddleware


@pytest.fixture
def test_app():
    """Cria uma aplicação FastAPI de teste"""
    app = FastAPI()

    @app.get("/static/test.css")
    async def static_css():
        return JSONResponse({"content": "body { color: red; }"}, media_type="text/css")

    @app.get("/static/test.js")
    async def static_js():
        return JSONResponse(
            {"content": "console.log('test');"}, media_type="application/javascript"
        )

    @app.get("/assets/test.jpg")
    async def asset_image():
        return JSONResponse({"content": "image"}, media_type="image/jpeg")

    @app.get("/api/test")
    async def api_endpoint():
        return JSONResponse({"message": "test"})

    app.add_middleware(StaticCacheMiddleware)
    return app


@pytest.fixture
def client(test_app):
    """Cria um cliente de teste"""
    return TestClient(test_app)


def test_static_cache_headers_css(client):
    """Testa que headers de cache são adicionados para CSS"""
    response = client.get("/static/test.css")

    assert response.status_code == 200
    assert "Cache-Control" in response.headers
    assert "public, max-age=86400, immutable" in response.headers["Cache-Control"]
    assert "Vary" in response.headers
    assert response.headers["Vary"] == "Accept-Encoding"


def test_static_cache_headers_js(client):
    """Testa que headers de cache são adicionados para JS"""
    response = client.get("/static/test.js")

    assert response.status_code == 200
    assert "Cache-Control" in response.headers
    assert "public, max-age=86400, immutable" in response.headers["Cache-Control"]


def test_assets_cache_headers_images(client):
    """Testa que headers de cache são adicionados para imagens"""
    response = client.get("/assets/test.jpg")

    assert response.status_code == 200
    assert "Cache-Control" in response.headers
    assert "public, max-age=604800, immutable" in response.headers["Cache-Control"]
    assert "Vary" in response.headers
    assert response.headers["Vary"] == "Accept-Encoding"


def test_api_endpoint_no_cache_headers(client):
    """Testa que endpoints de API não recebem headers de cache"""
    response = client.get("/api/test")

    assert response.status_code == 200
    # Endpoints de API não devem ter Cache-Control para assets
    # (podem ter outros headers de cache, mas não os de StaticCacheMiddleware)
    cache_control = response.headers.get("Cache-Control", "")
    assert "immutable" not in cache_control


def test_static_cache_different_ttls(client):
    """Testa que diferentes tipos de assets têm TTLs diferentes"""
    css_response = client.get("/static/test.css")
    image_response = client.get("/assets/test.jpg")

    assert css_response.status_code == 200
    assert image_response.status_code == 200

    css_ttl = css_response.headers.get("Cache-Control", "")
    image_ttl = image_response.headers.get("Cache-Control", "")

    # CSS deve ter TTL de 1 dia (86400)
    assert "max-age=86400" in css_ttl

    # Imagens devem ter TTL de 7 dias (604800)
    assert "max-age=604800" in image_ttl
