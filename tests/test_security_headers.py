"""
Testes para o middleware de segurança
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from backend.middleware import SecurityHeadersMiddleware


@pytest.fixture
def test_app():
    """Cria uma aplicação FastAPI de teste"""
    app = FastAPI()

    @app.get("/test")
    async def test_endpoint():
        return JSONResponse({"message": "test"})

    app.add_middleware(SecurityHeadersMiddleware)
    return app


@pytest.fixture
def client(test_app):
    """Cria um cliente de teste"""
    return TestClient(test_app)


def test_security_headers_presentes(client):
    """Testa que todos os headers de segurança estão presentes"""
    response = client.get("/test")

    assert response.status_code == 200

    # Verifica headers de segurança
    assert "Strict-Transport-Security" in response.headers
    assert "Content-Security-Policy" in response.headers
    assert "X-Content-Type-Options" in response.headers
    assert "X-Frame-Options" in response.headers
    assert "X-XSS-Protection" in response.headers
    assert "Referrer-Policy" in response.headers
    assert "Permissions-Policy" in response.headers


def test_strict_transport_security_header(client):
    """Testa o header Strict-Transport-Security"""
    response = client.get("/test")
    hsts = response.headers.get("Strict-Transport-Security")

    assert hsts is not None
    assert "max-age=31536000" in hsts
    assert "includeSubDomains" in hsts


def test_content_security_policy_header(client):
    """Testa o header Content-Security-Policy"""
    response = client.get("/test")
    csp = response.headers.get("Content-Security-Policy")

    assert csp is not None
    assert "default-src 'self'" in csp
    assert "script-src" in csp
    assert "style-src" in csp


def test_x_content_type_options_header(client):
    """Testa o header X-Content-Type-Options"""
    response = client.get("/test")
    x_content_type = response.headers.get("X-Content-Type-Options")

    assert x_content_type == "nosniff"


def test_x_frame_options_header(client):
    """Testa o header X-Frame-Options"""
    response = client.get("/test")
    x_frame = response.headers.get("X-Frame-Options")

    assert x_frame == "DENY"


def test_x_xss_protection_header(client):
    """Testa o header X-XSS-Protection"""
    response = client.get("/test")
    x_xss = response.headers.get("X-XSS-Protection")

    assert x_xss == "1; mode=block"


def test_referrer_policy_header(client):
    """Testa o header Referrer-Policy"""
    response = client.get("/test")
    referrer = response.headers.get("Referrer-Policy")

    assert referrer == "strict-origin-when-cross-origin"


def test_permissions_policy_header(client):
    """Testa o header Permissions-Policy"""
    response = client.get("/test")
    permissions = response.headers.get("Permissions-Policy")

    assert permissions is not None
    assert "geolocation=()" in permissions
    assert "microphone=()" in permissions


def test_security_headers_disabled():
    """Testa que headers não são adicionados quando desabilitados"""
    from unittest.mock import patch

    with patch("backend.middleware.settings") as mock_settings:
        mock_settings.security_headers_enabled = False

        app = FastAPI()

        @app.get("/test")
        async def test_endpoint():
            return JSONResponse({"message": "test"})

        app.add_middleware(SecurityHeadersMiddleware)
        client = TestClient(app)

        response = client.get("/test")

        # Headers não devem estar presentes quando desabilitados
        assert "Strict-Transport-Security" not in response.headers
        assert "Content-Security-Policy" not in response.headers


def test_csp_custom_policy():
    """Testa que CSP customizado é usado quando configurado"""
    from unittest.mock import patch

    custom_csp = "default-src 'self'; script-src 'none'"

    with patch("backend.middleware.settings") as mock_settings:
        mock_settings.security_headers_enabled = True
        mock_settings.csp_policy = custom_csp

        app = FastAPI()

        @app.get("/test")
        async def test_endpoint():
            return JSONResponse({"message": "test"})

        app.add_middleware(SecurityHeadersMiddleware)
        client = TestClient(app)

        response = client.get("/test")
        csp = response.headers.get("Content-Security-Policy")

        assert csp == custom_csp


def test_security_headers_all_endpoints(client):
    """Testa que headers são adicionados em todos os endpoints"""
    # Testa diferentes tipos de resposta
    response1 = client.get("/test")
    assert "Strict-Transport-Security" in response1.headers

    # Testa 404 também deve ter headers
    response2 = client.get("/nonexistent")
    assert "Strict-Transport-Security" in response2.headers

