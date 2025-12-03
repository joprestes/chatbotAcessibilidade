"""
Testes unitários para os middlewares de segurança, cache e compressão
"""

from backend.middleware import (
    SecurityHeadersMiddleware,
    StaticCacheMiddleware,
)

import pytest
from unittest.mock import MagicMock, patch
from starlette.requests import Request
from starlette.responses import Response

# ==========================================
# Testes para SecurityHeadersMiddleware
# ==========================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_security_headers_middleware_adds_headers():
    """Testa se o middleware adiciona todos os headers de segurança"""
    middleware = SecurityHeadersMiddleware(app=MagicMock())

    # Mock request
    mock_request = MagicMock(spec=Request)

    # Mock response
    mock_response = Response(content="Test", status_code=200)

    # Mock call_next como função assíncrona
    async def mock_call_next(request):
        return mock_response

    with patch("backend.middleware.settings") as mock_settings:
        mock_settings.security_headers_enabled = True
        mock_settings.csp_policy = ""

        response = await middleware.dispatch(mock_request, mock_call_next)

        # Verifica headers de segurança
        assert "Strict-Transport-Security" in response.headers
        assert (
            response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"
        )

        assert "Content-Security-Policy" in response.headers
        assert "default-src 'self'" in response.headers["Content-Security-Policy"]

        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"

        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"

        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"

        assert "Referrer-Policy" in response.headers
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

        assert "Permissions-Policy" in response.headers
        assert "geolocation=()" in response.headers["Permissions-Policy"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_security_headers_middleware_custom_csp():
    """Testa se o middleware usa CSP customizada quando configurada"""
    middleware = SecurityHeadersMiddleware(app=MagicMock())
    custom_csp = "default-src 'none'; script-src 'self'"

    mock_request = MagicMock(spec=Request)
    mock_response = Response(content="Test", status_code=200)

    async def mock_call_next(request):
        return mock_response

    with patch("backend.middleware.settings") as mock_settings:
        mock_settings.security_headers_enabled = True
        mock_settings.csp_policy = custom_csp

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response.headers["Content-Security-Policy"] == custom_csp


@pytest.mark.unit
@pytest.mark.asyncio
async def test_security_headers_middleware_disabled():
    """Testa se o middleware não adiciona headers quando desabilitado"""
    middleware = SecurityHeadersMiddleware(app=MagicMock())

    mock_request = MagicMock(spec=Request)
    mock_response = Response(content="Test", status_code=200)

    async def mock_call_next(request):
        return mock_response

    with patch("backend.middleware.settings") as mock_settings:
        mock_settings.security_headers_enabled = False

        response = await middleware.dispatch(mock_request, mock_call_next)

        # Não deve adicionar headers de segurança
        assert "Strict-Transport-Security" not in response.headers
        assert "Content-Security-Policy" not in response.headers


# ==========================================
# Testes para StaticCacheMiddleware
# ==========================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_static_cache_middleware_static_files():
    """Testa se o middleware adiciona headers de cache para arquivos estáticos"""
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/static/css/style.css"

    mock_response = Response(content="Test", status_code=200)

    async def mock_call_next(request):
        return mock_response

    with patch("chatbot_acessibilidade.core.constants.STATIC_CACHE_TTL_SECONDS", 86400):
        middleware = StaticCacheMiddleware(app=MagicMock())
        response = await middleware.dispatch(mock_request, mock_call_next)

        assert "Cache-Control" in response.headers
        # Rollback: Cache desabilitado
        assert "no-cache, no-store, must-revalidate" in response.headers["Cache-Control"]
        assert response.headers["Vary"] == "Accept-Encoding"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_static_cache_middleware_assets():
    """Testa se o middleware adiciona headers de cache para assets"""
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/assets/logo.png"

    mock_response = Response(content="Test", status_code=200)

    async def mock_call_next(request):
        return mock_response

    with patch("chatbot_acessibilidade.core.constants.ASSETS_CACHE_TTL_SECONDS", 604800):
        middleware = StaticCacheMiddleware(app=MagicMock())
        response = await middleware.dispatch(mock_request, mock_call_next)

        assert "Cache-Control" in response.headers
        # Rollback: Cache desabilitado
        assert "no-cache, no-store, must-revalidate" in response.headers["Cache-Control"]
        assert response.headers["Vary"] == "Accept-Encoding"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_static_cache_middleware_no_cache_for_api():
    """Testa se o middleware não adiciona cache para rotas de API"""
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/api/chat"

    mock_response = Response(content="Test", status_code=200)

    async def mock_call_next(request):
        return mock_response

    middleware = StaticCacheMiddleware(app=MagicMock())
    response = await middleware.dispatch(mock_request, mock_call_next)

    # Não deve adicionar headers de cache para APIs
    assert "Cache-Control" not in response.headers or "immutable" not in response.headers.get(
        "Cache-Control", ""
    )
