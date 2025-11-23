from google.adk.agents import Agent
from google.adk.tools import google_search

NOME_MODELO_ADK = "gemini-2.0-flash"


def criar_agentes():
    return {
        "assistente": Agent(
            name="assistente_acessibilidade_digital",
            model=NOME_MODELO_ADK,
            tools=[google_search],
            instruction=(
                "Você é um(a) especialista em acessibilidade digital, com foco em Qualidade de Software. "
                "Responda perguntas de forma clara, acessível e didática, como se estivesse explicando para uma pessoa curiosa "
                "sobre o tema. Use exemplos práticos sempre que possível. Utilize a busca para complementar com fontes atuais quando necessário."
            ),
        ),
        "validador": Agent(
            name="validador_resposta_acessibilidade",
            model=NOME_MODELO_ADK,
            instruction=(
                "Você é um(a) especialista técnico(a) em acessibilidade digital. Receberá uma resposta gerada para uma dúvida real sobre acessibilidade. "
                "Sua tarefa é verificar se o conteúdo está tecnicamente correto de acordo com WCAG, ARIA e boas práticas. "
                "Se necessário, corrija e reescreva a resposta de forma clara e precisa, pronta para ser lida por quem fez a pergunta."
            ),
        ),
        "revisor": Agent(
            name="revisor_clareza_acessibilidade",
            model=NOME_MODELO_ADK,
            instruction=(
                "Você é um(a) comunicador(a) acessível. Reescreva o conteúdo recebido de forma clara, gentil e fácil de entender, "
                "como se estivesse explicando para um usuário leigo. Evite termos técnicos sem explicação e use exemplos simples."
            ),
        ),
        "testador": Agent(
            name="sugestor_testabilidade_acessibilidade",
            model=NOME_MODELO_ADK,
            tools=[google_search],
            instruction=(
                "Você é um(a) especialista em testes de acessibilidade. Com base em uma pergunta e na resposta, "
                "sugira formas práticas de testá-la. Mencione ferramentas como axe, NVDA, VoiceOver, Lighthouse e testes com teclado, contraste etc."
            ),
        ),
        "aprofundador": Agent(
            name="guia_aprofundamento_acessibilidade",
            model=NOME_MODELO_ADK,
            tools=[google_search],
            instruction=(
                "Você é um(a) curador(a) de conteúdo especializado em acessibilidade digital. "
                "Com base em uma dúvida real e uma resposta, sugira materiais de estudo aprofundado como cursos, artigos, livros ou ferramentas confiáveis."
            ),
        ),
    }
