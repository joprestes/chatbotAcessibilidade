import asyncio
from chatbot_acessibilidade.agents.dispatcher import get_agent_response
from chatbot_acessibilidade.core.formatter import (
    eh_erro,
    gerar_dica_final,
    formatar_resposta_final,
    extrair_primeiro_paragrafo
)

async def pipeline_acessibilidade(pergunta: str) -> dict:
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
        return {"erro": " ❌ Por favor, digite uma pergunta sobre acessibilidade digital."}

     # 1. Agente Assistente
    prompt_assistente = (
        f"Você recebeu a seguinte pergunta sobre acessibilidade digital. "
        f"Responda de forma clara, acessível e didática, explicando bem os conceitos e oferecendo exemplos práticos:\n\n{pergunta}"
    )
    resposta = await get_agent_response("assistente", prompt_assistente, "assistente")
    if eh_erro(resposta):
        return {"erro": f"❌ Falha ao processar sua pergunta: {resposta}"}

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
    conceitos_essenciais = base if eh_erro(revisada) else revisada

    # 4 & 5. Executar agentes Testador e Aprofundador em paralelo 
    prompt_testes = (
        f"Um usuário fez a seguinte pergunta: {pergunta}\n\nE recebeu esta resposta: {conceitos_essenciais}\n\n"
        f"Com base nos conceitos apresentados, sugira formas práticas de testar a acessibilidade relacionada a esse tema."
    )
    prompt_aprofundar = (
        f"Um usuário perguntou: {pergunta}\n\nE recebeu esta resposta: {conceitos_essenciais}\n\n"
        f"Sugira materiais confiáveis e práticos para quem deseja estudar mais sobre esse tema."
    )
    
    task_testes = get_agent_response("testador", prompt_testes, "teste")
    task_aprofundar = get_agent_response("aprofundador", prompt_aprofundar, "aprofundar")

    resultados_paralelos = await asyncio.gather(task_testes, task_aprofundar)
    testes, aprofundar = resultados_paralelos

    if eh_erro(testes):
        testes = "Não foi possível gerar sugestões de testes desta vez."
    if eh_erro(aprofundar):
        aprofundar = "Não foi possível gerar sugestões de aprofundamento desta vez."

    # Monta a resposta final usando a nova estrutura
    introducao = extrair_primeiro_paragrafo(conceitos_essenciais)
    dica = gerar_dica_final(pergunta, conceitos_essenciais)
    return formatar_resposta_final(introducao, conceitos_essenciais, testes, aprofundar, dica)