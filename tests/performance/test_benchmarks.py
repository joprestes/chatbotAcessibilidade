"""
Testes de Performance com pytest-benchmark

Estes testes medem o desempenho de componentes críticos do sistema
usando pytest-benchmark.

Execução:
    # Executar benchmarks
    pytest tests/performance/ --benchmark-only

    # Executar com comparação
    pytest tests/performance/ --benchmark-autosave

    # Ver histórico
    pytest-benchmark list
    pytest-benchmark compare
"""

import pytest
from unittest.mock import patch


@pytest.mark.performance
def test_pipeline_performance(benchmark):
    """
    Testa performance do pipeline completo de processamento.

    Meta: < 30s para pergunta nova (sem cache)
    """
    from chatbot_acessibilidade.pipeline import pipeline_acessibilidade
    import asyncio

    pergunta = "Como testar contraste de cores em um site?"

    # Mock do LLM para ter resultados consistentes
    with patch("chatbot_acessibilidade.agents.dispatcher.get_agent_response") as mock_agent:
        mock_agent.return_value = "Resposta mockada para benchmark"

        def run_pipeline():
            return asyncio.run(pipeline_acessibilidade(pergunta))

        result = benchmark(run_pipeline)
        assert result is not None


@pytest.mark.performance
def test_cache_performance(benchmark):
    """
    Testa performance do cache (get e set).

    Meta: < 10ms para operações de cache
    """
    from chatbot_acessibilidade.core.cache import (
        get_cached_response,
        set_cached_response,
        clear_cache,
    )

    # Limpa cache antes do teste
    clear_cache()

    pergunta = "Como testar acessibilidade?"
    resposta = {"teste": "resposta"}

    def cache_operations():
        # Set
        set_cached_response(pergunta, resposta)
        # Get
        result = get_cached_response(pergunta)
        return result

    result = benchmark(cache_operations)
    assert result == resposta


@pytest.mark.performance
def test_validation_performance(benchmark):
    """
    Testa performance da validação de entrada.

    Meta: < 1ms para validação
    """
    from chatbot_acessibilidade.core.validators import (
        sanitize_input,
        validate_content,
        detect_injection_patterns,
    )

    pergunta = "Como testar contraste de cores? <script>alert('test')</script>"

    def validation_operations():
        sanitized = sanitize_input(pergunta)
        is_valid, reason = validate_content(sanitized, strict=False)
        patterns = detect_injection_patterns(sanitized)
        return sanitized, is_valid, patterns

    result = benchmark(validation_operations)
    assert result is not None


@pytest.mark.performance
def test_formatter_performance(benchmark):
    """
    Testa performance do formatador de respostas.

    Meta: < 100ms para formatação
    """
    from chatbot_acessibilidade.core.formatter import formatar_resposta_final

    # resposta_agentes removido pois agora usamos args posicionais

    args = ("Resumo...", "Conceitos...", "Testes...", "Aprofundar...", "Dica...")
    result = benchmark(formatar_resposta_final, *args)
    assert isinstance(result, dict)


@pytest.mark.performance
def test_metrics_collection_performance(benchmark):
    """
    Testa performance da coleta de métricas.

    Meta: < 1ms para registrar métrica
    """
    from chatbot_acessibilidade.core.metrics import (
        record_request,
        record_cache_hit,
        record_cache_miss,
        get_metrics,
    )

    def metrics_operations():
        record_request()
        record_cache_hit()
        record_cache_miss()
        return get_metrics()

    result = benchmark(metrics_operations)
    assert result is not None


@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_requests_performance(benchmark):
    """
    Testa performance de múltiplas requisições concorrentes.

    Meta: Processar 10 requisições em < 5s (com mocks)
    """
    from chatbot_acessibilidade.pipeline import pipeline_acessibilidade
    import asyncio

    perguntas = [
        "Como testar contraste?",
        "O que é WCAG?",
        "Como usar ARIA?",
        "Testes de acessibilidade?",
        "Navegação por teclado?",
        "Skip links?",
        "Leitores de tela?",
        "Alt text em imagens?",
        "Formulários acessíveis?",
        "Tabelas acessíveis?",
    ]

    with patch("chatbot_acessibilidade.agents.dispatcher.get_agent_response") as mock_agent:
        mock_agent.return_value = "Resposta mockada"

        async def run_concurrent():
            tasks = [pipeline_acessibilidade(p) for p in perguntas]
            return await asyncio.gather(*tasks)

        # benchmark.pedantic não funciona bem com async, então usamos uma abordagem diferente
        import time

        start = time.time()
        result = await run_concurrent()
        elapsed = time.time() - start

        assert len(result) == 10
        assert elapsed < 5.0, f"Concurrent requests took {elapsed}s, expected < 5s"
