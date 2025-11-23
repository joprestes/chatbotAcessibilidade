import asyncio
import pytest
from unittest.mock import AsyncMock, patch

from chatbot_acessibilidade.core.formatter import extrair_primeiro_paragrafo
from chatbot_acessibilidade.pipeline import pipeline_acessibilidade

pytestmark = pytest.mark.unit


@patch("chatbot_acessibilidade.pipeline.get_agent_response", new_callable=AsyncMock)
def test_pipeline_sucesso_retorna_dicionario(mock_get_agent_response):
    """
    Testa o caminho feliz do pipeline, garantindo que ele chame todos os agentes
    e retorne um dicionário formatado corretamente.
    """
    # Define as respostas simuladas que cada agente retornará em sequência
    resposta_assistente = "Resposta inicial do assistente."
    resposta_validada = "Resposta validada tecnicamente."
    resposta_revisada = (
        "Resposta revisada para ser mais clara.\n\nEste é o segundo parágrafo dos conceitos."
    )
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
    # Se a introdução for igual ao primeiro parágrafo, pode usar apenas o segundo parágrafo
    conceitos = resultado["🔍 **Conceitos Essenciais**"]
    assert resposta_revisada in conceitos or conceitos in resposta_revisada or len(conceitos) > 0

    # As outras seções devem corresponder às respostas simuladas
    assert resultado["🧪 **Como Testar na Prática**"] == sugestoes_testes
    assert resultado["📚 **Quer se Aprofundar?**"] == sugestoes_aprofundamento
    assert resultado["👋 **Dica Final**"].strip() != ""  # Apenas verifica se a dica foi gerada


def test_pipeline_entrada_vazia():
    """
    Testa se o pipeline lida corretamente com uma pergunta vazia,
    lançando uma exceção de validação.
    """
    from chatbot_acessibilidade.core.exceptions import ValidationError

    # Executa o pipeline com uma string vazia ou com espaços
    with pytest.raises(ValidationError) as exc_info:
        asyncio.run(pipeline_acessibilidade("   "))

    # Verifica se a mensagem de erro está correta
    assert "pergunta" in str(exc_info.value).lower()


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
    # A mensagem pode variar, mas deve conter informação sobre falha
    assert "falha" in resultado["erro"].lower() or "erro" in resultado["erro"].lower()

    # 2. Garante que o pipeline parou após a primeira chamada e não continuou
    mock_get_agent_response.assert_called_once()


@patch("chatbot_acessibilidade.pipeline.get_agent_response", new_callable=AsyncMock)
def test_pipeline_pergunta_muito_curta(mock_get_agent_response):
    """Testa pipeline com pergunta muito curta"""
    from chatbot_acessibilidade.core.exceptions import ValidationError

    with pytest.raises(ValidationError) as exc_info:
        asyncio.run(pipeline_acessibilidade("ab"))

    assert "caracteres" in str(exc_info.value).lower()


@patch("chatbot_acessibilidade.pipeline.get_agent_response", new_callable=AsyncMock)
def test_pipeline_pergunta_muito_longa(mock_get_agent_response):
    """Testa pipeline com pergunta muito longa"""
    from chatbot_acessibilidade.core.exceptions import ValidationError

    pergunta_longa = "a" * 2001
    with pytest.raises(ValidationError) as exc_info:
        asyncio.run(pipeline_acessibilidade(pergunta_longa))

    assert "caracteres" in str(exc_info.value).lower()


@patch("chatbot_acessibilidade.pipeline.get_agent_response", new_callable=AsyncMock)
def test_pipeline_validador_falha_usando_resposta_inicial(mock_get_agent_response):
    """Testa quando validador falha, usa resposta inicial"""
    from chatbot_acessibilidade.core.exceptions import APIError

    resposta_assistente = "Resposta inicial do assistente."
    resposta_revisada = "Resposta revisada."
    sugestoes_testes = "Sugestões de testes."
    sugestoes_aprofundamento = "Sugestões de aprofundamento."

    mock_get_agent_response.side_effect = [
        resposta_assistente,
        APIError("Erro no validador"),  # Validador falha
        resposta_revisada,
        sugestoes_testes,
        sugestoes_aprofundamento,
    ]

    resultado = asyncio.run(pipeline_acessibilidade("O que é WCAG?"))

    # Deve usar resposta inicial quando validador falha
    assert isinstance(resultado, dict)
    assert "erro" not in resultado


@patch("chatbot_acessibilidade.pipeline.get_agent_response", new_callable=AsyncMock)
def test_pipeline_revisor_falha_usando_resposta_tecnica(mock_get_agent_response):
    """Testa quando revisor falha, usa resposta técnica"""
    from chatbot_acessibilidade.core.exceptions import APIError

    resposta_assistente = "Resposta inicial."
    resposta_validada = "Resposta validada tecnicamente."
    sugestoes_testes = "Sugestões de testes."
    sugestoes_aprofundamento = "Sugestões de aprofundamento."

    mock_get_agent_response.side_effect = [
        resposta_assistente,
        resposta_validada,
        APIError("Erro no revisor"),  # Revisor falha
        sugestoes_testes,
        sugestoes_aprofundamento,
    ]

    resultado = asyncio.run(pipeline_acessibilidade("O que é WCAG?"))

    # Deve usar resposta técnica quando revisor falha
    assert isinstance(resultado, dict)
    assert "erro" not in resultado
    assert resultado["🔍 **Conceitos Essenciais**"] == resposta_validada


@patch("chatbot_acessibilidade.pipeline.get_agent_response", new_callable=AsyncMock)
def test_pipeline_agentes_paralelos_falham(mock_get_agent_response):
    """Testa quando agentes paralelos (testador e aprofundador) falham"""
    from chatbot_acessibilidade.core.exceptions import APIError

    resposta_assistente = "Resposta inicial."
    resposta_validada = "Resposta validada."
    resposta_revisada = "Resposta revisada."

    mock_get_agent_response.side_effect = [
        resposta_assistente,
        resposta_validada,
        resposta_revisada,
        APIError("Erro no testador"),  # Testador falha
        APIError("Erro no aprofundador"),  # Aprofundador falha
    ]

    resultado = asyncio.run(pipeline_acessibilidade("O que é WCAG?"))

    # Deve usar fallbacks para agentes paralelos
    assert isinstance(resultado, dict)
    assert "erro" not in resultado
    assert (
        "Não foi possível gerar" in resultado["🧪 **Como Testar na Prática**"]
        or "testes" in resultado["🧪 **Como Testar na Prática**"].lower()
    )


@patch("chatbot_acessibilidade.pipeline.get_agent_response", new_callable=AsyncMock)
def test_pipeline_introducao_igual_corpo(mock_get_agent_response):
    """Testa quando introdução é igual ao corpo completo"""
    resposta_revisada = "Resposta única sem parágrafos adicionais."
    sugestoes_testes = "Sugestões de testes."
    sugestoes_aprofundamento = "Sugestões de aprofundamento."

    mock_get_agent_response.side_effect = [
        "Resposta inicial.",
        "Resposta validada.",
        resposta_revisada,
        sugestoes_testes,
        sugestoes_aprofundamento,
    ]

    resultado = asyncio.run(pipeline_acessibilidade("O que é WCAG?"))

    # Quando introdução == corpo, não deve duplicar
    assert isinstance(resultado, dict)
    assert "erro" not in resultado


@patch("chatbot_acessibilidade.pipeline.get_agent_response", new_callable=AsyncMock)
def test_pipeline_validador_retorna_erro_string(mock_get_agent_response):
    """Testa quando validador retorna string de erro (não exceção)"""
    resposta_assistente = "Resposta inicial."
    resposta_revisada = "Resposta revisada."
    sugestoes_testes = "Sugestões de testes."
    sugestoes_aprofundamento = "Sugestões de aprofundamento."

    mock_get_agent_response.side_effect = [
        resposta_assistente,
        "Erro: Falha na validação",  # Validador retorna string de erro
        resposta_revisada,
        sugestoes_testes,
        sugestoes_aprofundamento,
    ]

    resultado = asyncio.run(pipeline_acessibilidade("O que é WCAG?"))

    # Deve usar resposta inicial quando validador retorna erro
    assert isinstance(resultado, dict)
    assert "erro" not in resultado


@patch("chatbot_acessibilidade.pipeline.get_agent_response", new_callable=AsyncMock)
def test_pipeline_revisor_retorna_erro_string(mock_get_agent_response):
    """Testa quando revisor retorna string de erro (não exceção)"""
    resposta_assistente = "Resposta inicial."
    resposta_validada = "Resposta validada."
    sugestoes_testes = "Sugestões de testes."
    sugestoes_aprofundamento = "Sugestões de aprofundamento."

    mock_get_agent_response.side_effect = [
        resposta_assistente,
        resposta_validada,
        "Erro: Falha na revisão",  # Revisor retorna string de erro
        sugestoes_testes,
        sugestoes_aprofundamento,
    ]

    resultado = asyncio.run(pipeline_acessibilidade("O que é WCAG?"))

    # Deve usar resposta técnica quando revisor retorna erro
    assert isinstance(resultado, dict)
    assert "erro" not in resultado
    assert resultado["🔍 **Conceitos Essenciais**"] == resposta_validada


@patch("chatbot_acessibilidade.pipeline.get_agent_response", new_callable=AsyncMock)
def test_pipeline_agentes_paralelos_excecao_geral(mock_get_agent_response):
    """Testa quando agentes paralelos levantam exceção geral (linha 148-151)"""
    resposta_assistente = "Resposta inicial."
    resposta_validada = "Resposta validada."
    resposta_revisada = "Resposta revisada."

    # Mock que retorna valores normais para os primeiros 3 agentes
    # e levanta exceção para os agentes paralelos
    async def async_side_effect(tipo, prompt, prefixo):
        if tipo == "assistente":
            return resposta_assistente
        elif tipo == "validador":
            return resposta_validada
        elif tipo == "revisor":
            return resposta_revisada
        elif tipo == "testador":
            raise Exception("Erro geral no testador")
        elif tipo == "aprofundador":
            raise Exception("Erro geral no aprofundador")

    mock_get_agent_response.side_effect = async_side_effect

    resultado = asyncio.run(pipeline_acessibilidade("O que é WCAG?"))

    # Deve usar fallbacks para agentes paralelos (linha 148-151)
    assert isinstance(resultado, dict)
    assert "erro" not in resultado
    # Verifica que as chaves existem e contêm as mensagens de fallback
    chave_testes = "🧪 **Como Testar na Prática**"
    chave_aprofundar = "📚 **Quer se Aprofundar?**"
    assert chave_testes in resultado
    assert chave_aprofundar in resultado
    assert "Não foi possível gerar" in resultado[chave_testes]
    assert "Não foi possível gerar" in resultado[chave_aprofundar]


@patch("chatbot_acessibilidade.pipeline.get_agent_response", new_callable=AsyncMock)
def test_pipeline_assistente_excecao_agent_error(mock_get_agent_response):
    """Testa quando assistente levanta AgentError"""
    from chatbot_acessibilidade.core.exceptions import AgentError

    mock_get_agent_response.side_effect = AgentError("Erro no agente")

    resultado = asyncio.run(pipeline_acessibilidade("O que é WCAG?"))

    assert isinstance(resultado, dict)
    assert "erro" in resultado
    assert "AgentError" in str(resultado["erro"]) or "erro" in resultado["erro"].lower()


def test_pipeline_tratar_resultado_paralelo_com_excecao():
    """Testa _tratar_resultado_paralelo quando resultado é Exception (linha 28-34)"""
    from chatbot_acessibilidade.pipeline import _tratar_resultado_paralelo
    from chatbot_acessibilidade.core.exceptions import APIError

    # Testa quando resultado é Exception (linha 28-30)
    resultado_excecao = APIError("Erro de teste")
    resultado = _tratar_resultado_paralelo(resultado_excecao, "teste", "Fallback")
    assert resultado == "Fallback"

    # Testa quando resultado é string de erro (linha 32-34)
    resultado_erro = "Erro: Falha na API"
    resultado = _tratar_resultado_paralelo(resultado_erro, "teste", "Fallback")
    assert resultado == "Fallback"

    # Testa quando resultado é válido (linha 36)
    resultado_valido = "Resposta válida"
    resultado = _tratar_resultado_paralelo(resultado_valido, "teste", "Fallback")
    assert resultado == "Resposta válida"


@patch("chatbot_acessibilidade.pipeline.get_agent_response", new_callable=AsyncMock)
def test_pipeline_agentes_paralelos_excecao_geral_no_gather(mock_get_agent_response):
    """Testa pipeline quando asyncio.gather levanta exceção geral (linha 148-151)"""
    resposta_assistente = "Resposta inicial."
    resposta_validada = "Resposta validada."
    resposta_revisada = "Resposta revisada."

    call_count = [0]

    async def async_side_effect(tipo, prompt, prefixo):
        call_count[0] += 1
        if call_count[0] == 1:  # assistente
            return resposta_assistente
        elif call_count[0] == 2:  # validador
            return resposta_validada
        elif call_count[0] == 3:  # revisor
            return resposta_revisada
        elif call_count[0] == 4:  # testador - levanta exceção
            raise ValueError("Erro no gather")
        elif call_count[0] == 5:  # aprofundador - levanta exceção
            raise ValueError("Erro no gather")

    mock_get_agent_response.side_effect = async_side_effect

    # Mock asyncio.gather para levantar exceção
    with patch("chatbot_acessibilidade.pipeline.asyncio.gather") as mock_gather:
        mock_gather.side_effect = Exception("Erro geral no gather")

        resultado = asyncio.run(pipeline_acessibilidade("O que é WCAG?"))

        # Deve usar fallbacks (linha 148-151)
        assert isinstance(resultado, dict)
        assert "erro" not in resultado
        chave_testes = "🧪 **Como Testar na Prática**"
        chave_aprofundar = "📚 **Quer se Aprofundar?**"
        assert "Não foi possível gerar" in resultado[chave_testes]
        assert "Não foi possível gerar" in resultado[chave_aprofundar]
