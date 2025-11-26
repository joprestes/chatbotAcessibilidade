"""
Testes unitários para os middlewares de segurança, cache e compressão
"""

import gzip
import pytest
from unittest.mock import MagicMock, patch
from starlette.requests import Request
from starlette.responses import Response
from starlette.datastructures import Headers

from backend.middleware import (
    SecurityHeadersMiddleware,
    StaticCacheMiddleware,
    CompressionMiddleware,
)


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
        assert response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"
        
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
        assert "public, max-age=86400, immutable" in response.headers["Cache-Control"]
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
        assert "public, max-age=604800, immutable" in response.headers["Cache-Control"]
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
    assert "Cache-Control" not in response.headers or "immutable" not in response.headers.get("Cache-Control", "")


# ==========================================
# Testes para CompressionMiddleware
# ==========================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_compression_middleware_compresses_large_response():
    """Testa se o middleware comprime respostas grandes"""
    from starlette.responses import StreamingResponse
    
    # Cria uma resposta grande (> 1KB)
    large_content = "x" * 2000
    
    mock_request = MagicMock(spec=Request)
    mock_request.headers = Headers({"accept-encoding": "gzip, deflate"})
    
    async def content_generator():
        yield large_content.encode()
    
    async def mock_call_next(request):
        response = StreamingResponse(content_generator(), status_code=200)
        response.headers["Content-Type"] = "application/json"
        return response
    
    with patch("backend.middleware.settings") as mock_settings:
        mock_settings.compression_enabled = True
        
        with patch("chatbot_acessibilidade.core.constants.COMPRESSION_MIN_SIZE_BYTES", 1000):
            middleware = CompressionMiddleware(app=MagicMock())
            response = await middleware.dispatch(mock_request, mock_call_next)
            
            # Verifica se foi comprimido
            assert response.headers["Content-Encoding"] == "gzip"
            assert "Content-Length" in response.headers
            
            # Verifica se o conteúdo está realmente comprimido
            decompressed = gzip.decompress(response.body)
            assert decompressed.decode() == large_content


@pytest.mark.unit
@pytest.mark.asyncio
async def test_compression_middleware_skips_small_response():
    """Testa se o middleware não comprime respostas pequenas"""
    from starlette.responses import StreamingResponse
    
    small_content = "small"
    
    mock_request = MagicMock(spec=Request)
    mock_request.headers = Headers({"accept-encoding": "gzip"})
    
    async def content_generator():
        yield small_content.encode()
    
    async def mock_call_next(request):
        response = StreamingResponse(content_generator(), status_code=200)
        response.headers["Content-Type"] = "application/json"
        return response
    
    with patch("backend.middleware.settings") as mock_settings:
        mock_settings.compression_enabled = True
        
        with patch("chatbot_acessibilidade.core.constants.COMPRESSION_MIN_SIZE_BYTES", 1000):
            middleware = CompressionMiddleware(app=MagicMock())
            response = await middleware.dispatch(mock_request, mock_call_next)
            
            # Não deve comprimir
            assert "Content-Encoding" not in response.headers
            assert response.body.decode() == small_content


@pytest.mark.unit
@pytest.mark.asyncio
async def test_compression_middleware_disabled():
    """Testa se o middleware não comprime quando desabilitado"""
    large_content = "x" * 2000
    
    mock_request = MagicMock(spec=Request)
    mock_request.headers = Headers({"accept-encoding": "gzip"})
    
    async def mock_call_next(request):
        response = Response(content=large_content, status_code=200)
        response.headers["Content-Type"] = "application/json"
        return response
    
    with patch("backend.middleware.settings") as mock_settings:
        mock_settings.compression_enabled = False
        
        middleware = CompressionMiddleware(app=MagicMock())
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        # Não deve comprimir
        assert "Content-Encoding" not in response.headers


@pytest.mark.unit
@pytest.mark.asyncio
async def test_compression_middleware_no_gzip_support():
    """Testa se o middleware não comprime quando cliente não aceita gzip"""
    large_content = "x" * 2000
    
    mock_request = MagicMock(spec=Request)
    mock_request.headers = Headers({"accept-encoding": "deflate"})  # Sem gzip
    
    async def mock_call_next(request):
        response = Response(content=large_content, status_code=200)
        response.headers["Content-Type"] = "application/json"
        return response
    
    with patch("backend.middleware.settings") as mock_settings:
        mock_settings.compression_enabled = True
        
        middleware = CompressionMiddleware(app=MagicMock())
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        # Não deve comprimir
        assert "Content-Encoding" not in response.headers


@pytest.mark.unit
@pytest.mark.asyncio
async def test_compression_middleware_already_compressed():
    """Testa se o middleware não comprime respostas já comprimidas"""
    large_content = "x" * 2000
    
    mock_request = MagicMock(spec=Request)
    mock_request.headers = Headers({"accept-encoding": "gzip, br"})
    
    async def mock_call_next(request):
        response = Response(content=large_content, status_code=200)
        response.headers["Content-Type"] = "application/json"
        response.headers["Content-Encoding"] = "br"  # Já comprimido com Brotli
        return response
    
    with patch("backend.middleware.settings") as mock_settings:
        mock_settings.compression_enabled = True
        
        middleware = CompressionMiddleware(app=MagicMock())
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        # Não deve comprimir novamente
        assert response.headers["Content-Encoding"] == "br"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_compression_middleware_non_compressible_type():
    """Testa se o middleware não comprime tipos não comprimíveis"""
    large_content = b"\x00" * 2000  # Conteúdo binário
    
    mock_request = MagicMock(spec=Request)
    mock_request.headers = Headers({"accept-encoding": "gzip"})
    
    async def mock_call_next(request):
        response = Response(content=large_content, status_code=200)
        response.headers["Content-Type"] = "image/png"  # Tipo não comprimível
        return response
    
    with patch("backend.middleware.settings") as mock_settings:
        mock_settings.compression_enabled = True
        
        with patch("chatbot_acessibilidade.core.constants.COMPRESSION_MIN_SIZE_BYTES", 1000):
            middleware = CompressionMiddleware(app=MagicMock())
            response = await middleware.dispatch(mock_request, mock_call_next)
            
            # Não deve comprimir
            assert "Content-Encoding" not in response.headers
