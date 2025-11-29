"""
Gerenciamento de múltiplos provedores de LLM com fallback automático
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, List
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
        self._current_api_key: str = ""
        self._using_secondary_key: bool = False

    def _get_genai_client(self) -> genai.Client:
        """Inicializa o cliente Gemini de forma lazy"""
        if self._genai_client is None:
            logger.info("Inicializando cliente Gemini")
            # Usa a API key primária das configurações
            api_key = settings.google_api_key
            if not api_key:
                logger.error(LogMessages.CONFIG_MISSING_API_KEY)
                raise ValueError("GOOGLE_API_KEY não configurada")

            self._current_api_key = api_key
            self._using_secondary_key = False

            logger.debug("Inicializando genai.Client com chave primária...")
            try:
                self._genai_client = genai.Client(api_key=api_key)
                logger.info("genai.Client inicializado com sucesso (chave primária)")
            except Exception as e:
                logger.error(LogMessages.CONFIG_GENAI_INIT_ERROR.format(error=e))
                raise
        return self._genai_client

    def _switch_to_secondary_key(self) -> bool:
        """
        Tenta trocar para a chave secundária.

        Returns:
            True se conseguiu trocar, False se não há chave secundária
        """
        if not settings.google_api_key_second:
            logger.warning("Chave secundária não configurada, não é possível fazer fallback")
            return False

        if self._using_secondary_key:
            logger.warning("Já está usando a chave secundária, não há mais fallback disponível")
            return False

        logger.info("Trocando para chave secundária do Google Gemini...")
        try:
            self._genai_client = genai.Client(api_key=settings.google_api_key_second)
            self._current_api_key = settings.google_api_key_second
            self._using_secondary_key = True
            logger.info("✅ Chave secundária ativada com sucesso!")
            return True
        except Exception as e:
            logger.error(f"Erro ao trocar para chave secundária: {e}")
            return False

        # Garante que o cliente está inicializado
        self._get_genai_client()

    async def _execute_runner_with_retry(self, prompt: str, session_id: str, app_name: str) -> str:
        """Executa o runner com lógica de retry para coletar resposta"""
        session_service = InMemorySessionService()
        runner = Runner(agent=self.agent, app_name=app_name, session_service=session_service)

        await session_service.create_session(
            user_id="user", session_id=session_id, app_name=app_name
        )
        content = types.Content(role="user", parts=[types.Part(text=prompt)])
        final_response_content = None

        async def coletar_resposta():
            nonlocal final_response_content
            async for evento in runner.run_async(
                user_id="user", session_id=session_id, new_message=content
            ):
                if evento.is_final_response():
                    final_response_content = evento.content
                    break

        # Coleta a resposta final com timeout
        await asyncio.wait_for(coletar_resposta(), timeout=settings.api_timeout_seconds)

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
        return str(resultado.strip())

    async def generate(self, prompt: str, model: Optional[str] = None) -> str:
        """Gera resposta usando Google Gemini"""
        logger.debug("Usando Google Gemini para gerar resposta")

        # Garante que o cliente está inicializado
        self._get_genai_client()

        import os

        session_id = f"gemini_{os.urandom(4).hex()}"
        app_name = "agents"

        try:
            return await self._execute_runner_with_retry(prompt, session_id, app_name)

        except asyncio.TimeoutError:
            raise APIError(
                ErrorMessages.TIMEOUT_GEMINI.format(timeout=settings.api_timeout_seconds)
            )
        except (google_exceptions.ResourceExhausted, google_exceptions.GoogleAPICallError) as e:
            # Verifica se é erro de quota (429 ou ResourceExhausted)
            is_quota_error = isinstance(e, google_exceptions.ResourceExhausted)
            if not is_quota_error and isinstance(e, google_exceptions.GoogleAPICallError):
                error_code = getattr(e, "code", None)
                if error_code == 429 or "RESOURCE_EXHAUSTED" in str(e):
                    is_quota_error = True

            if is_quota_error:
                logger.error(LogMessages.API_ERROR_GEMINI_RATE_LIMIT)

                # Tenta trocar para chave secundária
                if self._switch_to_secondary_key():
                    logger.info("Tentando novamente com chave secundária...")
                    try:
                        # Reinicializa cliente com nova chave (feito no switch) e tenta novamente
                        return await self._execute_runner_with_retry(prompt, session_id, app_name)
                    except Exception as retry_error:
                        logger.error(f"Erro mesmo com chave secundária: {retry_error}")
                        # Se falhar novamente, retorna mensagem de manutenção
                        return str(ErrorMessages.MAINTENANCE_MESSAGE)
                else:
                    # Se não tem chave secundária ou já usou, retorna mensagem de manutenção
                    return str(ErrorMessages.MAINTENANCE_MESSAGE)

            # Outros erros de API
            if isinstance(e, google_exceptions.PermissionDenied):
                logger.error(LogMessages.API_ERROR_GEMINI_AUTH)
                raise APIError(ErrorMessages.API_ERROR_SERVER_CONFIG)

            error_code = getattr(e, "code", None)
            if error_code == 503:
                logger.warning("Modelo indisponível (503)")
                raise ModelUnavailableError(ErrorMessages.MODEL_UNAVAILABLE_GEMINI)

            logger.error(f"Erro na API do Google: {e}")
            raise APIError(f"Erro na API do Google: {str(e)}")

        except APIError:
            # Re-raise APIError para que seja propagado corretamente
            raise
        except Exception as e:
            error_str = str(e).lower()
            logger.error(f"Erro inesperado no Gemini: {e}", exc_info=True)

            # Verifica se é erro de quota em Exception genérica
            if "429" in error_str or "resource_exhausted" in error_str or "quota" in error_str:
                logger.error("Quota esgotada detectada em Exception genérica")

                # Tenta trocar para chave secundária
                if self._switch_to_secondary_key():
                    logger.info("Tentando novamente com chave secundária...")
                    try:
                        return await self._execute_runner_with_retry(prompt, session_id, app_name)
                    except Exception as retry_error:
                        logger.error(f"Erro mesmo com chave secundária: {retry_error}")
                        return str(ErrorMessages.MAINTENANCE_MESSAGE)
                else:
                    return str(ErrorMessages.MAINTENANCE_MESSAGE)

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


class FireworksAIClient(LLMClient):
    """Cliente para Fireworks AI usando API compatível com OpenAI"""

    def __init__(self):
        """Inicializa o cliente Fireworks AI"""
        if not settings.huggingface_api_key:
            raise ValueError("HUGGINGFACE_API_KEY não configurada (usada para Fireworks)")
        self.api_key = settings.huggingface_api_key
        self.timeout = settings.huggingface_timeout_seconds
        self._client = None

    def _get_client(self):
        """Inicializa o cliente OpenAI apontando para Fireworks"""
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.fireworks.ai/inference/v1",
                timeout=self.timeout,
            )
        return self._client

    async def generate(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Gera resposta usando Fireworks AI.

        Args:
            prompt: Texto do prompt
            model: Nome do modelo Fireworks (obrigatório)

        Returns:
            Resposta gerada como string
        """
        if not model:
            raise ValueError("Modelo deve ser especificado para Fireworks AI")

        logger.debug(f"Usando Fireworks AI com modelo '{model}' para gerar resposta")

        client = self._get_client()

        try:
            # Usa chat.completions (formato OpenAI)
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    client.chat.completions.create,
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=HUGGINGFACE_MAX_TOKENS,
                    temperature=0.7,
                ),
                timeout=self.timeout,
            )

            # Extrai a resposta do formato OpenAI
            if not response.choices or len(response.choices) == 0:
                raise APIError("Resposta inválida do Fireworks AI: sem choices")

            content = response.choices[0].message.content
            if not content:
                raise APIError("Resposta inválida do Fireworks AI: content vazio")

            logger.debug(f"Fireworks AI modelo '{model}' executado com sucesso")
            return str(content.strip())

        except asyncio.TimeoutError:
            logger.error(f"Timeout ao executar Fireworks AI modelo '{model}' após {self.timeout}s")
            raise APIError(
                f"Timeout: A requisição ao Fireworks AI demorou mais de {self.timeout} segundos."
            )
        except Exception as e:
            error_str = str(e).lower()

            # Verifica erros específicos
            if "429" in error_str or "rate limit" in error_str:
                logger.error(f"Rate limit no Fireworks AI modelo '{model}'")
                raise QuotaExhaustedError(
                    ErrorMessages.RATE_LIMIT_EXCEEDED.format(
                        provider=f"Fireworks AI modelo {model}"
                    )
                )
            elif "503" in error_str or "unavailable" in error_str or "loading" in error_str:
                logger.warning(f"Modelo '{model}' indisponível no Fireworks AI")
                raise ModelUnavailableError(
                    f"Modelo {model} temporariamente indisponível no Fireworks AI"
                )
            elif "401" in error_str or "403" in error_str or "unauthorized" in error_str:
                logger.error("Erro de autenticação no Fireworks AI")
                raise APIError("API key inválida ou sem permissão no Fireworks AI")
            else:
                logger.error(f"Erro ao chamar Fireworks AI: {e}", exc_info=True)
                raise APIError(f"Erro ao chamar Fireworks AI: {str(e)}")

    def should_fallback(self, exception: Exception) -> bool:
        """Determina se deve acionar fallback para outro modelo"""
        if isinstance(exception, QuotaExhaustedError):
            return True
        if isinstance(exception, ModelUnavailableError):
            return True
        return False

    def get_provider_name(self) -> str:
        return "Fireworks AI"


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
            # Para clientes de fallback, tenta com modelos específicos se fornecidos
            if fallback_models:
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
