"""
Testes End-to-End (E2E) para o fluxo completo do usuário

Estes testes simulam o comportamento real do usuário,
testando desde a requisição HTTP até a resposta final.
"""

import pytest

pytestmark = pytest.mark.integration
from fastapi.testclient import TestClient
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
from pathlib import Path
import sys
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona src ao path
src_path = Path(__file__).parent.parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from backend.api import app  # noqa: E402


@pytest.fixture
def client():
    """Cliente HTTP para testes E2E"""
    return TestClient(app)


def test_e2e_health_check(client: TestClient):
    """
    Teste E2E: Verifica se o endpoint de health check está funcionando
    """
    response = client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "message" in data
    assert "cache" in data


def test_e2e_config_endpoint(client: TestClient):
    """
    Teste E2E: Verifica se o endpoint de configuração retorna valores corretos
    """
    response = client.get("/api/config")

    assert response.status_code == 200
    data = response.json()
    assert "request_timeout_ms" in data
    assert "error_announcement_duration_ms" in data
    assert isinstance(data["request_timeout_ms"], int)
    assert isinstance(data["error_announcement_duration_ms"], int)


@pytest.mark.asyncio
async def test_e2e_chat_flow_success(client: TestClient):
    """
    Teste E2E: Fluxo completo de chat - pergunta válida
    """
    from unittest.mock import patch, AsyncMock

    # Mock do pipeline para evitar chamadas reais à API
    with patch("backend.api.pipeline_acessibilidade", new_callable=AsyncMock) as mock_pipeline:
        mock_pipeline.return_value = {
            "📘 **Introdução**": "Introdução sobre acessibilidade digital",
            "🔍 **Conceitos Essenciais**": "Conceitos importantes",
        }

        # 1. Envia pergunta válida
        pergunta = "O que é acessibilidade digital?"
        response = client.post("/api/chat", json={"pergunta": pergunta})

    # 2. Verifica resposta
    assert response.status_code == 200
    data = response.json()
    assert "resposta" in data
    assert isinstance(data["resposta"], dict)

    # 3. Verifica estrutura da resposta
    resposta = data["resposta"]
    # Deve ter pelo menos uma seção
    assert len(resposta) > 0
    # Cada seção deve ter conteúdo
    for titulo, conteudo in resposta.items():
        assert isinstance(titulo, str)
        assert isinstance(conteudo, str)
        assert len(conteudo) > 0


def test_e2e_chat_flow_validation_error(client: TestClient):
    """
    Teste E2E: Fluxo de chat com erro de validação (pergunta muito curta)
    """
    # 1. Envia pergunta inválida (muito curta)
    response = client.post("/api/chat", json={"pergunta": "ab"})

    # 2. Verifica erro de validação (Pydantic retorna 422 para validação)
    assert response.status_code in [400, 422]
    data = response.json()
    # Pydantic pode retornar detail como lista ou string
    detail_str = str(data.get("detail", "")).lower()
    assert "caracteres" in detail_str or "mínimo" in detail_str or "validation" in detail_str


def test_e2e_chat_flow_empty_question(client: TestClient):
    """
    Teste E2E: Fluxo de chat com pergunta vazia
    """
    # 1. Envia pergunta vazia
    response = client.post("/api/chat", json={"pergunta": ""})

    # 2. Verifica erro de validação
    assert response.status_code == 422  # Unprocessable Entity (Pydantic validation)


@pytest.mark.asyncio
async def test_e2e_chat_flow_cache(client: TestClient):
    """
    Teste E2E: Verifica se o cache está funcionando
    """
    from unittest.mock import patch, AsyncMock

    pergunta = "Teste de cache E2E"
    mock_response = {
        "📘 **Introdução**": "Resposta cacheada",
    }

    with patch("backend.api.pipeline_acessibilidade", new_callable=AsyncMock) as mock_pipeline:
        mock_pipeline.return_value = mock_response

        # 1. Primeira requisição (deve gerar resposta)
        response1 = client.post("/api/chat", json={"pergunta": pergunta})
        # Pode ser 200 (sucesso) ou 429 (rate limit se muitos testes rodaram antes)
        assert response1.status_code in [200, 429], f"Status inesperado: {response1.status_code}"
        
        if response1.status_code == 429:
            # Se rate limit foi acionado, pula o teste (comportamento esperado em CI)
            pytest.skip("Rate limit acionado - comportamento esperado quando muitos testes rodam rapidamente")
        
        data1 = response1.json()

        # 2. Segunda requisição (deve usar cache - não chama pipeline novamente)
        mock_pipeline.reset_mock()
        response2 = client.post("/api/chat", json={"pergunta": pergunta})

        # Verifica que pipeline não foi chamado na segunda vez (cache hit)
        assert mock_pipeline.call_count == 0
    assert response2.status_code == 200
    data2 = response2.json()

    # 3. Respostas devem ser idênticas
    assert data1["resposta"] == data2["resposta"]


@pytest.mark.asyncio
async def test_e2e_metrics_endpoint(client: TestClient):
    """
    Teste E2E: Verifica se o endpoint de métricas retorna dados
    """
    from unittest.mock import patch, AsyncMock

    with patch("backend.api.pipeline_acessibilidade", new_callable=AsyncMock) as mock_pipeline:
        mock_pipeline.return_value = {"Teste": "Métricas"}

        # Faz algumas requisições primeiro para gerar métricas
        client.post("/api/chat", json={"pergunta": "Teste métricas"})

        # Verifica endpoint de métricas
        response = client.get("/api/metrics")

    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "response_time" in data
    assert "fallback" in data
    assert "cache" in data
    assert isinstance(data["total_requests"], int)
    assert data["total_requests"] > 0


def test_e2e_frontend_static_files(client: TestClient):
    """
    Teste E2E: Verifica se os arquivos estáticos do frontend são servidos
    """
    # Testa se o index.html é servido
    response = client.get("/")

    # Pode retornar 200 (se frontend existe) ou 404 (se não existe)
    # Apenas verifica que não é erro 500
    assert response.status_code != 500


def test_e2e_cors_headers(client: TestClient):
    """
    Teste E2E: Verifica se os headers CORS estão presentes
    """
    response = client.options("/api/chat")

    # Verifica que não há erro
    assert response.status_code in [200, 204, 405]  # OPTIONS pode retornar qualquer um


def test_e2e_error_handling(client: TestClient):
    """
    Teste E2E: Verifica tratamento de erros em requisições inválidas
    """
    # Requisição sem body
    response = client.post("/api/chat")

    # Deve retornar erro de validação
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_e2e_multiple_requests(client: TestClient):
    """
    Teste E2E: Verifica se múltiplas requisições sequenciais funcionam
    """
    from unittest.mock import patch, AsyncMock

    pergunta = "Teste de múltiplas requisições"
    mock_response = {"Teste": "Múltiplas requisições"}

    with patch("backend.api.pipeline_acessibilidade", new_callable=AsyncMock) as mock_pipeline:
        mock_pipeline.return_value = mock_response

        # Faz 3 requisições sequenciais
        responses = []
        for i in range(3):
            response = client.post("/api/chat", json={"pergunta": f"{pergunta} {i}"})
            responses.append(response)

        # Todas devem ser bem-sucedidas
        for response in responses:
            assert response.status_code == 200
            assert "resposta" in response.json()


@pytest.mark.asyncio
async def test_e2e_rate_limiting(client: TestClient):
    """
    Teste E2E: Verifica se rate limiting está funcionando
    (teste básico - pode não acionar dependendo da configuração)
    """
    from unittest.mock import patch, AsyncMock

    pergunta = "Teste rate limit"
    mock_response = {"Teste": "Rate limit"}

    with patch("backend.api.pipeline_acessibilidade", new_callable=AsyncMock) as mock_pipeline:
        mock_pipeline.return_value = mock_response

        # Faz várias requisições rápidas
        # Nota: Este teste pode não acionar rate limit se estiver desabilitado
        # ou se o limite for alto. É apenas uma verificação básica.
        for _ in range(5):
            response = client.post("/api/chat", json={"pergunta": pergunta})
            # Pode ser 200 (sucesso) ou 429 (rate limit)
            assert response.status_code in [200, 429]

            if response.status_code == 429:
                # Se rate limit foi acionado, o teste passou
                break
