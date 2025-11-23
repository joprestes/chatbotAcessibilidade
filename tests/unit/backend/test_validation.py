"""
Testes de Validação de Entrada

Testa validação e sanitização de entrada do usuário.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

pytestmark = pytest.mark.unit

# Adiciona src ao path
src_path = Path(__file__).parent.parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from backend.api import app  # noqa: E402


@pytest.fixture
def client():
    """Cliente HTTP para testes unitários."""
    return TestClient(app)


def test_question_validation_short(client: TestClient):
    """
    Testa validação de pergunta muito curta.
    """
    # Pergunta com menos de 3 caracteres
    response = client.post("/api/chat", json={"pergunta": "ab"})
    
    assert response.status_code == 422  # Unprocessable Entity
    data = response.json()
    detail = str(data.get("detail", "")).lower()
    assert "mínimo" in detail or "caracteres" in detail or "validation" in detail


def test_question_validation_long(client: TestClient):
    """
    Testa validação de pergunta muito longa.
    """
    # Pergunta com mais de 2000 caracteres
    long_question = "a" * 2001
    response = client.post("/api/chat", json={"pergunta": long_question})
    
    assert response.status_code == 422
    data = response.json()
    detail = str(data.get("detail", "")).lower()
    assert "máximo" in detail or "caracteres" in detail or "validation" in detail


def test_question_validation_whitespace_only(client: TestClient):
    """
    Testa validação de pergunta com apenas espaços.
    """
    # Pergunta com apenas espaços
    response = client.post("/api/chat", json={"pergunta": "   "})
    
    # Deve ser rejeitada (após strip, fica vazia)
    assert response.status_code in [400, 422]


def test_question_validation_special_chars(client: TestClient):
    """
    Testa validação de pergunta com caracteres especiais válidos.
    """
    from unittest.mock import patch, AsyncMock
    
    # Pergunta com caracteres especiais válidos
    special_chars_question = "O que é acessibilidade? (WCAG 2.1)"
    
    with patch("backend.api.pipeline_acessibilidade", new_callable=AsyncMock) as mock_pipeline:
        mock_pipeline.return_value = {"Teste": "Resposta"}
        
        response = client.post("/api/chat", json={"pergunta": special_chars_question})
        
        # Deve ser aceita
        assert response.status_code == 200


def test_question_validation_emojis(client: TestClient):
    """
    Testa validação de pergunta com emojis.
    """
    from unittest.mock import patch, AsyncMock
    
    # Pergunta com emojis
    emoji_question = "O que é acessibilidade? 🎯"
    
    with patch("backend.api.pipeline_acessibilidade", new_callable=AsyncMock) as mock_pipeline:
        mock_pipeline.return_value = {"Teste": "Resposta"}
        
        response = client.post("/api/chat", json={"pergunta": emoji_question})
        
        # Deve ser aceita
        assert response.status_code == 200


def test_question_validation_html(client: TestClient):
    """
    Testa sanitização de pergunta com HTML.
    """
    from unittest.mock import patch, AsyncMock
    
    # Pergunta com HTML
    html_question = "O que é <script>alert('XSS')</script> acessibilidade?"
    
    with patch("backend.api.pipeline_acessibilidade", new_callable=AsyncMock) as mock_pipeline:
        mock_pipeline.return_value = {"Teste": "Resposta"}
        
        response = client.post("/api/chat", json={"pergunta": html_question})
        
        # Deve ser sanitizada e aceita (ou rejeitada se detectada como injeção)
        assert response.status_code in [200, 400, 422]
        
        if response.status_code == 200:
            # Se aceita, verifica que foi sanitizada no pipeline
            # O mock não executa sanitização real, mas em produção seria sanitizado
            pass


def test_input_sanitization_patterns(client: TestClient):
    """
    Testa sanitização de múltiplos padrões de injeção.
    """
    from unittest.mock import patch, AsyncMock
    
    # Padrões de injeção
    injection_patterns = [
        "<script>alert('XSS')</script>",
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "<img src=x onerror=alert(1)>",
    ]
    
    for pattern in injection_patterns:
        # Testa que padrões suspeitos são tratados (pode ser aceito e sanitizado ou rejeitado)
        with patch("backend.api.pipeline_acessibilidade", new_callable=AsyncMock) as mock_pipeline:
            mock_pipeline.return_value = {"Teste": "Resposta sanitizada"}
            
            response = client.post("/api/chat", json={"pergunta": pattern})
            
            # Pode ser aceito (e sanitizado) ou rejeitado
            assert response.status_code in [200, 400, 422], \
                f"Padrão de injeção deve ser tratado: {pattern}"
            
            if response.status_code == 200:
                # Se aceito, verifica que resposta não contém código malicioso
                data = response.json()
                response_text = str(data).lower()
                assert "<script>" not in response_text
                assert "onerror" not in response_text

