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
if "resposta" in st.session_state:
    st.markdown("---")
    st.markdown(st.session_state.resposta)

# Espaço reservado para não esconder a resposta
st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

# ========================
# Campo de entrada com avatar fixo no rodapé
# ========================
st.markdown("<div class='input-container'>", unsafe_allow_html=True)

with st.form("pergunta_form"):
    pergunta = st.text_input("Digite sua pergunta sobre acessibilidade digital:", label_visibility="collapsed")
    enviar = st.form_submit_button("Enviar")

st.markdown("</div>", unsafe_allow_html=True)

# ========================
# Geração da resposta
# ========================
if enviar and pergunta.strip():
    with st.spinner("🔎 Gerando resposta..."):
        try:
            resposta = asyncio.run(pipeline_acessibilidade(pergunta))
        except RuntimeError:
            loop = asyncio.get_event_loop()
            resposta = loop.run_until_complete(pipeline_acessibilidade(pergunta))
        except Exception as e:
            resposta = f"❌ Ocorreu um erro ao processar sua pergunta: {e}"

        st.session_state.resposta = resposta
        st.rerun()

# ========================
# Rodapé
# ========================
st.markdown("---")
st.caption("🛠️ Desenvolvido para promover inclusão digital por meio de acessibilidade.\nPor Joelma De Oliveira Prestes Ferreira.")