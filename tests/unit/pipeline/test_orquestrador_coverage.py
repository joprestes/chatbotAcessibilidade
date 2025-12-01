"""
Testes adicionais para aumentar cobertura do PipelineOrquestrador.

Estes testes focam em cenários específicos que não eram cobertos pelos testes existentes,
especialmente casos onde eh_erro() retorna True e exceções genéricas.
"""

import pytest
from unittest.mock import AsyncMock, patch

from chatbot_acessibilidade.core.exceptions import AgentError
from chatbot_acessibilidade.pipeline.orquestrador import (
    PipelineOrquestrador,
    _tratar_resultado_paralelo,
)

pytestmark = pytest.mark.unit


def test_tratar_resultado_paralelo_com_erro_detectado():
    """
    Testa _tratar_resultado_paralelo quando eh_erro() retorna True.

    Cobre linhas 47-48 do orquestrador.py.
    """
    # Mock da função eh_erro para retornar True
    with patch("chatbot_acessibilidade.pipeline.orquestrador.eh_erro", return_value=True):
        resultado = "ERRO: Algo deu errado"
        fallback = "Mensagem de fallback"

        resultado_tratado = _tratar_resultado_paralelo(resultado, "testador", fallback)

        # Deve retornar o fallback quando eh_erro() retorna True
        assert resultado_tratado == fallback


def test_tratar_resultado_paralelo_com_sucesso():
    """Testa _tratar_resultado_paralelo com resultado válido."""
    with patch("chatbot_acessibilidade.pipeline.orquestrador.eh_erro", return_value=False):
        resultado = "Resultado válido"
        fallback = "Mensagem de fallback"

        resultado_tratado = _tratar_resultado_paralelo(resultado, "testador", fallback)

        # Deve retornar o resultado original quando não há erro
        assert resultado_tratado == resultado


@patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock)
async def test_executar_sequencial_assistente_retorna_erro(mock_get_agent_response):
    """
    Testa quando assistente retorna resposta com erro detectado por eh_erro().

    Cobre linhas 126-127 do orquestrador.py.
    """
    orquestrador = PipelineOrquestrador()
    orquestrador.pergunta = "O que é WCAG?"

    # Mock da função eh_erro para retornar True na primeira chamada
    with patch("chatbot_acessibilidade.pipeline.orquestrador.eh_erro", return_value=True):
        mock_get_agent_response.return_value = "ERRO: Falha na geração"

        # Deve levantar AgentError quando eh_erro() retorna True
        with pytest.raises(AgentError) as exc_info:
            await orquestrador.executar_sequencial()

        assert "Erro na resposta inicial" in str(exc_info.value) or "ERRO" in str(exc_info.value)


@patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock)
async def test_executar_sequencial_validador_retorna_erro(mock_get_agent_response):
    """
    Testa quando validador retorna resposta com erro detectado por eh_erro().

    Cobre linhas 150-151 do orquestrador.py.
    """
    orquestrador = PipelineOrquestrador()
    orquestrador.pergunta = "O que é WCAG?"

    resposta_assistente = "Resposta inicial válida"

    # Primeira chamada (assistente) retorna sucesso, segunda (validador) retorna erro
    mock_get_agent_response.side_effect = [
        resposta_assistente,  # Assistente OK
        "ERRO: Validação falhou",  # Validador com erro
        "Resposta revisada",  # Revisor OK
    ]

    # Mock eh_erro para retornar False na primeira chamada e True na segunda
    with patch("chatbot_acessibilidade.pipeline.orquestrador.eh_erro") as mock_eh_erro:
        mock_eh_erro.side_effect = [False, True, False]  # assistente OK, validador ERRO, revisor OK

        await orquestrador.executar_sequencial()

        # Deve usar resposta inicial quando validador retorna erro
        assert orquestrador.resposta_validada == resposta_assistente


@patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock)
async def test_executar_sequencial_revisor_retorna_erro(mock_get_agent_response):
    """
    Testa quando revisor retorna resposta com erro detectado por eh_erro().

    Cobre linhas 178-179 do orquestrador.py.
    """
    orquestrador = PipelineOrquestrador()
    orquestrador.pergunta = "O que é WCAG?"

    resposta_assistente = "Resposta inicial"
    resposta_validada = "Resposta validada"

    mock_get_agent_response.side_effect = [
        resposta_assistente,
        resposta_validada,
        "ERRO: Revisão falhou",  # Revisor com erro
    ]

    # Mock eh_erro para retornar False nas duas primeiras e True na terceira
    with patch("chatbot_acessibilidade.pipeline.orquestrador.eh_erro") as mock_eh_erro:
        mock_eh_erro.side_effect = [False, False, True]  # assistente OK, validador OK, revisor ERRO

        await orquestrador.executar_sequencial()

        # Deve usar resposta validada quando revisor retorna erro
        assert orquestrador.resposta_final == resposta_validada


@patch("chatbot_acessibilidade.pipeline.orquestrador.get_agent_response", new_callable=AsyncMock)
@patch("chatbot_acessibilidade.pipeline.orquestrador.asyncio.gather")
async def test_executar_paralelo_exception_generica(mock_gather, mock_get_agent_response):
    """
    Testa quando asyncio.gather levanta uma Exception genérica.

    Cobre linhas 249-253 do orquestrador.py.
    """
    orquestrador = PipelineOrquestrador()
    orquestrador.pergunta = "O que é WCAG?"
    orquestrador.resposta_final = "Resposta final"

    # Simula uma Exception genérica (não APIError/AgentError)
    mock_gather.side_effect = RuntimeError("Erro inesperado no gather")

    testes, aprofundar = await orquestrador.executar_paralelo()

    # Deve retornar mensagens de fallback quando ocorre Exception genérica
    assert "Não foi possível gerar sugestões de testes" in testes
    assert "Não foi possível gerar sugestões de aprofundamento" in aprofundar
    assert orquestrador.testes == testes
    assert orquestrador.aprofundar == aprofundar
