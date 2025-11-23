"""
Testes para o módulo validators.py
"""

import pytest

pytestmark = pytest.mark.unit

import sys
from pathlib import Path

# Adiciona src ao path para imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from chatbot_acessibilidade.core.validators import (  # noqa: E402
    sanitize_input,
    validate_content,
    detect_injection_patterns,
    escape_html,
    sanitize_html,
)


def test_sanitize_input_basico():
    """Testa sanitização básica de entrada"""
    result = sanitize_input("  teste  ")
    assert result == "teste"


def test_sanitize_input_caracteres_controle():
    """Testa remoção de caracteres de controle"""
    result = sanitize_input("teste\x00\x01\x02")
    assert "\x00" not in result
    assert "\x01" not in result


def test_sanitize_input_espacos_multiplos():
    """Testa normalização de espaços múltiplos"""
    result = sanitize_input("teste    com    espaços")
    assert "  " not in result


def test_sanitize_input_max_length():
    """Testa truncamento com max_length"""
    text = "a" * 100
    result = sanitize_input(text, max_length=50)
    assert len(result) == 50


def test_sanitize_input_nao_string():
    """Testa sanitização de não-string"""
    result = sanitize_input(None)
    assert result == ""

    result = sanitize_input(123)
    assert result == ""


def test_validate_content_valido():
    """Testa validação de conteúdo válido"""
    is_valid, reason = validate_content("Pergunta normal sobre acessibilidade")
    assert is_valid is True
    assert reason is None


def test_validate_content_sql_injection():
    """Testa detecção de SQL injection"""
    is_valid, reason = validate_content("test' OR 1=1--", strict=True)
    assert is_valid is False
    assert reason is not None
    assert "sql" in reason.lower() or "injection" in reason.lower()


def test_validate_content_sql_injection_nao_strict():
    """Testa detecção de SQL injection em modo não-strict"""
    is_valid, reason = validate_content("test' OR 1=1--", strict=False)
    # Em modo não-strict, detecta mas não rejeita
    assert is_valid is True
    assert reason is None


def test_validate_content_xss():
    """Testa detecção de XSS"""
    is_valid, reason = validate_content("<script>alert('xss')</script>", strict=True)
    assert is_valid is False
    assert reason is not None
    # Pode detectar como command injection ou XSS, ambos são válidos
    assert "injection" in reason.lower() or "xss" in reason.lower()


def test_validate_content_command_injection():
    """Testa detecção de command injection"""
    is_valid, reason = validate_content("test; rm -rf /", strict=True)
    assert is_valid is False
    assert "command injection" in reason.lower()


def test_validate_content_path_traversal():
    """Testa detecção de path traversal"""
    is_valid, reason = validate_content("../../../etc/passwd", strict=True)
    assert is_valid is False
    assert "path traversal" in reason.lower()


def test_validate_content_nao_string():
    """Testa validação de não-string"""
    is_valid, reason = validate_content(None)
    assert is_valid is False
    assert "string" in reason.lower()


def test_detect_injection_patterns_multiplos():
    """Testa detecção de múltiplos padrões"""
    text = "test' OR 1=1-- <script>alert('xss')</script>"
    detected = detect_injection_patterns(text)
    assert len(detected) >= 2
    assert any("SQL" in d for d in detected)
    assert any("XSS" in d for d in detected)


def test_detect_injection_patterns_nenhum():
    """Testa detecção quando não há padrões"""
    detected = detect_injection_patterns("Pergunta normal")
    assert len(detected) == 0


def test_detect_injection_patterns_nao_string():
    """Testa detecção em não-string"""
    detected = detect_injection_patterns(None)
    assert len(detected) == 0


def test_escape_html_basico():
    """Testa escape HTML básico"""
    result = escape_html("<script>alert('xss')</script>")
    assert "<" not in result or "&lt;" in result
    assert ">" not in result or "&gt;" in result


def test_escape_html_aspas():
    """Testa escape de aspas"""
    result = escape_html('teste com "aspas"')
    assert '"' not in result or "&quot;" in result


def test_escape_html_nao_string():
    """Testa escape de não-string"""
    result = escape_html(None)
    assert result == ""


def test_sanitize_html_remove_script():
    """Testa remoção de tags script"""
    text = "<p>Texto</p><script>alert('xss')</script>"
    result = sanitize_html(text, allow_basic=True)
    assert "<script>" not in result.lower()
    assert "Texto" in result


def test_sanitize_html_remove_style():
    """Testa remoção de tags style"""
    text = "<p>Texto</p><style>body { color: red; }</style>"
    result = sanitize_html(text, allow_basic=True)
    assert "<style>" not in result.lower()


def test_sanitize_html_remove_event_handlers():
    """Testa remoção de event handlers"""
    text = "<p onclick=\"alert('xss')\">Texto</p>"
    result = sanitize_html(text, allow_basic=True)
    assert "onclick" not in result.lower()


def test_sanitize_html_remove_javascript_url():
    """Testa remoção de javascript: URLs"""
    text = "<a href=\"javascript:alert('xss')\">Link</a>"
    result = sanitize_html(text, allow_basic=True)
    assert "javascript:" not in result.lower()


def test_sanitize_html_remove_todas_tags():
    """Testa remoção de todas as tags quando allow_basic=False"""
    text = "<p>Texto <strong>negrito</strong></p>"
    result = sanitize_html(text, allow_basic=False)
    assert "<" not in result
    assert ">" not in result
    assert "Texto" in result
    assert "negrito" in result


def test_sanitize_html_nao_string():
    """Testa sanitização de não-string"""
    result = sanitize_html(None)
    assert result == ""
