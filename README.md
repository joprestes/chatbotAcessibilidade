<div align="center">

# ♿ Chatbot de Acessibilidade Digital

**Um assistente inteligente para tornar a web mais acessível** 💡

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000?style=for-the-badge)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-98%25%2B-success?style=for-the-badge)](docs/TESTES.md)
[![WCAG](https://img.shields.io/badge/WCAG-2.1%20AA-7C3AED?style=for-the-badge)](https://www.w3.org/WAI/WCAG21/quickref/)
[![CI](https://github.com/joprestes/chatbotAcessibilidade/workflows/CI/badge.svg)](https://github.com/joprestes/chatbotAcessibilidade/actions)

[Português 🇧🇷](#-versão-em-português) | [English 🇺🇸](#-english-version)

---

<img
  src="assets/banner.webp"
  alt="Banner Acessibilidade com Qualidade"
  width="100%"
  style="border-radius: 10px; margin: 20px 0; box-shadow: 0 4px 12px rgba(124, 58, 237, 0.2);">

**Desenvolvido por:** [Joelma De O. Prestes Ferreira](https://www.linkedin.com/in/joprestes84/)

[![GitHub stars](https://img.shields.io/github/stars/joprestes/chatbotAcessibilidade?style=social)](https://github.com/joprestes/chatbotAcessibilidade)
[![GitHub forks](https://img.shields.io/github/forks/joprestes/chatbotAcessibilidade?style=social)](https://github.com/joprestes/chatbotAcessibilidade)

</div>

---

## 📑 Índice

<details>
<summary>📋 Clique para expandir</summary>

- [🇧🇷 Versão em Português](#-versão-em-português)
  - [✨ Visão Geral](#-visão-geral)
  - [🎯 Funcionalidades](#-funcionalidades)
  - [🏗️ Arquitetura](#️-arquitetura)
  - [🚀 Quick Start](#-quick-start)
  - [📖 Documentação](#-documentação)
  - [🧪 Testes e Qualidade](#-testes-e-qualidade)
  - [🔒 Segurança](#-segurança)
  - [🌐 Deploy](#-deploy)
  - [🛠️ Tecnologias](#️-tecnologias)
  - [👤 Sobre a Autora](#-sobre-a-autora)
- [🇺🇸 English Version](#-english-version)

</details>

---

## 🇧🇷 Versão em Português

### ✨ Visão Geral

O **Chatbot de Acessibilidade Digital** é uma solução inteligente e educativa desenvolvida para profissionais, desenvolvedores e equipes de QA que buscam aprimorar seus conhecimentos sobre acessibilidade digital.

Utilizando a **API Gemini 2.0 Flash** da Google (via Google ADK) com **fallback automático** para múltiplos LLMs via OpenRouter, o chatbot gera respostas completas, testáveis e com referências confiáveis, seguindo os padrões **WCAG 2.1 AA** e **ARIA**.

#### 🎯 Por que usar este projeto?

<div align="center">

| 🎓 **Educativo** | ⚡ **Rápido** | 🔒 **Confiável** | ♿ **Acessível** |
|:---:|:---:|:---:|:---:|
| Respostas completas com exemplos práticos | Interface moderna e responsiva | Validação técnica WCAG/ARIA | Interface 100% acessível (WCAG AA) |
| Materiais de estudo recomendados | Cache inteligente | Rate limiting e segurança | Navegação por teclado completa |
| Sugestões de testes práticos | Fallback automático entre LLMs | Logging estruturado | Suporte a leitores de tela |

</div>

#### 💬 Exemplos de Perguntas

<div align="center">

| 📝 Categoria | 💡 Exemplo |
|:---:|:---|
| **🧪 Testes** | Como testar contraste de cores? |
| **⌨️ Navegação** | O que é navegação por teclado? |
| **🔊 Leitores de Tela** | Como tornar um site acessível a leitores de tela? |
| **📋 WCAG** | Quais são os critérios de sucesso do WCAG 2.1? |
| **🛠️ Ferramentas** | Quais ferramentas usar para testar acessibilidade? |

</div>

---

### 🎯 Funcionalidades

<div align="center">

#### 🎨 Interface Moderna

| ✨ Recurso | 📱 Descrição |
|:---:|:---|
| **🎨 Design "Lavanda Inclusiva"** | Paleta de cores roxo/lilás com contraste WCAG AA/AAA |
| **📐 Layout Profissional** | Card de introdução, mensagens estilo card, hierarquia visual clara |
| **🌙 Tema Claro/Escuro** | Dark mode "Beringela" com transições suaves |
| **📝 Textarea Auto-expansível** | Cresce automaticamente conforme o usuário digita |
| **🔔 Toast Notifications** | Notificações acessíveis com `aria-live` |
| **⏳ Skeleton Loading** | Feedback visual durante processamento |
| **👤 Avatares e Timestamps** | Identificação visual clara das mensagens |
| **🔍 Busca no Histórico** | Busque mensagens anteriores rapidamente |

#### 🔧 Recursos Técnicos

| ⚙️ Recurso | 🚀 Descrição |
|:---:|:---|
| **🤖 Multiagente Especializado** | 5 agentes trabalhando em conjunto |
| **🔄 Fallback Automático** | Múltiplos LLMs via OpenRouter |
| **⚡ Cache Inteligente** | Respostas em cache com invalidação semântica |
| **🛡️ Rate Limiting** | Proteção contra abuso (10 req/min) |
| **📊 Métricas de Performance** | Coleta de tempo de resposta, uso de agentes, etc. |
| **🧪 Testes E2E Completos** | Suite completa de testes end-to-end |
| **📝 Logging Estruturado** | Rastreamento completo de atividades |

#### 📚 Conteúdo Educativo

| 🎓 Recurso | 📖 Descrição |
|:---:|:---|
| **✅ Validação Técnica** | Verificação automática WCAG/ARIA |
| **📝 Exemplos Práticos** | Código e exemplos testáveis |
| **🧪 Sugestões de Testes** | Testes práticos recomendados |
| **📚 Materiais de Estudo** | Links e referências confiáveis |
| **💡 Dicas Finais** | Resumos e lembretes importantes |

</div>

#### 🧠 Arquitetura Multiagente

O chatbot utiliza **5 agentes especializados** trabalhando em conjunto:

<div align="center">

| 🤖 Agente | 📋 Responsabilidade | ⚡ Execução |
|:---:|:---|:---:|
| **Assistente** | Gera a resposta inicial completa | Sequencial |
| **Validador** | Valida técnica (WCAG, ARIA) | Sequencial |
| **Revisor** | Simplifica a linguagem | Sequencial |
| **Testador** | Sugere testes práticos | Paralelo |
| **Aprofundador** | Recomenda materiais de estudo | Paralelo |

</div>

---

### 🏗️ Arquitetura

```
chatbot-acessibilidade/
├── 📚 docs/                       # Documentação completa
│   ├── CHANGELOG.md              # Histórico de mudanças
│   ├── REGRAS_REVISAO.md         # Regras e padrões (inclui linters)
│   ├── DEPLOY.md                 # Guia de deploy
│   └── TESTES.md                 # Documentação de testes
│
├── 🤖 src/                       # Código fonte
│   ├── chatbot_acessibilidade/   # Core do chatbot
│   │   ├── agents/               # Agentes especializados
│   │   ├── core/                 # Utilitários e formatters
│   │   └── pipeline.py           # Orquestração dos agentes
│   └── backend/                  # API REST
│       └── api.py                # FastAPI endpoints
│
├── 💻 frontend/                  # Interface Web
│   ├── index.html                # HTML acessível
│   ├── styles.css                # Estilos responsivos
│   └── app.js                    # Lógica JavaScript
│
├── 🧪 tests/                     # Testes automatizados
│   ├── unit/                     # Testes unitários
│   ├── integration/              # Testes de integração
│   ├── e2e/                      # Testes end-to-end
│   └── reports/                  # Relatórios de testes
│
├── 📦 static/                     # Recursos estáticos
│   └── images/                   # Imagens (banner, avatar)
│
├── 🔧 scripts/                   # Scripts auxiliares
│   └── setup/                    # Scripts de configuração
│
├── 📄 README.md                   # Este arquivo
├── ⚙️  requirements.txt          # Dependências Python
├── 🛠️  pyproject.toml            # Configuração do projeto
├── 🔨 Makefile                   # Comandos de automação
└── 📜 LICENSE                    # Licença do projeto
```

---

### 🚀 Quick Start

#### 📋 Pré-requisitos

- ✅ Python 3.12 ou superior (recomendado 3.12.x)
- ✅ Chave da API Google Gemini
- ✅ Git

#### 🔧 Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/joprestes/chatbotAcessibilidade.git
cd chatbotAcessibilidade

# 2. Crie e ative o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt
```

#### 🔑 Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
# Chave da API Google Gemini (obrigatória)
GOOGLE_API_KEY="sua_chave_aqui"

# OpenRouter (opcional - para fallback automático)
OPENROUTER_API_KEY="sua_chave_openrouter"
FALLBACK_ENABLED=true
OPENROUTER_MODELS=meta-llama/llama-3.3-70b-instruct:free,google/gemini-flash-1.5:free,mistralai/mistral-7b-instruct:free

# CORS (opcional - padrão: *)
CORS_ORIGINS="*"

# Rate Limiting (opcional)
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=10

# Logging (opcional)
LOG_LEVEL=INFO
```

> 💡 **Dica:** Veja `.env.example` para todas as opções disponíveis.

#### 🔄 Sistema de Fallback Automático

O chatbot agora suporta **fallback automático** entre múltiplos LLMs:

1. **Provedor Primário**: Google Gemini (padrão)
2. **Provedor Secundário**: OpenRouter com modelos gratuitos
3. **Comportamento**: Se o Gemini esgotar quota ou falhar, o sistema automaticamente tenta modelos OpenRouter em sequência

**Modelos OpenRouter Gratuitos Recomendados:**
- `meta-llama/llama-3.3-70b-instruct:free`
- `google/gemini-flash-1.5:free`
- `mistralai/mistral-7b-instruct:free`
- `qwen/qwen-2.5-7b-instruct:free`
- `microsoft/phi-3-medium-4k-instruct:free`

**Para habilitar o fallback:**
1. Obtenha uma chave API do [OpenRouter](https://openrouter.ai/)
2. Configure `OPENROUTER_API_KEY` no `.env`
3. Configure `FALLBACK_ENABLED=true`
4. Opcionalmente, ajuste `OPENROUTER_MODELS` com seus modelos preferidos

#### ▶️ Execução

**Frontend Web Moderno** ⭐

```bash
uvicorn src.backend.api:app --reload --port 8000
```

Acesse: **http://localhost:8000**

#### 🔧 Troubleshooting

**Erro: "GOOGLE_API_KEY não encontrada"**
- Verifique se o arquivo `.env` existe na raiz do projeto
- Certifique-se de que contém: `GOOGLE_API_KEY="sua_chave_aqui"`

**Erro: "fallback_enabled=True requer openrouter_api_key configurada"**
- Se você habilitou o fallback, configure `OPENROUTER_API_KEY` no `.env`
- Ou desabilite o fallback: `FALLBACK_ENABLED=false`

**Erro: "Frontend não encontrado"**
- Verifique se a pasta `frontend/` existe com os arquivos `index.html`, `styles.css` e `app.js`

**Erro: "Assets não encontrados"**
- Verifique se a pasta `assets/` existe com as imagens `banner.webp` e `avatar.webp`

**Porta já em uso**
- Use outra porta: `uvicorn src.backend.api:app --reload --port 8001`

**Características da Interface:**
- 🎨 Layout moderno com card de introdução
- 💜 Paleta "Lavanda Inclusiva" (roxo/lilás acessível)
- 📱 Design responsivo e mobile-first
- 🔔 Toast notifications acessíveis
- ⏳ Skeleton loading durante processamento
- 📝 Textarea auto-expansível com glassmorphism
- 👤 Avatares e timestamps nas mensagens
- 🌙 Tema claro/escuro com transições suaves
- 🎯 Hierarquia visual clara e profissional

---

### 📖 Documentação

<div align="center">

| 📘 Documento | 📝 Descrição |
|:---:|:---|
| [📝 CHANGELOG.md](docs/CHANGELOG.md) | Histórico de mudanças |
| [📋 REGRAS_REVISAO.md](docs/REGRAS_REVISAO.md) | Regras e padrões do projeto (inclui linters) |
| [🚀 DEPLOY.md](docs/DEPLOY.md) | Guia completo de deploy |
| [🧪 TESTES.md](docs/TESTES.md) | Documentação de testes |
| [📚 API Interativa](http://localhost:8000/docs) | Swagger UI (quando servidor rodando) |
| [📚 API ReDoc](http://localhost:8000/redoc) | ReDoc (quando servidor rodando) |

</div>

---

### 🧪 Testes e Qualidade

#### 📊 Cobertura de Testes

<div align="center">

**98.52% de cobertura** 🎯

| Categoria | Cobertura |
|:---:|:---:|
| **Testes Unitários** | ✅ Completo |
| **Testes de Integração** | ✅ Completo |
| **Testes E2E** | ✅ Completo |
| **Total** | **98.52%** |

</div>

#### 🧪 Executar Testes

```bash
# Testes básicos
pytest -v

# Com relatório HTML
pytest --html=relatorio_testes.html --self-contained-html

# Com cobertura
pytest --cov=src --cov-report=html
```

#### 🔍 Linters e Formatação

```bash
# Instalar ferramentas
make install

# Formatar código
make format

# Verificar lint
make lint

# Verificar tipos
make type-check

# Executar todas as verificações
make check
```

> 📚 Veja [REGRAS_REVISAO.md](docs/REGRAS_REVISAO.md) para mais detalhes sobre linters e formatação.

#### 🚀 CI/CD com GitHub Actions

O projeto utiliza **GitHub Actions** para automação completa de testes e validações:

**Workflows Disponíveis:**

1. **CI (Continuous Integration)**
   - Executa em cada push e pull request
   - Valida código com `ruff` (lint) e `mypy` (type check)
   - Executa testes unitários e de integração
   - Executa testes E2E com Playwright
   - Gera relatórios de testes automaticamente

2. **Accessibility Tests**
   - Executa testes de acessibilidade com axe-core
   - Valida conformidade WCAG 2.1 AA
   - Executa diariamente via schedule e em PRs

**Status do CI:**
- ✅ Todos os testes passam automaticamente
- ✅ Relatórios disponíveis como artifacts
- ✅ Badge de status no README

**Configuração de Secrets (GitHub):**
- `GOOGLE_API_KEY` - Obrigatório para testes que usam API real
- `OPENROUTER_API_KEY` - Opcional, para testes de fallback

> 📚 Veja [TESTES.md](docs/TESTES.md) para detalhes completos sobre os testes E2E.

---

### 🔒 Segurança

O projeto implementa várias camadas de segurança:

<div align="center">

| 🔐 Recurso | 🛡️ Descrição |
|:---:|:---|
| **CORS Configurável** | Controle de origens permitidas |
| **Rate Limiting** | Proteção contra abuso (10 req/min) |
| **Validação de Entrada** | Sanitização e limites (3-2000 chars) |
| **Logging Estruturado** | Rastreamento de atividades |
| **Variáveis de Ambiente** | Segredos não versionados |
| **Headers de Segurança** | HSTS, CSP, X-Frame-Options, etc. |

</div>

---

### 🌐 Deploy

Veja o guia completo de deploy em [docs/DEPLOY.md](docs/DEPLOY.md) que inclui:
- ⚙️ Configuração de servidor web (Nginx, Caddy)
- 🔒 Configuração HTTPS com Certbot
- ☁️ CDN (Cloudflare, AWS CloudFront)
- 🔑 Variáveis de ambiente de produção
- 📊 Monitoramento e logs

#### 🐳 Docker (Em breve)

```bash
# Em desenvolvimento
docker-compose up
```

---

### 🛠️ Tecnologias

<div align="center">

| Categoria | Tecnologias |
|:---------:|:-----------|
| **🐍 Backend** | Python 3.12+, FastAPI, Uvicorn |
| **🤖 IA** | Google Gemini 2.0 Flash, Google ADK, OpenRouter (fallback) |
| **💻 Frontend** | HTML5, CSS3, JavaScript (Vanilla), Glassmorphism |
| **🧪 Testes** | Pytest, Pytest-cov, Testes E2E |
| **🔍 Qualidade** | Black, Ruff, MyPy, Pre-commit |
| **📊 Métricas** | Coleta de performance e uso |

</div>

---

### 👤 Sobre a Autora

<div align="center">

**Joelma De Oliveira Prestes Ferreira**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/joprestes84/)
[![Medium](https://img.shields.io/badge/Medium-12100E?style=for-the-badge&logo=medium&logoColor=white)](https://medium.com/@joprestes)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:joprestes@hotmail.com)

</div>

---

### 📄 Licença

Este projeto está licenciado sob a **Licença MIT**. Veja o arquivo [LICENSE](LICENSE) para detalhes.

> 📖 Uma tradução não-oficial para o português está disponível [aqui](LICENSE.pt-BR.md).

---

## 🇺🇸 English Version

### ✨ Overview

The **Digital Accessibility Chatbot** is an intelligent and educational solution developed for professionals, developers, and QA teams seeking to enhance their knowledge about digital accessibility.

Using Google's **Gemini 2.0 Flash API** (via Google ADK) with **automatic fallback** to multiple LLMs via OpenRouter, the chatbot generates comprehensive, testable responses with trusted references, following **WCAG 2.1 AA** and **ARIA** standards.

#### 💬 Example Questions

<div align="center">

| Category | Example |
|:---:|:---|
| **Testing** | How do I test color contrast? |
| **Navigation** | What is keyboard navigation? |
| **Screen Readers** | How to make a website accessible to screen readers? |
| **WCAG** | What are the WCAG 2.1 success criteria? |
| **Tools** | Which tools should I use to test accessibility? |

</div>

---

### 🎯 Features

<div align="center">

| 🎨 **Interface** | 🔧 **Technical** | 📚 **Educational** |
|:---:|:---:|:---:|
| ✅ Accessible interface (WCAG AA) | ✅ WCAG/ARIA technical validation | ✅ Practical examples |
| ✅ Modern layout with intro card | ✅ Specialized multi-agent | ✅ Testing suggestions |
| ✅ "Lavanda Inclusiva" palette | ✅ Rate limiting | ✅ Study materials |
| ✅ Light/dark theme | ✅ Structured logging | ✅ Links and references |
| ✅ Toast notifications | ✅ Performance metrics | ✅ Conversation history |
| ✅ Skeleton loading | ✅ Intelligent cache | ✅ Search in history |
| ✅ Auto-expandable textarea | ✅ Complete E2E tests | ✅ Timestamps in messages |

</div>

#### 🧠 Multi-Agent Architecture

The chatbot uses **5 specialized agents** working together:

1. **🤖 Assistant** - Generates initial response
2. **✅ Validator** - Technical validation (WCAG, ARIA)
3. **✍️ Reviewer** - Simplifies language
4. **🧪 Tester** - Suggests practical tests *(parallel)*
5. **📚 Deepener** - Recommends materials *(parallel)*

---

### 🏗️ Project Structure

```
chatbot-acessibilidade/
├── 🤖 src/                       # Source code
│   ├── chatbot_acessibilidade/   # Chatbot core
│   │   ├── agents/               # Specialized agents
│   │   ├── core/                 # Utilities and formatters
│   │   └── pipeline.py           # Agent orchestration
│   └── backend/                   # REST API
│       └── api.py                # FastAPI endpoints
│
├── 💻 frontend/                  # Web Interface
│   ├── index.html                # Accessible HTML
│   ├── styles.css                # Responsive styles
│   └── app.js                    # JavaScript logic
│
├── 🧪 tests/                     # Automated tests
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   ├── e2e/                      # End-to-end tests
│   └── reports/                  # Test reports
│
├── 📦 static/                     # Static resources
│   └── images/                   # Images (banner, avatar)
└── ⚙️  requirements.txt          # Dependencies
```

---

### 🚀 Quick Start

#### 📋 Prerequisites

- Python 3.12 or higher (recommended 3.12.x)
- Google Gemini API key
- Git

#### 🔧 Installation

```bash
# 1. Clone the repository
git clone https://github.com/joprestes/chatbotAcessibilidade.git
cd chatbotAcessibilidade

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

#### 🔑 Configuration

Create a `.env` file in the project root:

```env
# Google Gemini API key (required)
GOOGLE_API_KEY="your_api_key_here"

# CORS (optional - default: *)
CORS_ORIGINS="*"

# Rate Limiting (optional)
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=10

# Logging (optional)
LOG_LEVEL=INFO
```

> 💡 **Tip:** See `.env.example` for all available options.

#### ▶️ Running

**Modern Web Frontend** ⭐

```bash
uvicorn src.backend.api:app --reload --port 8000
```

Access: **http://localhost:8000**

**Interface Features:**
- 🎨 Modern layout with intro card
- 💜 "Lavanda Inclusiva" palette (accessible purple/lavender)
- 📱 Responsive and mobile-first design
- 🔔 Accessible toast notifications
- ⏳ Skeleton loading during processing
- 📝 Auto-expandable textarea with glassmorphism
- 👤 Avatares and timestamps in messages
- 🌙 Light/dark theme with smooth transitions
- 🎯 Clear and professional visual hierarchy

---

### 📖 Documentation

<div align="center">

| Document | Description |
|:---:|:---|
| [📝 CHANGELOG.md](docs/CHANGELOG.md) | Change history |
| [📋 REGRAS_REVISAO.md](docs/REGRAS_REVISAO.md) | Project rules and standards |
| [🚀 DEPLOY.md](docs/DEPLOY.md) | Complete deployment guide |
| [🧪 TESTES.md](docs/TESTES.md) | Testing documentation |

</div>

---

### 🧪 Testing and Quality

#### 🧪 Run Tests

```bash
# Basic tests
pytest -v

# With HTML report
pytest --html=test_report.html --self-contained-html

# With coverage
pytest --cov=src --cov-report=html
```

#### 🔍 Linters and Formatting

```bash
# Install tools
make install

# Format code
make format

# Check lint
make lint

# Check types
make type-check

# Run all checks
make check
```

> 📚 See [REGRAS_REVISAO.md](docs/REGRAS_REVISAO.md) for more details about linters and formatting.

---

### 🔒 Security

The project implements multiple security layers:

<div align="center">

| Feature | Description |
|:---:|:---|
| **Configurable CORS** | Control of allowed origins |
| **Rate Limiting** | Protection against abuse (10 req/min) |
| **Input Validation** | Sanitization and limits (3-2000 chars) |
| **Structured Logging** | Activity tracking |
| **Environment Variables** | Non-versioned secrets |
| **Security Headers** | HSTS, CSP, X-Frame-Options, etc. |

</div>

---

### 🌐 Deploy

See the complete deployment guide in [docs/DEPLOY.md](docs/DEPLOY.md) which includes:
- Server web configuration (Nginx, Caddy)
- HTTPS configuration with Certbot
- CDN (Cloudflare, AWS CloudFront)
- Production environment variables
- Monitoring and logs

#### 🐳 Docker (Coming soon)

```bash
# In development
docker-compose up
```

---

### 🛠️ Tech Stack

<div align="center">

| Category | Technologies |
|:---:|:---|
| **🐍 Backend** | Python 3.12+, FastAPI, Uvicorn |
| **🤖 AI** | Google Gemini 2.0 Flash, Google ADK, OpenRouter (fallback) |
| **💻 Frontend** | HTML5, CSS3, JavaScript (Vanilla), Glassmorphism |
| **🧪 Testing** | Pytest, Pytest-cov, E2E Tests |
| **🔍 Quality** | Black, Ruff, MyPy, Pre-commit |
| **📊 Metrics** | Performance and usage collection |

</div>

---

### 👤 About the Author

<div align="center">

**Joelma De Oliveira Prestes Ferreira**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/joprestes84/)
[![Medium](https://img.shields.io/badge/Medium-12100E?style=for-the-badge&logo=medium&logoColor=white)](https://medium.com/@joprestes)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:joprestes@hotmail.com)

</div>

---

### 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

> 📖 An unofficial Portuguese translation is available [here](LICENSE.pt-BR.md).

---

<div align="center">

**⭐ Se este projeto foi útil, considere dar uma estrela! ⭐**

Made with ❤️ by [Joelma De O. Prestes Ferreira](https://www.linkedin.com/in/joprestes84/)

</div>
