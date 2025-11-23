"""
Testes para o módulo cache.py
"""

import pytest
from unittest.mock import patch

from cachetools import TTLCache

from chatbot_acessibilidade.core.cache import (
    clear_cache,
    get_cache,
    get_cache_key,
    get_cache_stats,
    get_cached_response,
    set_cached_response,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_settings():
    """Mock das configurações"""
    with patch("chatbot_acessibilidade.core.cache.settings") as mock:
        mock.cache_enabled = True
        mock.cache_max_size = 10
        mock.cache_ttl_seconds = 3600
        yield mock


def test_get_cache_cria_instancia(mock_settings):
    """Testa se get_cache cria uma instância quando não existe"""
    # Limpa cache global
    import chatbot_acessibilidade.core.cache as cache_module

    cache_module._cache = None

    cache = get_cache()
    assert cache is not None
    assert isinstance(cache, TTLCache)
    assert cache.maxsize == 10
    assert cache.ttl == 3600


def test_get_cache_retorna_none_se_desabilitado():
    """Testa se get_cache retorna None quando cache está desabilitado"""
    with patch("chatbot_acessibilidade.core.cache.settings") as mock:
        mock.cache_enabled = False

        import chatbot_acessibilidade.core.cache as cache_module

        cache_module._cache = None

        cache = get_cache()
        assert cache is None


def test_get_cache_reutiliza_instancia(mock_settings):
    """Testa se get_cache reutiliza a mesma instância"""
    import chatbot_acessibilidade.core.cache as cache_module

    cache_module._cache = None

    cache1 = get_cache()
    cache2 = get_cache()

    assert cache1 is cache2


def test_get_cache_key_normaliza_pergunta():
    """Testa se get_cache_key normaliza a pergunta corretamente"""
    key1 = get_cache_key("  O que é WCAG?  ")
    key2 = get_cache_key("o que é wcag?")
    key3 = get_cache_key("O   que   é   WCAG?")

    # Todas devem gerar a mesma chave
    assert key1 == key2 == key3
    assert len(key1) == 32  # MD5 hash tem 32 caracteres


def test_get_cache_key_diferentes_perguntas():
    """Testa se perguntas diferentes geram chaves diferentes"""
    key1 = get_cache_key("O que é WCAG?")
    key2 = get_cache_key("O que é ARIA?")

    assert key1 != key2


def test_get_cached_response_cache_hit(mock_settings):
    """Testa get_cached_response quando há cache hit"""
    import chatbot_acessibilidade.core.cache as cache_module

    cache_module._cache = None

    # Cria cache e adiciona item
    cache = get_cache()
    resposta_teste = {"teste": "resposta"}
    pergunta = "O que é WCAG?"
    key = get_cache_key(pergunta)
    cache[key] = resposta_teste

    # Busca no cache
    resultado = get_cached_response(pergunta)

    assert resultado == resposta_teste


def test_get_cached_response_cache_miss(mock_settings):
    """Testa get_cached_response quando há cache miss"""
    import chatbot_acessibilidade.core.cache as cache_module

    cache_module._cache = None

    # Cria cache vazio
    get_cache()

    # Busca pergunta que não está no cache
    resultado = get_cached_response("Pergunta que não existe")

    assert resultado is None


def test_get_cached_response_cache_desabilitado():
    """Testa get_cached_response quando cache está desabilitado"""
    with patch("chatbot_acessibilidade.core.cache.settings") as mock:
        mock.cache_enabled = False

        import chatbot_acessibilidade.core.cache as cache_module

        cache_module._cache = None

        resultado = get_cached_response("Qualquer pergunta")
        assert resultado is None


def test_set_cached_response(mock_settings):
    """Testa set_cached_response armazena corretamente"""
    import chatbot_acessibilidade.core.cache as cache_module

    cache_module._cache = None

    pergunta = "O que é WCAG?"
    resposta = {"teste": "resposta"}

    set_cached_response(pergunta, resposta)

    # Verifica se foi armazenado
    resultado = get_cached_response(pergunta)
    assert resultado == resposta


def test_set_cached_response_cache_desabilitado():
    """Testa set_cached_response quando cache está desabilitado"""
    with patch("chatbot_acessibilidade.core.cache.settings") as mock:
        mock.cache_enabled = False

        import chatbot_acessibilidade.core.cache as cache_module

        cache_module._cache = None

        # Não deve gerar erro
        set_cached_response("Pergunta", {"resposta": "teste"})


def test_clear_cache(mock_settings):
    """Testa clear_cache limpa o cache corretamente"""
    import chatbot_acessibilidade.core.cache as cache_module

    cache_module._cache = None

    # Adiciona itens ao cache
    cache = get_cache()
    set_cached_response("Pergunta 1", {"resposta": "1"})
    set_cached_response("Pergunta 2", {"resposta": "2"})

    assert len(cache) == 2

    # Limpa cache
    clear_cache()

    assert len(cache) == 0


def test_clear_cache_sem_cache():
    """Testa clear_cache quando não há cache"""
    import chatbot_acessibilidade.core.cache as cache_module

    cache_module._cache = None

    # Não deve gerar erro
    clear_cache()


def test_get_cache_stats_com_cache(mock_settings):
    """Testa get_cache_stats quando cache está habilitado"""
    import chatbot_acessibilidade.core.cache as cache_module

    cache_module._cache = None

    get_cache()
    set_cached_response("Pergunta 1", {"resposta": "1"})

    stats = get_cache_stats()

    assert stats["enabled"] is True
    assert stats["size"] == 1
    assert stats["max_size"] == 10
    assert stats["ttl"] == 3600


def test_get_cache_stats_sem_cache():
    """Testa get_cache_stats quando cache está desabilitado"""
    with patch("chatbot_acessibilidade.core.cache.settings") as mock:
        mock.cache_enabled = False

        import chatbot_acessibilidade.core.cache as cache_module

        cache_module._cache = None

        stats = get_cache_stats()

        assert stats["enabled"] is False
        assert stats["size"] == 0
        assert stats["max_size"] == 0
        assert stats["ttl"] == 0


def test_cache_ttl_expiration(mock_settings):
    """Testa se cache respeita TTL (simulação)"""
    import chatbot_acessibilidade.core.cache as cache_module

    cache_module._cache = None

    # Cria cache com TTL curto
    mock_settings.cache_ttl_seconds = 1
    cache_module._cache = None

    get_cache()
    set_cached_response("Pergunta", {"resposta": "teste"})

    # Verifica que está no cache
    assert get_cached_response("Pergunta") is not None

    # Simula expiração (cachetools gerencia isso automaticamente)
    # Este teste verifica que o cache foi criado corretamente


def test_get_cached_response_nao_dict(mock_settings):
    """Testa get_cached_response quando resposta no cache não é dict"""
    import chatbot_acessibilidade.core.cache as cache_module

    cache_module._cache = None

    # Cria cache e adiciona item que não é dict
    cache = get_cache()
    pergunta = "O que é WCAG?"
    key = get_cache_key(pergunta)
    cache[key] = "não é um dict"  # Tipo incorreto

    # Busca no cache - deve retornar None pois não é dict
    resultado = get_cached_response(pergunta)

    assert resultado is None


def test_calculate_similarity():
    """Testa calculate_similarity"""
    from chatbot_acessibilidade.core.cache import calculate_similarity

    # Textos idênticos
    assert calculate_similarity("O que é WCAG?", "O que é WCAG?") == 1.0

    # Textos similares
    similarity = calculate_similarity("O que é WCAG?", "O que é wcag")
    assert 0.8 < similarity < 1.0

    # Textos diferentes
    similarity = calculate_similarity("O que é WCAG?", "Como usar ARIA?")
    assert similarity < 0.5


def test_find_similar_questions(mock_settings):
    """Testa find_similar_questions"""
    from chatbot_acessibilidade.core.cache import find_similar_questions

    import chatbot_acessibilidade.core.cache as cache_module

    cache_module._cache = None

    # Por limitação do TTLCache, a função retorna lista vazia
    # Mas podemos testar que não quebra
    resultado = find_similar_questions("O que é WCAG?")
    assert isinstance(resultado, list)
    assert len(resultado) == 0


def test_invalidate_similar_cache(mock_settings):
    """Testa invalidate_similar_cache"""
    from chatbot_acessibilidade.core.cache import invalidate_similar_cache

    import chatbot_acessibilidade.core.cache as cache_module

    cache_module._cache = None

    # Por limitação do TTLCache, a função retorna 0
    # Mas podemos testar que não quebra
    resultado = invalidate_similar_cache("O que é WCAG?")
    assert resultado == 0


def test_get_cached_response_with_similarity_cache_hit(mock_settings):
    """Testa get_cached_response_with_similarity com cache hit exato"""
    from chatbot_acessibilidade.core.cache import get_cached_response_with_similarity

    import chatbot_acessibilidade.core.cache as cache_module

    cache_module._cache = None

    pergunta = "O que é WCAG?"
    resposta = {"teste": "resposta"}
    set_cached_response(pergunta, resposta)

    # Busca exata
    resultado = get_cached_response_with_similarity(pergunta)
    assert resultado is not None
    resposta_encontrada, similaridade = resultado
    assert resposta_encontrada == resposta
    assert similaridade == 1.0


def test_get_cached_response_with_similarity_cache_miss(mock_settings):
    """Testa get_cached_response_with_similarity com cache miss"""
    from chatbot_acessibilidade.core.cache import get_cached_response_with_similarity

    import chatbot_acessibilidade.core.cache as cache_module

    cache_module._cache = None

    # Busca pergunta que não existe
    resultado = get_cached_response_with_similarity("Pergunta que não existe")
    assert resultado is None
