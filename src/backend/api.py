"""
API FastAPI para o Chatbot de Acessibilidade Digital
"""

import logging
import os
import time
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import sys

# Adiciona src ao path para imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Carrega .env antes de importar settings
from dotenv import load_dotenv  # noqa: E402

load_dotenv()

from chatbot_acessibilidade.config import settings  # noqa: E402
from backend.middleware import (  # noqa: E402
    SecurityHeadersMiddleware,
    CompressionMiddleware,
    StaticCacheMiddleware,
)

# Garante que GOOGLE_API_KEY está disponível como variável de ambiente
# O Google ADK precisa disso para criar o cliente internamente
if settings.google_api_key and not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = settings.google_api_key
from chatbot_acessibilidade.pipeline import pipeline_acessibilidade  # noqa: E402
from chatbot_acessibilidade.core.exceptions import ValidationError  # noqa: E402
from chatbot_acessibilidade.core.cache import (  # noqa: E402
    get_cached_response,
    set_cached_response,
    get_cache_stats,
)
from chatbot_acessibilidade.core.metrics import (  # noqa: E402
    record_request,
    record_cache_hit,
    record_cache_miss,
    get_metrics,
    MetricsContext,
)
from chatbot_acessibilidade.core.validators import (  # noqa: E402
    sanitize_input,
    validate_content,
    detect_injection_patterns,
)

# Configuração de logging
logging.basicConfig(level=getattr(logging, settings.log_level), format=settings.log_format)
logger = logging.getLogger(__name__)

# Inicializa FastAPI com documentação completa
app = FastAPI(
    title="Chatbot de Acessibilidade Digital API",
    description="""
    ## 🎯 API para Chatbot de Acessibilidade Digital
    
    API REST desenvolvida com FastAPI que fornece respostas inteligentes sobre acessibilidade digital,
    utilizando Google Gemini 2.0 Flash com fallback automático para múltiplos LLMs via OpenRouter.
    
    ### ✨ Funcionalidades
    
    - 💬 **Chat Inteligente**: Respostas completas sobre WCAG, ARIA e acessibilidade
    - 🔄 **Fallback Automático**: Múltiplos LLMs para garantir disponibilidade
    - ⚡ **Cache Inteligente**: Respostas em cache com invalidação semântica
    - 📊 **Métricas**: Coleta de performance e uso
    - 🛡️ **Segurança**: Rate limiting, CORS, validação de entrada
    - ♿ **Acessibilidade**: Interface 100% acessível (WCAG 2.1 AA)
    
    ### 📚 Documentação Interativa
    
    - **Swagger UI**: `/docs` - Interface interativa para testar a API
    - **ReDoc**: `/redoc` - Documentação alternativa em formato ReDoc
    - **OpenAPI JSON**: `/openapi.json` - Especificação OpenAPI 3.0
    
    ### 🔐 Autenticação
    
    Atualmente a API não requer autenticação, mas implementa:
    - Rate limiting por IP (10 requisições/minuto padrão)
    - Validação rigorosa de entrada
    - Sanitização de dados
    
    ### 📖 Exemplos de Uso
    
    Veja a seção de exemplos em cada endpoint para requisições e respostas de exemplo.
    """,
    version="3.7.0",
    contact={
        "name": "Joelma De O. Prestes Ferreira",
        "url": "https://www.linkedin.com/in/joprestes84/",
        "email": "joprestes@hotmail.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    tags_metadata=[
        {
            "name": "Chat",
            "description": "Endpoints relacionados ao chat e processamento de perguntas.",
        },
        {
            "name": "Health",
            "description": "Endpoints de verificação de saúde e status da API.",
        },
        {
            "name": "Config",
            "description": "Endpoints de configuração e métricas.",
        },
        {
            "name": "Frontend",
            "description": "Endpoints para servir arquivos estáticos do frontend.",
        },
    ],
)

# Configura Rate Limiting (sempre inicializa, mas pode estar desabilitado)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
# Handler de rate limit - usa o handler padrão do slowapi
# type: ignore necessário porque slowapi usa tipos específicos que MyPy não reconhece
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

# Middleware de segurança (deve ser adicionado primeiro)
app.add_middleware(SecurityHeadersMiddleware)

# Middleware de cache para assets estáticos (após segurança)
app.add_middleware(StaticCacheMiddleware)

# Middleware de compressão (após cache, antes de CORS)
app.add_middleware(CompressionMiddleware)

# Configura CORS com origens permitidas
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# Middleware de logging
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        logger.info(f"Incoming request: {request.method} {request.url.path}")

        response = await call_next(request)

        process_time = time.time() - start_time
        logger.info(
            f"Request completed: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Time: {process_time:.3f}s"
        )

        return response


app.add_middleware(LoggingMiddleware)


# Modelos Pydantic para validação
class ChatRequest(BaseModel):
    pergunta: str = Field(..., min_length=1, description="Pergunta sobre acessibilidade digital")

    @field_validator("pergunta")
    @classmethod
    def validate_pergunta(cls, v: str) -> str:
        """Valida e sanitiza a pergunta"""
        # Valida tamanho máximo ANTES de sanitizar (para dar erro correto)
        if len(v) > settings.max_question_length:
            raise ValueError(
                f"A pergunta não pode ter mais de {settings.max_question_length} caracteres."
            )

        # Sanitiza entrada (sem truncar, pois já validamos o tamanho)
        v = sanitize_input(v)

        # Valida tamanho mínimo (após sanitização)
        if len(v) < settings.min_question_length:
            raise ValueError(
                f"A pergunta deve ter pelo menos {settings.min_question_length} caracteres."
            )

        # Valida conteúdo (modo não-strict: detecta mas não rejeita)
        is_valid, reason = validate_content(v, strict=False)
        if not is_valid and reason:
            # Loga mas não rejeita em modo não-strict
            from chatbot_acessibilidade.core.constants import LogMessages  # noqa: E402

            logger.warning(LogMessages.VALIDATION_SUSPICIOUS_PATTERN.format(reason=reason))

        # Detecta padrões de injection para logging
        detected = detect_injection_patterns(v)
        if detected:
            logger.warning(
                LogMessages.VALIDATION_INJECTION_PATTERNS.format(patterns=", ".join(detected))
            )

        return v


class ChatResponse(BaseModel):
    resposta: dict


class HealthResponse(BaseModel):
    """
    Modelo de resposta do endpoint de health check.
    
    Attributes:
        status: Status da API ("ok" ou "error")
        message: Mensagem descritiva do status
        cache: Estatísticas do cache (opcional)
    
    Example:
        ```json
        {
            "status": "ok",
            "message": "API funcionando corretamente",
            "cache": {
                "hits": 10,
                "misses": 5,
                "size": 15
            }
        }
        ```
    """
    status: str = Field(..., description="Status da API", examples=["ok"])
    message: str = Field(..., description="Mensagem descritiva", examples=["API funcionando corretamente"])
    cache: Optional[dict] = Field(None, description="Estatísticas do cache", examples=[{"hits": 10, "misses": 5}])
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "message": "API funcionando corretamente",
                "cache": {
                    "hits": 10,
                    "misses": 5,
                    "size": 15,
                }
            }
        }


# Endpoint de saúde
@app.get(
    "/api/config",
    tags=["Config"],
    summary="Configurações do Frontend",
    description="""
    Retorna configurações necessárias para o frontend, como timeouts e durações.
    
    Essas configurações são usadas pelo frontend para:
    - Configurar timeout de requisições
    - Definir duração de anúncios de erro
    - Sincronizar comportamento entre backend e frontend
    """,
    response_description="Configurações do frontend em milissegundos",
)
async def get_config():
    """
    Retorna configurações do frontend.
    
    Returns:
        dict: Dicionário com configurações:
            - request_timeout_ms: Timeout para requisições (padrão: 120000ms)
            - error_announcement_duration_ms: Duração de anúncios de erro (padrão: 5000ms)
    """
    from chatbot_acessibilidade.core.constants import FrontendConstants  # noqa: E402

    return {
        "request_timeout_ms": FrontendConstants.REQUEST_TIMEOUT_MS,
        "error_announcement_duration_ms": FrontendConstants.ERROR_ANNOUNCEMENT_DURATION_MS,
    }


@app.get(
    "/api/metrics",
    tags=["Config"],
    summary="Métricas de Performance",
    description="""
    Retorna métricas de performance e uso da API.
    
    Inclui:
    - Total de requisições
    - Tempo médio de resposta
    - Taxa de cache hit/miss
    - Taxa de fallback para LLMs alternativos
    - Tempo médio por agente
    """,
    response_description="Dicionário com todas as métricas coletadas",
)
async def get_metrics_endpoint():
    """
    Retorna métricas de performance da API.
    
    Returns:
        dict: Métricas incluindo:
            - total_requests: Total de requisições processadas
            - avg_response_time: Tempo médio de resposta (ms)
            - cache_hit_rate: Taxa de acerto do cache (%)
            - fallback_rate: Taxa de uso de fallback (%)
            - agent_times: Tempo médio por agente (ms)
    """
    return get_metrics()


@app.get(
    "/api/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health Check",
    description="""
    Verifica se a API está funcionando corretamente.
    
    Este endpoint é útil para:
    - Monitoramento de saúde da API
    - Verificação de disponibilidade
    - Health checks em load balancers
    - Integração com sistemas de monitoramento
    """,
    response_description="Status da API e estatísticas do cache",
)
async def health_check():
    """
    Verifica se a API está funcionando.
    
    Returns:
        HealthResponse: Status da API com informações do cache:
            - status: "ok" se tudo estiver funcionando
            - message: Mensagem descritiva
            - cache: Estatísticas do cache (hits, misses, size)
    
    Example:
        ```json
        {
            "status": "ok",
            "message": "API funcionando corretamente",
            "cache": {
                "hits": 10,
                "misses": 5,
                "size": 15
            }
        }
        ```
    """
    cache_stats = get_cache_stats()

    return {
        "status": "ok",
        "message": "API do Chatbot de Acessibilidade Digital está funcionando",
        "cache": cache_stats,
    }


# Endpoint principal de chat
from chatbot_acessibilidade.core.constants import (  # noqa: E402
    FALLBACK_RATE_LIMIT_PER_MINUTE,
)

rate_limit_str = (
    f"{settings.rate_limit_per_minute}/minute"
    if settings.rate_limit_enabled
    else f"{FALLBACK_RATE_LIMIT_PER_MINUTE}/minute"
)


@app.post(
    "/api/chat",
    response_model=ChatResponse,
    tags=["Chat"],
    summary="Processar Pergunta",
    description="""
    Processa uma pergunta sobre acessibilidade digital e retorna uma resposta completa e formatada.
    
    ### 🔄 Fluxo de Processamento
    
    1. **Validação**: Valida e sanitiza a entrada
    2. **Cache**: Verifica se a resposta está em cache
    3. **Pipeline**: Processa através de 5 agentes especializados:
       - 🤖 Assistente: Gera resposta inicial
       - ✅ Validador: Valida técnica (WCAG, ARIA)
       - ✍️ Revisor: Simplifica linguagem
       - 🧪 Testador: Sugere testes práticos (paralelo)
       - 📚 Aprofundador: Recomenda materiais (paralelo)
    4. **Cache**: Salva resposta no cache
    5. **Resposta**: Retorna resposta formatada em seções
    
    ### ⚡ Performance
    
    - Respostas em cache: < 50ms
    - Respostas novas: 5-30s (dependendo do LLM)
    - Fallback automático se LLM principal falhar
    
    ### 🛡️ Segurança
    
    - Rate limiting: 10 requisições/minuto por IP (configurável)
    - Validação rigorosa de entrada
    - Sanitização de caracteres de controle
    - Detecção de padrões de injeção
    
    ### 📝 Formato da Resposta
    
    A resposta é um dicionário com seções organizadas:
    - 📘 **Introdução**: Visão geral do tema
    - 🔍 **Conceitos Essenciais**: Conceitos importantes
    - 🧪 **Como Testar na Prática**: Sugestões de testes
    - 📚 **Quer se Aprofundar?**: Materiais de estudo
    """,
    response_description="Resposta formatada em seções organizadas",
    responses={
        200: {
            "description": "Resposta gerada com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "resposta": {
                            "📘 **Introdução**": "Olá! Vamos entender juntos...",
                            "🔍 **Conceitos Essenciais**": "WCAG é um conjunto de diretrizes...",
                        }
                    }
                }
            },
        },
        400: {
            "description": "Erro de validação (pergunta muito curta/longa ou inválida)",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Pergunta deve ter entre 3 e 2000 caracteres"
                    }
                }
            },
        },
        429: {
            "description": "Rate limit excedido (muitas requisições)",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Rate limit exceeded: 10 per 1 minute"
                    }
                }
            },
        },
        500: {
            "description": "Erro interno do servidor",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Erro ao processar pergunta"
                    }
                }
            },
        },
    },
)
@limiter.limit(rate_limit_str)
async def chat(request: Request, chat_request: ChatRequest):
    """
    Processa uma pergunta sobre acessibilidade digital.
    
    Args:
        request: Objeto Request do FastAPI (usado para rate limiting)
        chat_request: Dados da requisição contendo a pergunta
    
    Returns:
        ChatResponse: Resposta formatada em seções organizadas
    
    Raises:
        HTTPException: 
            - 400: Erro de validação
            - 429: Rate limit excedido
            - 500: Erro interno
    
    Example Request:
        ```json
        {
            "pergunta": "Como testar contraste de cores em um site?"
        }
        ```
    
    Example Response:
        ```json
        {
            "resposta": {
                "📘 **Introdução**": "Testar contraste é essencial...",
                "🔍 **Conceitos Essenciais**": "WCAG 2.1 define...",
                "🧪 **Como Testar na Prática**": "1. Use ferramentas como WAVE...",
            }
        }
        ```
    """
    record_request()
    logger.info(f"Processando pergunta: {chat_request.pergunta[:50]}...")

    try:
        # Verifica cache antes de processar
        resposta_dict = get_cached_response(chat_request.pergunta)

        if resposta_dict is not None:
            record_cache_hit()
            logger.info("Resposta retornada do cache")
            return ChatResponse(resposta=resposta_dict)

        record_cache_miss()

        # Chama o pipeline assíncrono com métricas
        with MetricsContext():
            resposta_dict = await pipeline_acessibilidade(chat_request.pergunta)

        # Salva no cache apenas se não houver erro
        if not (isinstance(resposta_dict, dict) and "erro" in resposta_dict):
            set_cached_response(chat_request.pergunta, resposta_dict)

        # Verifica se houve erro no pipeline
        if isinstance(resposta_dict, dict) and "erro" in resposta_dict:
            logger.error(f"Erro no pipeline: {resposta_dict['erro']}")
            raise HTTPException(status_code=500, detail=resposta_dict["erro"])

        logger.info("Resposta gerada com sucesso")
        return ChatResponse(resposta=resposta_dict)

    except ValidationError as e:
        logger.warning(f"Erro de validação: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        # Re-raise HTTPExceptions
        raise
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
        from chatbot_acessibilidade.core.constants import ErrorMessages  # noqa: E402

        raise HTTPException(
            status_code=500,
            detail=ErrorMessages.API_ERROR_GENERIC,
        )


# Servir arquivos estáticos do frontend e assets
# Caminhos relativos à raiz do projeto
project_root = Path(__file__).parent.parent.parent
frontend_path = project_root / "frontend"
static_path = project_root / "static"

if frontend_path.exists():
    # Serve arquivos do frontend (CSS, JS) em /static
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

    # Serve index.html na raiz
    @app.get("/")
    async def read_root():
        """Serve a página principal do frontend"""
        return FileResponse(str(frontend_path / "index.html"))


static_images_path = static_path / "images"
if static_images_path.exists():
    # Serve assets (imagens) em /assets
    app.mount("/assets", StaticFiles(directory=str(static_images_path)), name="assets")
