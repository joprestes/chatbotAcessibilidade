import pytest
from unittest.mock import AsyncMock, patch
from chatbot_acessibilidade.pipeline.orquestrador import PipelineOrquestrador

@pytest.mark.asyncio
async def test_simular_persona_flow():
    """Testa o fluxo completo do comando /simular com nomes inclusivos."""
    # Mock da resposta do agente
    mock_response = "Olá, sou Maria, tenho baixa visão. Ao tentar ler este texto, senti dificuldade com o contraste cinza claro no fundo branco."
    
    with patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock) as mock_agent:
        mock_agent.return_value = mock_response
        
        orquestrador = PipelineOrquestrador()
        
        pergunta = "/simular zoom-contraste O que você acha deste texto cinza?"
        
        resultado = await orquestrador.executar(pergunta)
        
        # Verifica se o agente persona foi chamado
        mock_agent.assert_called_once()
        args, _ = mock_agent.call_args
        assert args[0] == "persona"
        # Verifica se mapeou corretamente zoom-contraste -> Baixa Visão
        assert "Persona: Baixa Visão" in args[1]
        assert "Contexto: O que você acha deste texto cinza?" in args[1]
        
        # Verifica a estrutura da resposta
        assert "🎭 **Análise de Cenário**" in resultado
        assert "ℹ️ **Nota**" in resultado
        
        # Verifica conteúdo
        assert "Maria" in resultado["🎭 **Análise de Cenário**"]
        assert "baixa visão" in resultado["🎭 **Análise de Cenário**"]

@pytest.mark.asyncio
async def test_persona_command_invalid_format():
    """Testa o comando /simular com formato inválido."""
    orquestrador = PipelineOrquestrador()
    pergunta = "/simular apenas_uma_palavra"
    
    resultado = await orquestrador.executar(pergunta)
    
    assert "erro" in resultado
    assert "Formato inválido" in resultado["erro"]
