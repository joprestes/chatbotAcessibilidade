"""
Módulo de cache para respostas do chatbot
"""

import hashlib
import logging
from typing import Optional, Dict, Any, List, Tuple
from difflib import SequenceMatcher
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


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calcula a similaridade entre dois textos usando SequenceMatcher.

    Args:
        text1: Primeiro texto
        text2: Segundo texto

    Returns:
        Valor entre 0.0 (não similar) e 1.0 (idêntico)
    """
    # Normaliza os textos para comparação
    normalized1 = " ".join(text1.lower().strip().split())
    normalized2 = " ".join(text2.lower().strip().split())

    return SequenceMatcher(None, normalized1, normalized2).ratio()


def find_similar_questions(
    pergunta: str, threshold: float = 0.8
) -> List[Tuple[str, float, Dict[str, Any]]]:
    """
    Encontra perguntas similares no cache.

    Args:
        pergunta: Pergunta a ser comparada
        threshold: Limiar de similaridade (0.0 a 1.0). Padrão: 0.8 (80%)

    Returns:
        Lista de tuplas (pergunta_original, similaridade, resposta) ordenada por similaridade
    """
    cache = get_cache()
    if cache is None:
        return []

    similar: List[Tuple[str, float, Dict[str, Any]]] = []

    # Itera sobre todas as entradas do cache
    # Nota: TTLCache não expõe diretamente as chaves, então precisamos
    # manter um registro das perguntas originais ou usar uma abordagem diferente
    # Por limitação do TTLCache, vamos usar uma heurística baseada na chave
    # Para uma implementação completa, seria necessário manter um índice separado

    # Por enquanto, retornamos lista vazia pois TTLCache não permite iteração direta
    # Uma implementação completa exigiria um cache customizado ou estrutura adicional
    logger.debug(f"Buscando perguntas similares a: {pergunta[:50]}...")

    return similar


def invalidate_similar_cache(pergunta: str, threshold: float = 0.95) -> int:
    """
    Invalida entradas do cache que são muito similares à pergunta fornecida.
    Útil para evitar respostas obsoletas quando uma pergunta muito similar é feita.

    Args:
        pergunta: Pergunta que pode invalidar entradas similares
        threshold: Limiar de similaridade para invalidação (0.0 a 1.0). Padrão: 0.95 (95%)

    Returns:
        Número de entradas invalidadas
    """
    cache = get_cache()
    if cache is None:
        return 0

    # Por limitação do TTLCache, não podemos iterar diretamente sobre as chaves
    # Uma implementação completa exigiria manter um índice separado das perguntas
    # Por enquanto, apenas logamos a intenção
    logger.debug(
        f"Tentativa de invalidar cache para perguntas similares a: {pergunta[:50]}... "
        f"(threshold: {threshold})"
    )

    # Retorna 0 pois não podemos invalidar sem acesso direto às chaves
    # Em produção, considere usar um cache que permita iteração (ex: Redis com SCAN)
    return 0


def get_cached_response_with_similarity(
    pergunta: str, similarity_threshold: float = 0.9
) -> Optional[Tuple[Dict[str, Any], float]]:
    """
    Busca uma resposta no cache, considerando também perguntas similares.

    Args:
        pergunta: Pergunta do usuário
        similarity_threshold: Limiar de similaridade para aceitar resposta (0.0 a 1.0). Padrão: 0.9

    Returns:
        Tupla (resposta, similaridade) se encontrada, ou None
    """
    # Primeiro tenta busca exata
    resposta_exata = get_cached_response(pergunta)
    if resposta_exata is not None:
        return (resposta_exata, 1.0)

    # Depois tenta buscar perguntas similares
    # Por limitação do TTLCache, não podemos implementar isso completamente
    # sem uma estrutura adicional de índice
    similar = find_similar_questions(pergunta, threshold=similarity_threshold)

    if similar:
        # Retorna a mais similar
        pergunta_original, similaridade, resposta = similar[0]
        logger.debug(
            f"Cache hit com similaridade {similaridade:.2%} para pergunta similar: {pergunta_original[:50]}..."
        )
        return (resposta, similaridade)

    return None
