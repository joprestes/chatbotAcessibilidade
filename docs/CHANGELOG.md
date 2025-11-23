# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [3.1.0] - 2025-11-22

### Modificado
- **Atualização do Python**: Projeto atualizado para Python 3.12 (versão estável mais recente)
  - `pyproject.toml`: Atualizado `target-version` para `py312` e `py313`
  - `pyproject.toml`: Atualizado `python_version` do MyPy para `3.12`
  - `README.md`: Atualizada recomendação de Python 3.10+ para Python 3.12+
  - `docs/INSTRUCOES_EXECUCAO.md`: Atualizada versão mínima do Python
  - Resolve warnings sobre EOL do Python 3.9
  - Aproveita features e melhorias de performance do Python 3.12

## [2.1.1] - 2025-11-22

### Adicionado
- **Linters e Formatação**:
  - Configuração do Black para formatação automática
  - Configuração do Ruff para linting rápido e moderno
  - Configuração do MyPy para verificação de tipos
  - Pre-commit hooks para verificação automática antes de commits
  - Makefile com comandos úteis (format, lint, type-check, test, etc)
  - EditorConfig para consistência entre editores
  - Documentação completa em `LINTERS.md`

### Modificado
- `requirements.txt`: Adicionadas dependências de desenvolvimento (black, ruff, mypy, pre-commit, pytest-cov)
- `.gitignore`: Adicionados arquivos gerados por linters e formatters
- `README.md`: Adicionada seção sobre linters

## [2.1.0] - 2025-11-22

### Adicionado
- **Sistema de Configuração Centralizada**:
  - Arquivo `chatbot_acessibilidade/config.py` com Pydantic Settings
  - Validação automática de variáveis de ambiente
  - Type hints completos e documentação

- **Exceções Customizadas**:
  - Arquivo `chatbot_acessibilidade/core/exceptions.py`
  - Hierarquia clara de exceções (ValidationError, APIError, AgentError, RateLimitExceeded)

- **Rate Limiting**:
  - Proteção contra abuso usando `slowapi`
  - Configurável via variáveis de ambiente
  - Limite padrão: 10 requisições/minuto por IP

- **Logging Estruturado**:
  - Substituição de `print()` por logging Python padrão
  - Middleware de logging na API (método, path, status, tempo)
  - Níveis configuráveis (DEBUG, INFO, WARNING, ERROR)

- **Testes Adicionais**:
  - `tests/test_dispatcher.py`: Testes unitários para dispatcher
  - `tests/test_api.py`: Testes de integração para API FastAPI
  - ~15 novos casos de teste

- **Documentação**:
  - `MELHORIAS_IMPLEMENTADAS.md`: Resumo das melhorias da Fase 1
  - `.env.example`: Exemplo de variáveis de ambiente (quando disponível)

### Modificado
- **Segurança**:
  - CORS configurável via variável de ambiente `CORS_ORIGINS`
  - Validação de entrada: tamanho mínimo (3) e máximo (2000 caracteres)
  - Sanitização básica de caracteres de controle

- **Tratamento de Erros**:
  - Uso de exceções customizadas em vez de strings
  - Fallbacks robustos no pipeline
  - Logging de erros com contexto completo

- **Arquitetura**:
  - Lazy loading do `genai.Client()` em `dispatcher.py`
  - Validação de entrada no pipeline e na API
  - Middleware de logging na API

- **Testes**:
  - Corrigida função duplicada em `test_formatter.py`
  - Removida implementação local de `extrair_primeiro_paragrafo`

### Corrigido
- Função `extrair_primeiro_paragrafo` duplicada em `test_formatter.py`
- Uso de `print()` substituído por logging estruturado
- CORS muito permissivo (`*`) agora configurável

### Segurança
- CORS configurável para produção
- Rate limiting implementado
- Validação e sanitização de entrada do usuário

## [2.0.0] - 2025-11-22

### Adicionado
- **Frontend Web sem Streamlit**: Nova interface HTML/CSS/JavaScript pura
  - Interface acessível com suporte completo a WCAG AA
  - Chat interativo com histórico persistente (localStorage)
  - Expanders para organizar respostas em seções
  - Suporte a tema claro/escuro com toggle
  - Navegação completa por teclado
  - Indicadores de carregamento durante processamento
  - Formatação automática de markdown nas respostas

- **API REST com FastAPI**: Backend separado do frontend
  - Endpoint `POST /api/chat` para processar perguntas
  - Endpoint `GET /api/health` para verificação de saúde da API
  - Servir arquivos estáticos do frontend automaticamente
  - Tratamento de erros padronizado com respostas JSON
  - CORS configurado para desenvolvimento

- **Estrutura de Projeto Reorganizada**:
  - Nova pasta `backend/` com API FastAPI
  - Nova pasta `frontend/` com arquivos HTML, CSS e JavaScript
  - Mantida compatibilidade com Streamlit (`app.py`)

- **Documentação**:
  - Arquivo `INSTRUCOES_EXECUCAO.md` com guia de execução
  - README.md atualizado com instruções para ambos os frontends
  - Changelog para rastreamento de mudanças

### Modificado
- `requirements.txt`: Adicionadas dependências `fastapi`, `uvicorn[standard]` e `python-multipart`
- `README.md`: Atualizado com instruções para execução do novo frontend web
- Estrutura de arquivos: Organização mais clara separando backend e frontend

### Mantido
- Código core (`chatbot_acessibilidade/`) permanece intacto e sem mudanças
- Interface Streamlit (`app.py`) mantida como alternativa
- Todos os testes existentes continuam funcionando
- Funcionalidades do chatbot permanecem as mesmas

## [1.0.0] - 2025-11-22

### Adicionado
- Chatbot de Acessibilidade Digital com arquitetura multiagente
- Interface Streamlit com suporte a tema claro/escuro
- Pipeline assíncrono com 5 agentes especializados:
  - Assistente: Gera resposta inicial
  - Validador: Valida técnica (WCAG, ARIA)
  - Revisor: Simplifica linguagem
  - Testador: Sugere testes práticos
  - Aprofundador: Recomenda materiais de estudo
- Integração com Google Gemini 2.0 Flash via Google ADK
- Formatação de respostas em seções organizadas:
  - Introdução
  - Conceitos Essenciais
  - Como Testar na Prática
  - Quer se Aprofundar?
  - Dica Final
- Testes unitários com pytest
- Tratamento robusto de erros da API
- Suporte a busca na web via google_search
- Acessibilidade otimizada na interface:
  - Contraste reforçado
  - Foco visível para teclado
  - Labels para leitores de tela
- Documentação completa em português e inglês
- Script de setup automatizado (`setup.sh`)

---

## Tipos de Mudanças

- **Adicionado**: Para novas funcionalidades
- **Modificado**: Para mudanças em funcionalidades existentes
- **Descontinuado**: Para funcionalidades que serão removidas
- **Removido**: Para funcionalidades removidas
- **Corrigido**: Para correções de bugs
- **Segurança**: Para vulnerabilidades corrigidas

