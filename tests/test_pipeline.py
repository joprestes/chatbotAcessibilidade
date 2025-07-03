import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from chatbot_acessibilidade.pipeline import pipeline_acessibilidade
from chatbot_acessibilidade.core.formatter import extrair_primeiro_paragrafo

@patch("chatbot_acessibilidade.pipeline.get_agent_response", new_callable=AsyncMock)
def test_pipeline_sucesso_retorna_dicionario(mock_get_agent_response):
    """
    Testa o caminho feliz do pipeline, garantindo que ele chame todos os agentes
    e retorne um dicionário formatado corretamente.
    """
    # Define as respostas simuladas que cada agente retornará em sequência
    resposta_assistente = "Resposta inicial do assistente."
    resposta_validada = "Resposta validada tecnicamente."
    resposta_revisada = "Resposta revisada para ser mais clara.\n\nEste é o segundo parágrafo dos conceitos."
    sugestoes_testes = "Sugestões de como testar na prática."
    sugestoes_aprofundamento = "Links e materiais para aprofundar."

    mock_get_agent_response.side_effect = [
        resposta_assistente,
        resposta_validada,
        resposta_revisada,
        sugestoes_testes,
        sugestoes_aprofundamento,
    ]

    pergunta = "O que é WCAG?"
    
    # Executa a função assíncrona do pipeline dentro do teste síncrono
    resultado = asyncio.run(pipeline_acessibilidade(pergunta))

    # 1. Verifica se o resultado é um dicionário e se não contém erros
    assert isinstance(resultado, dict)
    assert "erro" not in resultado

    # 2. Garante que todos os 5 agentes foram chamados
    assert mock_get_agent_response.call_count == 5

    # 3. Verifica o conteúdo de cada seção do dicionário
    # A introdução deve ser o primeiro parágrafo da resposta final (revisada)
    assert resultado["📘 **Introdução**"] == extrair_primeiro_paragrafo(resposta_revisada)
    
    # A seção de conceitos deve conter a resposta completa e revisada
    assert resultado["🔍 **Conceitos Essenciais**"] == resposta_revisada
    
    # As outras seções devem corresponder às respostas simuladas
    assert resultado["🧪 **Como Testar na Prática**"] == sugestoes_testes
    assert resultado["📚 **Quer se Aprofundar?**"] == sugestoes_aprofundamento
    assert resultado["👋 **Dica Final**"].strip() != ""  # Apenas verifica se a dica foi gerada

def test_pipeline_entrada_vazia():
    """
    Testa se o pipeline lida corretamente com uma pergunta vazia,
    retornando um dicionário de erro.
    """
    # Executa o pipeline com uma string vazia ou com espaços
    resultado = asyncio.run(pipeline_acessibilidade("   "))
    
    # A mensagem de erro esperada, incluindo o emoji que você sugeriu
    mensagem_esperada = " ❌ Por favor, digite uma pergunta sobre acessibilidade digital."
    
    # Verifica se o resultado é um dicionário e se a mensagem de erro está correta
    assert isinstance(resultado, dict)
    assert "erro" in resultado
    assert resultado["erro"] == mensagem_esperada


@patch("chatbot_acessibilidade.pipeline.get_agent_response", new_callable=AsyncMock)
def test_pipeline_falha_no_primeiro_agente(mock_get_agent_response):
    """
    Testa o que acontece se o primeiro agente (assistente) falhar,
    garantindo que o pipeline pare e retorne um erro.
    """
    # Simula uma resposta de erro do primeiro agente
    mock_get_agent_response.return_value = "Erro: Falha na API do Gemini"

    pergunta = "O que é WCAG?"
    
    # Executa o pipeline
    resultado = asyncio.run(pipeline_acessibilidade(pergunta))
    
    # 1. Verifica se o resultado é um dicionário de erro
    assert isinstance(resultado, dict)
    assert "erro" in resultado
    assert "Falha ao processar sua pergunta" in resultado["erro"]
    
    # 2. Garante que o pipeline parou após a primeira chamada e não continuou
    mock_get_agent_response.assert_called_once()