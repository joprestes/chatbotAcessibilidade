<p align="center">
  <img src="assets/banner.png" alt="Banner com o título Chatbot de Acessibilidade Digital, ilustração de interface e ícones de acessibilidade como teclado, contraste e leitor de tela" width="100%">
</p>
<p align="center">
  <strong>Um assistente inteligente para tornar a web mais acessível. 💡</strong>
</p>

# ♿ Chatbot de Acessibilidade Digital

Um assistente inteligente para responder dúvidas sobre acessibilidade digital, com foco em qualidade de software e usabilidade para pessoas com deficiência.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## ✨ Visão Geral

Este projeto é um chatbot acessível e didático, voltado para profissionais, desenvolvedores e equipes de qualidade que desejam tirar dúvidas sobre acessibilidade digital. A solução utiliza a API Gemini da Google (via Google ADK) para gerar respostas completas, testáveis e com referências confiáveis.

💬 Exemplos de perguntas:
- Como testar contraste de cores?
- O que é navegação por teclado?
- Como tornar um site acessível a leitores de tela?

---

## 🔍 Funcionalidades

✅ Respostas claras com exemplos práticos  
✅ Validação técnica com base em WCAG e ARIA  
✅ Reescrita para linguagem acessível e inclusiva  
✅ Sugestões de testes práticos com ferramentas como axe, NVDA, Lighthouse  
✅ Recomendações de estudo com links úteis, cursos e livros

---

## 🧠 Arquitetura

O projeto é organizado em módulos, com agentes especializados para cada etapa da resposta:

```
chatbot_acessibilidade/
│
├── agents/               # Define os agentes (assistente, revisor, etc.)
├── core/                 # Funções utilitárias (ex: validadores, formatadores)
├── pipeline.py           # Pipeline principal que orquestra todos os agentes
├── app.py                # Frontend com Streamlit
└── .env                  # Chave da API Google (não versionar)
```

---

## 🚀 Como Executar Localmente

1. Clone o repositório:

```bash
git clone https://github.com/seuusuario/chatbot-acessibilidade.git
cd chatbot-acessibilidade
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Configure a variável de ambiente:

Crie um arquivo `.env` com sua chave da API Google:

```
GOOGLE_API_KEY=coloque_sua_chave_aqui
```

4. Execute a aplicação com o Streamlit:

```bash
streamlit run app.py
```

---

## 📚 Tecnologias Utilizadas

- Python 3.10+
- [Google ADK (Gemini)](https://ai.google.dev/)
- Streamlit
- dotenv
- Ferramentas de acessibilidade (axe, NVDA, Lighthouse etc.)

---

## 🙋 Sobre a Autora

Desenvolvido por **Joelma De Oliveira Prestes Ferreira**, Líder de Engenharia de qualidade com mais de 4 anos de experiência em testes, acessibilidade e automação de software.

🔗 [LinkedIn](https://www.linkedin.com/in/joprestes84/)  
💌 joprestes@hotmail.copm

---

## 📄 Licença

Este projeto está licenciado sob os termos da [MIT License](LICENSE).
