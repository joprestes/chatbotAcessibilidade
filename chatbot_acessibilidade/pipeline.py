import asyncio
from chatbot_acessibilidade.agents.dispatcher import get_agent_response
from chatbot_acessibilidade.core.formatter import (
    eh_erro,
    gerar_dica_final,
    formatar_resposta_final,
    extrair_primeiro_paragrafo
)

async def pipeline_acessibilidade(pergunta: str) -> str:
    """
    Executa o pipeline completo de geração de resposta para uma pergunta sobre acessibilidade digital.
    A pipeline envolve os seguintes passos:
      - Geração da resposta principal
      - Validação técnica (WCAG, ARIA)
      - Reescrita acessível
      - Sugestão de formas de teste
      - Sugestão de materiais de aprofundamento
    """
    if not pergunta.strip():
        return "Por favor, digite uma pergunta sobre acessibilidade digital."

    # 1. Agente Assistente
    prompt_assistente = (
        f"Você recebeu a seguinte pergunta sobre acessibilidade digital. "
        f"Responda de forma clara, acessível e didática, explicando bem os conceitos e oferecendo exemplos práticos:\n\n{pergunta}"
    )
    resposta = await get_agent_response("assistente", prompt_assistente, "assistente")
    if eh_erro(resposta):
        return f"❌ Falha ao processar sua pergunta: {resposta}"

    # 2. Agente Validador
    prompt_validador = (
        f"Abaixo está uma resposta sobre acessibilidade digital. Verifique se ela está tecnicamente correta "
        f"de acordo com as diretrizes WCAG, ARIA e boas práticas. Se necessário, corrija e reescreva:\n\n{resposta}"
    )
    validada = await get_agent_response("validador", prompt_validador, "validador")
    base = resposta if eh_erro(validada) else validada

    # 3. Agente Revisor
    prompt_revisor = (
        f"Reescreva esta resposta de forma clara, acessível e gentil, como se estivesse explicando para um usuário curioso "
        f"sobre acessibilidade digital:\n\n{base}"
    )
    revisada = await get_agent_response("revisor", prompt_revisor, "revisor")
    final = base if eh_erro(revisada) else revisada

    # 4. Agente Testador
    prompt_testes = (
        f"Um usuário fez a seguinte pergunta: {pergunta}\n\nE recebeu esta resposta: {final}\n\n"
        f"Com base nos conceitos apresentados, sugira formas práticas de testar a acessibilidade relacionada a esse tema."
    )
    testes = await get_agent_response("testador", prompt_testes, "teste")
    if eh_erro(testes):
        testes = "Não foi possível gerar sugestões de testes desta vez."

    # 5. Agente Aprofundador
    prompt_aprofundar = (
        f"Um usuário perguntou: {pergunta}\n\nE recebeu esta resposta: {final}\n\n"
        f"Sugira materiais confiáveis e práticos para quem deseja estudar mais sobre esse tema."
    )
    aprofundar = await get_agent_response("aprofundador", prompt_aprofundar, "aprofundar")
    if eh_erro(aprofundar):
        aprofundar = "Não foi possível gerar sugestões de aprofundamento desta vez."

    # Monta resposta final formatada
    introducao = extrair_primeiro_paragrafo(final)
    dica = gerar_dica_final(pergunta, final)

    return formatar_resposta_final(introducao, final, testes, aprofundar, dica)
