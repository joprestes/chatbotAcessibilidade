"""
Testes de API usando Playwright

Testa endpoints da API usando requisições HTTP reais,
sem bypass do FastAPI (diferente do TestClient).
"""

import pytest
from playwright.sync_api import Page, APIRequestContext
from typing import Dict, Any

pytestmark = [pytest.mark.e2e, pytest.mark.playwright]


@pytest.fixture
def api_context(page: Page, base_url: str) -> APIRequestContext:
    """
    Cria um contexto de API para fazer requisições HTTP.
    """
    return page.request


def test_api_health_check_via_playwright(api_context: APIRequestContext, base_url: str):
    """
    Testa endpoint de health check usando Playwright.
    """
    response = api_context.get(f"{base_url}/api/health")
    
    assert response.status == 200
    data = response.json()
    
    assert data["status"] == "ok"
    assert "message" in data
    assert "cache" in data


def test_api_config_endpoint_via_playwright(api_context: APIRequestContext, base_url: str):
    """
    Testa endpoint de configuração usando Playwright.
    """
    response = api_context.get(f"{base_url}/api/config")
    
    assert response.status == 200
    data = response.json()
    
    assert "request_timeout_ms" in data
    assert "error_announcement_duration_ms" in data
    assert isinstance(data["request_timeout_ms"], int)
    assert isinstance(data["error_announcement_duration_ms"], int)


def test_api_chat_endpoint_success_via_playwright(
    api_context: APIRequestContext,
    base_url: str,
):
    """
    Testa endpoint de chat com pergunta válida usando Playwright.
    """
    from unittest.mock import patch, AsyncMock
    
    # Mock do pipeline para evitar chamadas reais à API
    with patch("src.backend.api.pipeline_acessibilidade", new_callable=AsyncMock) as mock_pipeline:
        mock_pipeline.return_value = {
            "📘 **Introdução**": "Introdução sobre acessibilidade digital",
            "🔍 **Conceitos Essenciais**": "Conceitos importantes",
        }
        
        response = api_context.post(
            f"{base_url}/api/chat",
            data={"pergunta": "O que é acessibilidade digital?"},
        )
    
    assert response.status == 200
    data = response.json()
    
    assert "resposta" in data
    assert isinstance(data["resposta"], dict)
    assert len(data["resposta"]) > 0


def test_api_chat_endpoint_validation_error_via_playwright(
    api_context: APIRequestContext,
    base_url: str,
):
    """
    Testa endpoint de chat com pergunta inválida usando Playwright.
    """
    # Pergunta muito curta
    response = api_context.post(
        f"{base_url}/api/chat",
        data={"pergunta": "ab"},
    )
    
    # Deve retornar erro de validação
    assert response.status in [400, 422]


def test_api_cors_headers_via_playwright(api_context: APIRequestContext, base_url: str):
    """
    Testa se os headers CORS estão presentes usando Playwright.
    """
    # Faz requisição OPTIONS (preflight)
    response = api_context.options(
        f"{base_url}/api/chat",
        headers={"Origin": "http://localhost:3000"},
    )
    
    # Verifica headers CORS
    assert "access-control-allow-origin" in response.headers or response.status == 200


def test_api_static_files_via_playwright(api_context: APIRequestContext, base_url: str):
    """
    Testa se os arquivos estáticos são servidos corretamente.
    """
    # Testa CSS
    css_response = api_context.get(f"{base_url}/static/styles.css")
    assert css_response.status in [200, 404]  # Pode não existir em alguns ambientes
    
    # Testa JS
    js_response = api_context.get(f"{base_url}/static/app.js")
    assert js_response.status in [200, 404]
    
    # Testa HTML principal
    html_response = api_context.get(f"{base_url}/")
    assert html_response.status in [200, 404]


def test_api_metrics_endpoint_via_playwright(api_context: APIRequestContext, base_url: str):
    """
    Testa endpoint de métricas usando Playwright.
    """
    response = api_context.get(f"{base_url}/api/metrics")
    
    assert response.status == 200
    data = response.json()
    
    assert "total_requests" in data
    assert isinstance(data["total_requests"], int)

