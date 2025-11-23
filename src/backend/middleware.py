"""
Middleware de segurança e compressão para adicionar headers HTTP de segurança
e comprimir respostas
"""

import gzip
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable

from chatbot_acessibilidade.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware que adiciona headers de segurança HTTP"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Adiciona headers de segurança à resposta"""
        response = await call_next(request)

        # Verifica se headers de segurança estão habilitados
        if not settings.security_headers_enabled:
            return response

        # Strict-Transport-Security (HSTS)
        # Força uso de HTTPS por 1 ano, incluindo subdomínios
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Content-Security-Policy (CSP)
        # Usa política customizada se configurada, senão usa padrão
        if settings.csp_policy:
            csp_policy = settings.csp_policy
        else:
            # Política restritiva mas funcional para o frontend
            csp_policy = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
        response.headers["Content-Security-Policy"] = csp_policy

        # X-Content-Type-Options
        # Previne MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options
        # Previne clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # X-XSS-Protection
        # Proteção adicional contra XSS (legacy, mas ainda útil)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy
        # Controla informações de referrer
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy (antigo Feature-Policy)
        # Desabilita features desnecessárias
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "speaker=()"
        )

        return response


class StaticCacheMiddleware(BaseHTTPMiddleware):
    """Middleware que adiciona headers de cache para assets estáticos."""

    # TTLs em segundos (usando constantes)
    STATIC_TTL = None  # Será definido via constantes
    ASSETS_TTL = None  # Será definido via constantes

    def __init__(self, app):
        super().__init__(app)
        from chatbot_acessibilidade.core.constants import (
            STATIC_CACHE_TTL_SECONDS,
            ASSETS_CACHE_TTL_SECONDS,
        )

        self.STATIC_TTL = STATIC_CACHE_TTL_SECONDS
        self.ASSETS_TTL = ASSETS_CACHE_TTL_SECONDS

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Adiciona headers de cache para assets estáticos"""
        response = await call_next(request)

        # Verifica se é um asset estático
        path = request.url.path

        if path.startswith("/static/"):
            # CSS, JS, etc. - cache por 1 dia
            response.headers["Cache-Control"] = f"public, max-age={self.STATIC_TTL}, immutable"
            response.headers["Vary"] = "Accept-Encoding"
        elif path.startswith("/assets/"):
            # Imagens - cache por 7 dias
            response.headers["Cache-Control"] = f"public, max-age={self.ASSETS_TTL}, immutable"
            response.headers["Vary"] = "Accept-Encoding"

        return response


class CompressionMiddleware(BaseHTTPMiddleware):
    """Middleware que comprime respostas usando gzip"""

    # Tipos de conteúdo que devem ser comprimidos
    COMPRESSIBLE_TYPES = [
        "text/html",
        "text/css",
        "text/javascript",
        "application/javascript",
        "application/json",
        "application/xml",
        "text/xml",
        "text/plain",
    ]

    # Tamanho mínimo para comprimir (em bytes)
    MIN_SIZE = None  # Será definido via constantes

    def __init__(self, app):
        super().__init__(app)
        from chatbot_acessibilidade.core.constants import COMPRESSION_MIN_SIZE_BYTES

        self.MIN_SIZE = COMPRESSION_MIN_SIZE_BYTES

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Comprime resposta se necessário"""
        response = await call_next(request)

        # Verifica se compressão está habilitada
        if not settings.compression_enabled:
            return response

        # Verifica se o cliente aceita gzip
        accept_encoding = request.headers.get("Accept-Encoding", "")
        if "gzip" not in accept_encoding.lower():
            return response

        # Verifica se a resposta já está comprimida
        if response.headers.get("Content-Encoding"):
            return response

        # Verifica o tipo de conteúdo
        content_type = response.headers.get("Content-Type", "")
        if not any(ct in content_type for ct in self.COMPRESSIBLE_TYPES):
            return response

        # Verifica o tamanho do conteúdo
        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        if len(body) < self.MIN_SIZE:
            # Resposta muito pequena, não comprime
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        # Comprime o conteúdo
        compressed_body = gzip.compress(body, compresslevel=6)

        # Atualiza headers
        headers = dict(response.headers)
        headers["Content-Encoding"] = "gzip"
        headers["Content-Length"] = str(len(compressed_body))
        # Remove Content-Length original se existir
        headers.pop("Content-Length", None)

        return Response(
            content=compressed_body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type,
        )
