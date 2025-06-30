import pytest
from chatbot_acessibilidade import agent
from chatbot_acessibilidade.agent import pipeline_acessibilidade
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_pipeline_setup():
    with patch('chatbot_acessibilidade.agent.assistente_acessibilidade') as mock_assistente, \
         patch('chatbot_acessibilidade.agent.revisor_clareza') as mock_revisor, \
         patch('chatbot_acessibilidade.agent.validador_resposta') as mock_validador, \
         patch('chatbot_acessibilidade.agent.validador_links') as mock_links, \
         patch('chatbot_acessibilidade.agent.testabilidade') as mock_testabilidade, \
         patch('chatbot_acessibilidade.agent.aprofundador') as mock_aprofundador:

        mock_assistente.return_value = "Resposta inicial padrão do assistente ADK."
        mock_revisor.return_value = "Resposta padrão revisada para clareza (ADK)."
        mock_validador.return_value = "Resposta padrão validada tecnicamente (ADK)."
        mock_links.return_value = "✅ https://example.com (Status: 200)"
        mock_testabilidade.return_value = "Sugestões padrão de como testar (ADK)."
        mock_aprofundador.return_value = "Sugestões padrão para aprofundamento (ADK)."

        yield

def test_pipeline_retorna_resposta_str(mock_pipeline_setup):
    pergunta = "O que é WCAG?"
    resposta = pipeline_acessibilidade(pergunta)

    assert isinstance(resposta, str)
    assert len(resposta) > 0

    agent.assistente_acessibilidade.assert_called_once_with(pergunta)
    agent.revisor_clareza.assert_called_once_with(agent.assistente_acessibilidade.return_value)
    agent.validador_resposta.assert_called_once_with(agent.revisor_clareza.return_value)
    agent.validador_links.assert_called_once_with(agent.validador_resposta.return_value)
    agent.testabilidade.assert_called_once_with(pergunta, agent.validador_resposta.return_value)
    agent.aprofundador.assert_called_once_with(pergunta, agent.validador_resposta.return_value)


def test_pipeline_entrada_vazia(mock_pipeline_setup):
    pergunta = ""
    resposta_esperada = "Por favor, digite uma pergunta sobre acessibilidade digital."

    resposta = pipeline_acessibilidade(pergunta)

    assert resposta == resposta_esperada

    agent.assistente_acessibilidade.assert_not_called()
    agent.revisor_clareza.assert_not_called()
    agent.validador_resposta.assert_not_called()
    agent.testabilidade.assert_not_called()
    agent.aprofundador.assert_not_called()
    agent.validador_links.assert_not_called()


def test_pipeline_estrutura_resposta(mock_pipeline_setup):
    pergunta = "Como melhorar o contraste de um site?"
    resposta = pipeline_acessibilidade(pergunta).lower()

    palavras_chave_esperadas = ["resposta principal:", "verificação de links:", "como testar ou experimentar:", "quer se aprofundar?"]

    for palavra in palavras_chave_esperadas:
        assert palavra in resposta, f"A seção '{palavra}' não foi encontrada na resposta."


def test_pipeline_aria(mock_pipeline_setup):
    pergunta = "O que é aria-label?"
    frase_esperada_aria = "Usado para fornecer um rótulo acessível para elementos"

    agent.validador_resposta.return_value = (
        f"Resposta validada sobre aria-label (ADK). É importante saber que é "
        f"{frase_esperada_aria}."
    )

    resposta = pipeline_acessibilidade(pergunta)

    assert frase_esperada_aria in resposta, "A resposta deveria conter a explicação sobre aria-label."
    agent.assistente_acessibilidade.assert_called_once_with(pergunta)
    agent.validador_resposta.assert_called_once_with(agent.revisor_clareza.return_value)


def test_pipeline_contexto_acessibilidade_implicito(mock_pipeline_setup):
    pergunta_generica = "O que é contraste?"
    frase_contexto_esperada = "Considerando o contexto de acessibilidade digital, o contraste"

    agent.assistente_acessibilidade.return_value = (
        f"{frase_contexto_esperada} é a diferença de luminosidade entre cores (ADK)."
    )

    agent.revisor_clareza.side_effect = lambda x: x
    agent.validador_resposta.side_effect = lambda x: x


    resposta = pipeline_acessibilidade(pergunta_generica)

    assert frase_contexto_esperada.lower() in resposta.lower(), \
        "A resposta deveria indicar que o contexto de acessibilidade digital foi assumido."

    agent.assistente_acessibilidade.assert_called_once_with(pergunta_generica)