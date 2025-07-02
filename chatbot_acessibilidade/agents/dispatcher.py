import os
import asyncio
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from google import genai
from google.genai import types

from chatbot_acessibilidade.agents.factory import criar_agentes

# =======================
# Inicialização do modelo
# =======================
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Chave API do Google não encontrada no arquivo .env.")

genai.Client()

# =======================
# Agentes disponíveis
# =======================
AGENTES = criar_agentes()

# =======================
# Execução de um agente
# =======================
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

# =======================
# Interface pública
# =======================
async def get_agent_response(tipo: str, prompt: str, prefixo: str) -> str:
    if tipo not in AGENTES:
        return f"Erro: agente '{tipo}' não encontrado."
    return await rodar_agente(AGENTES[tipo], prompt, session_prefix=prefixo)
