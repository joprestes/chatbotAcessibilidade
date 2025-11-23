"""
Módulo de cache para respostas do chatbot
"""

import hashlib
import logging
from typing import Optional, Dict, Any
from cachetools import TTLCache  # type: ignore[import-untyped]

from chatbot_acessibilidade.config import settings
from chatbot_acessibilidade.core.constants import (
    CACHE_MAX_SIZE,
    CACHE_TTL_SECONDS,
    LogMessages,
)

logger = logging.getLogger(__name__)

# Cache global (inicializado quando necessário)
_cache: Optional[TTLCache] = None


def get_cache() -> Optional[TTLCache]:
    """
    Retorna a instância do cache, criando se necessário.

    Returns:
        Instância do TTLCache ou None se cache desabilitado
    """
    global _cache

    if not getattr(settings, "cache_enabled", True):
        return None

    if _cache is None:
        max_size = getattr(settings, "cache_max_size", CACHE_MAX_SIZE)
        ttl = getattr(settings, "cache_ttl_seconds", CACHE_TTL_SECONDS)
        _cache = TTLCache(maxsize=max_size, ttl=ttl)
        logger.info(LogMessages.CACHE_INITIALIZED.format(max_size=max_size, ttl=ttl))

    return _cache


def get_cache_key(pergunta: str) -> str:
    """
    Gera uma chave de cache normalizada a partir da pergunta.

    Args:
        pergunta: Pergunta do usuário

    Returns:
        Hash MD5 da pergunta normalizada
    """
    # Normaliza a pergunta (lowercase, strip, remove espaços extras)
    pergunta_normalizada = " ".join(pergunta.lower().strip().split())
    return hashlib.md5(pergunta_normalizada.encode("utf-8")).hexdigest()


def get_cached_response(pergunta: str) -> Optional[Dict[str, Any]]:
    """
    Busca uma resposta no cache.

    Args:
        pergunta: Pergunta do usuário

    Returns:
        Resposta em cache ou None se não encontrada
    """
    cache = get_cache()
    if cache is None:
        return None

    key = get_cache_key(pergunta)
    resposta = cache.get(key)

    if resposta is not None:
        logger.debug(LogMessages.CACHE_HIT.format(pergunta=pergunta[:50]))
        # Garante que retorna dict[str, Any] ou None
        if isinstance(resposta, dict):
            return resposta
        return None

    logger.debug(LogMessages.CACHE_MISS.format(pergunta=pergunta[:50]))
    return None


def set_cached_response(pergunta: str, resposta: Dict[str, Any]) -> None:
    """
    Armazena uma resposta no cache.

    Args:
        pergunta: Pergunta do usuário
        resposta: Resposta a ser cacheada
    """
    cache = get_cache()
    if cache is None:
        return

    key = get_cache_key(pergunta)
    cache[key] = resposta
    logger.debug(LogMessages.CACHE_CACHED.format(pergunta=pergunta[:50]))


def clear_cache() -> None:
    """
    Limpa todo o cache.
    """
    global _cache
    if _cache is not None:
        _cache.clear()
        logger.info(LogMessages.CACHE_CLEARED)


def get_cache_stats() -> Dict[str, Any]:
    """
    Retorna estatísticas do cache.

    Returns:
        Dicionário com estatísticas do cache
    """
    cache = get_cache()
    if cache is None:
        return {"enabled": False, "size": 0, "max_size": 0, "ttl": 0}

    return {"enabled": True, "size": len(cache), "max_size": cache.maxsize, "ttl": cache.ttl}
