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

