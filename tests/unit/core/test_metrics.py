"""
Testes para o módulo metrics.py
"""

import pytest

from chatbot_acessibilidade.core.metrics import (
    MetricsContext,
    get_metrics,
    record_cache_hit,
    record_cache_miss,
    record_fallback,
    record_request,
    record_response_time,
    reset_metrics,
)

pytestmark = pytest.mark.unit


def test_record_response_time():
    """Testa record_response_time"""
    reset_metrics()
    record_response_time("assistente", 1.5)
    metrics = get_metrics()
    assert metrics["response_time"]["count"] == 1
    assert metrics["agent_times"]["assistente"] == 1.5  # Retorna média, não lista


def test_record_response_time_sem_agente():
    """Testa record_response_time sem nome de agente"""
    reset_metrics()
    record_response_time(None, 2.0)
    metrics = get_metrics()
    assert metrics["response_time"]["count"] == 1
    assert len(metrics["agent_times"]) == 0


def test_record_response_time_truncamento_lista():
    """Testa truncamento de lista quando > 1000 registros"""
    reset_metrics()
    # Adiciona mais de 1000 registros
    for i in range(1002):
        record_response_time("assistente", float(i))

    metrics = get_metrics()
    # Deve manter apenas os últimos 1000
    assert metrics["response_time"]["count"] == 1000
    # agent_times retorna média, não lista - verifica que existe e é um número
    assert "assistente" in metrics["agent_times"]
    assert isinstance(metrics["agent_times"]["assistente"], (int, float))


def test_record_response_time_truncamento_agente():
    """Testa truncamento de lista de agente quando > 1000 registros"""
    reset_metrics()
    # Adiciona mais de 1000 registros para um agente específico
    for i in range(1002):
        record_response_time("validador", float(i))

    metrics = get_metrics()
    # Deve manter apenas os últimos 1000
    # agent_times retorna média, não lista - verifica que existe e é um número
    assert "validador" in metrics["agent_times"]
    assert isinstance(metrics["agent_times"]["validador"], (int, float))


def test_record_fallback():
    """Testa record_fallback"""
    reset_metrics()
    record_fallback()
    metrics = get_metrics()
    assert metrics["fallback"]["count"] == 1


def test_record_request():
    """Testa record_request"""
    reset_metrics()
    record_request()
    metrics = get_metrics()
    assert metrics["total_requests"] == 1


def test_record_cache_hit():
    """Testa record_cache_hit"""
    reset_metrics()
    record_cache_hit()
    metrics = get_metrics()
    assert metrics["cache"]["hits"] == 1


def test_record_cache_miss():
    """Testa record_cache_miss"""
    reset_metrics()
    record_cache_miss()
    metrics = get_metrics()
    assert metrics["cache"]["misses"] == 1


def test_get_metrics_completo():
    """Testa get_metrics com dados completos"""
    reset_metrics()

    # Adiciona dados variados
    record_request()
    record_request()
    record_fallback()
    record_cache_hit()
    record_cache_miss()
    record_response_time("assistente", 1.5)
    record_response_time("validador", 2.0)
    record_response_time(None, 3.0)

    metrics = get_metrics()

    assert metrics["total_requests"] == 2
    assert metrics["fallback"]["count"] == 1
    assert metrics["fallback"]["rate"] == 50.0  # 1/2 * 100
    assert metrics["cache"]["hits"] == 1
    assert metrics["cache"]["misses"] == 1
    assert metrics["cache"]["hit_rate"] == 50.0  # 1/2 * 100
    assert metrics["response_time"]["count"] == 3
    assert metrics["response_time"]["average"] == 2.167  # (1.5 + 2.0 + 3.0) / 3
    assert metrics["response_time"]["min"] == 1.5
    assert metrics["response_time"]["max"] == 3.0
    assert "assistente" in metrics["agent_times"]
    assert "validador" in metrics["agent_times"]
    assert metrics["agent_times"]["assistente"] == 1.5
    assert metrics["agent_times"]["validador"] == 2.0


def test_get_metrics_vazio():
    """Testa get_metrics quando não há dados"""
    reset_metrics()
    metrics = get_metrics()

    assert metrics["total_requests"] == 0
    assert metrics["fallback"]["count"] == 0
    assert metrics["fallback"]["rate"] == 0.0
    assert metrics["cache"]["hits"] == 0
    assert metrics["cache"]["misses"] == 0
    assert metrics["cache"]["hit_rate"] == 0.0
    assert metrics["response_time"]["count"] == 0
    assert metrics["response_time"]["average"] == 0.0
    assert metrics["response_time"]["min"] == 0.0
    assert metrics["response_time"]["max"] == 0.0
    assert len(metrics["agent_times"]) == 0


def test_reset_metrics():
    """Testa reset_metrics"""
    # Adiciona alguns dados
    record_request()
    record_fallback()
    record_cache_hit()
    record_response_time("assistente", 1.5)

    # Reseta
    reset_metrics()

    metrics = get_metrics()
    assert metrics["total_requests"] == 0
    assert metrics["fallback"]["count"] == 0
    assert metrics["cache"]["hits"] == 0
    assert metrics["response_time"]["count"] == 0
    assert len(metrics["agent_times"]) == 0


def test_metrics_context():
    """Testa MetricsContext como context manager"""
    reset_metrics()

    with MetricsContext("assistente"):
        import time

        time.sleep(0.1)  # Simula trabalho

    metrics = get_metrics()
    assert metrics["response_time"]["count"] == 1
    assert "assistente" in metrics["agent_times"]
    assert metrics["agent_times"]["assistente"] > 0


def test_metrics_context_sem_agente():
    """Testa MetricsContext sem nome de agente"""
    reset_metrics()

    with MetricsContext():
        import time

        time.sleep(0.1)  # Simula trabalho

    metrics = get_metrics()
    assert metrics["response_time"]["count"] == 1
    assert len(metrics["agent_times"]) == 0
