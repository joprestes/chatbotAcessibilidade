# chatbot_acessibilidade/pipeline.py
from chatbot_acessibilidade.agent_factory import executar_agente_por_tipo
from chatbot_acessibilidade.utils import eh_erro, gerar_dica_final, formatar_resposta_final, extrair_primeiro_paragrafo

async def pipeline_acessibilidade(pergunta: str) -> str:
    if not pergunta.strip():
        return "Por favor, digite uma pergunta sobre acessibilidade digital."

    prompt_assistente = (
        f"Pergunta do usuário sobre acessibilidade digital:\n\n{pergunta}\n\n"
        "Responda com clareza e didatismo, como se estivesse ensinando esse conceito para alguém leigo. "
        "Inclua exemplos práticos quando possível, e use uma linguagem simples, sem parecer que está avaliando um texto ou comentário anterior."
    )
    resposta = await executar_agente_por_tipo("assistente", prompt_assistente, "assistente")
    if eh_erro(resposta):
        return f"❌ Falha ao processar sua pergunta: {resposta}"

    prompt_validador = (
        f"Abaixo está uma resposta sobre acessibilidade digital para uma pergunta real de um usuário.\n\n{resposta}\n\n"
        "Verifique se está tecnicamente correta com base em WCAG, ARIA e boas práticas. "
        "Se necessário, corrija diretamente o texto para que ele possa ser entregue ao usuário, como uma resposta final clara e confiável."
    )
    validada = await executar_agente_por_tipo("validador", prompt_validador, "validador")
    base = resposta if eh_erro(validada) else validada

    prompt_revisor = (
        f"Reescreva a seguinte resposta de forma clara, acessível e bem estruturada, como se estivesse explicando diretamente ao usuário que fez a pergunta:\n\n{base}"
    )
    revisada = await executar_agente_por_tipo("revisor", prompt_revisor, "revisor")
    final = base if eh_erro(revisada) else revisada

    prompt_testes = (
        f"Um usuário fez a seguinte pergunta: {pergunta}\n\nE recebeu esta resposta: {final}\n\n"
        f"Com base nos conceitos apresentados, sugira formas práticas de testar a acessibilidade relacionada a esse tema."
    )
    testes = await executar_agente_por_tipo("testador", prompt_testes, "teste")
    if eh_erro(testes):
        testes = "Não foi possível gerar sugestões de testes desta vez."

    prompt_aprofundar = (
        f"Um usuário perguntou: {pergunta}\n\nE recebeu esta resposta: {final}\n\n"
        f"Sugira materiais confiáveis e práticos para quem deseja estudar mais sobre esse tema."
    )
    aprofundar = await executar_agente_por_tipo("aprofundador", prompt_aprofundar, "aprofundar")
    if eh_erro(aprofundar):
        aprofundar = "Não foi possível gerar sugestões de aprofundamento desta vez."

    introducao = extrair_primeiro_paragrafo(final)
    dica = gerar_dica_final(pergunta, final)

    return formatar_resposta_final(introducao, final, testes, aprofundar, dica)
