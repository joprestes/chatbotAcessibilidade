"""
Configuração centralizada do projeto usando Pydantic Settings
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Configurações da aplicação"""

    # API Google - Chave primária (obrigatória)
    google_api_key: str = Field(..., description="Chave da API do Google Gemini (primária)")

    # API Google - Chave secundária (opcional, para fallback)
    google_api_key_second: str = Field(
        default="", description="Chave da API do Google Gemini (secundária, opcional para fallback)"
    )

    # CORS
    cors_origins: str = Field(
        default="*",
        description="Origens permitidas para CORS (separadas por vírgula ou '*' para todas)",
    )

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Habilitar rate limiting")
    rate_limit_per_minute: int = Field(
        default=10, description="Número máximo de requisições por minuto por IP"
    )

    # Validação de entrada
    max_question_length: int = Field(
        default=2000, description="Tamanho máximo da pergunta em caracteres"
    )
    min_question_length: int = Field(
        default=3, description="Tamanho mínimo da pergunta em caracteres"
    )

    # Timeout
    api_timeout_seconds: int = Field(
        default=60, description="Timeout para chamadas à API Google em segundos"
    )

    # Cache
    cache_enabled: bool = Field(default=True, description="Habilitar cache de respostas")
    cache_ttl_seconds: int = Field(
        default=3600, description="TTL do cache em segundos (1 hora padrão)"
    )
    cache_max_size: int = Field(
        default=100, description="Tamanho máximo do cache (número de itens)"
    )

    # Logging
    log_level: str = Field(
        default="INFO", description="Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Formato das mensagens de log",
    )

    # Segurança
    security_headers_enabled: bool = Field(
        default=True, description="Habilitar headers de segurança HTTP"
    )
    csp_policy: str = Field(
        default="",
        description="Política CSP customizada (vazio usa padrão). Exemplo: default-src 'self'",
    )

    # Performance
    compression_enabled: bool = Field(
        default=True, description="Habilitar compressão gzip de respostas"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @field_validator("cors_origins")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse CORS origins from string"""
        if v == "*":
            return ["*"]
        # Filtra strings vazias após split
        return [origin.strip() for origin in v.split(",") if origin.strip()]

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Valida nível de log"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level deve ser um de: {', '.join(valid_levels)}")
        return v_upper


# Instância global de configurações
# Em ambiente de teste, as variáveis são definidas em conftest.py antes da importação
# Em produção, devem estar no .env
import os  # noqa: E402

# Verifica se está em ambiente de teste
if os.getenv("PYTEST_CURRENT_TEST"):
    # Em testes, usa valores padrão se não estiverem definidos
    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = "test_key_for_pytest"


settings = Settings()  # type: ignore[call-arg]
