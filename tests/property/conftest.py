"""Configuração de fixtures para property-based tests"""

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_property_tests():
    """Configura ambiente para property-based tests"""
    import os
    
    # Garante que estamos em modo de teste
    os.environ["PYTEST_CURRENT_TEST"] = "true"
    os.environ["GOOGLE_API_KEY"] = "test_key_for_property"
    os.environ["HUGGINGFACE_API_KEY"] = ""
    os.environ["FALLBACK_ENABLED"] = "false"
    os.environ["RATE_LIMIT_ENABLED"] = "false"
    os.environ["CACHE_ENABLED"] = "true"
    
    yield
