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
        return {"erro": "❌ Por favor, digite uma pergunta sobre acessibilidade digital."}

    # 1. Agente Assistente: Gera a primeira versão da resposta.
    prompt_assistente = (
        f"Você é um especialista em acessibilidade digital. Responda à seguinte pergunta de forma clara, "
        f"acessível e didática, explicando os conceitos e oferecendo exemplos práticos:\n\nPERGUNTA: '{pergunta}'"
    )
    resposta_inicial = await get_agent_response("assistente", prompt_assistente, "assistente")
    if eh_erro(resposta_inicial):
        return {"erro": f"❌ Falha ao gerar a resposta inicial: {resposta_inicial}"}

    # 2. Agente Validador: Corrige e aprimora tecnicamente a resposta.
    prompt_validador = (
        f"Você é um especialista técnico em WCAG e ARIA. Sua tarefa é validar e, se necessário, corrigir o rascunho de resposta abaixo.\n"
        f"A pergunta original do usuário foi: '{pergunta}'.\n\n"
        f"Rascunho da resposta:\n'{resposta_inicial}'\n\n"
        f"**Reescreva o texto, corrigindo qualquer imprecisão ou adicionando detalhes técnicos importantes. "
        f"ENTREGUE APENAS O TEXTO CORRIGIDO E FINAL, SEM INTRODUÇÕES OU COMENTÁRIOS.**"
    )
    base_tecnica = await get_agent_response("validador", prompt_validador, "validador")
    if eh_erro(base_tecnica):
        base_tecnica = resposta_inicial  # Fallback: se o validador falhar, usa a resposta inicial.

    # 3. Agente Revisor: Torna a linguagem mais clara e acessível.
    prompt_revisor = (
        f"Você é um(a) comunicador(a) especialista em linguagem clara. Sua tarefa é reescrever o texto técnico abaixo para que qualquer pessoa possa entender.\n"
        f"A pergunta original foi: '{pergunta}'.\n\n"
        f"Texto a ser reescrito:\n'{base_tecnica}'\n\n"
        f"**Reescreva o texto de forma didática e gentil. SUA SAÍDA DEVE SER APENAS O TEXTO FINAL, sem comentários como 'aqui está a versão revisada'.**"
    )
    resposta_final = await get_agent_response("revisor", prompt_revisor, "revisor")
    if eh_erro(resposta_final):
        resposta_final = base_tecnica  # Fallback: se o revisor falhar, usa a resposta técnica.

    # 4 & 5. Agentes Testador e Aprofundador: Executados em paralelo para mais eficiência.
    prompt_testes = (
        f"Você é um especialista em QA e testes de acessibilidade. Com base na pergunta e na resposta final, gere uma lista de passos práticos para testar o que foi explicado.\n\n"
        f"Pergunta: '{pergunta}'\n"
        f"Resposta: '{resposta_final}'\n\n"
        f"**Gere uma lista de ações ou um checklist em formato de tópicos (usando '-' ou '*'). "
        f"NÃO adicione frases introdutórias. Comece diretamente com as sugestões.**"
    )
    prompt_aprofundar = (
        f"Você é um curador de conteúdo sobre acessibilidade digital. Para um usuário que perguntou sobre '{pergunta}', sugira materiais de estudo confiáveis (artigos, cursos, livros).\n\n"
        f"**Gere uma lista de recomendações em formato de tópicos (usando '-' ou '*'). "
        f"Comece diretamente com os links ou nomes dos materiais, sem introduções.**"
    )

    # Executa as tarefas em paralelo
    task_testes = get_agent_response("testador", prompt_testes, "teste")
    task_aprofundar = get_agent_response("aprofundador", prompt_aprofundar, "aprofundar")
    resultados_paralelos = await asyncio.gather(task_testes, task_aprofundar)
    testes, aprofundar = resultados_paralelos

    # Tratamento de erro para os resultados paralelos
    if eh_erro(testes):
        testes = "Não foi possível gerar sugestões de testes desta vez."
    if eh_erro(aprofundar):
        aprofundar = "Não foi possível gerar sugestões de aprofundamento desta vez."

    # 1. Extrai a introdução (primeiro parágrafo) da resposta completa.
    introducao = extrair_primeiro_paragrafo(resposta_final)
    
    # 2. Cria a variável para o corpo principal dos conceitos.
    corpo_conceitos = resposta_final

    # 3. Se a introdução for diferente do texto completo, removemos a introdução do corpo.
    #    Isso evita que o mesmo parágrafo apareça duas vezes.
    if introducao.strip() != resposta_final.strip():
        corpo_conceitos = resposta_final.replace(introducao, "", 1).strip()
    
    # 4. Gera a dica final com base na pergunta.
    dica = gerar_dica_final(pergunta, resposta_final)
    
    # 5. Formata a resposta final, passando a introdução e o corpo de conceitos separados.
    return formatar_resposta_final(introducao, corpo_conceitos, testes, aprofundar, dica)
