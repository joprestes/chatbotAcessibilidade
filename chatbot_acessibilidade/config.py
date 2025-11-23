"""
Configuração centralizada do projeto usando Pydantic Settings
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # API Google
    google_api_key: str = Field(..., description="Chave da API do Google Gemini")
    
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


# Instância global de configurações
settings = Settings()

