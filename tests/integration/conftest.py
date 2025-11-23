"""
Fixtures específicas para testes de integração

Este módulo contém fixtures para testes de integração que testam
a interação entre múltiplos componentes usando TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Adiciona src ao path para imports
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from src.backend.api import app  # noqa: E402


@pytest.fixture
def client() -> TestClient:
    """
    Cliente de teste para integração.
    
    Cria uma instância de TestClient para testar a API FastAPI
    sem precisar de um servidor HTTP real rodando.
    
    Returns:
        TestClient configurado com a aplicação FastAPI
    """
    return TestClient(app)


@pytest.fixture
def sample_question() -> str:
    """
    Pergunta de exemplo para testes de integração.
    
    Returns:
        String com uma pergunta de teste válida
    """
    return "O que é acessibilidade web?"


@pytest.fixture
def sample_response_data() -> dict:
    """
    Dados de resposta de exemplo para testes.
    
    Returns:
        Dict com estrutura de resposta esperada
    """
    return {
        "resposta": "Resposta de teste",
        "agentes_usados": ["assistente"],
        "tempo_resposta_ms": 100
    }

