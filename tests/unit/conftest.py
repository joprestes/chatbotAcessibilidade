"""
Fixtures específicas para testes unitários

Este módulo contém fixtures comuns e reutilizáveis para testes unitários,
incluindo mocks, factories e configurações específicas.
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock
from typing import Dict, Any


@pytest.fixture
def mock_llm_response() -> Dict[str, Any]:
    """
    Mock de resposta LLM padrão para testes unitários.
    
    Returns:
        Dict com estrutura de resposta LLM simulada
    """
    return {
        "text": "Resposta de teste do LLM",
        "metadata": {
            "model": "test-model",
            "usage": {"prompt_tokens": 10, "completion_tokens": 20}
        }
    }


@pytest.fixture
def mock_async_llm_client() -> AsyncMock:
    """
    Mock de cliente LLM assíncrono para testes.
    
    Returns:
        AsyncMock configurado para simular chamadas LLM
    """
    mock = AsyncMock()
    mock.generate.return_value = "Resposta mockada do LLM"
    return mock


@pytest.fixture
def mock_cache_stats() -> Dict[str, Any]:
    """
    Mock de estatísticas de cache para testes.
    
    Returns:
        Dict com estatísticas simuladas de cache
    """
    return {
        "hits": 5,
        "misses": 3,
        "size": 8,
        "max_size": 100
    }

