"""
Testes unitários para PipelineOrquestrador.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch

from chatbot_acessibilidade.core.exceptions import APIError, AgentError, ValidationError
from chatbot_acessibilidade.pipeline.orquestrador import PipelineOrquestrador

pytestmark = pytest.mark.unit


def test_pipeline_orquestrador_inicializacao():
    """Testa se PipelineOrquestrador inicializa corretamente"""
    orquestrador = PipelineOrquestrador()

    assert orquestrador.pergunta == ""
    assert orquestrador.resposta_inicial == ""
    assert orquestrador.resposta_validada == ""
    assert orquestrador.resposta_final == ""
    assert orquestrador.testes == ""
    assert orquestrador.aprofundar == ""


def test_validar_entrada_pergunta_vazia():
    """Testa validação de entrada com pergunta vazia"""
    orquestrador = PipelineOrquestrador()

    with pytest.raises(ValidationError) as exc_info:
        orquestrador.validar_entrada("   ")

    assert "pergunta" in str(exc_info.value).lower()


def test_validar_entrada_pergunta_muito_curta():
    """Testa validação de entrada com pergunta muito curta"""
    orquestrador = PipelineOrquestrador()

    with pytest.raises(ValidationError) as exc_info:
        orquestrador.validar_entrada("ab")

    assert "caracteres" in str(exc_info.value).lower()


def test_validar_entrada_pergunta_muito_longa():
    """Testa validação de entrada com pergunta muito longa"""
    orquestrador = PipelineOrquestrador()
    pergunta_longa = "a" * 2001

    with pytest.raises(ValidationError) as exc_info:
        orquestrador.validar_entrada(pergunta_longa)

    assert "caracteres" in str(exc_info.value).lower()


def test_validar_entrada_pergunta_valida():
    """Testa validação de entrada com pergunta válida"""
    orquestrador = PipelineOrquestrador()
    pergunta = "O que é WCAG?"

    orquestrador.validar_entrada(pergunta)

    assert orquestrador.pergunta == pergunta


@patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock)
def test_executar_sequencial_sucesso(mock_get_agent_response):
    """Testa execução sequencial bem-sucedida"""
    orquestrador = PipelineOrquestrador()
    orquestrador.pergunta = "O que é WCAG?"

    resposta_assistente = "Resposta inicial do assistente."
    resposta_validada = "Resposta validada tecnicamente."
    resposta_revisada = "Resposta revisada para ser mais clara."

    mock_get_agent_response.side_effect = [
        resposta_assistente,
        resposta_validada,
        resposta_revisada,
    ]

    asyncio.run(orquestrador.executar_sequencial())

    assert orquestrador.resposta_inicial == resposta_assistente
    assert orquestrador.resposta_validada == resposta_validada
    assert orquestrador.resposta_final == resposta_revisada
    assert mock_get_agent_response.call_count == 3


@patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock)
def test_executar_sequencial_validador_retorna_ok(mock_get_agent_response):
    """Testa quando validador retorna 'OK'"""
    orquestrador = PipelineOrquestrador()
    orquestrador.pergunta = "O que é WCAG?"

    resposta_assistente = "Resposta inicial do assistente."
    resposta_revisada = "Resposta revisada."

    mock_get_agent_response.side_effect = [
        resposta_assistente,
        "OK",  # Validador aprova
        resposta_revisada,
    ]

    asyncio.run(orquestrador.executar_sequencial())

    # Quando validador retorna OK, mantém resposta inicial
    assert orquestrador.resposta_validada == resposta_assistente
    assert orquestrador.resposta_final == resposta_revisada


@patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock)
def test_executar_sequencial_validador_falha(mock_get_agent_response):
    """Testa quando validador falha, usa resposta inicial"""
    orquestrador = PipelineOrquestrador()
    orquestrador.pergunta = "O que é WCAG?"

    resposta_assistente = "Resposta inicial do assistente."
    resposta_revisada = "Resposta revisada."

    mock_get_agent_response.side_effect = [
        resposta_assistente,
        APIError("Erro no validador"),  # Validador falha
        resposta_revisada,
    ]

    asyncio.run(orquestrador.executar_sequencial())

    # Deve usar resposta inicial quando validador falha
    assert orquestrador.resposta_validada == resposta_assistente
    assert orquestrador.resposta_final == resposta_revisada


@patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock)
def test_executar_sequencial_revisor_falha(mock_get_agent_response):
    """Testa quando revisor falha, usa resposta validada"""
    orquestrador = PipelineOrquestrador()
    orquestrador.pergunta = "O que é WCAG?"

    resposta_assistente = "Resposta inicial."
    resposta_validada = "Resposta validada."

    mock_get_agent_response.side_effect = [
        resposta_assistente,
        resposta_validada,
        APIError("Erro no revisor"),  # Revisor falha
    ]

    asyncio.run(orquestrador.executar_sequencial())

    # Deve usar resposta validada quando revisor falha
    assert orquestrador.resposta_final == resposta_validada


@patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock)
def test_executar_sequencial_assistente_falha(mock_get_agent_response):
    """Testa quando assistente falha, levanta exceção"""
    orquestrador = PipelineOrquestrador()
    orquestrador.pergunta = "O que é WCAG?"

    mock_get_agent_response.side_effect = AgentError("Erro no assistente")

    with pytest.raises(AgentError):
        asyncio.run(orquestrador.executar_sequencial())


@patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock)
def test_executar_paralelo_sucesso(mock_get_agent_response):
    """Testa execução paralela bem-sucedida"""
    orquestrador = PipelineOrquestrador()
    orquestrador.pergunta = "O que é WCAG?"
    orquestrador.resposta_final = "Resposta final."

    sugestoes_testes = "Sugestões de testes."
    sugestoes_aprofundamento = "Sugestões de aprofundamento."

    mock_get_agent_response.side_effect = [
        sugestoes_testes,
        sugestoes_aprofundamento,
    ]

    testes, aprofundar = asyncio.run(orquestrador.executar_paralelo())

    assert testes == sugestoes_testes
    assert aprofundar == sugestoes_aprofundamento
    assert orquestrador.testes == sugestoes_testes
    assert orquestrador.aprofundar == sugestoes_aprofundamento


@patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock)
def test_executar_paralelo_testador_falha(mock_get_agent_response):
    """Testa quando testador falha, usa fallback"""
    orquestrador = PipelineOrquestrador()
    orquestrador.pergunta = "O que é WCAG?"
    orquestrador.resposta_final = "Resposta final."

    sugestoes_aprofundamento = "Sugestões de aprofundamento."

    mock_get_agent_response.side_effect = [
        APIError("Erro no testador"),  # Testador falha
        sugestoes_aprofundamento,
    ]

    testes, aprofundar = asyncio.run(orquestrador.executar_paralelo())

    assert "Não foi possível gerar" in testes
    assert aprofundar == sugestoes_aprofundamento


@patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock)
def test_executar_paralelo_aprofundador_falha(mock_get_agent_response):
    """Testa quando aprofundador falha, usa fallback"""
    orquestrador = PipelineOrquestrador()
    orquestrador.pergunta = "O que é WCAG?"
    orquestrador.resposta_final = "Resposta final."

    sugestoes_testes = "Sugestões de testes."

    mock_get_agent_response.side_effect = [
        sugestoes_testes,
        APIError("Erro no aprofundador"),  # Aprofundador falha
    ]

    testes, aprofundar = asyncio.run(orquestrador.executar_paralelo())

    assert testes == sugestoes_testes
    assert "Não foi possível gerar" in aprofundar


def test_formatar_saida():
    """Testa formatação de saída"""
    orquestrador = PipelineOrquestrador()
    orquestrador.resposta_final = "Primeiro parágrafo.\n\nSegundo parágrafo dos conceitos."
    orquestrador.testes = "Sugestões de testes."
    orquestrador.aprofundar = "Sugestões de aprofundamento."

    resultado = orquestrador.formatar_saida()

    assert isinstance(resultado, dict)
    assert "📘 **Introdução**" in resultado
    assert "🔍 **Conceitos Essenciais**" in resultado
    assert "🧪 **Como Testar na Prática**" in resultado
    assert "📚 **Quer se Aprofundar?**" in resultado
    assert "👋 **Dica Final**" in resultado


@patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock)
@patch("chatbot_acessibilidade.pipeline.orquestrador.record_request")
def test_executar_completo(mock_record_request, mock_get_agent_response):
    """Testa execução completa do pipeline"""
    orquestrador = PipelineOrquestrador()

    resposta_assistente = "Resposta inicial."
    resposta_validada = "Resposta validada."
    resposta_revisada = "Resposta revisada."
    sugestoes_testes = "Sugestões de testes."
    sugestoes_aprofundamento = "Sugestões de aprofundamento."

    mock_get_agent_response.side_effect = [
        resposta_assistente,
        resposta_validada,
        resposta_revisada,
        sugestoes_testes,
        sugestoes_aprofundamento,
    ]

    resultado = asyncio.run(orquestrador.executar("O que é WCAG?"))

    # Verifica que record_request foi chamado
    mock_record_request.assert_called_once()

    # Verifica resultado
    assert isinstance(resultado, dict)
    assert "📘 **Introdução**" in resultado
    assert "🔍 **Conceitos Essenciais**" in resultado
    assert "🧪 **Como Testar na Prática**" in resultado
    assert "📚 **Quer se Aprofundar?**" in resultado
    assert "👋 **Dica Final**" in resultado

    # Verifica que todos os agentes foram chamados
    assert mock_get_agent_response.call_count == 5


@patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock)
def test_executar_validacao_falha(mock_get_agent_response):
    """Testa quando validação de entrada falha"""
    orquestrador = PipelineOrquestrador()

    with pytest.raises(ValidationError):
        asyncio.run(orquestrador.executar(""))  # Pergunta vazia


@patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock)
def test_executar_assistente_falha_levanta_excecao(mock_get_agent_response):
    """Testa quando assistente falha, execução para e levanta exceção"""
    orquestrador = PipelineOrquestrador()

    mock_get_agent_response.side_effect = AgentError("Erro no assistente")

    with pytest.raises(AgentError):
        asyncio.run(orquestrador.executar("O que é WCAG?"))
