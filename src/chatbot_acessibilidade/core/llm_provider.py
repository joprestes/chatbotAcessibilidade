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
from chatbot_acessibilidade.core.constants import (
    HUGGINGFACE_MAX_TOKENS,
    ErrorMessages,
    LogMessages,
)
from chatbot_acessibilidade.core.metrics import record_fallback  # noqa: E402

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Enum para identificar o provedor de LLM"""

    GOOGLE_GEMINI = "google_gemini"
    HUGGINGFACE = "huggingface"


class LLMClient(ABC):
    """Interface base para clientes de LLM"""

    @abstractmethod
    async def generate(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Gera uma resposta para o prompt fornecido.

        Args:
            prompt: Texto do prompt
            model: Nome do modelo (opcional, usado principalmente para Hugging Face)

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
            # Usa a API key das configurações
            api_key = settings.google_api_key
            if not api_key:
                logger.error(LogMessages.CONFIG_MISSING_API_KEY)
                raise ValueError("GOOGLE_API_KEY não configurada")
            logger.debug("Inicializando genai.Client...")
            try:
                self._genai_client = genai.Client(api_key=api_key)
                logger.info("genai.Client inicializado com sucesso")
            except Exception as e:
                logger.error(LogMessages.CONFIG_GENAI_INIT_ERROR.format(error=e))
                raise
        return self._genai_client

    async def generate(self, prompt: str, model: Optional[str] = None) -> str:
        """Gera resposta usando Google Gemini"""
        logger.debug("Usando Google Gemini para gerar resposta")

        # Garante que o cliente está inicializado
        self._get_genai_client()

        session_service = InMemorySessionService()
        # O app_name deve ser "agents" quando o agente é carregado do pacote google.adk.agents
        # Isso evita o erro "App name mismatch detected"
        app_name = "agents"
        runner = Runner(agent=self.agent, app_name=app_name, session_service=session_service)
        import os

        session_id = f"gemini_{os.urandom(4).hex()}"

        try:
            await session_service.create_session(
                user_id="user", session_id=session_id, app_name=app_name
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
                logger.error(
                    LogMessages.TIMEOUT_GEMINI.format(timeout=settings.api_timeout_seconds)
                )
                raise APIError(
                    ErrorMessages.TIMEOUT_GEMINI.format(timeout=settings.api_timeout_seconds)
                )

            # Verifica se a resposta recebida é válida
            if not final_response_content or not final_response_content.parts:
                logger.warning("Resposta vazia do Gemini")
                raise APIError(ErrorMessages.API_ERROR_EMPTY_RESPONSE)

            # Verifica se foi bloqueado por segurança
            primeira_parte = final_response_content.parts[0]
            if (
                hasattr(primeira_parte, "finish_reason")
                and primeira_parte.finish_reason == types.FinishReason.SAFETY
            ):
                logger.warning("Pergunta bloqueada por segurança no Gemini")
                raise APIError(ErrorMessages.API_ERROR_SAFETY_BLOCK)

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
                ErrorMessages.TIMEOUT_GEMINI.format(timeout=settings.api_timeout_seconds)
            )
        except google_exceptions.ResourceExhausted:
            logger.error(LogMessages.API_ERROR_GEMINI_RATE_LIMIT)
            raise QuotaExhaustedError(
                ErrorMessages.RATE_LIMIT_EXCEEDED.format(provider="Google Gemini")
            )
        except google_exceptions.PermissionDenied:
            logger.error(LogMessages.API_ERROR_GEMINI_AUTH)
            raise APIError(ErrorMessages.API_ERROR_SERVER_CONFIG)
        except google_exceptions.GoogleAPICallError as e:
            error_str = str(e).lower()
            if "503" in error_str or "overloaded" in error_str:
                logger.warning(f"API sobrecarregada no Gemini: {e}")
                raise ModelUnavailableError(ErrorMessages.MODEL_UNAVAILABLE_GEMINI)
            logger.error(LogMessages.API_ERROR_GEMINI_COMMUNICATION.format(error=e))
            raise APIError(ErrorMessages.API_ERROR_COMMUNICATION)
        except APIError:
            # Re-raise APIError para que seja propagado corretamente
            raise
        except Exception as e:
            logger.error(f"Erro inesperado no Gemini: {e}", exc_info=True)
            # Loga o erro completo para debug
            import traceback

            logger.error(f"Traceback completo: {traceback.format_exc()}")
            raise AgentError(f"Erro: Ocorreu uma falha inesperada. Detalhes: {str(e)}")

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


class HuggingFaceClient(LLMClient):
    """Cliente para Hugging Face Inference API"""

    BASE_URL = "https://api-inference.huggingface.co/models"

    def __init__(self):
        """Inicializa o cliente Hugging Face"""
        if not settings.huggingface_api_key:
            raise ValueError("HUGGINGFACE_API_KEY não configurada")
        self.api_key = settings.huggingface_api_key
        self.timeout = settings.huggingface_timeout_seconds
        self._client: Optional[httpx.AsyncClient] = None

    def _get_client(self) -> httpx.AsyncClient:
        """Inicializa o cliente HTTP de forma lazy"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout, connect=10.0),
                headers=(
                    {
                        "Authorization": f"Bearer {self.api_key}",
                    }
                    if self.api_key
                    else {}
                ),
            )
        return self._client

    async def generate(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Gera resposta usando Hugging Face.

        Args:
            prompt: Texto do prompt
            model: Nome do modelo Hugging Face (obrigatório)

        Returns:
            Resposta gerada como string
        """
        if not model:
            raise ValueError("Modelo deve ser especificado para Hugging Face")

        logger.debug(f"Usando Hugging Face com modelo '{model}' para gerar resposta")

        client = self._get_client()

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": HUGGINGFACE_MAX_TOKENS,
        }

        try:
            response = await asyncio.wait_for(
                client.post(f"{self.BASE_URL}/{model}", json=payload), timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()

            # Extrai a resposta
            if "choices" not in data or not data["choices"]:
                raise APIError("Resposta inválida do Hugging Face: sem choices")

            choice = data["choices"][0]
            if "message" not in choice or "content" not in choice["message"]:
                raise APIError("Resposta inválida do Hugging Face: sem content")

            content = choice["message"]["content"]
            if not isinstance(content, str):
                raise APIError("Resposta inválida do Hugging Face: content não é string")
            logger.debug(f"Hugging Face modelo '{model}' executado com sucesso")
            return str(content.strip())

        except asyncio.TimeoutError:
            logger.error(f"Timeout ao executar Hugging Face modelo '{model}' após {self.timeout}s")
            raise APIError(
                f"Timeout: A requisição ao Hugging Face demorou mais de {self.timeout} segundos."
            )
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            if status_code == 429:
                logger.error(LogMessages.API_ERROR_HUGGINGFACE_RATE_LIMIT.format(model=model))
                raise QuotaExhaustedError(
                    ErrorMessages.RATE_LIMIT_EXCEEDED.format(provider=f"modelo {model}")
                )
            elif status_code == 503:
                logger.warning(f"Modelo '{model}' indisponível no Hugging Face")
                raise ModelUnavailableError(
                    ErrorMessages.MODEL_UNAVAILABLE_HUGGINGFACE.format(model=model)
                )
            elif status_code == 401 or status_code == 403:
                logger.error(LogMessages.API_ERROR_HUGGINGFACE_AUTH)
                raise APIError(ErrorMessages.API_ERROR_HUGGINGFACE_INVALID_KEY)
            else:
                logger.error(
                    LogMessages.API_ERROR_HUGGINGFACE_HTTP.format(status_code=status_code, error=e)
                )
                raise APIError(
                    ErrorMessages.API_ERROR_HUGGINGFACE_COMMUNICATION.format(
                        status_code=status_code
                    )
                )
        except httpx.RequestError as e:
            logger.error(LogMessages.API_ERROR_HUGGINGFACE_REQUEST.format(error=e))
            raise APIError(ErrorMessages.API_ERROR_HUGGINGFACE_CONNECTION)
        except Exception as e:
            logger.error(LogMessages.API_ERROR_HUGGINGFACE_GENERIC.format(error=e), exc_info=True)
            raise APIError(ErrorMessages.API_ERROR_HUGGINGFACE_GENERIC)

    def should_fallback(self, exception: Exception) -> bool:
        """Determina se deve acionar fallback para outro modelo"""
        if isinstance(exception, QuotaExhaustedError):
            return True
        if isinstance(exception, ModelUnavailableError):
            return True
        return False

    def get_provider_name(self) -> str:
        return "HuggingFace"


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
        fallback_clients: Lista de clientes de fallback (Hugging Face)
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

        # Registra que fallback será usado
        record_fallback()

        # Tenta cada cliente de fallback com seus modelos
        for client in fallback_clients:
            if isinstance(client, HuggingFaceClient) and fallback_models:
                # Para Hugging Face, tenta cada modelo
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
