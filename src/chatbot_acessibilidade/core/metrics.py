"""
Módulo de métricas de performance para o chatbot
"""

import time
import logging
from typing import Dict, Any, Optional
from collections import defaultdict
from threading import Lock

logger = logging.getLogger(__name__)

# Armazenamento de métricas (thread-safe)
_metrics_lock = Lock()
_metrics: Dict[str, Any] = {
    "response_times": [],  # Lista de tempos de resposta
    "agent_times": defaultdict(list),  # Tempos por agente
    "fallback_count": 0,  # Número de vezes que fallback foi usado
    "total_requests": 0,  # Total de requisições
    "cache_hits": 0,  # Cache hits
    "cache_misses": 0,  # Cache misses
}

_lock = Lock()


def record_response_time(agent_name: Optional[str], duration: float) -> None:
    """
    Registra o tempo de resposta de um agente.

    Args:
        agent_name: Nome do agente (ou None se não aplicável)
        duration: Duração em segundos
    """
    with _lock:
        _metrics["response_times"].append(duration)
        if agent_name:
            _metrics["agent_times"][agent_name].append(duration)

        # Mantém apenas os últimos 1000 registros para evitar uso excessivo de memória
        if len(_metrics["response_times"]) > 1000:
            _metrics["response_times"] = _metrics["response_times"][-1000:]

        if agent_name and len(_metrics["agent_times"][agent_name]) > 1000:
            _metrics["agent_times"][agent_name] = _metrics["agent_times"][agent_name][-1000:]


def record_fallback() -> None:
    """Registra que um fallback foi usado."""
    with _lock:
        _metrics["fallback_count"] += 1


def record_request() -> None:
    """Registra uma nova requisição."""
    with _lock:
        _metrics["total_requests"] += 1


def record_cache_hit() -> None:
    """Registra um cache hit."""
    with _lock:
        _metrics["cache_hits"] += 1


def record_cache_miss() -> None:
    """Registra um cache miss."""
    with _lock:
        _metrics["cache_misses"] += 1


def get_metrics() -> Dict[str, Any]:
    """
    Retorna todas as métricas coletadas.

    Returns:
        Dicionário com métricas agregadas
    """
    with _lock:
        response_times = _metrics["response_times"]
        total_requests = _metrics["total_requests"]
        fallback_count = _metrics["fallback_count"]
        cache_hits = _metrics["cache_hits"]
        cache_misses = _metrics["cache_misses"]

        # Calcula estatísticas de tempo
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        min_response_time = min(response_times) if response_times else 0.0
        max_response_time = max(response_times) if response_times else 0.0

        # Calcula taxa de fallback
        fallback_rate = (fallback_count / total_requests * 100) if total_requests > 0 else 0.0

        # Calcula taxa de cache
        total_cache_requests = cache_hits + cache_misses
        cache_hit_rate = (
            (cache_hits / total_cache_requests * 100) if total_cache_requests > 0 else 0.0
        )

        # Calcula tempos médios por agente
        agent_avg_times = {}
        for agent_name, times in _metrics["agent_times"].items():
            if times:
                agent_avg_times[agent_name] = sum(times) / len(times)

        return {
            "total_requests": total_requests,
            "response_time": {
                "average": round(avg_response_time, 3),
                "min": round(min_response_time, 3),
                "max": round(max_response_time, 3),
                "count": len(response_times),
            },
            "fallback": {
                "count": fallback_count,
                "rate": round(fallback_rate, 2),
            },
            "cache": {
                "hits": cache_hits,
                "misses": cache_misses,
                "hit_rate": round(cache_hit_rate, 2),
            },
            "agent_times": {
                agent: round(avg_time, 3) for agent, avg_time in agent_avg_times.items()
            },
        }


def reset_metrics() -> None:
    """Reseta todas as métricas."""
    with _lock:
        _metrics["response_times"] = []
        _metrics["agent_times"] = defaultdict(list)
        _metrics["fallback_count"] = 0
        _metrics["total_requests"] = 0
        _metrics["cache_hits"] = 0
        _metrics["cache_misses"] = 0


class MetricsContext:
    """Context manager para medir tempo de execução."""

    def __init__(self, agent_name: Optional[str] = None):
        self.agent_name = agent_name
        self.start_time: Optional[float] = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.time() - self.start_time
            record_response_time(self.agent_name, duration)
        return False
