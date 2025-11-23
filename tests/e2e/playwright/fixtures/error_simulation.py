"""
Fixtures para simulação de erros em testes E2E
"""

import pytest
from playwright.sync_api import Page, Route
from typing import Generator, Optional
import json


@pytest.fixture
def mock_slow_request(page: Page, base_url: str) -> Generator[None, None, None]:
    """
    Intercepta requisições e adiciona delay para simular timeout.
    """

    def handle_route(route: Route) -> None:
        # Adiciona delay de 130 segundos (maior que timeout padrão de 120s)
        route.continue_()

    page.route(f"{base_url}/api/chat", handle_route)
    yield
    page.unroute(f"{base_url}/api/chat")


@pytest.fixture
def mock_offline(page: Page) -> Generator[None, None, None]:
    """
    Simula estado offline do navegador.
    """
    page.context.set_offline(True)
    yield
    page.context.set_offline(False)


@pytest.fixture
def mock_rate_limit_response(page: Page, base_url: str) -> Generator[None, None, None]:
    """
    Mock de resposta 429 (Rate Limit).
    """

    def handle_route(route: Route) -> None:
        route.fulfill(
            status=429,
            headers={"Content-Type": "application/json"},
            body=json.dumps({"detail": "Rate limit exceeded"}),
        )

    page.route(f"{base_url}/api/chat", handle_route)
    yield
    page.unroute(f"{base_url}/api/chat")


@pytest.fixture
def mock_server_error_500(page: Page, base_url: str) -> Generator[None, None, None]:
    """
    Mock de resposta 500 (Erro do Servidor).
    """

    def handle_route(route: Route) -> None:
        route.fulfill(
            status=500,
            headers={"Content-Type": "application/json"},
            body=json.dumps({"detail": "Internal server error"}),
        )

    page.route(f"{base_url}/api/chat", handle_route)
    yield
    page.unroute(f"{base_url}/api/chat")


@pytest.fixture
def mock_malformed_response(page: Page, base_url: str) -> Generator[None, None, None]:
    """
    Mock de resposta malformada (JSON inválido).
    """

    def handle_route(route: Route) -> None:
        route.fulfill(
            status=200,
            headers={"Content-Type": "application/json"},
            body="{invalid json}",
        )

    page.route(f"{base_url}/api/chat", handle_route)
    yield
    page.unroute(f"{base_url}/api/chat")


@pytest.fixture
def mock_api_response(page: Page, base_url: str) -> Generator[callable, None, None]:
    """
    Fixture que retorna função para mockar respostas da API.
    """

    def _mock_response(
        status: int = 200,
        body: Optional[dict] = None,
        delay: Optional[int] = None,
    ) -> None:
        def handle_route(route: Route) -> None:
            # Delay removido - Playwright já sincroniza automaticamente
            # Se delay for necessário no futuro, usar page.wait_for_timeout() no teste
            route.fulfill(
                status=status,
                headers={"Content-Type": "application/json"},
                body=json.dumps(body or {"resposta": {"Teste": "Resposta mockada"}}),
            )

        page.route(f"{base_url}/api/chat", handle_route)

    yield _mock_response
    page.unroute(f"{base_url}/api/chat")
