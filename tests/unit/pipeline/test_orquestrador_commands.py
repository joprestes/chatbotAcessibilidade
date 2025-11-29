"""
Testes unitários para comandos especiais do PipelineOrquestrador (/simular e /refatorar).
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from chatbot_acessibilidade.pipeline.orquestrador import PipelineOrquestrador

pytestmark = pytest.mark.unit


@patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock)
@patch("chatbot_acessibilidade.pipeline.orquestrador.record_request")
async def test_comando_simular_sucesso(mock_record, mock_get_agent_response):
    """Testa comando /simular com sucesso"""
    orquestrador = PipelineOrquestrador()
    mock_get_agent_response.return_value = "Análise da persona cega..."

    resultado = await orquestrador.executar("/simular cega Como faço login?")

    assert "🎭 **Análise de Cenário**" in resultado
    assert "**Persona:** Cega" in resultado["🎭 **Análise de Cenário**"]
    assert "Análise da persona cega..." in resultado["🎭 **Análise de Cenário**"]
    assert "ℹ️ **Nota**" in resultado


@patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock)
@patch("chatbot_acessibilidade.pipeline.orquestrador.record_request")
async def test_comando_simular_alias_persona(mock_record, mock_get_agent_response):
    """Testa comando /simular com alias de persona (leitor-tela -> Cega)"""
    orquestrador = PipelineOrquestrador()
    mock_get_agent_response.return_value = "Análise..."

    resultado = await orquestrador.executar("/simular leitor-tela teste")

    assert "**Persona:** Cega" in resultado["🎭 **Análise de Cenário**"]


@patch("chatbot_acessibilidade.pipeline.orquestrador.record_request")
async def test_comando_simular_formato_invalido(mock_record):
    """Testa comando /simular sem argumentos suficientes"""
    orquestrador = PipelineOrquestrador()

    resultado = await orquestrador.executar("/simular cega")

    assert "erro" in resultado
    assert "Formato inválido" in resultado["erro"]


@patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock)
@patch("chatbot_acessibilidade.pipeline.orquestrador.record_request")
async def test_comando_simular_erro_execucao(mock_record, mock_get_agent_response):
    """Testa erro durante execução do agente de persona"""
    orquestrador = PipelineOrquestrador()
    mock_get_agent_response.side_effect = Exception("Erro no agente")

    resultado = await orquestrador.executar("/simular cega teste")

    assert "erro" in resultado
    assert "Erro ao simular persona" in resultado["erro"]


@patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock)
@patch("chatbot_acessibilidade.pipeline.orquestrador.record_request")
async def test_comando_refatorar_sucesso(mock_record, mock_get_agent_response):
    """Testa comando /refatorar com sucesso"""
    orquestrador = PipelineOrquestrador()

    json_response = {
        "language": "html",
        "code": "<button>Click</button>",
        "explanation": "Adicionado botão",
        "wcag_criteria": ["1.1.1"],
    }
    mock_get_agent_response.return_value = json.dumps(json_response)

    resultado = await orquestrador.executar("/refatorar <div>Click</div>")

    assert "💻 **Código Refatorado**" in resultado
    assert "📝 **Explicação**" in resultado
    assert "✅ **Critérios WCAG**" in resultado
    assert "<button>Click</button>" in resultado["💻 **Código Refatorado**"]


@patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock)
@patch("chatbot_acessibilidade.pipeline.orquestrador.record_request")
async def test_comando_refatorar_json_markdown(mock_record, mock_get_agent_response):
    """Testa comando /refatorar com resposta em markdown block"""
    orquestrador = PipelineOrquestrador()

    json_str = json.dumps({"code": "test"})
    mock_get_agent_response.return_value = f"```json\n{json_str}\n```"

    resultado = await orquestrador.executar("/refatorar codigo")

    assert "💻 **Código Refatorado**" in resultado


@patch("chatbot_acessibilidade.pipeline.orquestrador.record_request")
async def test_comando_refatorar_sem_codigo(mock_record):
    """Testa comando /refatorar sem código"""
    orquestrador = PipelineOrquestrador()

    resultado = await orquestrador.executar("/refatorar")

    assert "erro" in resultado
    assert "forneça o código" in resultado["erro"]


@patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock)
@patch("chatbot_acessibilidade.pipeline.orquestrador.record_request")
async def test_comando_refatorar_json_invalido(mock_record, mock_get_agent_response):
    """Testa comando /refatorar com resposta JSON inválida (fallback)"""
    orquestrador = PipelineOrquestrador()
    mock_get_agent_response.return_value = "Não é um JSON válido"

    resultado = await orquestrador.executar("/refatorar codigo")

    assert "⚠️ **Resultado (Formato Bruto)**" in resultado
    assert resultado["⚠️ **Resultado (Formato Bruto)**"] == "Não é um JSON válido"


@patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock)
@patch("chatbot_acessibilidade.pipeline.orquestrador.record_request")
async def test_comando_refatorar_erro_execucao(mock_record, mock_get_agent_response):
    """Testa erro durante execução do agente refatorador"""
    orquestrador = PipelineOrquestrador()
    mock_get_agent_response.side_effect = Exception("Erro no agente")

    resultado = await orquestrador.executar("/refatorar codigo")

    assert "erro" in resultado
    assert "Erro ao refatorar código" in resultado["erro"]
