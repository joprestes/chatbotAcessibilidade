import os
import asyncio
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search

from google import genai
from google.genai import types

# Carrega variáveis do .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Chave API do Google não encontrada no .env.")

genai.Client()
NOME_MODELO_ADK = 'gemini-2.0-flash'

# Função genérica para execução de agentes
async def rodar_agente(agent: Agent, prompt: str, user_id="user", session_prefix="sessao") -> str:
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    session_id = f"{session_prefix}_{os.urandom(4).hex()}"

    await session_service.create_session(user_id=user_id, session_id=session_id, app_name=agent.name)
    content = types.Content(role="user", parts=[types.Part(text=prompt)])
    resultado = ""

    async for evento in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if evento.is_final_response():
            resultado += "".join(parte.text + "\n" for parte in evento.content.parts if getattr(parte, "text", None))

    return resultado.strip()

# Fábrica de agentes com prompts ajustados
def criar_agentes():
    return {
        "assistente": Agent(
            name="assistente_acessibilidade_digital",
            model=NOME_MODELO_ADK,
            tools=[google_search],
            instruction=(
                "Você é um(a) especialista em acessibilidade digital. Receberá uma pergunta real feita por um usuário. "
                "Responda de forma clara, objetiva e didática, como se estivesse explicando diretamente para alguém que busca aprender sobre o tema. "
                "Use exemplos simples, linguagem acessível e organize a resposta com boas práticas de comunicação. "
                "Evite frases introdutórias genéricas ou comentários sobre a qualidade do conteúdo."
            )
        ),
        "validador": Agent(
            name="validador_resposta_acessibilidade",
            model=NOME_MODELO_ADK,
            instruction=(
                "Você é um(a) especialista técnico(a) em acessibilidade digital. "
                "Receberá uma resposta escrita para uma dúvida real de um usuário. "
                "Corrija apenas se houver imprecisão técnica com base nas diretrizes WCAG, ARIA e boas práticas. "
                "Reescreva a resposta corrigida diretamente, sem explicar que foi corrigida, e sem usar frases como 'sua resposta está boa, mas...'"
            )
        ),
        "revisor": Agent(
            name="revisor_clareza_acessibilidade",
            model=NOME_MODELO_ADK,
            instruction=(
                "Você é um(a) comunicador(a) acessível. Reescreva a resposta recebida com foco em clareza, organização e didatismo. "
                "Trate o conteúdo como resposta final para uma pergunta real de um usuário. "
                "Não use linguagem que sugira revisão ou comentários sobre o texto original. Apenas reescreva de forma direta, fluida e acessível."
            )
        ),
        "testador": Agent(
            name="sugestor_testabilidade_acessibilidade",
            model=NOME_MODELO_ADK,
            tools=[google_search],
            instruction=(
                "Você é um(a) especialista em testes de acessibilidade. Com base em uma pergunta e na resposta, "
                "sugira formas práticas de testá-la. Mencione ferramentas como axe, NVDA, VoiceOver, Lighthouse e testes com teclado, contraste etc."
            )
        ),
        "aprofundador": Agent(
            name="guia_aprofundamento_acessibilidade",
            model=NOME_MODELO_ADK,
            tools=[google_search],
            instruction=(
                "Você é um(a) curador(a) de conteúdo especializado em acessibilidade digital. "
                "Com base em uma dúvida real e uma resposta, sugira materiais de estudo aprofundado como cursos, artigos, livros ou ferramentas confiáveis."
            )
        ),
    }

AGENTES = criar_agentes()

# Função de execução por tipo
async def executar_agente_por_tipo(tipo: str, prompt: str, prefixo: str) -> str:
    return await rodar_agente(AGENTES[tipo], prompt, session_prefix=prefixo)

# Utilitários
def eh_erro(texto: str) -> bool:
    return texto.startswith("Erro") or "falha" in texto.lower()

def gerar_dica_final(pergunta: str, resposta: str) -> str:
    p = pergunta.lower()
    if "teclado" in p:
        return "Verifique se é possível navegar usando apenas o teclado, com foco visível e ordem lógica."
    if "contraste" in p:
        return "Use ferramentas como WebAIM ou axe para validar o contraste entre elementos visuais."
    if "leitor de tela" in p:
        return "Use o NVDA ou VoiceOver para testar se o conteúdo é lido corretamente por leitores de tela."
    return "A acessibilidade é um processo contínuo. Teste, colete feedback real e melhore sempre."

def formatar_resposta_final(resumo: str, conceitos: str, testes: str, aprofundar: str, dica: str) -> str:
    return f"""
📘 **Introdução**  
{resumo.strip()}

---

🔍 **Conceitos Essenciais**  
{conceitos.strip()}

---

🧪 **Como Testar na Prática**  
{testes.strip()}

---

📚 **Quer se Aprofundar?**  
{aprofundar.strip()}

---

👋 **Dica Final**  
{dica.strip()}
""".strip()

def extrair_primeiro_paragrafo(texto: str) -> str:
    paragrafos = [p.strip() for p in texto.split("\n\n") if len(p.strip()) > 30]
    if paragrafos:
        return paragrafos[0]
    return texto[:300].rsplit('.', 1)[0] + '.' if '.' in texto[:300] else texto[:300] + "..."

# Pipeline principal
async def pipeline_acessibilidade(pergunta: str) -> str:
    if not pergunta.strip():
        return "Por favor, digite uma pergunta sobre acessibilidade digital."

    # ASSISTENTE
    prompt_assistente = (
        f"Pergunta do usuário sobre acessibilidade digital:\n\n{pergunta}\n\n"
        "Responda com clareza e didatismo, como se estivesse ensinando esse conceito para alguém leigo. "
        "Inclua exemplos práticos quando possível, e use uma linguagem simples, sem parecer que está avaliando um texto ou comentário anterior."
    )
    resposta = await executar_agente_por_tipo("assistente", prompt_assistente, "assistente")
    if eh_erro(resposta):
        return f"❌ Falha ao processar sua pergunta: {resposta}"

    # VALIDADOR
    prompt_validador = (
        f"Abaixo está uma resposta sobre acessibilidade digital para uma pergunta real de um usuário.\n\n{resposta}\n\n"
        "Verifique se está tecnicamente correta com base em WCAG, ARIA e boas práticas. "
        "Se necessário, corrija diretamente o texto para que ele possa ser entregue ao usuário, como uma resposta final clara e confiável."
    )
    validada = await executar_agente_por_tipo("validador", prompt_validador, "validador")
    base = resposta if eh_erro(validada) else validada

    # REVISOR
    prompt_revisor = (
        f"Reescreva a seguinte resposta de forma clara, acessível e bem estruturada, como se estivesse explicando diretamente ao usuário que fez a pergunta:\n\n{base}"
    )
    revisada = await executar_agente_por_tipo("revisor", prompt_revisor, "revisor")
    final = base if eh_erro(revisada) else revisada

    # TESTADOR
    prompt_testes = (
        f"Um usuário fez a seguinte pergunta: {pergunta}\n\nE recebeu esta resposta: {final}\n\n"
        f"Com base nos conceitos apresentados, sugira formas práticas de testar a acessibilidade relacionada a esse tema."
    )
    testes = await executar_agente_por_tipo("testador", prompt_testes, "teste")
    if eh_erro(testes):
        testes = "Não foi possível gerar sugestões de testes desta vez."

    # APROFUNDADOR
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

# Execução local para testes
if __name__ == "__main__":
    async def testar():
        perguntas = [
            "O que é contraste de cores?",
            "Como usar leitor de tela?",
            "Navegação por teclado",
        ]
        for p in perguntas:
            print(f"\n🟡 Pergunta: {p}")
            r = await pipeline_acessibilidade(p)
            print(r)
            print("\n" + "=" * 60)

    asyncio.run(testar())
