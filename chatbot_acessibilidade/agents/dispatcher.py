import os
import asyncio
from dotenv import load_dotenv

# Dependências do Google
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google import genai
from google.genai import types
from google.api_core import exceptions as google_exceptions

# Dependências locais do seu projeto
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
# Execução de um agente (com tratamento de erros robusto)
# =======================
async def rodar_agente(agent: Agent, prompt: str, user_id="user", session_prefix="sessao") -> str:
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    session_id = f"{session_prefix}_{os.urandom(4).hex()}"

    await session_service.create_session(user_id=user_id, session_id=session_id, app_name=agent.name)
    content = types.Content(role="user", parts=[types.Part(text=prompt)])

    try:
        final_response_content = None
        
        # Coleta a resposta final primeiro
        async for evento in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
            if evento.is_final_response():
                final_response_content = evento.content
                break  # Sai do loop assim que tiver a resposta final

        # Verifica se a resposta recebida é válida
        if not final_response_content or not final_response_content.parts:
            return "Erro: A resposta da API veio vazia. Por favor, tente novamente."

        # Verifica de forma segura se o motivo da finalização foi por segurança
        primeira_parte = final_response_content.parts[0]
        if hasattr(primeira_parte, 'finish_reason') and primeira_parte.finish_reason == types.FinishReason.SAFETY:
            return "Erro: Sua pergunta não pôde ser processada devido às diretrizes de segurança. Por favor, tente reformular sua consulta."

        # Se tudo correu bem, constrói o resultado a partir das partes da resposta
        resultado = "".join(parte.text + "\n" for parte in final_response_content.parts if getattr(parte, "text", None))
        return resultado.strip()

    # Erro específico para cota excedida (Too Many Requests - 429)
    except google_exceptions.ResourceExhausted as e:
        return "Erro: Estou recebendo muitas perguntas no momento! Por favor, aguarde um minuto e tente novamente. 🕒"

    # Erro de autenticação ou permissão (Chave de API inválida - 401/403)
    except google_exceptions.PermissionDenied as e:
        print(f"ERRO DE AUTENTICAÇÃO: {e}")
        return "Erro: Houve um problema com a configuração do servidor. A equipe de desenvolvimento foi notificada."

    # Erros genéricos da API do Google, incluindo o 503 (sobrecarga)
    except google_exceptions.GoogleAPICallError as e:
        error_str = str(e).lower()
        if "503" in error_str or "overloaded" in error_str:
            return "Erro: A API do Google parece estar sobrecarregada. Por favor, tente sua pergunta novamente em alguns instantes. 🙏"
        
        print(f"ERRO DE API DO GOOGLE: {e}")
        return "Erro: Ocorreu um problema de comunicação com a API."

    # Captura de qualquer outro erro inesperado no código
    except Exception as e:
        print(f"ERRO INESPERADO no agente '{agent.name}': {e}") 
        return "Erro: Ocorreu uma falha inesperada. Por favor, tente novamente."

# =======================
# Interface pública 
# =======================
async def get_agent_response(tipo: str, prompt: str, prefixo: str) -> str:
    if tipo not in AGENTES:
        return f"Erro: agente '{tipo}' não encontrado."
    return await rodar_agente(AGENTES[tipo], prompt, session_prefix=prefixo)