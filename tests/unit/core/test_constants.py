"""
Testes para o módulo de constantes
"""

import pytest

from chatbot_acessibilidade.core.constants import (
    # Timeouts
    DEFAULT_API_TIMEOUT_SECONDS,
    HUGGINGFACE_TIMEOUT_SECONDS,
    FRONTEND_REQUEST_TIMEOUT_MS,
    HTTPX_CONNECT_TIMEOUT_SECONDS,
    # Limites
    MAX_QUESTION_LENGTH,
    MIN_QUESTION_LENGTH,
    MIN_PARAGRAPH_LENGTH,
    # Cache
    CACHE_MAX_SIZE,
    CACHE_TTL_SECONDS,
    STATIC_CACHE_TTL_SECONDS,
    ASSETS_CACHE_TTL_SECONDS,
    # Compressão
    COMPRESSION_MIN_SIZE_BYTES,
    # Tokens
    HUGGINGFACE_MAX_TOKENS,
    # Retry
    MAX_RETRY_ATTEMPTS,
    # Rate Limiting
    DEFAULT_RATE_LIMIT_PER_MINUTE,
    FALLBACK_RATE_LIMIT_PER_MINUTE,
    # Mensagens
    ErrorMessages,
    LogMessages,
    FrontendConstants,
)

pytestmark = pytest.mark.unit


class TestTimeouts:
    """Testes para constantes de timeout"""

    def test_default_api_timeout(self):
        """Verifica que DEFAULT_API_TIMEOUT_SECONDS é um valor válido"""
        assert isinstance(DEFAULT_API_TIMEOUT_SECONDS, int)
        assert DEFAULT_API_TIMEOUT_SECONDS > 0
        assert DEFAULT_API_TIMEOUT_SECONDS == 60

    def test_openrouter_timeout(self):
        """Verifica que HUGGINGFACE_TIMEOUT_SECONDS é um valor válido"""
        assert isinstance(HUGGINGFACE_TIMEOUT_SECONDS, int)
        assert HUGGINGFACE_TIMEOUT_SECONDS > 0
        assert HUGGINGFACE_TIMEOUT_SECONDS == 60

    def test_frontend_timeout(self):
        """Verifica que FRONTEND_REQUEST_TIMEOUT_MS é um valor válido"""
        assert isinstance(FRONTEND_REQUEST_TIMEOUT_MS, int)
        assert FRONTEND_REQUEST_TIMEOUT_MS > 0
        assert FRONTEND_REQUEST_TIMEOUT_MS == 120000

    def test_httpx_connect_timeout(self):
        """Verifica que HTTPX_CONNECT_TIMEOUT_SECONDS é um valor válido"""
        assert isinstance(HTTPX_CONNECT_TIMEOUT_SECONDS, float)
        assert HTTPX_CONNECT_TIMEOUT_SECONDS > 0
        assert HTTPX_CONNECT_TIMEOUT_SECONDS == 10.0


class TestLimits:
    """Testes para constantes de limites"""

    def test_max_question_length(self):
        """Verifica que MAX_QUESTION_LENGTH é um valor válido"""
        assert isinstance(MAX_QUESTION_LENGTH, int)
        assert MAX_QUESTION_LENGTH > 0
        assert MAX_QUESTION_LENGTH == 2000

    def test_min_question_length(self):
        """Verifica que MIN_QUESTION_LENGTH é um valor válido"""
        assert isinstance(MIN_QUESTION_LENGTH, int)
        assert MIN_QUESTION_LENGTH > 0
        assert MIN_QUESTION_LENGTH == 3

    def test_min_paragraph_length(self):
        """Verifica que MIN_PARAGRAPH_LENGTH é um valor válido"""
        assert isinstance(MIN_PARAGRAPH_LENGTH, int)
        assert MIN_PARAGRAPH_LENGTH > 0
        assert MIN_PARAGRAPH_LENGTH == 30

    def test_max_question_greater_than_min(self):
        """Verifica que MAX_QUESTION_LENGTH > MIN_QUESTION_LENGTH"""
        assert MAX_QUESTION_LENGTH > MIN_QUESTION_LENGTH


class TestCache:
    """Testes para constantes de cache"""

    def test_cache_max_size(self):
        """Verifica que CACHE_MAX_SIZE é um valor válido"""
        assert isinstance(CACHE_MAX_SIZE, int)
        assert CACHE_MAX_SIZE > 0
        assert CACHE_MAX_SIZE == 100

    def test_cache_ttl(self):
        """Verifica que CACHE_TTL_SECONDS é um valor válido"""
        assert isinstance(CACHE_TTL_SECONDS, int)
        assert CACHE_TTL_SECONDS > 0
        assert CACHE_TTL_SECONDS == 3600

    def test_static_cache_ttl(self):
        """Verifica que STATIC_CACHE_TTL_SECONDS é um valor válido"""
        assert isinstance(STATIC_CACHE_TTL_SECONDS, int)
        assert STATIC_CACHE_TTL_SECONDS > 0
        assert STATIC_CACHE_TTL_SECONDS == 86400  # 1 dia

    def test_assets_cache_ttl(self):
        """Verifica que ASSETS_CACHE_TTL_SECONDS é um valor válido"""
        assert isinstance(ASSETS_CACHE_TTL_SECONDS, int)
        assert ASSETS_CACHE_TTL_SECONDS > 0
        assert ASSETS_CACHE_TTL_SECONDS == 604800  # 7 dias

    def test_assets_ttl_greater_than_static(self):
        """Verifica que ASSETS_CACHE_TTL_SECONDS > STATIC_CACHE_TTL_SECONDS"""
        assert ASSETS_CACHE_TTL_SECONDS > STATIC_CACHE_TTL_SECONDS


class TestCompression:
    """Testes para constantes de compressão"""

    def test_compression_min_size(self):
        """Verifica que COMPRESSION_MIN_SIZE_BYTES é um valor válido"""
        assert isinstance(COMPRESSION_MIN_SIZE_BYTES, int)
        assert COMPRESSION_MIN_SIZE_BYTES > 0
        assert COMPRESSION_MIN_SIZE_BYTES == 500


class TestTokens:
    """Testes para constantes de tokens"""

    def test_openrouter_max_tokens(self):
        """Verifica que HUGGINGFACE_MAX_TOKENS é um valor válido"""
        assert isinstance(HUGGINGFACE_MAX_TOKENS, int)
        assert HUGGINGFACE_MAX_TOKENS > 0
        assert HUGGINGFACE_MAX_TOKENS == 2000


class TestRetry:
    """Testes para constantes de retry"""

    def test_max_retry_attempts(self):
        """Verifica que MAX_RETRY_ATTEMPTS é um valor válido"""
        assert isinstance(MAX_RETRY_ATTEMPTS, int)
        assert MAX_RETRY_ATTEMPTS > 0
        assert MAX_RETRY_ATTEMPTS == 3


class TestRateLimiting:
    """Testes para constantes de rate limiting"""

    def test_default_rate_limit(self):
        """Verifica que DEFAULT_RATE_LIMIT_PER_MINUTE é um valor válido"""
        assert isinstance(DEFAULT_RATE_LIMIT_PER_MINUTE, int)
        assert DEFAULT_RATE_LIMIT_PER_MINUTE > 0
        assert DEFAULT_RATE_LIMIT_PER_MINUTE == 10

    def test_fallback_rate_limit(self):
        """Verifica que FALLBACK_RATE_LIMIT_PER_MINUTE é um valor válido"""
        assert isinstance(FALLBACK_RATE_LIMIT_PER_MINUTE, int)
        assert FALLBACK_RATE_LIMIT_PER_MINUTE > 0
        assert FALLBACK_RATE_LIMIT_PER_MINUTE == 1000

    def test_fallback_greater_than_default(self):
        """Verifica que FALLBACK_RATE_LIMIT_PER_MINUTE > DEFAULT_RATE_LIMIT_PER_MINUTE"""
        assert FALLBACK_RATE_LIMIT_PER_MINUTE > DEFAULT_RATE_LIMIT_PER_MINUTE


class TestErrorMessages:
    """Testes para mensagens de erro"""

    def test_error_messages_class_exists(self):
        """Verifica que ErrorMessages existe"""
        assert ErrorMessages is not None

    def test_pergunta_vazia(self):
        """Verifica que PERGUNTA_VAZIA está definida"""
        assert hasattr(ErrorMessages, "PERGUNTA_VAZIA")
        assert isinstance(ErrorMessages.PERGUNTA_VAZIA, str)
        assert len(ErrorMessages.PERGUNTA_VAZIA) > 0

    def test_pergunta_muito_curta_format(self):
        """Verifica que PERGUNTA_MUITO_CURTA aceita formatação"""
        msg = ErrorMessages.PERGUNTA_MUITO_CURTA.format(min=5)
        assert "5" in msg

    def test_pergunta_muito_longa_format(self):
        """Verifica que PERGUNTA_MUITO_LONGA aceita formatação"""
        msg = ErrorMessages.PERGUNTA_MUITO_LONGA.format(max=1000)
        assert "1000" in msg

    def test_timeout_gemini_format(self):
        """Verifica que TIMEOUT_GEMINI aceita formatação"""
        msg = ErrorMessages.TIMEOUT_GEMINI.format(timeout=60)
        assert "60" in msg

    def test_timeout_openrouter_format(self):
        """Verifica que TIMEOUT_HUGGINGFACE aceita formatação"""
        msg = ErrorMessages.TIMEOUT_HUGGINGFACE.format(timeout=60)
        assert "60" in msg

    def test_rate_limit_exceeded_format(self):
        """Verifica que RATE_LIMIT_EXCEEDED aceita formatação"""
        msg = ErrorMessages.RATE_LIMIT_EXCEEDED.format(provider="Google Gemini")
        assert "Google Gemini" in msg

    def test_model_unavailable_openrouter_format(self):
        """Verifica que MODEL_UNAVAILABLE_HUGGINGFACE aceita formatação"""
        msg = ErrorMessages.MODEL_UNAVAILABLE_HUGGINGFACE.format(model="test-model")
        assert "test-model" in msg

    def test_fallback_disabled_format(self):
        """Verifica que FALLBACK_DISABLED aceita formatação"""
        msg = ErrorMessages.FALLBACK_DISABLED.format(error="test error")
        assert "test error" in msg

    def test_agent_error_initial_format(self):
        """Verifica que AGENT_ERROR_INITIAL aceita formatação"""
        msg = ErrorMessages.AGENT_ERROR_INITIAL.format(error="test error")
        assert "test error" in msg

    def test_agent_error_generic_format(self):
        """Verifica que AGENT_ERROR_GENERIC aceita formatação"""
        msg = ErrorMessages.AGENT_ERROR_GENERIC.format(details="test details")
        assert "test details" in msg

    def test_validation_error_generic_format(self):
        """Verifica que VALIDATION_ERROR_GENERIC aceita formatação"""
        msg = ErrorMessages.VALIDATION_ERROR_GENERIC.format(error="test error")
        assert "test error" in msg

    def test_api_error_openrouter_communication_format(self):
        """Verifica que API_ERROR_HUGGINGFACE_COMMUNICATION aceita formatação"""
        msg = ErrorMessages.API_ERROR_HUGGINGFACE_COMMUNICATION.format(status_code=500)
        assert "500" in msg


class TestLogMessages:
    """Testes para mensagens de log"""

    def test_log_messages_class_exists(self):
        """Verifica que LogMessages existe"""
        assert LogMessages is not None

    def test_retry_attempt_format(self):
        """Verifica que RETRY_ATTEMPT aceita formatação"""
        msg = LogMessages.RETRY_ATTEMPT.format(attempt=1, max=3, error="test")
        assert "1" in msg
        assert "3" in msg
        assert "test" in msg

    def test_cache_hit_format(self):
        """Verifica que CACHE_HIT aceita formatação"""
        msg = LogMessages.CACHE_HIT.format(pergunta="test")
        assert "test" in msg

    def test_cache_miss_format(self):
        """Verifica que CACHE_MISS aceita formatação"""
        msg = LogMessages.CACHE_MISS.format(pergunta="test")
        assert "test" in msg

    def test_cache_cached_format(self):
        """Verifica que CACHE_CACHED aceita formatação"""
        msg = LogMessages.CACHE_CACHED.format(pergunta="test")
        assert "test" in msg

    def test_timeout_gemini_format(self):
        """Verifica que TIMEOUT_GEMINI aceita formatação"""
        msg = LogMessages.TIMEOUT_GEMINI.format(timeout=60)
        assert "60" in msg

    def test_timeout_openrouter_format(self):
        """Verifica que TIMEOUT_HUGGINGFACE aceita formatação"""
        msg = LogMessages.TIMEOUT_HUGGINGFACE.format(model="test", timeout=60)
        assert "test" in msg
        assert "60" in msg

    def test_cache_initialized_format(self):
        """Verifica que CACHE_INITIALIZED aceita formatação"""
        msg = LogMessages.CACHE_INITIALIZED.format(max_size=100, ttl=3600)
        assert "100" in msg
        assert "3600" in msg

    def test_cache_truncated_warning_format(self):
        """Verifica que CACHE_TRUNCATED_WARNING aceita formatação"""
        msg = LogMessages.CACHE_TRUNCATED_WARNING.format(max_length=1000)
        assert "1000" in msg

    def test_validation_suspicious_pattern_format(self):
        """Verifica que VALIDATION_SUSPICIOUS_PATTERN aceita formatação"""
        msg = LogMessages.VALIDATION_SUSPICIOUS_PATTERN.format(reason="test")
        assert "test" in msg

    def test_validation_injection_patterns_format(self):
        """Verifica que VALIDATION_INJECTION_PATTERNS aceita formatação"""
        msg = LogMessages.VALIDATION_INJECTION_PATTERNS.format(patterns="test")
        assert "test" in msg

    def test_api_error_gemini_communication_format(self):
        """Verifica que API_ERROR_GEMINI_COMMUNICATION aceita formatação"""
        msg = LogMessages.API_ERROR_GEMINI_COMMUNICATION.format(error="test")
        assert "test" in msg

    def test_api_error_openrouter_http_format(self):
        """Verifica que API_ERROR_HUGGINGFACE_HTTP aceita formatação"""
        msg = LogMessages.API_ERROR_HUGGINGFACE_HTTP.format(status_code=500, error="test")
        assert "500" in msg
        assert "test" in msg

    def test_api_error_openrouter_request_format(self):
        """Verifica que API_ERROR_HUGGINGFACE_REQUEST aceita formatação"""
        msg = LogMessages.API_ERROR_HUGGINGFACE_REQUEST.format(error="test")
        assert "test" in msg

    def test_api_error_openrouter_generic_format(self):
        """Verifica que API_ERROR_HUGGINGFACE_GENERIC aceita formatação"""
        msg = LogMessages.API_ERROR_HUGGINGFACE_GENERIC.format(error="test")
        assert "test" in msg


class TestFrontendConstants:
    """Testes para constantes do frontend"""

    def test_frontend_constants_class_exists(self):
        """Verifica que FrontendConstants existe"""
        assert FrontendConstants is not None

    def test_request_timeout_ms(self):
        """Verifica que REQUEST_TIMEOUT_MS é um valor válido"""
        assert isinstance(FrontendConstants.REQUEST_TIMEOUT_MS, int)
        assert FrontendConstants.REQUEST_TIMEOUT_MS > 0
        assert FrontendConstants.REQUEST_TIMEOUT_MS == 120000

    def test_error_announcement_duration_ms(self):
        """Verifica que ERROR_ANNOUNCEMENT_DURATION_MS é um valor válido"""
        assert isinstance(FrontendConstants.ERROR_ANNOUNCEMENT_DURATION_MS, int)
        assert FrontendConstants.ERROR_ANNOUNCEMENT_DURATION_MS > 0
        assert FrontendConstants.ERROR_ANNOUNCEMENT_DURATION_MS == 1000
