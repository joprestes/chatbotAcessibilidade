# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [3.5.0] - 2025-01-22

### Adicionado
- Testes adicionais para aumentar cobertura de `config.py` e `llm_provider.py`
- `tests/test_config_coverage.py`: Testes para linhas não cobertas de `config.py` (linhas 127, 150-153)
- `tests/test_llm_provider_coverage.py`: Testes para linhas não cobertas de `llm_provider.py` (linhas 191, 311, 435-439)

### Melhorado
- Cobertura de testes de `config.py`: 92.31% → 98.46% (+6.15%)
- Cobertura de testes de `llm_provider.py`: 98.11% → 99.53% (+1.42%)
- Ambos os arquivos agora têm cobertura acima da meta de 98%

### Detalhes Técnicos
- Linha 127 de `config.py`: Teste para `openrouter_models_list` quando `openrouter_models` é string
- Linhas 150-153 de `config.py`: Testes para inicialização de variáveis de ambiente em ambiente de teste
- Linha 191 de `llm_provider.py`: Teste para `TimeoutError` no except externo do `generate`
- Linha 311 de `llm_provider.py`: Teste para validação de `content` não sendo string no OpenRouter
- Linhas 435-439 de `llm_provider.py`: Teste para `continue` quando `should_fallback` retorna `True` para clientes não-OpenRouter

## [3.4.0] - 2025-11-23

### Adicionado
- **Arquivo de Constantes Centralizadas:**
  - Novo módulo `src/chatbot_acessibilidade/core/constants.py` com todas as constantes do projeto
  - Constantes para timeouts (API, OpenRouter, Frontend, HTTPX)
  - Constantes para limites (pergunta, parágrafo)
  - Constantes para cache (TTL, tamanho máximo, assets estáticos)
  - Constantes para compressão (tamanho mínimo)
  - Constantes para tokens LLM (OpenRouter max tokens)
  - Constantes para retry (máximo de tentativas)
  - Constantes para rate limiting (padrão e fallback)
  - Classe `ErrorMessages` com todas as mensagens de erro padronizadas
  - Classe `LogMessages` com todas as mensagens de log padronizadas
  - Classe `FrontendConstants` com constantes específicas do frontend
  - 50 testes unitários para validar todas as constantes

### Modificado
- `src/backend/middleware.py`: Substituídos valores mágicos por constantes (TTL de cache, tamanho mínimo de compressão)
- `src/backend/api.py`: Substituídos valores mágicos por constantes (rate limit fallback, mensagens de erro)
- `src/chatbot_acessibilidade/core/llm_provider.py`: Substituídos valores mágicos por constantes (max tokens, timeouts, mensagens)
- `src/chatbot_acessibilidade/agents/dispatcher.py`: Substituídos valores mágicos por constantes (retry attempts, mensagens)
- `src/chatbot_acessibilidade/core/cache.py`: Substituídos valores mágicos por constantes (TTL, tamanho máximo, mensagens de log)
- `src/chatbot_acessibilidade/core/formatter.py`: Substituído valor mágico por constante (tamanho mínimo de parágrafo)
- `src/chatbot_acessibilidade/core/validators.py`: Substituída mensagem hardcoded por constante
- `src/chatbot_acessibilidade/pipeline.py`: Substituídas mensagens de erro hardcoded por constantes
- `frontend/app.js`: Adicionadas constantes locais para timeout e duração de anúncios de erro

### Testes
- Adicionado `tests/test_constants.py` com 50 testes cobrindo todas as constantes
- Testes para validação de tipos, valores e formatação de mensagens
- Todos os testes passando (254 testes no total)

### Benefícios
- Código mais manutenível (valores centralizados)
- Mensagens de erro e log padronizadas
- Facilita futuras alterações de configuração
- Melhor rastreabilidade de valores mágicos

## [3.3.0] - 2025-11-23

### Adicionado
- **Melhorias de UX:**
  - Indicador de digitação (typing indicator) animado com 3 pontos pulsantes
  - 5 tipos diferentes de mensagens de erro com cores específicas:
    - Timeout (laranja #f59e0b)
    - Offline (cinza #6b7280)
    - Rate Limit (vermelho #ef4444)
    - Server Error (vermelho escuro #dc2626)
    - Network Error (azul #3b82f6)
  - Animações de transição suaves para mensagens:
    - Mensagens do usuário: slide da direita
    - Mensagens do assistente: slide da esquerda
    - Erros: slide horizontal
  - Feedback visual melhorado durante processamento
  - Typing indicator aparece durante processamento e desaparece automaticamente

### Melhorado
- Experiência do usuário mais fluida e responsiva
- Feedback visual mais claro e diferenciado
- Animações suaves e não intrusivas
- Acessibilidade mantida (ARIA labels, data-testid)
- Compatibilidade com tema claro/escuro

## [3.2.0] - 2025-11-22

### Adicionado
- **CDN e Cache para Assets Estáticos:**
  - `StaticCacheMiddleware` para adicionar headers de cache apropriados
  - Cache de 1 dia para arquivos `/static/` (CSS, JS)
  - Cache de 7 dias para arquivos `/assets/` (imagens)
  - Header `Vary: Accept-Encoding` para suporte a compressão
  - Script `build_assets.sh` para otimização de assets (minificação, compressão)
  - Documentação completa de deploy (`docs/DEPLOY.md`) com:
    - Guia de configuração HTTPS (Nginx, Caddy, Certbot)
    - Instruções para CDN (Cloudflare, AWS CloudFront)
    - Configuração de servidor web
    - Variáveis de ambiente de produção
    - Monitoramento e logs

### Melhorado
- Cobertura de testes aumentada para 97.52% (de 97.47%)
- Middleware com 100% de cobertura de testes
- 5 novos testes para validação de cache de assets

### Testes
- Adicionados 5 testes em `tests/test_static_cache.py`:
  - Teste de headers de cache para CSS
  - Teste de headers de cache para JavaScript
  - Teste de headers de cache para imagens
  - Teste de endpoints de API sem cache
  - Teste de TTLs diferentes para diferentes tipos de assets

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

