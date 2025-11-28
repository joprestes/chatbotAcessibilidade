import pytest
from unittest.mock import AsyncMock, patch
from chatbot_acessibilidade.pipeline.orquestrador import PipelineOrquestrador

@pytest.mark.asyncio
async def test_refactor_command_flow():
    """
    Testa o fluxo completo do comando /refatorar.
    Verifica se o orquestrador detecta o comando, chama o agente correto
    e formata a resposta adequadamente.
    """
    # Mock do get_agent_response para retornar um JSON simulado
    mock_response = """
    ```json
    {
        "code": "<button>Click me</button>",
        "explanation": "Changed div to button",
        "wcag_criteria": ["2.1.1", "4.1.2"],
        "language": "html"
    }
    ```
    """
    
    with patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock) as mock_agent:
        mock_agent.return_value = mock_response
        
        orquestrador = PipelineOrquestrador()
        pergunta = "/refatorar <div onclick='alert()'>Click me</div>"
        
        resultado = await orquestrador.executar(pergunta)
        
        # Verifica se o agente refatorador foi chamado
        mock_agent.assert_called_once()
        args, _ = mock_agent.call_args
        assert args[0] == "refatorador"
        assert "<div onclick='alert()'>Click me</div>" in args[1]
        
        # Verifica a estrutura da resposta
        assert "💻 **Código Refatorado**" in resultado
        assert "📝 **Explicação**" in resultado
        assert "✅ **Critérios WCAG**" in resultado
        
        # Verifica conteúdo
        assert "<button>Click me</button>" in resultado["💻 **Código Refatorado**"]
        assert "Changed div to button" in resultado["📝 **Explicação**"]
        assert "2.1.1" in resultado["✅ **Critérios WCAG**"]

@pytest.mark.asyncio
async def test_refactor_command_empty_code():
    """Testa o comando /refatorar sem código."""
    orquestrador = PipelineOrquestrador()
    pergunta = "/refatorar   "
    
    resultado = await orquestrador.executar(pergunta)
    
    assert "erro" in resultado
    assert "forneça o código" in resultado["erro"]
