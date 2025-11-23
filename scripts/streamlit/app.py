import streamlit as st
import os
import sys
import asyncio
import base64
from pathlib import Path
from dotenv import load_dotenv

# Adiciona src ao path para imports
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from chatbot_acessibilidade.pipeline import pipeline_acessibilidade  # noqa: E402


# ========================
# FUNÇÃO AUXILIAR PARA IMAGENS
# ========================
@st.cache_data
def get_image_as_base64(path):
    """Lê um arquivo de imagem e o converte para uma string Base64."""
    try:
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        st.error(f"Arquivo de imagem não encontrado em: {path}")
        return None


# ========================
# CONFIGURAÇÃO DO AMBIENTE
# ========================
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("❌ A variável GOOGLE_API_KEY não foi encontrada no arquivo .env.")
    st.stop()

# ========================
# CONFIGURAÇÃO DA PÁGINA
# ========================
st.set_page_config(
    page_title="Chatbot de Acessibilidade Digital",
    page_icon="♿",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ========================
# CARREGAMENTO DE ESTILOS E CORREÇÃO DE TEMA
# ========================
# CSS injetado diretamente para garantir a compatibilidade com tema claro/escuro.
# Esta é a solução mais robusta para os problemas de cor.
st.markdown(
    """
<style>
/* Garante que o fundo de TODAS as bolhas de chat se adapte ao tema */
div[data-testid="chat-message-container"] {
    background-color: var(--secondary-background-color);
    border-radius: 10px;
}

/* Força TUDO (texto, ícones, etc.) dentro da bolha a usar a cor do tema */
div[data-testid="chat-message-container"] * {
    color: var(--text-color) !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# ========================
# BANNER E INTRODUÇÃO
# ========================
# Carregando imagens como Base64 para garantir que sempre apareçam.
img_base64_banner = get_image_as_base64("static/images/banner.webp")
if img_base64_banner:
    st.markdown(
        f"""
        <img src="data:image/webp;base64,{img_base64_banner}" alt="Banner Acessibilidade com Qualidade, por Joelma Ferreira" style="width: 100%; border-radius: 10px;">
        <p style="text-align: center; color: var(--text-color); font-size: 14px; margin-top: 5px;">
            Acessibilidade com Qualidade — desenvolvido por Joelma De O. Prestes Ferreira
        </p>
        """,
        unsafe_allow_html=True,
    )

col1, col2 = st.columns([7.5, 2.5])
with col1:
    st.markdown(
        """
    <div style='
        padding: 12px; 
        background-color: var(--secondary-background-color); 
        color: var(--text-color);
        border-radius: 10px; 
        margin-top: 10px; 
        font-size: 16px;
    '>
     👋 Opa! Eu sou a <strong>Ada</strong> — seu bot de confiança pra falar sobre <strong>acessibilidade digital</strong> com foco em <strong>qualidade de software</strong>.
Se você é de QA e quer deixar seus testes mais inclusivos, tá no lugar certo! Bora validar a acessibilidade juntos? ✅♿
    </div>
    """,
        unsafe_allow_html=True,
    )

with col2:
    img_base64_avatar = get_image_as_base64("static/images/avatar.webp")
    if img_base64_avatar:
        st.markdown(
            f"""
    <img src="data:image/webp;base64,{img_base64_avatar}" 
         alt="Avatar da Ada, o assistente virtual baseada em Ada Lovelace a primeira mulher programadora" 
         width="150" 
         style="
             float: right; 
             margin-top: 10px; 
             border-bottom-left-radius: 75px; 
             border-bottom-right-radius: 75px;
             border-top-left-radius: 10px;
             border-top-right-radius: 10px;
             overflow: hidden;
         ">
    """,
            unsafe_allow_html=True,
        )

# ========================
# LÓGICA DO CHAT
# ========================

# Inicializa o histórico de mensagens se não existir
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe o histórico de mensagens na tela
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Se for uma mensagem do usuário, apenas exibe o texto
        if message["role"] == "user":
            st.markdown(message["content"])
        # Se for uma mensagem do assistente, renderiza os expanders
        elif message["role"] == "assistant":
            resposta_dict = message["content"]
            if isinstance(resposta_dict, dict) and "erro" not in resposta_dict:
                for i, (titulo, conteudo) in enumerate(resposta_dict.items()):
                    expandido = i == 0
                    with st.expander(titulo, expanded=expandido):
                        st.markdown(conteudo, unsafe_allow_html=True)
            elif isinstance(resposta_dict, dict) and "erro" in resposta_dict:
                st.error(resposta_dict["erro"])
            else:  # Fallback para erros inesperados
                st.error("Ocorreu um erro ao exibir a resposta.")

# Campo de entrada do chat que fica fixo no rodapé
if prompt := st.chat_input("Digite sua pergunta sobre acessibilidade digital:"):

    # Adiciona e exibe a pergunta do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gera e exibe a resposta do assistente
    with st.chat_message("assistant"):
        with st.spinner("🔎 Gerando resposta..."):
            resposta_final = None
            try:
                # Chama o pipeline assíncrono para obter o dicionário de resposta
                try:
                    resposta_dict = asyncio.run(pipeline_acessibilidade(prompt))
                except RuntimeError:
                    loop = asyncio.get_event_loop()
                    resposta_dict = loop.run_until_complete(pipeline_acessibilidade(prompt))

                resposta_final = resposta_dict

                # Renderiza a resposta como expanders
                if "erro" not in resposta_dict:
                    for i, (titulo, conteudo) in enumerate(resposta_dict.items()):
                        expandido = i == 0  # Deixa a introdução aberta
                        with st.expander(titulo, expanded=expandido):
                            st.markdown(conteudo, unsafe_allow_html=True)
                else:
                    st.error(resposta_dict["erro"])

            except Exception as e:
                # Captura qualquer outra exceção e formata como erro
                error_dict = {"erro": f"❌ Ocorreu um erro inesperado: {e}"}
                resposta_final = error_dict
                st.error(error_dict["erro"])

            # Adiciona a resposta final (o dicionário) ao histórico
            if resposta_final:
                st.session_state.messages.append({"role": "assistant", "content": resposta_final})
