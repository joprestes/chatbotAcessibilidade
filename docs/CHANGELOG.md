# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [3.9.0] - 2025-01-23

### Adicionado
- **CI/CD com GitHub Actions:**
  - Workflow principal (`.github/workflows/ci.yml`) executando em push e pull requests
  - Workflow de acessibilidade (`.github/workflows/accessibility.yml`) com execução diária via schedule
  - Execução automática de lint (ruff), type check (mypy) e testes
  - Execução de testes unitários, de integração e E2E com Playwright
  - Upload automático de relatórios de testes como artifacts
  - Suporte para secrets do GitHub (GOOGLE_API_KEY, OPENROUTER_API_KEY)
  - Health check do servidor FastAPI antes de executar testes E2E
  - Badge de status do CI no README

- **Documentação CI/CD:**
  - Seção completa sobre CI/CD no README.md
  - Documentação dos workflows disponíveis
  - Instruções para configuração de secrets
  - Atualização do PLANO_PLAYWRIGHT.md para 100% concluído

### Modificado
- **README.md:**
  - Adicionado badge de status do CI/CD
  - Nova seção "CI/CD com GitHub Actions" na documentação
  - Links para workflows e artifacts

- **docs/PLANO_PLAYWRIGHT.md:**
  - Status atualizado de 85% para 100% concluído
  - CI/CD Integration marcado como completo
  - Melhorias futuras movidas para seção opcional

### Melhorias
- **Automação:**
  - Testes executam automaticamente em cada push/PR
  - Validação de código antes de merge
  - Relatórios disponíveis para download
  - Execução de testes de acessibilidade diariamente

## [3.8.0] - 2025-11-23

### Adicionado
- **Documentação Completa da API:**
  - Documentação interativa Swagger UI em `/docs`
  - Documentação alternativa ReDoc em `/redoc`
  - Especificação OpenAPI 3.0 em `/openapi.json`
  - Guia completo da API em `docs/API.md` com exemplos em cURL, Python e JavaScript
  - Descrições detalhadas em todos os endpoints com exemplos de requisição/resposta
  - Tags organizadas (Chat, Health, Config, Frontend) para melhor navegação
  - Modelos Pydantic com exemplos e descrições completas
  - Documentação de códigos de erro (400, 429, 500)
  - Informações de segurança, performance e fallback automático

- **Estrutura de Testes Playwright:**
  - Configuração completa do Playwright para testes E2E
  - Testes de API usando requisições HTTP reais (`test_api_playwright.py`)
  - Testes de frontend validando interface e interações (`test_frontend_playwright.py`)
  - Testes de acessibilidade com axe-core (`test_accessibility.py`)
  - Fixtures reutilizáveis para navegador, contexto e página
  - Suporte para múltiplos navegadores (Chromium, Firefox, WebKit)
  - Documentação do plano de implementação em `docs/PLANO_PLAYWRIGHT.md`

- **Comandos Makefile:**
  - `make test-playwright`: Executa todos os testes Playwright
  - `make test-playwright-ui`: Executa com UI (headed mode)
  - `make test-playwright-api`: Apenas testes de API
  - `make test-playwright-frontend`: Apenas testes de frontend
  - `make test-playwright-accessibility`: Apenas testes de acessibilidade
  - `make playwright-install`: Instala navegadores do Playwright

### Modificado
- **FastAPI App:**
  - Descrição completa com markdown e informações de contato
  - Tags organizadas para melhor categorização dos endpoints
  - Versão atualizada para 3.8.0

- **Modelos Pydantic:**
  - `ChatRequest`: Adicionados exemplos e validações detalhadas
  - `ChatResponse`: Estrutura de resposta documentada com exemplos
  - `HealthResponse`: Exemplos completos de resposta

- **Endpoints:**
  - `POST /api/chat`: Documentação completa com fluxo de processamento, exemplos e códigos de erro
  - `GET /api/health`: Descrição detalhada e casos de uso
  - `GET /api/config`: Explicação das configurações do frontend
  - `GET /api/metrics`: Descrição completa das métricas retornadas

- **Dependências:**
  - Adicionado `pytest-playwright>=0.4.0` para testes E2E
  - Adicionado `playwright>=1.40.0` para automação de navegadores
  - Adicionado `axe-playwright>=1.0.0` para testes de acessibilidade

- **Configuração pytest:**
  - Adicionados markers para organizar testes (playwright, api, frontend, accessibility, e2e, slow)

## [3.7.0] - 2025-11-23

### Adicionado
- **Card de Introdução:**
  - Novo card de boas-vindas com avatar da Ada e texto introdutório
  - Botões de sugestão movidos para dentro do card de introdução
  - Card desaparece automaticamente quando a conversa começa
  - Textos dos botões atualizados para serem mais específicos ("Como testar contraste?", "O que é navegação por teclado?", "Gerar Checklist WCAG")

- **Animações e Transições:**
  - Animação fade-in suave nas mensagens (0.4s)
  - Efeito hover com elevação nos balões (translateY -2px)
  - Transições suaves em todos os elementos interativos (0.2s)

### Modificado
- **Layout das Mensagens:**
  - Mensagens do assistente agora ocupam largura total (max-width: 95%)
  - Estilo "card" profissional em vez de balão de chat
  - Border-radius reduzido (12px) para aparência mais documental
  - Borda sutil (1px) substituindo borda roxa grossa anterior
  - Mensagens do usuário alinhadas à direita com melhor espaçamento

- **Tipografia e Contraste:**
  - Título "Ada": 1.75rem (~28px) mobile, 2rem (~32px) desktop
  - Subtítulo: 0.9375rem (~15px) mobile, 1rem (~16px) desktop, font-weight 500
  - Texto dos balões: 1.125rem (18px) para reduzir esforço cognitivo
  - Ícones do header: cor roxo profundo (#3B0764) para contraste WCAG 3:1+
  - Todas as fontes usam unidades `rem` (respeitam zoom do navegador)

- **Avatares:**
  - Avatar da Ada no header: 56px mobile, 64px desktop (era 40px/48px)
  - Avatar da Ada nas mensagens: 56px mobile, 64px desktop (era 48px/56px)
  - Bordas mais visíveis (3px mobile, 4px desktop)
  - Sombras roxas sutis para destacar

- **Espaçamento e Hierarquia Visual:**
  - Margin entre mensagens: 24px mobile, 28px desktop (era 16px)
  - Padding dos balões: 14px mobile, 16px desktop (era 12px/14px)
  - Padding do container: 32px vertical mobile, 40px desktop (era 24px)
  - Gap entre elementos: 24px mobile, 28px desktop (era 20px)
  - Gap entre avatar e mensagem: 16px mobile, 20px desktop (era 14px/16px)

- **Visual e Profundidade:**
  - Gradientes sutis nos balões (mais profundidade visual)
  - Sombras duplas para mais realismo
  - Bordas mais visíveis (melhor definição)
  - Timestamp com font-weight 500 e letter-spacing 0.3px

### Melhorado
- Hierarquia visual mais clara entre mensagens do usuário e assistente
- Layout mais profissional e respirável
- Contraste melhorado para baixa visão e uso ao sol
- Experiência visual mais polida e moderna

## [3.6.0] - 2025-01-22

### Adicionado
- **Layout Moderno com Sidebar:**
  - Sidebar fixa no lado esquerdo com informações da Ada
  - Avatar da Ada com animação de "respiração"
  - Chips de sugestões rápidas na sidebar
  - Layout responsivo que se adapta a mobile (sidebar vira header)

- **Paleta "Lavanda Inclusiva":**
  - Design moderno com tons de roxo, lilás e lavanda
  - Contraste WCAG AA/AAA garantido
  - Dark mode "Beringela" (roxo profundo)
  - Glassmorphism no header e input

- **Melhorias de UX:**
  - Textarea auto-expansível (cresce conforme o usuário digita)
  - Toast notifications acessíveis (role="alert", aria-live)
  - Skeleton loading durante carregamento
  - Avatares nas mensagens (👤 usuário, 💜 assistente)
  - Timestamps em todas as mensagens
  - Botão de envio apenas com ícone SVG
  - Skip link melhorado (visível ao focar)

- **Testes E2E:**
  - Suite completa de testes end-to-end (`tests/e2e/test_user_flow.py`)
  - 12 testes cobrindo fluxo completo do usuário
  - Testes de cache, rate limiting, CORS, e tratamento de erros

- **Métricas de Performance:**
  - Novo módulo `src/chatbot_acessibilidade/core/metrics.py`
  - Endpoint `/api/metrics` para expor estatísticas
  - Coleta de: tempo de resposta, uso de agentes, taxa de fallback, cache hit/miss

- **Endpoint de Configuração:**
  - Novo endpoint `/api/config` para expor configurações do frontend
  - Frontend carrega configurações dinamicamente (timeout, limites, etc.)

### Modificado
- **Frontend:**
  - Input transformado em textarea auto-expansível
  - Caminhos de arquivos estáticos corrigidos (`/static/` e `/assets/`)
  - Sistema de mensagens melhorado com avatares e timestamps
  - Animações mais suaves e profissionais
  - Tipografia: Fonte Atkinson Hyperlegible aplicada
  - Largura de linha limitada (65ch) para melhor legibilidade

- **Backend:**
  - Integração de métricas em todos os endpoints
  - Cache com invalidação inteligente baseada em similaridade
  - Logging melhorado (sem exposição de informações sensíveis)

### Removido
- `scripts/streamlit/app.py` - App Streamlit antigo não utilizado
- `docs/ANALISE_PROJETO.md` - Análise obsoleta (removida)
- `docs/REVISAO_PROJETO_2025-11-22.md` - Revisão pontual (removida, melhorias no CHANGELOG)
- `docs/REORGANIZACAO.md` - Documentação histórica de reorganização já concluída
- `docs/PLANO_MELHORIAS.md` - Redundante com MELHORIAS_IMPLEMENTADAS.md
- Pastas vazias: `docs/api/`, `docs/development/`, `docs/guides/`
- `.DS_Store` removido do rastreamento do Git

### Melhorado
- Acessibilidade: Skip link mais visível, toast notifications com aria-live
- Performance: Skeleton loading, cache inteligente, métricas de performance
- UX: Feedback visual melhorado, animações suaves, design moderno
- Manutenibilidade: Código mais limpo, documentação atualizada

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

