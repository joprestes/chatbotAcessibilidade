"""
Configuração centralizada do projeto usando Pydantic Settings
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, model_validator


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # API Google
    google_api_key: str = Field(..., description="Chave da API do Google Gemini")
    
    # OpenRouter (opcional, para fallback)
    openrouter_api_key: str = Field(
        default="",
        description="Chave da API do OpenRouter (opcional, necessário para fallback)"
    )
    openrouter_models: str = Field(
        default="meta-llama/llama-3.3-70b-instruct:free,google/gemini-flash-1.5:free,mistralai/mistral-7b-instruct:free",
        description="Lista de modelos OpenRouter em ordem de preferência (separados por vírgula)"
    )
    fallback_enabled: bool = Field(
        default=False,
        description="Habilitar fallback automático para OpenRouter quando Gemini falhar"
    )
    openrouter_timeout_seconds: int = Field(
        default=60,
        description="Timeout para chamadas à API OpenRouter em segundos"
    )
    
    # CORS
    cors_origins: str = Field(
        default="*",
        description="Origens permitidas para CORS (separadas por vírgula ou '*' para todas)"
    )
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(
        default=True,
        description="Habilitar rate limiting"
    )
    rate_limit_per_minute: int = Field(
        default=10,
        description="Número máximo de requisições por minuto por IP"
    )
    
    # Validação de entrada
    max_question_length: int = Field(
        default=2000,
        description="Tamanho máximo da pergunta em caracteres"
    )
    min_question_length: int = Field(
        default=3,
        description="Tamanho mínimo da pergunta em caracteres"
    )
    
    # Timeout
    api_timeout_seconds: int = Field(
        default=60,
        description="Timeout para chamadas à API Google em segundos"
    )
    
    # Cache
    cache_enabled: bool = Field(
        default=True,
        description="Habilitar cache de respostas"
    )
    cache_ttl_seconds: int = Field(
        default=3600,
        description="TTL do cache em segundos (1 hora padrão)"
    )
    cache_max_size: int = Field(
        default=100,
        description="Tamanho máximo do cache (número de itens)"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Formato das mensagens de log"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @field_validator("cors_origins")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse CORS origins from string"""
        if v == "*":
            return ["*"]
        return [origin.strip() for origin in v.split(",")]
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Valida nível de log"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level deve ser um de: {', '.join(valid_levels)}")
        return v_upper
    
    @field_validator("openrouter_models")
    @classmethod
    def parse_openrouter_models(cls, v: str) -> List[str]:
        """Parse OpenRouter models from string"""
        if not v:
            return []
        return [model.strip() for model in v.split(",") if model.strip()]
    
    @property
    def openrouter_models_list(self) -> List[str]:
        """Retorna a lista de modelos OpenRouter parseada"""
        if isinstance(self.openrouter_models, str):
            return self.parse_openrouter_models(self.openrouter_models)
        return self.openrouter_models
    
    @model_validator(mode='after')
    def validate_fallback_config(self):
        """Validação pós-inicialização"""
        if self.fallback_enabled:
            if not self.openrouter_api_key:
                raise ValueError(
                    "fallback_enabled=True requer openrouter_api_key configurada"
                )
            models_list = self.openrouter_models_list
            if not models_list:
                raise ValueError(
                    "fallback_enabled=True requer openrouter_models não vazio"
                )
        return self


# Instância global de configurações
settings = Settings()

