import os
import re
import requests
from dotenv import load_dotenv

# Importações do google-adk
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search # Ferramenta de busca pré-construída do ADK

# Importações do google.generativeai (para types.Content e configuração da API Key)
import google.generativeai as genai
from google.generativeai import types # Especificamente para types.Content e types.Part

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Chave API do Google não encontrada no .env.")

genai.configure(api_key=GOOGLE_API_KEY)

# ==========================
# Configurações
# ==========================
NOME_MODELO_ADK = 'gemini-1.5-flash-latest' # Use o modelo desejado

# ==========================
# Função Auxiliar para Chamar Agentes ADK (AJUSTADA CONFORME EXEMPLO DO CURSO)
# ==========================
def call_adk_agent(agent_instance: Agent, full_prompt_text: str, agente_nome_log: str) -> str: # Renomeado para full_prompt_text
    """
    Envia um prompt completo para um agente ADK via um Runner criado sob demanda
    e retorna a resposta final em texto.
    """
    try:
        session_service = InMemorySessionService()
        # A criação explícita de 'session' pode não ser estritamente necessária se
        # o runner.run com um session_id único para InMemorySessionService for suficiente.
        # Mas, para alinhar com o exemplo, vamos mantê-la se não causar problemas.
        # session_service.create_session(app_name=agent_instance.name, user_id="user_pipeline", session_id=session_id_str)

        runner = Runner(agent=agent_instance, app_name=agent_instance.name, session_service=session_service)
        content_input = types.Content(role="user", parts=[types.Part(text=full_prompt_text)]) # O prompt completo é o input
        final_response_text = ""

        # Usando IDs de usuário e sessão como no exemplo do curso para consistência
        user_id_adk = "user_pipeline_main" # Pode ser um ID genérico para o sistema
        # Um session_id único por chamada para simular uma nova interação limpa
        session_id_adk = f"{agente_nome_log}_session_{os.urandom(4).hex()}"


        # Iterar pelos eventos retornados durante a execução do agente
        for event in runner.run(user_id=user_id_adk, session_id=session_id_adk, new_message=content_input):
            if event.is_final_response():
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text is not None:
                        final_response_text += part.text
                        final_response_text += "\n" # Adiciona nova linha entre partes

        if final_response_text:
            return final_response_text.strip()
        else:
            return f"Agente ADK '{agente_nome_log}': Não houve resposta final ou a resposta estava vazia."
    except AttributeError as e:
        return f"Erro de atributo ao executar agente ADK '{agente_nome_log}': {e}. Verifique a API do Runner/Event do ADK."
    except Exception as e:
        return f"Erro ao executar agente ADK '{agente_nome_log}': {type(e).__name__} - {e}"

# ==========================
# Definições dos Agentes ADK (Instâncias de Agent)
# As 'instructions' agora são mais genéricas, pois o prompt completo será construído antes da chamada.
# ==========================
ASSISTENTE_ACESSIBILIDADE_AGENT_DEF = Agent( # Renomeado para _DEF para indicar que é a definição
    name="assistente_acessibilidade_digital",
    model=NOME_MODELO_ADK,
    tools=[google_search],
    instruction="""Você é um especialista em acessibilidade digital. Responda à pergunta do usuário abaixo,
considerando o contexto de acessibilidade digital, especialmente se a pergunta for genérica.
Use busca (Google Search) para informações recentes e cite fontes."""
    # O {input} não é mais necessário aqui se o prompt completo é passado para call_adk_agent
)

VALIDADOR_RESPOSTA_AGENT_DEF = Agent(
    name="validador_resposta_acessibilidade",
    model=NOME_MODELO_ADK,
    instruction="""Valide a correção técnica da resposta fornecida sobre acessibilidade digital (WCAG, ARIA).
Corrija ou complemente. Se correta, confirme. Se for erro anterior, não prossiga."""
)

REVISOR_CLAREZA_AGENT_DEF = Agent(
    name="revisor_clareza_acessibilidade",
    model=NOME_MODELO_ADK,
    instruction="""Revise a resposta para clareza e simplicidade na linguagem de acessibilidade.
Explique jargões. Se clara, confirme. Se for erro anterior, não prossiga."""
)

TESTABILIDADE_AGENT_DEF = Agent(
    name="sugestor_testabilidade_acessibilidade",
    model=NOME_MODELO_ADK,
    tools=[google_search],
    instruction="""Com base na pergunta e resposta fornecidas, sugira como testar os conceitos de acessibilidade.
Recomende ferramentas online e passos práticos. Use busca (Google Search)."""
)

APROFUNDADOR_AGENT_DEF = Agent(
    name="guia_aprofundamento_acessibilidade",
    model=NOME_MODELO_ADK,
    tools=[google_search],
    instruction="""Com base na pergunta e resposta fornecidas, sugira materiais para aprofundamento em acessibilidade digital.
Use busca (Google Search) para recursos relevantes."""
)

# ==========================
# Funções Wrapper que preparam o prompt completo e usam call_adk_agent
# ==========================
def assistente_acessibilidade(mensagem: str) -> str:
    # O prompt completo é construído aqui, como no exemplo do curso
    prompt_completo = f"""Pergunta do usuário: {mensagem}
---
Instruções para o agente:
{ASSISTENTE_ACESSIBILIDADE_AGENT_DEF.instruction}""" # Reutiliza a instrução base
    return call_adk_agent(ASSISTENTE_ACESSIBILIDADE_AGENT_DEF, prompt_completo, "assistente_acessibilidade")

def validador_resposta(texto_para_validar: str) -> str:
    prompt_completo = f"""Resposta a ser validada:
---
{texto_para_validar}
---
Instruções para o agente:
{VALIDADOR_RESPOSTA_AGENT_DEF.instruction}"""
    return call_adk_agent(VALIDADOR_RESPOSTA_AGENT_DEF, prompt_completo, "validador_resposta")

def revisor_clareza(texto_para_revisar: str) -> str:
    prompt_completo = f"""Texto a ser revisado:
---
{texto_para_revisar}
---
Instruções para o agente:
{REVISOR_CLAREZA_AGENT_DEF.instruction}"""
    return call_adk_agent(REVISOR_CLAREZA_AGENT_DEF, prompt_completo, "revisor_clareza")

def testabilidade(pergunta_original: str, contexto_resposta: str) -> str:
    prompt_completo = f"""Contexto:
Pergunta original do usuário: "{pergunta_original}"
Resposta fornecida ao usuário:
---
{contexto_resposta}
---
Instruções para o agente:
{TESTABILIDADE_AGENT_DEF.instruction}"""
    return call_adk_agent(TESTABILIDADE_AGENT_DEF, prompt_completo, "testabilidade")

def aprofundador(pergunta_original: str, contexto_resposta: str) -> str:
    prompt_completo = f"""Contexto:
Pergunta original do usuário: "{pergunta_original}"
Resposta fornecida ao usuário:
---
{contexto_resposta}
---
Instruções para o agente:
{APROFUNDADOR_AGENT_DEF.instruction}"""
    return call_adk_agent(APROFUNDADOR_AGENT_DEF, prompt_completo, "aprofundador")


# ... (validador_links, _eh_erro_adk e pipeline_acessibilidade permanecem os mesmos)
# A função _eh_erro_adk já deve cobrir os erros de call_adk_agent.

def validador_links(texto_com_links: str) -> str:
    if texto_com_links.startswith(("Erro ao executar agente ADK", "Erro no agente ADK", "Agente ADK")):
        return "Validação de links não realizada devido a erro na etapa anterior."
    links = re.findall(r'https?://\S+', texto_com_links)
    if not links: return "Nenhum link encontrado para validação."
    resultados = []
    for link in links:
        link_limpo = re.sub(r'[.,)!?]$', '', link)
        try:
            response = requests.head(link_limpo, timeout=7, allow_redirects=True)
            status_emoji = "✅" if 200 <= response.status_code < 400 else "❌"
            resultados.append(f"{status_emoji} {link_limpo} (Status: {response.status_code})")
        except requests.exceptions.Timeout: resultados.append(f"⚠️ {link_limpo} (Timeout)")
        except requests.exceptions.RequestException: resultados.append(f"❌ {link_limpo} (Quebrado/inacessível)")
    return "\n".join(resultados) if resultados else "Nenhum link encontrado."

def _eh_erro_adk(resultado_agente: str) -> bool:
    return resultado_agente.startswith(("Erro ao executar agente ADK", "Erro no agente ADK", "Agente ADK")) or \
           "Resposta em formato inesperado" in resultado_agente

def pipeline_acessibilidade(pergunta: str) -> str:
    if not pergunta or pergunta.strip() == "":
        return "Por favor, digite uma pergunta sobre acessibilidade digital."

    resposta_inicial = assistente_acessibilidade(pergunta)
    if _eh_erro_adk(resposta_inicial):
        return f"Falha ao processar sua pergunta.\nDetalhes: {resposta_inicial}"

    texto_para_validacao = resposta_inicial
    resposta_revisada_clareza = revisor_clareza(resposta_inicial)
    if not _eh_erro_adk(resposta_revisada_clareza) and "não pode prosseguir" not in resposta_revisada_clareza:
        texto_para_validacao = resposta_revisada_clareza

    resposta_final_principal = texto_para_validacao
    resposta_validada_tecnicamente = validador_resposta(texto_para_validacao)
    if not _eh_erro_adk(resposta_validada_tecnicamente) and "não pode prosseguir" not in resposta_validada_tecnicamente:
        resposta_final_principal = resposta_validada_tecnicamente

    resultado_validacao_links = validador_links(resposta_final_principal)

    sugestoes_testabilidade = testabilidade(pergunta, resposta_final_principal)
    if _eh_erro_adk(sugestoes_testabilidade):
        sugestoes_testabilidade = "Não foi possível gerar sugestões de teste desta vez."

    sugestoes_aprofundamento = aprofundador(pergunta, resposta_final_principal)
    if _eh_erro_adk(sugestoes_aprofundamento):
        sugestoes_aprofundamento = "Não foi possível gerar sugestões de aprofundamento desta vez."

    return f"""
🧠 Resposta Principal:
{resposta_final_principal}

🔗 Verificação de Links:
{resultado_validacao_links}

🧪 Como Testar ou Experimentar:
{sugestoes_testabilidade}

📚 Quer se Aprofundar?
{sugestoes_aprofundamento}
""".strip()

if __name__ == "__main__":
    if not GOOGLE_API_KEY:
        print("A variável GOOGLE_API_KEY não está definida. Crie um arquivo .env.")
    else:
        print("ADK configurado com call_adk_agent. Tentando executar o pipeline...")
        perguntas_teste = ["O que é contraste de cores?", "WCAG", "Fale sobre leitores de tela e como testá-los."]
        for pergunta_teste in perguntas_teste:
            print(f"\n--- Testando Pergunta: '{pergunta_teste}' ---")
            resposta_completa = pipeline_acessibilidade(pergunta_teste)
            print(resposta_completa)
            print("--------------------------------------")