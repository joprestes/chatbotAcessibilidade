"""
Testes adicionais para aumentar cobertura de config.py
Focando nas linhas não cobertas: 127, 150-153
"""

import os
import pytest
from unittest.mock import patch
import sys
from pathlib import Path

src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from chatbot_acessibilidade.config import Settings  # noqa: E402


def test_openrouter_models_list_quando_e_string():
    """
    Testa linha 127: quando openrouter_models é string,
    deve chamar parse_openrouter_models
    """
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_key",
            "OPENROUTER_MODELS": "model1,model2,model3",
        },
        clear=False,
    ):
        settings = Settings()
        # openrouter_models é string, então linha 127 deve ser executada
        models_list = settings.openrouter_models_list
        assert isinstance(models_list, list)
        assert len(models_list) == 3
        assert "model1" in models_list
        assert "model2" in models_list
        assert "model3" in models_list


def test_config_linhas_150_153_sem_google_api_key():
    """
    Testa linhas 150-153: quando PYTEST_CURRENT_TEST está definido
    e GOOGLE_API_KEY não está em os.environ
    """
    # Remove PYTEST_CURRENT_TEST temporariamente para testar o bloco
    original_pytest = os.environ.pop("PYTEST_CURRENT_TEST", None)
    original_google_key = os.environ.pop("GOOGLE_API_KEY", None)
    original_openrouter_key = os.environ.pop("OPENROUTER_API_KEY", None)

    try:
        # Define PYTEST_CURRENT_TEST para entrar no bloco if
        os.environ["PYTEST_CURRENT_TEST"] = "test_config_coverage.py::test_config_linhas_150_153"
        
        # Remove GOOGLE_API_KEY para testar linha 150-151
        if "GOOGLE_API_KEY" in os.environ:
            del os.environ["GOOGLE_API_KEY"]
        
        # Recarrega o módulo para executar o código de inicialização
        import importlib
        import chatbot_acessibilidade.config
        importlib.reload(chatbot_acessibilidade.config)
        
        # Verifica que GOOGLE_API_KEY foi definido
        assert "GOOGLE_API_KEY" in os.environ
        assert os.environ["GOOGLE_API_KEY"] == "test_key_for_pytest"
        
    finally:
        # Restaura estado original
        if original_pytest:
            os.environ["PYTEST_CURRENT_TEST"] = original_pytest
        elif "PYTEST_CURRENT_TEST" in os.environ:
            del os.environ["PYTEST_CURRENT_TEST"]
        
        if original_google_key:
            os.environ["GOOGLE_API_KEY"] = original_google_key
        elif "GOOGLE_API_KEY" in os.environ and os.environ["GOOGLE_API_KEY"] == "test_key_for_pytest":
            del os.environ["GOOGLE_API_KEY"]
        
        if original_openrouter_key:
            os.environ["OPENROUTER_API_KEY"] = original_openrouter_key
        
        # Recarrega o módulo novamente para restaurar estado
        import importlib
        import chatbot_acessibilidade.config
        importlib.reload(chatbot_acessibilidade.config)


def test_config_linhas_150_153_sem_openrouter_api_key():
    """
    Testa linhas 152-153: quando PYTEST_CURRENT_TEST está definido
    e OPENROUTER_API_KEY não está em os.environ
    """
    # Remove PYTEST_CURRENT_TEST temporariamente para testar o bloco
    original_pytest = os.environ.pop("PYTEST_CURRENT_TEST", None)
    original_google_key = os.environ.pop("GOOGLE_API_KEY", None)
    original_openrouter_key = os.environ.pop("OPENROUTER_API_KEY", None)

    try:
        # Define PYTEST_CURRENT_TEST para entrar no bloco if
        os.environ["PYTEST_CURRENT_TEST"] = "test_config_coverage.py::test_config_linhas_150_153_2"
        
        # Garante que GOOGLE_API_KEY existe
        os.environ["GOOGLE_API_KEY"] = "test_key"
        
        # Remove OPENROUTER_API_KEY para testar linha 152-153
        if "OPENROUTER_API_KEY" in os.environ:
            del os.environ["OPENROUTER_API_KEY"]
        
        # Recarrega o módulo para executar o código de inicialização
        import importlib
        import chatbot_acessibilidade.config
        importlib.reload(chatbot_acessibilidade.config)
        
        # Verifica que OPENROUTER_API_KEY foi definido como string vazia
        assert "OPENROUTER_API_KEY" in os.environ
        assert os.environ["OPENROUTER_API_KEY"] == ""
        
    finally:
        # Restaura estado original
        if original_pytest:
            os.environ["PYTEST_CURRENT_TEST"] = original_pytest
        elif "PYTEST_CURRENT_TEST" in os.environ:
            del os.environ["PYTEST_CURRENT_TEST"]
        
        if original_google_key:
            os.environ["GOOGLE_API_KEY"] = original_google_key
        
        if original_openrouter_key:
            os.environ["OPENROUTER_API_KEY"] = original_openrouter_key
        elif "OPENROUTER_API_KEY" in os.environ and os.environ["OPENROUTER_API_KEY"] == "":
            del os.environ["OPENROUTER_API_KEY"]
        
        # Recarrega o módulo novamente para restaurar estado
        import importlib
        import chatbot_acessibilidade.config
        importlib.reload(chatbot_acessibilidade.config)

