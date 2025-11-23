"""
Dispatcher de agentes - Gerencia a execução dos agentes do chatbot
"""
import os
import asyncio
import logging
from typing import Optional

# Dependências do Google
from google.adk.agents import Agent
from google.api_core import exceptions as google_exceptions

# Dependências de retry
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Dependências locais do seu projeto
from chatbot_acessibilidade.agents.factory import criar_agentes
from chatbot_acessibilidade.config import settings
from chatbot_acessibilidade.core.exceptions import APIError, AgentError
from chatbot_acessibilidade.core.llm_provider import (
    GoogleGeminiClient,
    OpenRouterClient,
    generate_with_fallback,
)

# Configuração de logging
logger = logging.getLogger(__name__)

# =======================
# Agentes disponíveis
# =======================
AGENTES = criar_agentes()

# =======================
# Inicialização de clientes LLM (lazy loading)
# =======================
_openrouter_client: Optional[OpenRouterClient] = None

def _get_openrouter_client() -> Optional[OpenRouterClient]:
    """Inicializa o cliente OpenRouter de forma lazy"""
    global _openrouter_client
    if _openrouter_client is None and settings.fallback_enabled and settings.openrouter_api_key:
        try:
            logger.info("Inicializando cliente OpenRouter")
            _openrouter_client = OpenRouterClient()
        except Exception as e:
            logger.warning(f"Não foi possível inicializar OpenRouter: {e}")
            return None
    return _openrouter_client

# =======================
# Execução de um agente (com tratamento de erros robusto e retry)
# =======================
def _should_retry(exception: Exception) -> bool:
    """Determina se uma exceção deve ser retentada"""
    # Retry apenas para erros temporários
    if isinstance(exception, google_exceptions.ResourceExhausted):
        return True  # 429 - Rate limit
    if isinstance(exception, google_exceptions.GoogleAPICallError):
        error_str = str(exception).lower()
        # Retry apenas para 503 (sobrecarga)
        if "503" in error_str or "overloaded" in error_str:
            return True
    # Não retry para outros erros
    return False


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((google_exceptions.ResourceExhausted, google_exceptions.GoogleAPICallError)),
    reraise=True,
    before_sleep=lambda retry_state: logger.warning(
        f"Tentativa {retry_state.attempt_number}/3 para agente após erro: {retry_state.outcome.exception()}"
    ) if retry_state.outcome else None
)
async def rodar_agente(agent: Agent, prompt: str, user_id="user", session_prefix="sessao") -> str:
    """
    Executa um agente com tratamento de erros, logging e fallback automático.
    
    Args:
        agent: Agente a ser executado
        prompt: Prompt para o agente
        user_id: ID do usuário
        session_prefix: Prefixo para o ID da sessão
        
    Returns:
        Resposta do agente como string
        
    Raises:
        AgentError: Se houver erro na execução do agente
        APIError: Se houver erro na comunicação com a API
    """
    logger.debug(f"Executando agente '{agent.name}' com prompt: {prompt[:50]}...")
    
    # Cria cliente primário (Google Gemini)
    primary_client = GoogleGeminiClient(agent)
    
    # Prepara clientes de fallback (OpenRouter)
    fallback_clients = []
    fallback_models = []
    
    if settings.fallback_enabled:
        openrouter_client = _get_openrouter_client()
        if openrouter_client:
            fallback_clients.append(openrouter_client)
            fallback_models = settings.openrouter_models_list
    
    try:
        # Usa o sistema de fallback automático
        resposta, provedor_usado = await generate_with_fallback(
            primary_client=primary_client,
            prompt=prompt,
            fallback_clients=fallback_clients if fallback_clients else None,
            fallback_models=fallback_models if fallback_models else None
        )
        
        logger.info(f"Agente '{agent.name}' executado com sucesso usando {provedor_usado}")
        return resposta
        
    except APIError as e:
        # Converte mensagens de erro para formato amigável
        error_msg = str(e)
        if "Timeout" in error_msg:
            raise APIError(f"Timeout: A requisição demorou mais de {settings.api_timeout_seconds} segundos para responder. Por favor, tente novamente.")
        elif "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            raise APIError("Erro: Estou recebendo muitas perguntas no momento! Por favor, aguarde um minuto e tente novamente. 🕒")
        elif "todos os provedores" in error_msg.lower():
            raise APIError("Erro: Todos os modelos disponíveis falharam. Por favor, tente novamente mais tarde.")
        else:
            raise
    except Exception as e:
        logger.error(f"Erro inesperado no agente '{agent.name}': {e}", exc_info=True)
        raise AgentError(f"Erro: Ocorreu uma falha inesperada. Por favor, tente novamente.")

# =======================
# Interface pública 
# =======================
async def get_agent_response(tipo: str, prompt: str, prefixo: str) -> str:
    if tipo not in AGENTES:
        return f"Erro: agente '{tipo}' não encontrado."
    return await rodar_agente(AGENTES[tipo], prompt, session_prefix=prefixo)