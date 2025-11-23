"""
Validação e sanitização de conteúdo para proteção contra injection attacks
"""

import re
import html
from typing import Optional

logger = None
try:
    import logging

    logger = logging.getLogger(__name__)
except ImportError:
    pass


# Padrões suspeitos comuns de injection
INJECTION_PATTERNS = [
    # SQL Injection
    (r"(?i)(union\s+select|drop\s+table|insert\s+into|delete\s+from|update\s+set)", "SQL injection"),
    (r"(?i)(or\s+1\s*=\s*1|or\s+'1'\s*=\s*'1')", "SQL injection"),
    # Command Injection
    (r"[;&|`$(){}[\]<>]", "Command injection"),
    (r"(?i)(exec|system|eval|shell_exec|passthru)", "Command injection"),
    # XSS básico
    (r"<script[^>]*>", "XSS attempt"),
    (r"javascript:", "XSS attempt"),
    (r"on\w+\s*=", "XSS attempt (event handler)"),
    # Path Traversal
    (r"\.\./|\.\.\\", "Path traversal"),
    # LDAP Injection
    (r"[()&|!]", "LDAP injection"),
]


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitiza entrada de texto removendo ou escapando conteúdo perigoso.

    Args:
        text: Texto a ser sanitizado
        max_length: Tamanho máximo permitido (None = sem limite)

    Returns:
        Texto sanitizado
    """
    if not isinstance(text, str):
        return ""

    # Remove caracteres de controle (exceto quebras de linha e tabs)
    text = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", text)

    # Normaliza espaços em branco
    text = re.sub(r"\s+", " ", text)

    # Remove caracteres não-ASCII perigosos (mantém acentos e caracteres válidos)
    # Permite caracteres Unicode válidos mas remove alguns caracteres especiais
    text = re.sub(r"[\u200B-\u200D\uFEFF]", "", text)  # Zero-width spaces

    # Aplica limite de tamanho se especificado
    if max_length and len(text) > max_length:
        text = text[:max_length]
        if logger:
            logger.warning(f"Texto truncado para {max_length} caracteres")

    return text.strip()


def validate_content(text: str, strict: bool = False) -> tuple[bool, Optional[str]]:
    """
    Valida conteúdo e detecta padrões suspeitos de injection.

    Args:
        text: Texto a ser validado
        strict: Se True, rejeita qualquer padrão suspeito. Se False, apenas detecta.

    Returns:
        Tupla (is_valid, reason)
        - is_valid: True se o conteúdo é válido
        - reason: Razão da rejeição (None se válido)
    """
    if not isinstance(text, str):
        return False, "Conteúdo deve ser uma string"

    # Verifica padrões de injection
    for pattern, attack_type in INJECTION_PATTERNS:
        if re.search(pattern, text):
            if logger:
                logger.warning(f"Padrão suspeito detectado: {attack_type} em '{text[:50]}...'")
            if strict:
                return False, f"Padrão suspeito detectado: {attack_type}"
            # Em modo não-strict, apenas loga mas permite

    return True, None


def detect_injection_patterns(text: str) -> list[str]:
    """
    Detecta padrões de injection no texto sem rejeitar.

    Args:
        text: Texto a ser analisado

    Returns:
        Lista de tipos de ataques detectados
    """
    if not isinstance(text, str):
        return []

    detected = []
    for pattern, attack_type in INJECTION_PATTERNS:
        if re.search(pattern, text):
            if attack_type not in detected:
                detected.append(attack_type)

    return detected


def escape_html(text: str) -> str:
    """
    Escapa caracteres HTML para prevenir XSS.

    Args:
        text: Texto a ser escapado

    Returns:
        Texto com caracteres HTML escapados
    """
    if not isinstance(text, str):
        return ""
    return html.escape(text, quote=True)


def sanitize_html(text: str, allow_basic: bool = True) -> str:
    """
    Remove tags HTML perigosas, mantendo apenas tags básicas se permitido.

    Args:
        text: Texto contendo HTML
        allow_basic: Se True, permite tags básicas (p, br, strong, em, etc.)

    Returns:
        Texto sanitizado
    """
    if not isinstance(text, str):
        return ""

    # Remove todas as tags script e style
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.IGNORECASE | re.DOTALL)

    # Remove event handlers
    text = re.sub(r"on\w+\s*=\s*['\"][^'\"]*['\"]", "", text, flags=re.IGNORECASE)

    # Remove javascript: e data: URLs perigosas
    text = re.sub(r"javascript:", "", text, flags=re.IGNORECASE)
    text = re.sub(r"data:text/html", "", text, flags=re.IGNORECASE)

    if not allow_basic:
        # Remove todas as tags HTML
        text = re.sub(r"<[^>]+>", "", text)

    return text.strip()

