"""
Testes de Integração: Formatter + Pipeline

Valida integração entre formatação de respostas e pipeline,
incluindo geração de exemplos, materiais e estruturação.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys
from unittest.mock import patch, AsyncMock

pytestmark = pytest.mark.integration

# Adiciona src ao path
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from backend.api import app  # noqa: E402


@pytest.fixture
def client():
    """Cliente HTTP para testes de integração."""
    return TestClient(app)


def test_formatter_generates_complete_response_structure(client: TestClient):
    """
    Testa que formatter gera estrutura completa de resposta.

    Categoria: Integration Test
    Objetivo: Validar integração Formatter + Pipeline
    Fluxo: Request → Pipeline → Formatter → Response estruturada
    """
    # Arrange
    mock_response = {
        "introducao": "Introdução formatada",
        "corpo": "Corpo formatado com detalhes",
        "conclusao": "Conclusão formatada",
        "exemplos": [
            {
                "titulo": "Exemplo Formatado",
                "codigo": "const exemplo = 'formatado';",
                "explicacao": "Explicação formatada do exemplo",
            }
        ],
        "testes_sugeridos": ["Teste formatado 1", "Teste formatado 2"],
        "materiais_estudo": ["Material formatado 1", "Material formatado 2"],
        "dica_final": "Dica final formatada",
    }

    # Act
    with patch("backend.api.pipeline_acessibilidade", new=AsyncMock(return_value=mock_response)):
        response = client.post("/api/chat", json={"pergunta": "Como formatar respostas?"})

    # Assert
    assert response.status_code == 200
    data = response.json()
    resposta = data["resposta"]

    # Valida estrutura completa
    assert "introducao" in resposta
    assert "corpo" in resposta
    assert "conclusao" in resposta
    assert "exemplos" in resposta
    assert "testes_sugeridos" in resposta
    assert "materiais_estudo" in resposta
    assert "dica_final" in resposta


def test_formatter_generates_valid_code_examples(client: TestClient):
    """
    Testa que formatter gera exemplos de código válidos.

    Categoria: Integration Test
    Objetivo: Validar geração de exemplos
    Fluxo: Request → Pipeline → Formatter → Exemplos estruturados
    """
    # Arrange
    mock_response = {
        "introducao": "Intro",
        "corpo": "Corpo",
        "conclusao": "Conclusão",
        "exemplos": [
            {
                "titulo": "Botão Acessível",
                "codigo": '<button aria-label="Fechar">X</button>',
                "explicacao": "Botão com label acessível",
            },
            {
                "titulo": "Link Descritivo",
                "codigo": '<a href="/sobre">Saiba mais sobre nós</a>',
                "explicacao": "Link com texto descritivo",
            },
        ],
        "testes_sugeridos": ["T"],
        "materiais_estudo": ["M"],
        "dica_final": "D",
    }

    # Act
    with patch("backend.api.pipeline_acessibilidade", new=AsyncMock(return_value=mock_response)):
        response = client.post("/api/chat", json={"pergunta": "Exemplos de código"})

    # Assert
    assert response.status_code == 200
    data = response.json()
    exemplos = data["resposta"]["exemplos"]

    # Valida estrutura dos exemplos
    assert len(exemplos) == 2
    for exemplo in exemplos:
        assert "titulo" in exemplo
        assert "codigo" in exemplo
        assert "explicacao" in exemplo
        assert len(exemplo["titulo"]) > 0
        assert len(exemplo["codigo"]) > 0
        assert len(exemplo["explicacao"]) > 0


def test_formatter_generates_relevant_test_suggestions(client: TestClient):
    """
    Testa que formatter gera sugestões de testes relevantes.

    Categoria: Integration Test
    Objetivo: Validar geração de testes sugeridos
    Fluxo: Request → Pipeline → Formatter → Testes sugeridos
    """
    # Arrange
    mock_response = {
        "introducao": "Intro",
        "corpo": "Corpo",
        "conclusao": "Conclusão",
        "exemplos": [{"titulo": "E", "codigo": "c", "explicacao": "e"}],
        "testes_sugeridos": [
            "Testar com leitor de tela",
            "Validar contraste de cores",
            "Verificar navegação por teclado",
        ],
        "materiais_estudo": ["M"],
        "dica_final": "D",
    }

    # Act
    with patch("backend.api.pipeline_acessibilidade", new=AsyncMock(return_value=mock_response)):
        response = client.post("/api/chat", json={"pergunta": "Testes de acessibilidade"})

    # Assert
    assert response.status_code == 200
    data = response.json()
    testes = data["resposta"]["testes_sugeridos"]

    # Valida testes sugeridos
    assert isinstance(testes, list)
    assert len(testes) >= 1
    for teste in testes:
        assert isinstance(teste, str)
        assert len(teste) > 0


def test_formatter_generates_study_materials(client: TestClient):
    """
    Testa que formatter gera materiais de estudo.

    Categoria: Integration Test
    Objetivo: Validar geração de materiais
    Fluxo: Request → Pipeline → Formatter → Materiais estruturados
    """
    # Arrange
    mock_response = {
        "introducao": "Intro",
        "corpo": "Corpo",
        "conclusao": "Conclusão",
        "exemplos": [{"titulo": "E", "codigo": "c", "explicacao": "e"}],
        "testes_sugeridos": ["T"],
        "materiais_estudo": [
            "WCAG 2.2 Guidelines",
            "MDN Web Accessibility",
            "A11y Project",
        ],
        "dica_final": "D",
    }

    # Act
    with patch("backend.api.pipeline_acessibilidade", new=AsyncMock(return_value=mock_response)):
        response = client.post("/api/chat", json={"pergunta": "Materiais sobre WCAG"})

    # Assert
    assert response.status_code == 200
    data = response.json()
    materiais = data["resposta"]["materiais_estudo"]

    # Valida materiais
    assert isinstance(materiais, list)
    assert len(materiais) >= 1
    for material in materiais:
        assert isinstance(material, str)
        assert len(material) > 0


def test_formatter_generates_practical_tip(client: TestClient):
    """
    Testa que formatter gera dica prática final.

    Categoria: Integration Test
    Objetivo: Validar geração de dica final
    Fluxo: Request → Pipeline → Formatter → Dica prática
    """
    # Arrange
    mock_response = {
        "introducao": "Intro",
        "corpo": "Corpo",
        "conclusao": "Conclusão",
        "exemplos": [{"titulo": "E", "codigo": "c", "explicacao": "e"}],
        "testes_sugeridos": ["T"],
        "materiais_estudo": ["M"],
        "dica_final": "Sempre teste com usuários reais que usam tecnologias assistivas",
    }

    # Act
    with patch("backend.api.pipeline_acessibilidade", new=AsyncMock(return_value=mock_response)):
        response = client.post("/api/chat", json={"pergunta": "Dicas de acessibilidade"})

    # Assert
    assert response.status_code == 200
    data = response.json()
    dica = data["resposta"]["dica_final"]

    # Valida dica
    assert isinstance(dica, str)
    assert len(dica) > 10  # Dica deve ser substantiva


def test_formatter_handles_long_content(client: TestClient):
    """
    Testa que formatter lida com conteúdo longo.

    Categoria: Integration Test
    Objetivo: Validar formatação de conteúdo extenso
    Fluxo: Request → Pipeline → Formatter → Conteúdo longo formatado
    """
    # Arrange
    long_content = "Conteúdo muito longo. " * 100
    mock_response = {
        "introducao": long_content,
        "corpo": long_content,
        "conclusao": long_content,
        "exemplos": [{"titulo": "E", "codigo": "c" * 500, "explicacao": "e" * 200}],
        "testes_sugeridos": ["T"] * 10,
        "materiais_estudo": ["M"] * 10,
        "dica_final": "D" * 100,
    }

    # Act
    with patch("backend.api.pipeline_acessibilidade", new=AsyncMock(return_value=mock_response)):
        response = client.post("/api/chat", json={"pergunta": "Conteúdo extenso"})

    # Assert
    assert response.status_code == 200
    data = response.json()
    resposta = data["resposta"]

    # Valida que conteúdo longo é aceito
    assert len(resposta["introducao"]) > 100
    assert len(resposta["corpo"]) > 100


def test_formatter_preserves_special_characters(client: TestClient):
    """
    Testa que formatter preserva caracteres especiais.

    Categoria: Integration Test
    Objetivo: Validar preservação de caracteres especiais
    Fluxo: Request → Pipeline → Formatter → Caracteres preservados
    """
    # Arrange
    mock_response = {
        "introducao": "Introdução com émojis 🎯 e acentuação",
        "corpo": "Corpo com símbolos: <, >, &, ', \"",
        "conclusao": "Conclusão com unicode: ñ, ç, ü",
        "exemplos": [
            {
                "titulo": "Exemplo com HTML",
                "codigo": '<div class="test">Código</div>',
                "explicacao": "Explicação com 'aspas' e \"aspas duplas\"",
            }
        ],
        "testes_sugeridos": ["Teste com ñ"],
        "materiais_estudo": ["Material com ç"],
        "dica_final": "Dica com émoji 💡",
    }

    # Act
    with patch("backend.api.pipeline_acessibilidade", new=AsyncMock(return_value=mock_response)):
        response = client.post("/api/chat", json={"pergunta": "Caracteres especiais"})

    # Assert
    assert response.status_code == 200
    data = response.json()
    resposta = data["resposta"]

    # Valida preservação de caracteres
    assert "🎯" in resposta["introducao"]
    assert "ñ" in resposta["conclusao"]
    assert "💡" in resposta["dica_final"]
