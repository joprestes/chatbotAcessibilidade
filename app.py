import streamlit as st
import os
import asyncio
from dotenv import load_dotenv
from chatbot_acessibilidade.agent import pipeline_acessibilidade

# ========================
# Configuração inicial
# ========================
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("A variável GOOGLE_API_KEY não foi encontrada no arquivo .env.")
    st.stop()

st.set_page_config(
    page_title="Chatbot de Acessibilidade Digital",
    page_icon="♿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("♿ Chatbot de Acessibilidade Digital")
st.markdown("Digite uma pergunta sobre acessibilidade digital.")

# ========================
# Entrada do usuário
# ========================
pergunta = st.text_area("💬 Sua pergunta:", height=100)

if st.button("Responder"):
    if not pergunta.strip():
        st.warning("Por favor, digite uma pergunta antes de continuar.")
    else:
        with st.spinner("Gerando resposta..."):

            try:
                resposta = asyncio.run(pipeline_acessibilidade(pergunta))
                st.markdown("---")
                st.markdown(resposta)

            except RuntimeError:
                # Compatibilidade com ambientes que já possuem um loop ativo (Streamlit Cloud, Jupyter)
                loop = asyncio.get_event_loop()
                resposta = loop.run_until_complete(pipeline_acessibilidade(pergunta))
                st.markdown("---")
                st.markdown(resposta)

            except Exception as e:
                st.error(f"❌ Ocorreu um erro ao processar sua pergunta: {e}")

st.markdown("---")
st.caption("🛠️ Desenvolvido para promover inclusão digital por meio de acessibilidade.")
