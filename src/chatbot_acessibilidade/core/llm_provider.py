"""
Gerenciamento de múltiplos provedores de LLM com fallback automático
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, List
import httpx
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google import genai
from google.genai import types
from google.api_core import exceptions as google_exceptions

from chatbot_acessibilidade.config import settings
from chatbot_acessibilidade.core.exceptions import (
    APIError,
    AgentError,
    QuotaExhaustedError,
    ModelUnavailableError,
)

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Enum para identificar o provedor de LLM"""

    GOOGLE_GEMINI = "google_gemini"
    OPENROUTER = "openrouter"


class LLMClient(ABC):
    """Interface base para clientes de LLM"""

    @abstractmethod
    async def generate(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Gera uma resposta para o prompt fornecido.

        Args:
            prompt: Texto do prompt
            model: Nome do modelo (opcional, usado principalmente para OpenRouter)

        Returns:
            Resposta gerada como string

        Raises:
            APIError: Se houver erro na comunicação com a API
            QuotaExhaustedError: Se a quota do modelo foi esgotada
            ModelUnavailableError: Se o modelo não está disponível
        """
        pass

    @abstractmethod
    def should_fallback(self, exception: Exception) -> bool:
        """
        Determina se uma exceção deve acionar fallback para outro provedor.

        Args:
            exception: Exceção que ocorreu

        Returns:
            True se deve acionar fallback, False caso contrário
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Retorna o nome do provedor"""
        pass


class GoogleGeminiClient(LLMClient):
    """Cliente para Google Gemini usando Google ADK"""

    def __init__(self, agent: Agent):
        """
        Inicializa o cliente Gemini.

        Args:
            agent: Agente do Google ADK a ser usado
        """
        self.agent = agent
        self._genai_client: Optional[genai.Client] = None

    def _get_genai_client(self) -> genai.Client:
        """Inicializa o cliente Gemini de forma lazy"""
        if self._genai_client is None:
            logger.info("Inicializando cliente Gemini")
            self._genai_client = genai.Client()
        return self._genai_client

    async def generate(self, prompt: str, model: Optional[str] = None) -> str:
        """Gera resposta usando Google Gemini"""
        logger.debug("Usando Google Gemini para gerar resposta")

        # Garante que o cliente está inicializado
        self._get_genai_client()

        session_service = InMemorySessionService()
        runner = Runner(agent=self.agent, app_name=self.agent.name, session_service=session_service)
        import os

        session_id = f"gemini_{os.urandom(4).hex()}"

        try:
            await session_service.create_session(
                user_id="user", session_id=session_id, app_name=self.agent.name
            )
            content = types.Content(role="user", parts=[types.Part(text=prompt)])

            final_response_content = None

            async def coletar_resposta():
                nonlocal final_response_content
                try:
                    async for evento in runner.run_async(
                        user_id="user", session_id=session_id, new_message=content
                    ):
                        if evento.is_final_response():
                            final_response_content = evento.content
                            break
                except google_exceptions.ResourceExhausted:
                    # Re-raise para ser capturado no bloco externo
                    raise
                except google_exceptions.PermissionDenied:
                    # Re-raise para ser capturado no bloco externo
                    raise
                except google_exceptions.GoogleAPICallError:
                    # Re-raise para ser capturado no bloco externo
                    raise

            # Coleta a resposta final com timeout
            try:
                await asyncio.wait_for(coletar_resposta(), timeout=settings.api_timeout_seconds)
            except asyncio.TimeoutError:
                logger.error(f"Timeout ao executar Gemini após {settings.api_timeout_seconds}s")
                raise APIError(
                    f"Timeout: A requisição demorou mais de {settings.api_timeout_seconds} segundos para responder."
                )

            # Verifica se a resposta recebida é válida
            if not final_response_content or not final_response_content.parts:
                logger.warning("Resposta vazia do Gemini")
                raise APIError("Erro: A resposta da API veio vazia.")

            # Verifica se foi bloqueado por segurança
            primeira_parte = final_response_content.parts[0]
            if (
                hasattr(primeira_parte, "finish_reason")
                and primeira_parte.finish_reason == types.FinishReason.SAFETY
            ):
                logger.warning("Pergunta bloqueada por segurança no Gemini")
                raise APIError(
                    "Erro: Sua pergunta não pôde ser processada devido às diretrizes de segurança."
                )

            # Constrói o resultado
            resultado = "".join(
                (parte.text or "") + "\n"
                for parte in final_response_content.parts
                if getattr(parte, "text", None) is not None
            )
            logger.debug("Google Gemini executado com sucesso")
            return str(resultado.strip())

        except asyncio.TimeoutError:
            raise APIError(
                f"Timeout: A requisição demorou mais de {settings.api_timeout_seconds} segundos."
            )
        except google_exceptions.ResourceExhausted as e:
            logger.error(f"Rate limit excedido no Gemini: {e}")
            raise QuotaExhaustedError("Rate limit excedido no Google Gemini")
        except google_exceptions.PermissionDenied as e:
            logger.error(f"Erro de autenticação no Gemini: {e}")
            raise APIError("Erro: Houve um problema com a configuração do servidor.")
        except google_exceptions.GoogleAPICallError as e:
            error_str = str(e).lower()
            if "503" in error_str or "overloaded" in error_str:
                logger.warning(f"API sobrecarregada no Gemini: {e}")
                raise ModelUnavailableError("API do Google sobrecarregada")
            logger.error(f"Erro de API do Google: {e}")
            raise APIError("Erro: Ocorreu um problema de comunicação com a API.")
        except APIError:
            # Re-raise APIError para que seja propagado corretamente
            raise
        except Exception as e:
            logger.error(f"Erro inesperado no Gemini: {e}", exc_info=True)
            raise AgentError("Erro: Ocorreu uma falha inesperada.")

    def should_fallback(self, exception: Exception) -> bool:
        """Determina se deve acionar fallback"""
        if isinstance(exception, QuotaExhaustedError):
            return True
        if isinstance(exception, ModelUnavailableError):
            return True
        if isinstance(exception, google_exceptions.ResourceExhausted):
            return True
        if isinstance(exception, google_exceptions.GoogleAPICallError):
            error_str = str(exception).lower()
            if "503" in error_str or "overloaded" in error_str:
                return True
        return False

    def get_provider_name(self) -> str:
        return "Google Gemini"


class OpenRouterClient(LLMClient):
    """Cliente para OpenRouter API"""

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self):
        """Inicializa o cliente OpenRouter"""
        if not settings.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY não configurada")
        self.api_key = settings.openrouter_api_key
        self.timeout = settings.openrouter_timeout_seconds
        self._client: Optional[httpx.AsyncClient] = None

    def _get_client(self) -> httpx.AsyncClient:
        """Inicializa o cliente HTTP de forma lazy"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout, connect=10.0),
                headers=(
                    {
                        "Authorization": f"Bearer {self.api_key}",
                        "HTTP-Referer": "https://github.com/chatbotAcessibilidade",
                        "X-Title": "Chatbot Acessibilidade",
                    }
                    if self.api_key
                    else {}
                ),
            )
        return self._client

    async def generate(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Gera resposta usando OpenRouter.

        Args:
            prompt: Texto do prompt
            model: Nome do modelo OpenRouter (obrigatório)

        Returns:
            Resposta gerada como string
        """
        if not model:
            raise ValueError("Modelo deve ser especificado para OpenRouter")

        logger.debug(f"Usando OpenRouter com modelo '{model}' para gerar resposta")

        client = self._get_client()

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        try:
            response = await asyncio.wait_for(
                client.post(f"{self.BASE_URL}/chat/completions", json=payload), timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()

            # Extrai a resposta
            if "choices" not in data or not data["choices"]:
                raise APIError("Resposta inválida do OpenRouter: sem choices")

            choice = data["choices"][0]
            if "message" not in choice or "content" not in choice["message"]:
                raise APIError("Resposta inválida do OpenRouter: sem content")

            content = choice["message"]["content"]
            if not isinstance(content, str):
                raise APIError("Resposta inválida do OpenRouter: content não é string")
            logger.debug(f"OpenRouter modelo '{model}' executado com sucesso")
            return str(content.strip())

        except asyncio.TimeoutError:
            logger.error(f"Timeout ao executar OpenRouter modelo '{model}' após {self.timeout}s")
            raise APIError(
                f"Timeout: A requisição ao OpenRouter demorou mais de {self.timeout} segundos."
            )
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            if status_code == 429:
                logger.error(f"Rate limit excedido no OpenRouter modelo '{model}'")
                raise QuotaExhaustedError(f"Rate limit excedido no modelo {model}")
            elif status_code == 503:
                logger.warning(f"Modelo '{model}' indisponível no OpenRouter")
                raise ModelUnavailableError(f"Modelo {model} indisponível")
            elif status_code == 401 or status_code == 403:
                logger.error("Erro de autenticação no OpenRouter")
                raise APIError("Erro: Chave API do OpenRouter inválida.")
            else:
                logger.error(f"Erro HTTP {status_code} do OpenRouter: {e}")
                raise APIError(
                    f"Erro: Ocorreu um problema de comunicação com o OpenRouter (HTTP {status_code})."
                )
        except httpx.RequestError as e:
            logger.error(f"Erro de requisição ao OpenRouter: {e}")
            raise APIError("Erro: Não foi possível conectar ao OpenRouter.")
        except Exception as e:
            logger.error(f"Erro inesperado no OpenRouter: {e}", exc_info=True)
            raise APIError("Erro: Ocorreu uma falha inesperada ao usar o OpenRouter.")

    def should_fallback(self, exception: Exception) -> bool:
        """Determina se deve acionar fallback para outro modelo"""
        if isinstance(exception, QuotaExhaustedError):
            return True
        if isinstance(exception, ModelUnavailableError):
            return True
        return False

    def get_provider_name(self) -> str:
        return "OpenRouter"


async def generate_with_fallback(
    primary_client: LLMClient,
    prompt: str,
    fallback_clients: Optional[List[LLMClient]] = None,
    fallback_models: Optional[List[str]] = None,
) -> tuple[str, str]:
    """
    Gera resposta com fallback automático.

    Args:
        primary_client: Cliente primário (Google Gemini)
        prompt: Texto do prompt
        fallback_clients: Lista de clientes de fallback (OpenRouter)
        fallback_models: Lista de modelos para usar com fallback clients

    Returns:
        Tupla (resposta, provedor_usado)

    Raises:
        APIError: Se todos os provedores falharem
    """
    # Tenta o provedor primário primeiro
    try:
        logger.info(f"Tentando gerar resposta com {primary_client.get_provider_name()}")
        resposta = await primary_client.generate(prompt)
        logger.info(f"Resposta gerada com sucesso usando {primary_client.get_provider_name()}")
        return resposta, primary_client.get_provider_name()
    except Exception as e:
        if not primary_client.should_fallback(e):
            # Erro que não deve acionar fallback, re-lança
            raise

        logger.warning(
            f"Falha no provedor primário ({primary_client.get_provider_name()}): {e}. "
            f"Acionando fallback..."
        )

        # Se fallback está desabilitado ou não há clientes de fallback, re-lança o erro
        if not settings.fallback_enabled or not fallback_clients:
            raise APIError(f"Erro no provedor primário e fallback desabilitado: {e}")

        # Tenta cada cliente de fallback com seus modelos
        for client in fallback_clients:
            if isinstance(client, OpenRouterClient) and fallback_models:
                # Para OpenRouter, tenta cada modelo
                for model in fallback_models:
                    try:
                        logger.info(
                            f"Tentando fallback com {client.get_provider_name()} modelo '{model}'"
                        )
                        resposta = await client.generate(prompt, model=model)
                        logger.info(
                            f"Fallback bem-sucedido usando {client.get_provider_name()} modelo '{model}'"
                        )
                        return resposta, f"{client.get_provider_name()} ({model})"
                    except Exception as fallback_error:
                        if client.should_fallback(fallback_error):
                            logger.warning(
                                f"Falha no modelo '{model}': {fallback_error}. "
                                f"Tentando próximo modelo..."
                            )
                            continue
                        else:
                            # Erro que não deve acionar fallback, re-lança
                            raise
            else:
                # Para outros clientes, tenta diretamente
                try:
                    logger.info(f"Tentando fallback com {client.get_provider_name()}")
                    resposta = await client.generate(prompt)
                    logger.info(f"Fallback bem-sucedido usando {client.get_provider_name()}")
                    return resposta, client.get_provider_name()
                except Exception as fallback_error:
                    if client.should_fallback(fallback_error):
                        logger.warning(
                            f"Falha no {client.get_provider_name()}: {fallback_error}. "
                            f"Tentando próximo cliente..."
                        )
                        continue
                    else:
                        raise

        # Se chegou aqui, todos os fallbacks falharam
        raise APIError(
            "Todos os provedores e modelos disponíveis falharam. Por favor, tente novamente mais tarde."
        )
