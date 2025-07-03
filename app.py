import streamlit as st
import os
import asyncio
from dotenv import load_dotenv
from chatbot_acessibilidade.pipeline import pipeline_acessibilidade

# ========================
# Configuração do ambiente
# ========================
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("❌ A variável GOOGLE_API_KEY não foi encontrada no arquivo .env.")
    st.stop()

# ========================
# Configuração da página
# ========================
st.set_page_config(
    page_title="Chatbot de Acessibilidade Digital",
    page_icon="♿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ========================
# Carregamento do estilo
# ========================
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ========================
# Banner com descrição via caption (renderizado com st.image)
# ========================
st.image(
    "assets/banner.webp",
    caption="Acessibilidade com Qualidade — desenvolvido por Joelma De O. Prestes Ferreira",
    use_container_width=True
)

# ========================
# Instrução
# ========================
col1, col2 = st.columns([7.5, 2.5])
with col1:
    st.markdown("""
    <div style='padding: 12px; background-color: #f5f5f5; border-radius: 10px; margin-top: 10px; font-size: 16px'>
      👋 Olá! Meu nome é <strong>Jota</strong> e estou aqui para te ajudar a entender mais sobre <strong>acessibilidade digital</strong>, com foco em <strong>qualidade de software</strong>.  
      O que vamos pesquisar hoje?
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.image("assets/avatar.webp", width=150)

# ========================
# Exibir resposta anterior (se houver)
# ========================

# Inicializa o histórico de mensagens se não existir
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe o histórico de mensagens na tela
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# Campo de entrada do chat no rodapé da página
if prompt := st.chat_input("Digite sua pergunta sobre acessibilidade digital:"):
    
    # Adiciona e exibe a pergunta do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gera e exibe a resposta do assistente
    with st.chat_message("assistant"):
        with st.spinner("🔎 Gerando resposta..."):
            try:
                # Mantém a lógica assíncrona original para chamar o pipeline
                try:
                    resposta = asyncio.run(pipeline_acessibilidade(prompt))
                except RuntimeError:
                    loop = asyncio.get_event_loop()
                    resposta = loop.run_until_complete(pipeline_acessibilidade(prompt))
                
                st.markdown(resposta, unsafe_allow_html=True)
                # Adiciona a resposta do bot ao histórico
                st.session_state.messages.append({"role": "assistant", "content": resposta})

            except Exception as e:
                error_message = f"❌ Ocorreu um erro ao processar sua pergunta: {e}"
                st.error(error_message)
                # Adiciona a mensagem de erro ao histórico para referência
                st.session_state.messages.append({"role": "assistant", "content": error_message})

# --- Rodapé ---
st.markdown("---")
st.caption("🛠️ Desenvolvido para promover inclusão digital por meio de acessibilidade.\nPor Joelma De Oliveira Prestes Ferreira.")
