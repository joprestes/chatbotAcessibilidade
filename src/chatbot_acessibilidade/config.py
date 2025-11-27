"""
Configuração centralizada do projeto usando Pydantic Settings
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, model_validator


class Settings(BaseSettings):
    """Configurações da aplicação"""

    # API Google
    google_api_key: str = Field(..., description="Chave da API do Google Gemini")

    # Hugging Face (opcional, para fallback)
    huggingface_api_key: str = Field(
        default="", description="Chave da API do Hugging Face (opcional, necessário para fallback)"
    )
    huggingface_models: str = Field(
        default="meta-llama/Llama-3.3-70B-Instruct,google/gemma-2-9b-it,mistralai/Mistral-7B-Instruct-v0.3",
        description="Lista de modelos Hugging Face em ordem de preferência (separados por vírgula)",
    )
    fallback_enabled: bool = Field(
        default=False,
        description="Habilitar fallback automático para Hugging Face quando Gemini falhar",
    )
    huggingface_timeout_seconds: int = Field(
        default=60, description="Timeout para chamadas à API Hugging Face em segundos"
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

    @field_validator("huggingface_models")
    @classmethod
    def parse_huggingface_models(cls, v: str) -> List[str]:
        """Parse Hugging Face models from string"""
        if not v:
            return []
        return [model.strip() for model in v.split(",") if model.strip()]

    @property
    def huggingface_models_list(self) -> List[str]:
        """Retorna a lista de modelos Hugging Face parseada"""
        from typing import cast

        if isinstance(self.huggingface_models, str):
            return self.parse_huggingface_models(self.huggingface_models)
        # Se já for uma lista, retorna diretamente (após validação do Pydantic)
        return cast(List[str], self.huggingface_models)

    @model_validator(mode="after")
    def validate_fallback_config(self):
        """Validação pós-inicialização"""
        if self.fallback_enabled:
            if not self.huggingface_api_key:
                raise ValueError("fallback_enabled=True requer huggingface_api_key configurada")
            models_list = self.huggingface_models_list
            if not models_list:
                raise ValueError("fallback_enabled=True requer huggingface_models não vazio")
        return self


# Instância global de configurações
# Em ambiente de teste, as variáveis são definidas em conftest.py antes da importação
# Em produção, devem estar no .env
import os  # noqa: E402

# Verifica se está em ambiente de teste
if os.getenv("PYTEST_CURRENT_TEST"):
    # Em testes, usa valores padrão se não estiverem definidos
    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = "test_key_for_pytest"
    if "HUGGINGFACE_API_KEY" not in os.environ:
        os.environ["HUGGINGFACE_API_KEY"] = ""

settings = Settings()  # type: ignore[call-arg]
