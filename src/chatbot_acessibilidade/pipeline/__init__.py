"""
Módulo de pipeline e orquestração de agentes.
"""

import logging

from chatbot_acessibilidade.core.constants import ErrorMessages
from chatbot_acessibilidade.core.exceptions import APIError, AgentError, ValidationError
from chatbot_acessibilidade.pipeline.orquestrador import PipelineOrquestrador

logger = logging.getLogger(__name__)


async def pipeline_acessibilidade(pergunta: str) -> dict:
    """
    Executa o pipeline completo de geração de resposta para uma pergunta sobre
    acessibilidade digital.

    Esta função é um wrapper de compatibilidade que usa internamente o PipelineOrquestrador.
    A pipeline envolve os seguintes passos:
      - Geração da resposta principal (Assistente)
      - Validação técnica (Validador - WCAG, ARIA)
      - Reescrita acessível (Revisor)
      - Sugestão de formas de teste (Testador - paralelo)
      - Sugestão de materiais de aprofundamento (Aprofundador - paralelo)

    Args:
        pergunta: Pergunta do usuário sobre acessibilidade digital

    Returns:
        Dicionário com a resposta formatada em seções:
        - "📘 **Introdução**": Resumo inicial
        - "🔍 **Conceitos Essenciais**": Corpo da resposta
        - "🧪 **Como Testar na Prática**": Plano de testes
        - "📚 **Quer se Aprofundar?**": Referências e materiais
        - "👋 **Dica Final**": Dica contextual

    Raises:
        ValidationError: Se a pergunta não for válida
        APIError: Se houver erro na comunicação com a API
        AgentError: Se houver erro na execução dos agentes
    """
    try:
        orquestrador = PipelineOrquestrador()
        resultado = await orquestrador.executar(pergunta)
        return dict(resultado)
    except ValidationError:
        # Re-raise ValidationError sem modificação
        raise
    except (APIError, AgentError) as e:
        # Converte erros de agente para formato de erro compatível
        logger.error(f"Erro no pipeline: {e}")
        return {"erro": str(e)}
    except Exception as e:
        # Captura qualquer outro erro inesperado
        logger.error(f"Erro inesperado no pipeline: {e}", exc_info=True)
        return {"erro": ErrorMessages.API_ERROR_GENERIC}


__all__ = ["PipelineOrquestrador", "pipeline_acessibilidade"]
