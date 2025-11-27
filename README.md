<div align="center">

# ♿ Chatbot de Acessibilidade Digital

**Um assistente inteligente para tornar a web mais acessível** 💡

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000?style=for-the-badge)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-98%25%2B-success?style=for-the-badge)](docs/TESTES.md)
[![WCAG](https://img.shields.io/badge/WCAG-2.2%20AAA-7C3AED?style=for-the-badge)](https://www.w3.org/WAI/WCAG22/quickref/)
[![CI](https://github.com/joprestes/chatbotAcessibilidade/workflows/CI/badge.svg)](https://github.com/joprestes/chatbotAcessibilidade/actions)

[Português 🇧🇷](#-versão-em-português)

</div>

---

<div align="center">

## 👤 Sobre a Autora

**Joelma De Oliveira Prestes Ferreira**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/joprestes84/)
[![Medium](https://img.shields.io/badge/Medium-12100E?style=for-the-badge&logo=medium&logoColor=white)](https://medium.com/@joprestes)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:joprestes@hotmail.com)

</div>

---

<div align="center">

### 👋 Olá! Eu sou a Ada

<img
  src="https://raw.githubusercontent.com/joprestes/chatbotAcessibilidade/main/assets/ada-animated.gif"
  alt="Ada - Assistente de Acessibilidade Digital"
  width="150"
  height="150"
  style="border-radius: 50%; border: 4px solid rgba(124, 58, 237, 0.3); box-shadow: 0 8px 24px rgba(124, 58, 237, 0.3); margin: 20px 0;">

**Sua Assistente de Acessibilidade e Inclusão Digital** 💜

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

</details>

---

## 🇧🇷 Versão em Português

### ✨ Visão Geral

O **Chatbot de Acessibilidade Digital** é uma solução inteligente e educativa desenvolvida para profissionais, desenvolvedores e equipes de QA que buscam aprimorar seus conhecimentos sobre acessibilidade digital.

Utilizando a **API Gemini 2.0 Flash** da Google (via Google ADK) com **fallback automático** para múltiplos LLMs via Hugging Face, o chatbot gera respostas completas, testáveis e com referências confiáveis, seguindo os padrões **WCAG 2.2 AA/AAA** e **ARIA 1.2**.

#### 🎯 Por que usar este projeto?

| 🎓 **Educativo** | ⚡ **Rápido** | 🔒 **Confiável** | ♿ **Acessível** |
|:---|:---|:---|:---|
| Respostas completas com exemplos práticos | Interface moderna e responsiva | Validação técnica WCAG/ARIA | Interface 100% acessível (WCAG AAA) |
| Materiais de estudo recomendados | Cache inteligente | Rate limiting e segurança | Navegação por teclado completa |
| Sugestões de testes práticos | Fallback automático entre LLMs | Logging estruturado | Suporte a leitores de tela |

#### 💬 Exemplos de Perguntas

| 📝 Categoria | 💡 Exemplo |
|:---|:---|
| **🧪 Testes** | Como testar contraste de cores? |
| **⌨️ Navegação** | O que é navegação por teclado? |
| **🔊 Leitores de Tela** | Como tornar um site acessível a leitores de tela? |
| **📋 WCAG** | Quais são os critérios de sucesso do WCAG 2.2? |
| **🛠️ Ferramentas** | Quais ferramentas usar para testar acessibilidade? |

---

### 🎯 Funcionalidades

#### 🎨 Interface Moderna

| ✨ Recurso | 📱 Descrição |
|:---|:---|
| **🎨 Design "Lavanda Inclusiva"** | Paleta de cores roxo/lilás com contraste WCAG AAA (7:1) |
| **📐 Layout Profissional** | Card de introdução, mensagens estilo card, hierarquia visual clara |
| **🌙 Tema Claro/Escuro** | Dark mode "Beringela" com transições suaves |
| **📝 Textarea Auto-expansível** | Cresce automaticamente conforme o usuário digita |
| **🔔 Toast Notifications** | Notificações acessíveis com `aria-live` |
| **⏳ Skeleton Loading** | Feedback visual durante processamento |
| **👤 Avatares e Timestamps** | Identificação visual clara das mensagens |
| **🔍 Busca no Histórico** | Busque mensagens anteriores rapidamente |

#### ♿ Conformidade WCAG AAA

| ✅ Critério | 🎯 Implementação |
|:---|:---|
| **1.4.6 Contraste AAA** | Razão de contraste 7:1 em todos os textos |
| **2.3.3 Reduced Motion** | Respeita preferência `prefers-reduced-motion` |
| **1.4.11 High Contrast** | Suporte a `prefers-contrast: high` |
| **2.4.7 Foco Visível** | Outline visível em todos os elementos interativos |
| **3.3.5 Ajuda Contextual** | Botão de ajuda e hints visuais |
| **2.4.10 Headings** | Estrutura semântica com h1, h2, h3 |
| **2.1.1 Teclado** | Navegação completa por teclado + atalho Escape |
| **1.1.1 Alt Text** | Descrições informativas em todas as imagens |

#### 🔧 Recursos Técnicos

| ⚙️ Recurso | 🚀 Descrição |
|:---|:---|
| **🤖 Multiagente Especializado** | 5 agentes trabalhando em conjunto |
| **🔄 Fallback Automático** | Múltiplos LLMs via Hugging Face |
| **⚡ Cache Inteligente** | Respostas em cache com invalidação semântica |
| **🛡️ Rate Limiting** | Proteção contra abuso (10 req/min) |
| **📊 Métricas de Performance** | Coleta de tempo de resposta, uso de agentes, etc. |
| **🧪 Testes E2E Completos** | Suite completa de testes end-to-end |
| **📝 Logging Estruturado** | Rastreamento completo de atividades |

#### 📚 Conteúdo Educativo

| 🎓 Recurso | 📖 Descrição |
|:---|:---|
| **✅ Validação Técnica** | Verificação automática WCAG/ARIA |
| **📝 Exemplos Práticos** | Código e exemplos testáveis |
| **🧪 Sugestões de Testes** | Testes práticos recomendados |
| **📚 Materiais de Estudo** | Links e referências confiáveis |
| **💡 Dicas Finais** | Resumos e lembretes importantes |

#### 🧠 Arquitetura Multiagente

O chatbot utiliza **5 agentes especializados** trabalhando em conjunto:

| 🤖 Agente | 📋 Responsabilidade | ⚡ Execução |
|:---|:---|:---|
| **Assistente** | Gera a resposta inicial completa | Sequencial |
| **Validador** | Valida técnica (WCAG, ARIA) | Sequencial |
| **Revisor** | Simplifica a linguagem | Sequencial |
| **Testador** | Sugere testes práticos | Paralelo |
| **Aprofundador** | Recomenda materiais de estudo | Paralelo |

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
│   │   └── pipeline/             # Orquestração dos agentes
│   │       ├── orquestrador.py   # PipelineOrquestrador
│   │       └── __init__.py       # Wrapper pipeline_acessibilidade()
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

# Hugging Face (opcional - para fallback automático)
HUGGINGFACE_API_KEY="sua_chave_huggingface"
FALLBACK_ENABLED=true
HUGGINGFACE_MODELS=meta-llama/Llama-3.3-70B-Instruct,google/gemma-2-9b-it,mistralai/Mistral-7B-Instruct-v0.3

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
2. **Provedor Secundário**: Hugging Face Inference API
3. **Comportamento**: Se o Gemini esgotar quota ou falhar, o sistema automaticamente tenta modelos Hugging Face em sequência

**Modelos Hugging Face Recomendados:**
- `meta-llama/Llama-3.3-70B-Instruct`
- `google/gemma-2-9b-it`
- `mistralai/Mistral-7B-Instruct-v0.3`
- `microsoft/Phi-3-mini-4k-instruct`

**Para habilitar o fallback:**
1. Obtenha uma chave API do [Hugging Face](https://huggingface.co/settings/tokens)
2. Configure `HUGGINGFACE_API_KEY` no `.env`
3. Configure `FALLBACK_ENABLED=true`
4. Opcionalmente, ajuste `HUGGINGFACE_MODELS` com seus modelos preferidos

#### ▶️ Execução

**Frontend Web Moderno** ⭐

```bash
make run
# ou
uvicorn src.backend.api:app --reload --port 8000
```

Acesse: **http://localhost:8000**

#### 🔧 Troubleshooting

**Erro: "GOOGLE_API_KEY não encontrada"**
- Verifique se o arquivo `.env` existe na raiz do projeto
- Certifique-se de que contém: `GOOGLE_API_KEY="sua_chave_aqui"`

**Erro: "fallback_enabled=True requer huggingface_api_key configurada"**
- Se você habilitou o fallback, configure `HUGGINGFACE_API_KEY` no `.env`
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

| 📘 Documento | 📝 Descrição |
|:---|:---|
| [📝 CHANGELOG.md](docs/CHANGELOG.md) | Histórico de mudanças |
| [📋 REGRAS_REVISAO.md](docs/REGRAS_REVISAO.md) | Regras e padrões do projeto (inclui linters) |
| [♿ PADROES_ACESSIBILIDADE.md](docs/PADROES_ACESSIBILIDADE.md) | Padrões de acessibilidade e gerenciamento de foco |
| [🚀 DEPLOY.md](docs/DEPLOY.md) | Guia completo de deploy |
| [🧪 TESTES.md](docs/TESTES.md) | Documentação de testes |
| [📚 API Interativa](http://localhost:8000/docs) | Swagger UI (quando servidor rodando) |
| [📚 API ReDoc](http://localhost:8000/redoc) | ReDoc (quando servidor rodando) |

---

### 🧪 Testes e Qualidade

#### 📊 Cobertura de Testes

**98.52% de cobertura** 🎯

| Categoria | Cobertura |
|:---|:---|
| **Testes Unitários** | ✅ Completo |
| **Testes de Integração** | ✅ Completo |

O projeto possui uma **suite de testes de classe mundial** com 8 ferramentas profissionais:

| Ferramenta | Propósito | Cobertura |
|:---|:---|:---|
| **pytest** | Testes unitários/integração | 384 testes |
| **pytest-cov** | Cobertura de código | 98.77% |
| **Playwright** | Testes E2E | 171 testes |
| **Locust** 🆕 | Testes de carga | 4 cenários |
| **pytest-benchmark** 🆕 | Benchmarks de performance | 6 testes |
| **Hypothesis** 🆕 | Property-based testing | 10 testes |
| **mutmut** 🆕 | Mutation testing | Configurado |
| **Allure** 🆕 | Relatórios visuais | Dashboards |

#### 🚀 Executar Testes

```bash
# Testes básicos
make test                    # Todos os testes
make test-cov                # Com cobertura

# Testes específicos
make test-unit               # Apenas unitários
make test-integration        # Apenas integração
make test-playwright         # E2E com Playwright

# Testes avançados 🆕
make test-benchmark          # Benchmarks de performance
make test-load-ui            # Testes de carga (Locust)
make test-property           # Property-based tests
make test-mutation           # Mutation testing
make allure-serve            # Relatórios visuais

# Qualidade de código
make lint                    # Ruff
make type-check              # MyPy
make check                   # Todas as verificações
```

#### 📊 Métricas de Qualidade

- ✅ **384 testes** passando (100%)
- ✅ **98.77% cobertura** de código
- ✅ **0 erros** de lint (Ruff)
- ✅ **0 erros** de type checking (MyPy)
- ✅ **Cache**: 2.7μs (367x mais rápido que meta!)

#### 📚 Documentação de Testes

- [📋 INDICE_TESTES.md](docs/INDICE_TESTES.md) - Índice completo
- [🧪 TESTES.md](docs/TESTES.md) - Estratégia geral
- [🔥 TESTES_CARGA.md](docs/TESTES_CARGA.md) - Locust + Benchmarks
- [🧬 MUTATION_TESTING.md](docs/MUTATION_TESTING.md) - mutmut
- [📊 ALLURE_REPORTS.md](docs/ALLURE_REPORTS.md) - Relatórios visuais

---

### 🔒 Segurança

O projeto implementa várias camadas de segurança:

| 🔐 Recurso | 🛡️ Descrição |
|:---|:---|
| **CORS Configurável** | Controle de origens permitidas |
| **Rate Limiting** | Proteção contra abuso (10 req/min) |
| **Validação de Entrada** | Sanitização e limites (3-2000 chars) |
| **Logging Estruturado** | Rastreamento de atividades |
| **Variáveis de Ambiente** | Segredos não versionados |
| **Headers de Segurança** | HSTS, CSP, X-Frame-Options, etc. |

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

| Categoria | Tecnologias |
|:---|:---|
| **🐍 Backend** | Python 3.12+, FastAPI, Uvicorn |
| **🤖 IA** | Google Gemini 2.0 Flash, Google ADK, Hugging Face (fallback) |
| **💻 Frontend** | HTML5, CSS3, JavaScript (Vanilla), Glassmorphism |
| **🧪 Testes** | Pytest, Pytest-cov, Testes E2E |
| **🔍 Qualidade** | Black, Ruff, MyPy, Pre-commit |
| **📊 Métricas** | Coleta de performance e uso |

---

### 📄 Licença

Este projeto está licenciado sob a **Licença MIT**. Veja o arquivo [LICENSE](LICENSE) para detalhes.

> 📖 Uma tradução não-oficial para o português está disponível [aqui](LICENSE.pt-BR.md).

---

**⭐ Se este projeto foi útil, considere dar uma estrela! ⭐**

Made with ❤️ by [Joelma De O. Prestes Ferreira](https://www.linkedin.com/in/joprestes84/)
