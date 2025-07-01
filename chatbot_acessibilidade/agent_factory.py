# chatbot_acessibilidade/agent_factory.py
import os
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google import genai
from google.genai import types

genai.Client()
NOME_MODELO_ADK = 'gemini-2.0-flash'

def criar_agentes():
    return {
        "assistente": Agent(
            name="assistente_acessibilidade_digital",
            model=NOME_MODELO_ADK,
            tools=[google_search],
            instruction=(
                "Você é um(a) especialista em acessibilidade digital. Receberá uma pergunta real feita por um usuário. "
                "Responda de forma clara, objetiva e didática..."
            )
        ),
        "validador": Agent(
            name="validador_resposta_acessibilidade",
            model=NOME_MODELO_ADK,
            instruction=(
                "Você é um(a) especialista técnico(a) em acessibilidade digital. "
                "Corrija se necessário, e reescreva a resposta final diretamente, sem comentários adicionais."
            )
        ),
        "revisor": Agent(
            name="revisor_clareza_acessibilidade",
            model=NOME_MODELO_ADK,
            instruction=(
                "Você é um(a) comunicador(a) acessível. Reescreva a resposta de forma clara, fluida e acessível."
            )
        ),
        "testador": Agent(
            name="sugestor_testabilidade_acessibilidade",
            model=NOME_MODELO_ADK,
            tools=[google_search],
            instruction=(
                "Sugira formas práticas de testar a acessibilidade da resposta com ferramentas e métodos reais."
            )
        ),
        "aprofundador": Agent(
            name="guia_aprofundamento_acessibilidade",
            model=NOME_MODELO_ADK,
            tools=[google_search],
            instruction=(
                "Sugira materiais confiáveis para estudo aprofundado do tema tratado na resposta."
            )
        ),
    }

AGENTES = criar_agentes()

async def rodar_agente(agent: Agent, prompt: str, user_id="user", session_prefix="sessao") -> str:
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    session_id = f"{session_prefix}_{os.urandom(4).hex()}"

    await session_service.create_session(user_id=user_id, session_id=session_id, app_name=agent.name)
    content = types.Content(role="user", parts=[types.Part(text=prompt)])
    resultado = ""

    async for evento in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if evento.is_final_response():
            resultado += "".join(parte.text + "\n" for parte in evento.content.parts if getattr(parte, "text", None))

    return resultado.strip()

async def executar_agente_por_tipo(tipo: str, prompt: str, prefixo: str) -> str:
    return await rodar_agente(AGENTES[tipo], prompt, session_prefix=prefixo)
