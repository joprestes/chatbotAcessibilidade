"""
Exceções customizadas para o projeto
"""


class ChatbotException(Exception):
    """Exceção base para o chatbot"""
    pass


class ValidationError(ChatbotException):
    """Erro de validação de entrada"""
    pass


class APIError(ChatbotException):
    """Erro na comunicação com API externa"""
    pass


class AgentError(ChatbotException):
    """Erro na execução de um agente"""
    pass


class RateLimitExceeded(ChatbotException):
    """Rate limit excedido"""
    pass


class QuotaExhaustedError(ChatbotException):
    """Quota de um modelo foi esgotada"""
    pass


class ModelUnavailableError(ChatbotException):
    """Modelo não está disponível no momento"""
    pass

