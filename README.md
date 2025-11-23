
# ♿ Chatbot de Acessibilidade Digital | Digital Accessibility Chatbot

<p align="center">
  <a href="#-versão-em-português">Português 🇧🇷</a> | 
  <a href="#-english-version">English 🇺🇸</a>
</p>

<p align="center">
  <img
    src="assets/banner.webp"
    alt="Banner com fundo escuro e ícone azul de acessibilidade representando uma pessoa estilizada com braços abertos em círculos conectados. À direita, o texto: 'Acessibilidade com Qualidade', seguido por 'Desenvolvido por: Joelma De O. Prestes Ferreira' e, abaixo, a frase: 'Assistente inteligente com arquitetura multiagente utilizando Gemini 2.0 Flash'."
    width="100%">
</p>

<p align="center">
  <strong>Um assistente inteligente para tornar a web mais acessível. 💡</strong>
</p>

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 🇧🇷 Versão em Português

### ✨ Visão Geral

Este projeto é um chatbot acessível e didático, voltado para profissionais, desenvolvedores e equipes de qualidade que desejam tirar dúvidas sobre acessibilidade digital. A solução utiliza a API Gemini da Google (via Google ADK) para gerar respostas completas, testáveis e com referências confiáveis.

💬 **Exemplos de perguntas:**
- Como testar contraste de cores?
- O que é navegação por teclado?
- Como tornar um site acessível a leitores de tela?

### 🔍 Funcionalidades

✅ Respostas claras com exemplos práticos  
✅ Validação técnica com base em WCAG e ARIA  
✅ Reescrita para linguagem acessível e inclusiva  
✅ Sugestões de testes práticos com ferramentas como axe, NVDA, Lighthouse  
✅ Recomendações de estudo com links úteis, cursos e livros  

### 🧠 Arquitetura

```
chatbot-acessibilidade/
├── chatbot_acessibilidade/
│   ├── agents/           # Define os agentes (assistente, revisor, etc.)
│   ├── core/             # Funções utilitárias (formatadores, etc.)
│   └── pipeline.py       # Orquestra os agentes para gerar a resposta
├── backend/
│   └── api.py            # API FastAPI (novo frontend)
├── frontend/
│   ├── index.html        # Interface HTML (novo frontend)
│   ├── styles.css        # Estilos acessíveis
│   └── app.js            # Lógica JavaScript
├── tests/                # Testes unitários com pytest
├── assets/               # Imagens e CSS
├── app.py                # Interface com Streamlit (alternativa)
├── requirements.txt      # Dependências do projeto
├── setup.sh              # Script de instalação
└── .env                  # Chave da API Google (não versionar)
```

### 🚀 Como Executar Localmente

```bash
git clone https://github.com/seu-usuario/chatbot-acessibilidade.git
cd chatbot-acessibilidade
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Crie um arquivo `.env` com sua chave:
```env
GOOGLE_API_KEY="sua_chave_aqui"
```

**Opção 1: Frontend Web (Recomendado)**
```bash
uvicorn backend.api:app --reload --port 8000
```
Acesse: http://localhost:8000

**Opção 2: Interface Streamlit (Alternativa)**
```bash
streamlit run app.py
```

### ✅ Testes Unitários

```bash
pytest -v
pytest --html=relatorio_testes.html --self-contained-html
```

### 🧑‍🦽 Acessibilidade Otimizada

- Contraste reforçado e fontes legíveis  
- Foco visível para teclado  
- Labels e descrições para leitores de tela  

### ☁️ Deploy com Streamlit Cloud

- Acesse: https://streamlit.io/cloud  
- Conecte ao GitHub e selecione o repositório  
- Configure o Secret `GOOGLE_API_KEY`  
- Clique em “Deploy”  

### 📚 Tecnologias Utilizadas

- Python 3.10+  
- Google Gemini API (via Google ADK)  
- FastAPI (API REST)  
- HTML/CSS/JavaScript (Frontend)  
- Streamlit (Interface alternativa)  
- Pytest  

### 🙋 Sobre a Autora

Desenvolvido por Joelma De Oliveira Prestes Ferreira.  
* 🔗 [LinkedIn](https://www.linkedin.com/in/joprestes84/)  
* 📧 joprestes@hotmail.com  
* 🔗 [Medium](https://medium.com/@joprestes)


### 📄 Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

*(Uma tradução não-oficial para o português está disponível [aqui](LICENSE.pt-BR.md).)*
---

## 🇺🇸 English Version

### ✨ Overview

This project is an accessible and educational chatbot aimed at professionals, developers, and QA teams who want to learn more about digital accessibility. It uses Google’s Gemini API (via Google ADK) to generate comprehensive, verifiable responses with trusted references.

💬 **Example questions:**
- How do I test color contrast?
- What is keyboard navigation?
- How to make a website accessible to screen readers?

### 🔍 Features

✅ Clear answers with practical examples  
✅ Technical validation based on WCAG and ARIA  
✅ Rewritten for accessible and inclusive language  
✅ Practical testing suggestions with tools like axe, NVDA, and Lighthouse  
✅ Study recommendations with useful links, courses, and books  

### 🧠 Project Structure

```
chatbot-acessibilidade/
├── chatbot_acessibilidade/
│   ├── agents/           # Defines agents (assistant, reviewer, etc.)
│   ├── core/             # Utility functions (formatters, etc.)
│   └── pipeline.py       # Orchestrates agents to generate the response
├── backend/
│   └── api.py            # FastAPI (new frontend)
├── frontend/
│   ├── index.html        # HTML interface (new frontend)
│   ├── styles.css        # Accessible styles
│   └── app.js            # JavaScript logic
├── tests/                # Unit tests with pytest
├── assets/               # Images and CSS
├── app.py                # Streamlit interface (alternative)
├── requirements.txt      # Project dependencies
├── setup.sh              # Installation script
└── .env                  # Google API key (do not version)
```

### 🚀 Running Locally

```bash
git clone https://github.com/your-user/chatbot-acessibilidade.git
cd chatbot-acessibilidade
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set your API key in a `.env` file:
```env
GOOGLE_API_KEY="your_api_key_here"
```

**Option 1: Web Frontend (Recommended)**
```bash
uvicorn backend.api:app --reload --port 8000
```
Access: http://localhost:8000

**Option 2: Streamlit Interface (Alternative)**
```bash
streamlit run app.py
```

### ✅ Unit Tests

```bash
pytest -v
pytest --html=test_report.html --self-contained-html
```

### 🧑‍🦽 Optimized Accessibility

- Enhanced contrast and legible fonts  
- Visible focus for keyboard users  
- Labels and image descriptions for screen readers  

### ☁️ Deploy to Streamlit Cloud

- Go to: https://streamlit.io/cloud  
- Connect your GitHub account and select the repository  
- Add your API key as a "Secret": `GOOGLE_API_KEY`  
- Click “Deploy”  

### 📚 Tech Stack

- Python 3.10+  
- Google Gemini API (via Google ADK)  
- FastAPI (REST API)  
- HTML/CSS/JavaScript (Frontend)  
- Streamlit (Alternative interface)  
- Pytest  

### 🙋 About the Author

Developed by Joelma De Oliveira Prestes Ferreira.  
* 🔗 [LinkedIn](https://www.linkedin.com/in/joprestes84/)  
* 📧 joprestes@hotmail.com  
* 🔗 [Medium](https://medium.com/@joprestes)


---

### 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

*(An unofficial Portuguese translation is available [here](LICENSE.pt-BR.md).)*
