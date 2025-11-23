"""
Orquestrador do Pipeline de Acessibilidade.

Este módulo contém a classe PipelineOrquestrador que gerencia o fluxo completo
de execução dos agentes especializados em acessibilidade digital.
"""

import asyncio
import logging
from typing import Dict, Tuple, Union

from chatbot_acessibilidade.agents.dispatcher import get_agent_response
from chatbot_acessibilidade.config import settings
from chatbot_acessibilidade.core.constants import ErrorMessages
from chatbot_acessibilidade.core.exceptions import APIError, AgentError, ValidationError
from chatbot_acessibilidade.core.formatter import (
    eh_erro,
    extrair_primeiro_paragrafo,
    formatar_resposta_final,
    gerar_dica_final,
)
from chatbot_acessibilidade.core.metrics import MetricsContext, record_request

logger = logging.getLogger(__name__)


def _tratar_resultado_paralelo(
    resultado: Union[str, Exception], nome_agente: str, fallback: str
) -> str:
    """
    Trata o resultado de um agente executado em paralelo.

    Args:
        resultado: Resultado do agente (pode ser Exception ou string)
        nome_agente: Nome do agente para logging
        fallback: Mensagem de fallback em caso de erro

    Returns:
        String com o resultado ou mensagem de fallback
    """
    if isinstance(resultado, Exception):
        logger.warning(f"Erro ao gerar sugestões de {nome_agente}: {resultado}")
        return fallback

    if eh_erro(resultado):
        logger.warning(f"Erro detectado na resposta do {nome_agente}")
        return fallback

    return resultado


class PipelineOrquestrador:
    """
    Orquestrador do pipeline de geração de respostas sobre acessibilidade digital.

    Gerencia o fluxo completo de execução dos agentes especializados:
    1. Assistente: Gera resposta inicial
    2. Validador: Valida e corrige tecnicamente
    3. Revisor: Simplifica a linguagem
    4. Testador: Gera plano de testes (paralelo)
    5. Aprofundador: Busca referências (paralelo)

    Attributes:
        pergunta: Pergunta do usuário sobre acessibilidade
        resposta_inicial: Resposta gerada pelo assistente
        resposta_validada: Resposta após validação técnica
        resposta_final: Resposta após revisão de linguagem
        testes: Plano de testes gerado
        aprofundar: Referências e materiais de estudo
    """

    def __init__(self):
        """Inicializa o orquestrador do pipeline."""
        self.pergunta: str = ""
        self.resposta_inicial: str = ""
        self.resposta_validada: str = ""
        self.resposta_final: str = ""
        self.testes: str = ""
        self.aprofundar: str = ""

    def validar_entrada(self, pergunta: str) -> None:
        """
        Valida a entrada do usuário.

        Args:
            pergunta: Pergunta do usuário a ser validada

        Raises:
            ValidationError: Se a pergunta não atender aos critérios de validação
        """
        pergunta = pergunta.strip()
        if not pergunta:
            raise ValidationError(ErrorMessages.PERGUNTA_VAZIA)

        if len(pergunta) < settings.min_question_length:
            raise ValidationError(
                ErrorMessages.PERGUNTA_MUITO_CURTA.format(min=settings.min_question_length)
            )

        if len(pergunta) > settings.max_question_length:
            raise ValidationError(
                ErrorMessages.PERGUNTA_MUITO_LONGA.format(max=settings.max_question_length)
            )

        self.pergunta = pergunta
        logger.info(f"Iniciando pipeline para pergunta: {pergunta[:50]}...")

    async def executar_sequencial(self) -> None:
        """
        Executa os agentes sequencialmente: Assistente → Validador → Revisor.

        Cada etapa tem fallback para a etapa anterior em caso de erro.
        Métricas são coletadas para cada agente usando MetricsContext.
        """
        # 1. Agente Assistente: Gera a primeira versão da resposta
        logger.debug("Executando agente Assistente...")
        with MetricsContext(agent_name="assistente"):
            try:
                # O agente assistente já tem instrução completa, apenas passamos a pergunta
                self.resposta_inicial = await get_agent_response(
                    "assistente", self.pergunta, "assistente"
                )

                if eh_erro(self.resposta_inicial):
                    logger.error(f"Erro na resposta inicial: {self.resposta_inicial}")
                    raise AgentError(
                        ErrorMessages.AGENT_ERROR_INITIAL.format(error=self.resposta_inicial)
                    )

                logger.debug("Agente Assistente executado com sucesso")
            except (APIError, AgentError) as e:
                logger.error(f"Erro no agente assistente: {e}")
                raise

        # 2. Agente Validador: Valida e corrige tecnicamente
        logger.debug("Executando agente Validador...")
        with MetricsContext(agent_name="validador"):
            try:
                # Validador recebe a resposta do assistente para validar
                prompt_validador = (
                    f"Analise esta resposta técnica sobre acessibilidade digital:\n\n"
                    f"{self.resposta_inicial}"
                )
                resposta_validacao = await get_agent_response(
                    "validador", prompt_validador, "validador"
                )

                if eh_erro(resposta_validacao):
                    logger.warning("Erro na resposta do validador, usando resposta inicial")
                    self.resposta_validada = self.resposta_inicial
                elif resposta_validacao.strip() == "OK":
                    # Validador aprovou, mantém resposta original
                    logger.debug("Validador aprovou a resposta (OK)")
                    self.resposta_validada = self.resposta_inicial
                else:
                    # Validador corrigiu, usa resposta corrigida
                    logger.debug("Validador corrigiu a resposta")
                    self.resposta_validada = resposta_validacao

            except (APIError, AgentError) as e:
                logger.warning(f"Erro no agente validador: {e}, usando resposta inicial")
                self.resposta_validada = self.resposta_inicial  # Fallback

        # 3. Agente Revisor: Simplifica a linguagem
        logger.debug("Executando agente Revisor...")
        with MetricsContext(agent_name="revisor"):
            try:
                # Revisor recebe a resposta validada para simplificar
                prompt_revisor = (
                    "Revise este texto sobre acessibilidade digital para linguagem "
                    "simples e inclusiva:\n\n"
                    f"{self.resposta_validada}"
                )
                self.resposta_final = await get_agent_response("revisor", prompt_revisor, "revisor")

                if eh_erro(self.resposta_final):
                    logger.warning("Erro na resposta do revisor, usando resposta validada")
                    self.resposta_final = self.resposta_validada
                else:
                    logger.debug("Agente Revisor executado com sucesso")

            except (APIError, AgentError) as e:
                logger.warning(f"Erro no agente revisor: {e}, usando resposta validada")
                self.resposta_final = self.resposta_validada  # Fallback

    async def executar_paralelo(self) -> Tuple[str, str]:
        """
        Executa os agentes Testador e Aprofundador em paralelo.

        Returns:
            Tupla com (testes, aprofundar) - resultados dos agentes paralelos
        """
        logger.debug("Executando agentes paralelos (Testador + Aprofundador)...")

        # Prepara prompts para os agentes paralelos
        # Testador recebe pergunta + resposta final
        prompt_testes = (
            "Crie um plano de testes práticos para validar esta solução de "
            "acessibilidade:\n\n"
            f"Pergunta: {self.pergunta}\n\n"
            f"Resposta: {self.resposta_final}"
        )

        # Aprofundador recebe apenas a pergunta (busca referências)
        prompt_aprofundar = (
            "Busque referências e materiais de estudo confiáveis sobre este tema:\n\n"
            f"Pergunta: {self.pergunta}"
        )

        # Executa as tarefas em paralelo
        task_testes = get_agent_response("testador", prompt_testes, "teste")
        task_aprofundar = get_agent_response("aprofundador", prompt_aprofundar, "aprofundar")

        try:
            resultados_paralelos = await asyncio.gather(
                task_testes, task_aprofundar, return_exceptions=True
            )
            testes_result, aprofundar_result = resultados_paralelos

            # Tratamento de erro para os resultados paralelos
            testes_result_typed: Union[str, Exception] = (
                testes_result if isinstance(testes_result, (str, Exception)) else str(testes_result)
            )
            aprofundar_result_typed: Union[str, Exception] = (
                aprofundar_result
                if isinstance(aprofundar_result, (str, Exception))
                else str(aprofundar_result)
            )

            # Mede tempo para cada agente paralelo
            with MetricsContext(agent_name="testador"):
                self.testes = _tratar_resultado_paralelo(
                    testes_result_typed,
                    "testes",
                    "Não foi possível gerar sugestões de testes desta vez.",
                )

            with MetricsContext(agent_name="aprofundador"):
                self.aprofundar = _tratar_resultado_paralelo(
                    aprofundar_result_typed,
                    "aprofundamento",
                    "Não foi possível gerar sugestões de aprofundamento desta vez.",
                )

            logger.debug("Agentes paralelos executados com sucesso")
            return (self.testes, self.aprofundar)

        except Exception as e:
            logger.error(f"Erro ao executar agentes paralelos: {e}")
            self.testes = "Não foi possível gerar sugestões de testes desta vez."
            self.aprofundar = "Não foi possível gerar sugestões de aprofundamento desta vez."
            return (self.testes, self.aprofundar)

    def formatar_saida(self) -> Dict[str, str]:
        """
        Formata a resposta final usando os formatadores existentes.

        Returns:
            Dicionário com a resposta formatada em seções
        """
        # Extrai a introdução (primeiro parágrafo) da resposta completa
        introducao = extrair_primeiro_paragrafo(self.resposta_final)

        # Cria a variável para o corpo principal dos conceitos
        corpo_conceitos = self.resposta_final

        # Se a introdução for diferente do texto completo, remove a introdução do corpo
        # Isso evita que o mesmo parágrafo apareça duas vezes
        if introducao.strip() != self.resposta_final.strip():
            corpo_conceitos = self.resposta_final.replace(introducao, "", 1).strip()

        # Gera a dica final com base na pergunta
        dica = gerar_dica_final(self.pergunta, self.resposta_final)

        # Formata a resposta final
        resultado_final: Dict[str, str] = formatar_resposta_final(
            introducao, corpo_conceitos, self.testes, self.aprofundar, dica
        )

        return resultado_final

    async def executar(self, pergunta: str) -> Dict[str, str]:
        """
        Executa o pipeline completo de geração de resposta.

        Args:
            pergunta: Pergunta do usuário sobre acessibilidade digital

        Returns:
            Dicionário com a resposta formatada em seções

        Raises:
            ValidationError: Se a pergunta não for válida
            APIError: Se houver erro na comunicação com a API
            AgentError: Se houver erro na execução dos agentes
        """
        # Registra requisição para métricas
        record_request()

        # Valida entrada
        self.validar_entrada(pergunta)

        # Executa sequencialmente: Assistente → Validador → Revisor
        await self.executar_sequencial()

        # Executa em paralelo: Testador + Aprofundador
        await self.executar_paralelo()

        # Formata e retorna a resposta final
        return self.formatar_saida()
