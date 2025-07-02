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
# Cabeçalho e introdução
# ========================
st.title("♿ Chatbot de Acessibilidade Digital")
st.image("assets/banner.png", caption="Banner com título e ícones de acessibilidade", use_container_width=True)
st.markdown("Digite abaixo uma pergunta sobre acessibilidade digital. O chatbot vai responder com base nas melhores práticas e diretrizes como WCAG, ARIA, entre outras.")

# ========================
# Exibir resposta anterior (se houver)
# ========================
if "resposta" in st.session_state:
    st.markdown("---")
    st.markdown(st.session_state.resposta)

# Espaço reservado para não esconder a resposta
st.markdown("<div style='height: 150px;'></div>", unsafe_allow_html=True)

# ========================
# Campo de entrada fixo no rodapé
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