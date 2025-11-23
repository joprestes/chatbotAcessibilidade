"""
Constantes centralizadas do projeto

Este módulo centraliza todos os valores mágicos (hardcoded) do projeto,
facilitando manutenção e configuração.
"""

# =========================================
# Timeouts (em segundos)
# =========================================
DEFAULT_API_TIMEOUT_SECONDS = 60  # Timeout padrão para APIs (Google Gemini)
OPENROUTER_TIMEOUT_SECONDS = 60  # Timeout para OpenRouter
FRONTEND_REQUEST_TIMEOUT_MS = 120000  # 120 segundos em milissegundos
HTTPX_CONNECT_TIMEOUT_SECONDS = 10.0  # Timeout de conexão para httpx

# =========================================
# Limites de Entrada
# =========================================
MAX_QUESTION_LENGTH = 2000  # Tamanho máximo da pergunta em caracteres
MIN_QUESTION_LENGTH = 3  # Tamanho mínimo da pergunta em caracteres
MIN_PARAGRAPH_LENGTH = 30  # Tamanho mínimo para considerar um parágrafo válido

# =========================================
# Limites de Cache
# =========================================
CACHE_MAX_SIZE = 100  # Tamanho máximo do cache (número de itens)
CACHE_TTL_SECONDS = 3600  # TTL do cache em segundos (1 hora)

# =========================================
# TTLs de Cache para Assets Estáticos
# =========================================
STATIC_CACHE_TTL_SECONDS = 86400  # 1 dia para CSS/JS
ASSETS_CACHE_TTL_SECONDS = 604800  # 7 dias para imagens

# =========================================
# Limites de Compressão
# =========================================
COMPRESSION_MIN_SIZE_BYTES = 500  # Tamanho mínimo para comprimir resposta

# =========================================
# Limites de Tokens (LLM)
# =========================================
OPENROUTER_MAX_TOKENS = 2000  # Máximo de tokens para OpenRouter

# =========================================
# Retry
# =========================================
MAX_RETRY_ATTEMPTS = 3  # Número máximo de tentativas em caso de erro

# =========================================
# Rate Limiting
# =========================================
DEFAULT_RATE_LIMIT_PER_MINUTE = 10  # Requisições por minuto (padrão)
FALLBACK_RATE_LIMIT_PER_MINUTE = 1000  # Requisições por minuto (quando desabilitado)


# =========================================
# Mensagens de Erro
# =========================================
class ErrorMessages:
    """Mensagens de erro padronizadas"""

    # Validação
    PERGUNTA_VAZIA = "❌ Por favor, digite uma pergunta sobre acessibilidade digital."
    PERGUNTA_MUITO_CURTA = "❌ A pergunta deve ter pelo menos {min} caracteres."
    PERGUNTA_MUITO_LONGA = "❌ A pergunta não pode ter mais de {max} caracteres."

    # Timeout
    TIMEOUT_GENERIC = (
        "⏱️ A requisição demorou muito para responder (timeout). Por favor, tente novamente."
    )
    TIMEOUT_GEMINI = "Timeout: A requisição demorou mais de {timeout}s para responder."
    TIMEOUT_OPENROUTER = "Timeout: A requisição ao OpenRouter demorou mais de {timeout} segundos."

    # Quota/Rate Limit
    QUOTA_EXHAUSTED = "Limite de uso atingido. Tente novamente mais tarde."
    RATE_LIMIT_EXCEEDED = "Rate limit excedido no {provider}"

    # API Errors
    API_ERROR_GENERIC = (
        "❌ Ocorreu um erro inesperado ao processar sua pergunta. Por favor, tente novamente."
    )
    API_ERROR_EMPTY_RESPONSE = "Erro: A resposta da API veio vazia."
    API_ERROR_SAFETY_BLOCK = (
        "Erro: Sua pergunta não pôde ser processada devido às diretrizes de segurança."
    )
    API_ERROR_SERVER_CONFIG = "Erro: Houve um problema com a configuração do servidor."
    API_ERROR_COMMUNICATION = "Erro: Ocorreu um problema de comunicação com a API."
    API_ERROR_OPENROUTER_INVALID_KEY = "Erro: Chave API do OpenRouter inválida."
    API_ERROR_OPENROUTER_COMMUNICATION = (
        "Erro: Ocorreu um problema de comunicação com o OpenRouter (HTTP {status_code})."
    )
    API_ERROR_OPENROUTER_CONNECTION = "Erro: Não foi possível conectar ao OpenRouter."
    API_ERROR_OPENROUTER_GENERIC = "Erro: Ocorreu uma falha inesperada ao usar o OpenRouter."

    # Model Unavailable
    MODEL_UNAVAILABLE_GEMINI = "API do Google sobrecarregada"
    MODEL_UNAVAILABLE_OPENROUTER = "Modelo {model} indisponível"

    # Fallback
    ALL_PROVIDERS_FAILED = (
        "Todos os provedores e modelos disponíveis falharam. Por favor, tente novamente mais tarde."
    )
    FALLBACK_DISABLED = "Erro no provedor primário e fallback desabilitado: {error}"

    # Agent Errors
    AGENT_ERROR_GENERIC = "Erro: Ocorreu uma falha inesperada. Detalhes: {details}"
    AGENT_ERROR_INITIAL = "❌ Falha ao gerar a resposta inicial: {error}"

    # Validation Errors
    VALIDATION_ERROR_GENERIC = "Erro de validação: {error}"

    # Cache
    CACHE_TRUNCATED_WARNING = "Texto truncado para {max_length} caracteres"


# =========================================
# Mensagens de Log
# =========================================
class LogMessages:
    """Mensagens de log padronizadas"""

    # Retry
    RETRY_ATTEMPT = "Tentativa {attempt}/{max} para agente após erro: {error}"

    # Cache
    CACHE_HIT = "Cache HIT para pergunta: {pergunta}..."
    CACHE_MISS = "Cache MISS para pergunta: {pergunta}..."
    CACHE_CACHED = "Resposta cacheada para pergunta: {pergunta}..."
    CACHE_CLEARED = "Cache limpo"
    CACHE_INITIALIZED = "Cache inicializado: max_size={max_size}, ttl={ttl}s"

    # Timeout
    TIMEOUT_GEMINI = "Timeout ao executar Gemini após {timeout}s"
    TIMEOUT_OPENROUTER = "Timeout ao executar OpenRouter modelo '{model}' após {timeout}s"

    # API Errors
    API_ERROR_GEMINI_RATE_LIMIT = "Rate limit excedido no Gemini"
    API_ERROR_GEMINI_AUTH = "Erro de autenticação no Gemini"
    API_ERROR_GEMINI_COMMUNICATION = "Erro de API do Google: {error}"
    API_ERROR_GEMINI_GENERIC = "Erro inesperado no Gemini: {error}"
    API_ERROR_OPENROUTER_RATE_LIMIT = "Rate limit excedido no OpenRouter modelo '{model}'"
    API_ERROR_OPENROUTER_AUTH = "Erro de autenticação no OpenRouter"
    API_ERROR_OPENROUTER_HTTP = "Erro HTTP {status_code} do OpenRouter: {error}"
    API_ERROR_OPENROUTER_REQUEST = "Erro de requisição ao OpenRouter: {error}"
    API_ERROR_OPENROUTER_GENERIC = "Erro inesperado no OpenRouter: {error}"

    # Validation
    VALIDATION_SUSPICIOUS_PATTERN = "Padrão suspeito detectado na pergunta: {reason}"
    VALIDATION_INJECTION_PATTERNS = "Padrões suspeitos detectados: {patterns}"

    # Cache
    CACHE_TRUNCATED_WARNING = "Texto truncado para {max_length} caracteres"

    # Configuration
    CONFIG_MISSING_API_KEY = "GOOGLE_API_KEY não configurada nas settings"
    CONFIG_GENAI_INIT_ERROR = "Erro ao inicializar genai.Client: {error}"


# =========================================
# Configurações de Frontend
# =========================================
class FrontendConstants:
    """Constantes específicas do frontend"""

    # Timeout
    REQUEST_TIMEOUT_MS = 120000  # 120 segundos

    # Animações
    ERROR_ANNOUNCEMENT_DURATION_MS = 1000  # Duração da mensagem de erro em acessibilidade
