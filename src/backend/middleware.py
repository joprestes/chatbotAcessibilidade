"""
Middleware de segurança e compressão para adicionar headers HTTP de segurança
e comprimir respostas
"""

from typing import Awaitable, Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from chatbot_acessibilidade.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware que adiciona headers de segurança HTTP"""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
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
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://vlibras.gov.br https://www.vlibras.gov.br https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; "
                "font-src 'self' data: https://fonts.gstatic.com https://cdn.jsdelivr.net https://vlibras.gov.br https://www.vlibras.gov.br; "
                "connect-src 'self' https://vlibras.gov.br https://www.vlibras.gov.br https://dicionario2.vlibras.gov.br https://cdn.jsdelivr.net; "
                "worker-src 'self' blob:; "
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
        # Permite microphone para reconhecimento de voz
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(self), "
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

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Adiciona headers de cache para assets estáticos"""
        response = await call_next(request)

        # Verifica se é um asset estático
        path = request.url.path

        if path.startswith("/static/"):
            # CSS, JS, etc. - cache desabilitado para dev
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            # response.headers["Cache-Control"] = f"public, max-age={self.STATIC_TTL}, immutable"
            response.headers["Vary"] = "Accept-Encoding"
        elif path.startswith("/assets/"):
            # Imagens - cache por 7 dias
            response.headers["Cache-Control"] = f"public, max-age={self.ASSETS_TTL}, immutable"
            response.headers["Vary"] = "Accept-Encoding"

        return response
