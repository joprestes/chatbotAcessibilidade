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
from chatbot_acessibilidade.core.validators import (  # noqa: E402
    sanitize_input,
    validate_content,
    detect_injection_patterns,
)

# Configuração de logging
logging.basicConfig(level=getattr(logging, settings.log_level), format=settings.log_format)
logger = logging.getLogger(__name__)

# Inicializa FastAPI
app = FastAPI(
    title="Chatbot de Acessibilidade Digital API",
    description="API para o chatbot de acessibilidade digital usando Gemini 2.0 Flash",
    version="1.0.0",
)

# Configura Rate Limiting (sempre inicializa, mas pode estar desabilitado)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
# Handler de rate limit - usa o handler padrão do slowapi
# type: ignore necessário porque slowapi usa tipos específicos que MyPy não reconhece
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

# Middleware de segurança (deve ser adicionado primeiro)
app.add_middleware(SecurityHeadersMiddleware)

# Middleware de compressão (após segurança, antes de CORS)
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
            logger.warning(f"Padrão suspeito detectado na pergunta: {reason}")

        # Detecta padrões de injection para logging
        detected = detect_injection_patterns(v)
        if detected:
            logger.warning(f"Padrões suspeitos detectados: {', '.join(detected)}")

        return v

        if len(v) > settings.max_question_length:
            raise ValueError(
                f"A pergunta não pode ter mais de {settings.max_question_length} caracteres."
            )

        # Sanitização básica - remove caracteres de controle
        v = "".join(char for char in v if ord(char) >= 32 or char in "\n\t")

        return v


class ChatResponse(BaseModel):
    resposta: dict


class HealthResponse(BaseModel):
    status: str
    message: str
    cache: Optional[dict] = None


# Endpoint de saúde
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Verifica se a API está funcionando"""
    cache_stats = get_cache_stats()

    return {
        "status": "ok",
        "message": "API do Chatbot de Acessibilidade Digital está funcionando",
        "cache": cache_stats,
    }


# Endpoint principal de chat
rate_limit_str = (
    f"{settings.rate_limit_per_minute}/minute" if settings.rate_limit_enabled else "1000/minute"
)


@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit(rate_limit_str)
async def chat(request: Request, chat_request: ChatRequest):
    """
    Processa uma pergunta sobre acessibilidade digital e retorna a resposta formatada.

    - **pergunta**: Pergunta sobre acessibilidade digital (3-2000 caracteres)

    Retorna um dicionário com as seções formatadas da resposta.
    """
    logger.info(f"Processando pergunta: {chat_request.pergunta[:50]}...")

    try:
        # Verifica cache antes de processar
        resposta_dict = get_cached_response(chat_request.pergunta)

        if resposta_dict is not None:
            logger.info("Resposta retornada do cache")
            return ChatResponse(resposta=resposta_dict)

        # Chama o pipeline assíncrono
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
        raise HTTPException(
            status_code=500,
            detail="❌ Ocorreu um erro inesperado ao processar sua pergunta. Por favor, tente novamente.",
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
