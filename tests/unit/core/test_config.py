"""
Testes para o módulo config.py
"""

import os
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError
from unittest.mock import patch

# Importa após configurar o path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from chatbot_acessibilidade.config import Settings  # noqa: E402

pytestmark = pytest.mark.unit


def test_settings_cria_instancia_com_variaveis_ambiente():
    """Testa se Settings cria instância com variáveis de ambiente"""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_key_123",
            "FALLBACK_ENABLED": "false",
        },
    ):
        settings = Settings()
        assert settings.google_api_key == "test_key_123"
        assert settings.fallback_enabled is False


def test_settings_valores_padrao():
    """Testa valores padrão das configurações"""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_key",
        },
        clear=False,
    ):
        settings = Settings()

        assert settings.cors_origins == ["*"]
        assert settings.rate_limit_enabled is True
        assert settings.rate_limit_per_minute == 10
        assert settings.max_question_length == 2000
        assert settings.min_question_length == 3
        assert settings.api_timeout_seconds == 60
        assert settings.cache_enabled is True
        assert settings.cache_ttl_seconds == 3600
        assert settings.cache_max_size == 100
        assert settings.log_level == "INFO"


def test_settings_parse_cors_origins_asterisco():
    """Testa parse de CORS origins com asterisco"""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_key",
            "CORS_ORIGINS": "*",
        },
    ):
        settings = Settings()
        assert settings.cors_origins == ["*"]


def test_settings_parse_cors_origins_multiplos():
    """Testa parse de CORS origins com múltiplas origens"""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_key",
            "CORS_ORIGINS": "http://localhost:3000,https://example.com",
        },
    ):
        settings = Settings()
        # cors_origins já é uma lista após o parse
        assert len(settings.cors_origins) == 2
        assert "http://localhost:3000" in settings.cors_origins
        assert "https://example.com" in settings.cors_origins


def test_settings_validate_log_level():
    """Testa validação de log_level"""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_key",
            "LOG_LEVEL": "DEBUG",
        },
    ):
        settings = Settings()
        assert settings.log_level == "DEBUG"


def test_settings_validate_log_level_invalido():
    """Testa validação de log_level inválido"""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_key",
            "LOG_LEVEL": "INVALIDO",
        },
    ):
        with pytest.raises(ValidationError):
            Settings()


def test_settings_parse_openrouter_models():
    """Testa parse de modelos OpenRouter"""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_key",
            "OPENROUTER_MODELS": "model1,model2,model3",
        },
    ):
        settings = Settings()
        models_list = settings.openrouter_models_list
        assert len(models_list) == 3
        assert "model1" in models_list
        assert "model2" in models_list
        assert "model3" in models_list


def test_settings_parse_openrouter_models_com_espacos():
    """Testa parse de modelos OpenRouter com espaços"""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_key",
            "OPENROUTER_MODELS": " model1 , model2 , model3 ",
        },
    ):
        settings = Settings()
        models_list = settings.openrouter_models_list
        assert len(models_list) == 3
        assert "model1" in models_list
        assert "model2" in models_list
        assert "model3" in models_list


def test_settings_validate_fallback_config_com_chave():
    """Testa validação de fallback quando habilitado com chave"""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_key",
            "OPENROUTER_API_KEY": "openrouter_key",
            "FALLBACK_ENABLED": "true",
            "OPENROUTER_MODELS": "model1,model2",
        },
    ):
        settings = Settings()
        assert settings.fallback_enabled is True
        assert settings.openrouter_api_key == "openrouter_key"


def test_settings_validate_fallback_config_sem_chave():
    """Testa validação de fallback quando habilitado sem chave"""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_key",
            "FALLBACK_ENABLED": "true",
        },
    ):
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        assert "openrouter_api_key" in str(exc_info.value).lower()


def test_settings_validate_fallback_config_sem_modelos():
    """Testa validação de fallback quando habilitado sem modelos"""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_key",
            "OPENROUTER_API_KEY": "openrouter_key",
            "FALLBACK_ENABLED": "true",
            "OPENROUTER_MODELS": "",
        },
    ):
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        assert "openrouter_models" in str(exc_info.value).lower()


def test_settings_openrouter_models_list_property():
    """Testa propriedade openrouter_models_list"""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_key",
            "OPENROUTER_MODELS": "model1,model2",
        },
    ):
        settings = Settings()
        models_list = settings.openrouter_models_list
        assert isinstance(models_list, list)
        assert len(models_list) == 2


def test_settings_openrouter_models_list_vazio():
    """Testa propriedade openrouter_models_list com string vazia"""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_key",
            "OPENROUTER_MODELS": "",
        },
    ):
        settings = Settings()
        models_list = settings.openrouter_models_list
        assert isinstance(models_list, list)


def test_settings_openrouter_models_list_nao_string():
    """Testa openrouter_models_list quando openrouter_models não é string (linha 111-113)"""
    import os
    from chatbot_acessibilidade.config import Settings

    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_key",
        },
        clear=False,
    ):
        settings = Settings()
        # Simula que openrouter_models já é uma lista (não string)
        # Isso acontece quando o Pydantic já parseou como lista
        # Atribui diretamente para testar o caminho da linha 113
        original_models = settings.openrouter_models
        settings.openrouter_models = ["model1", "model2"]
        # Testa a propriedade quando já é lista (linha 113)
        models_list = settings.openrouter_models_list
        assert isinstance(models_list, list)
        assert models_list == ["model1", "model2"]
        # Restaura
        settings.openrouter_models = original_models


def test_settings_validate_fallback_config_linhas_136_139():
    """Testa validação de fallback quando habilitado mas sem configuração (linhas 136-139)"""
    # Testa o caminho quando fallback_enabled=True mas openrouter_api_key está vazia
    # e openrouter_models também está vazio
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_key",
            "FALLBACK_ENABLED": "true",
            "OPENROUTER_API_KEY": "",
            "OPENROUTER_MODELS": "",
        },
    ):
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        # Deve falhar na validação (linha 119 ou 123)
        error_str = str(exc_info.value).lower()
        assert "openrouter" in error_str or "fallback" in error_str


def test_settings_parse_cors_origins_string_vazia():
    """Testa parse de CORS origins com string vazia"""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_key",
            "CORS_ORIGINS": "",
        },
    ):
        settings = Settings()
        # String vazia deve retornar lista vazia após split e filtro
        assert isinstance(settings.cors_origins, list)
        assert len(settings.cors_origins) == 0


def test_settings_parse_cors_origins_com_espacos():
    """Testa parse de CORS origins com espaços extras"""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_key",
            "CORS_ORIGINS": " http://localhost:3000 , https://example.com ",
        },
    ):
        settings = Settings()
        assert len(settings.cors_origins) == 2
        assert "http://localhost:3000" in settings.cors_origins
        assert "https://example.com" in settings.cors_origins


def test_settings_parse_openrouter_models_string_vazia():
    """Testa parse de modelos OpenRouter com string vazia"""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_key",
            "OPENROUTER_MODELS": "",
        },
    ):
        settings = Settings()
        models_list = settings.openrouter_models_list
        assert isinstance(models_list, list)
        assert len(models_list) == 0


def test_settings_parse_openrouter_models_com_virgulas_multiplas():
    """Testa parse de modelos OpenRouter com múltiplas vírgulas"""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_key",
            "OPENROUTER_MODELS": "model1,,model2, ,model3",
        },
    ):
        settings = Settings()
        models_list = settings.openrouter_models_list
        # Deve filtrar strings vazias
        assert len(models_list) == 3
        assert "model1" in models_list
        assert "model2" in models_list
        assert "model3" in models_list


def test_settings_validate_fallback_config_sem_api_key_detalhado():
    """Testa validação detalhada de fallback sem API key (linha 119)"""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_key",
            "OPENROUTER_API_KEY": "",  # Vazio
            "FALLBACK_ENABLED": "true",
            "OPENROUTER_MODELS": "model1,model2",
        },
    ):
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        error_str = str(exc_info.value).lower()
        assert "openrouter_api_key" in error_str or "fallback_enabled" in error_str


def test_settings_validate_fallback_config_sem_modelos_detalhado():
    """Testa validação detalhada de fallback sem modelos (linha 122)"""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_key",
            "OPENROUTER_API_KEY": "openrouter_key",
            "FALLBACK_ENABLED": "true",
            "OPENROUTER_MODELS": "",  # Vazio
        },
    ):
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        error_str = str(exc_info.value).lower()
        assert "openrouter_models" in error_str or "fallback_enabled" in error_str
