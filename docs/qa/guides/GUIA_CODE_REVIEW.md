# Regras do Workspace - Chatbot Acessibilidade

Este documento define as regras, padrões e convenções que devem ser seguidos por todos os desenvolvedores e agentes trabalhando no projeto Chatbot Acessibilidade.

## 1. Princípios Gerais

⚠️ **REGRA FUNDAMENTAL**: **NUNCA faça commits diretamente na branch `main`**. Sempre crie uma branch para qualquer alteração, por menor que seja.

*   **Idioma**: Todo o código, comentários, documentação e mensagens de commit devem ser em **Português Brasileiro (pt-BR)**. Termos técnicos universais (ex: *controller*, *service*, *payload*, *API*, *LLM*) podem ser mantidos em inglês.

*   **Clean Code**: O código deve ser legível, simples e autoexplicativo. Funções devem ser pequenas e ter uma única responsabilidade.

*   **SOLID**: Aplique os princípios SOLID onde fizer sentido, especialmente a separação de responsabilidades e injeção de dependências.

*   **KISS (Keep It Simple, Stupid)**: Evite complexidade acidental. A solução mais simples que resolve o problema é geralmente a melhor.

*   **YAGNI (You Aren't Gonna Need It)**: Não implemente funcionalidades pensando no futuro. Implemente apenas o necessário para os requisitos atuais.

*   **Acessibilidade**: Este é um projeto focado em acessibilidade. Sempre considere a experiência do usuário e garanta que todas as funcionalidades sejam acessíveis. Veja seção específica abaixo.

*   **Mobile First**: O design deve ser pensado primeiro para dispositivos móveis, depois adaptado para desktop. Use media queries progressivas (min-width) ao invés de regressivas (max-width).

## 2. Workflow de Desenvolvimento

*   **Makefile**: Utilize o `Makefile` para todas as tarefas comuns. Não execute comandos complexos manualmente.

    *   `make setup`: Configuração inicial do ambiente.
    *   `make run`: Executar a aplicação FastAPI.
    *   `make run-streamlit`: Executar a aplicação Streamlit (alternativa).
    *   `make test`: Rodar todos os testes.
    *   `make test-cov`: Rodar testes com relatório de cobertura.
    *   `make lint`: Verificar estilo e qualidade do código.
    *   `make format`: Formatar código automaticamente.

*   **Ambiente Virtual**: Sempre utilize o ambiente virtual (`.venv`). O `Makefile` gerencia isso automaticamente, mas garanta que seu terminal esteja usando o Python correto.

*   **Dependências**:

    *   Adicione dependências de produção em `requirements.txt`.
    *   Sempre congele as versões (`pip freeze`) após adicionar novas libs.
    *   Documente dependências opcionais (ex: OpenRouter) no README.

## 3. Qualidade de Código

### Ferramentas Configuradas

*   **Black** - Formatação de código Python seguindo PEP 8
*   **Ruff** - Linter rápido que substitui múltiplas ferramentas (pycodestyle, pyflakes, isort, flake8-bugbear, etc.)
*   **MyPy** - Verificação estática de tipos
*   **Pre-commit** - Hooks automáticos executados antes de cada commit

### Uso das Ferramentas

*   **Linting**: O projeto usa **Ruff**. Nenhum erro de lint deve ser ignorado sem uma justificativa forte (use `# noqa: EXXX` com o código do erro e explicação).

*   **Formatação**: O projeto usa **Black** e **Ruff format**. Todo código deve ser formatado automaticamente antes do commit.

*   **Type Checking**: Utilize type hints em todas as assinaturas de função. O projeto usa **MyPy** para verificação estática de tipos.

### Comandos Disponíveis

```bash
make lint          # Executa linters (ruff)
make format        # Formata código (black + ruff format)
make type-check    # Verifica tipos (mypy)
make check         # Executa todas as verificações
make fix           # Formata e corrige problemas automaticamente
```

### Configuração

*   **Black**: Configurado em `pyproject.toml` (line length: 100, target: Python 3.12+)
*   **Ruff**: Configurado em `pyproject.toml` (regras: E, W, F, I, B, C4, UP, ARG, SIM)
*   **MyPy**: Configurado em `pyproject.toml` (Python 3.12+, ignora imports externos)

### Pre-commit Hooks

Os hooks são executados automaticamente antes de cada commit:
1. Trailing whitespace - Remove espaços no final das linhas
2. End of file fixer - Adiciona nova linha no final do arquivo
3. YAML/JSON/TOML checker - Valida sintaxe
4. Black - Formata código Python
5. Ruff - Verifica e corrige problemas de lint
6. MyPy - Verifica tipos

### Regras de Lint

**Regras Habilitadas**: E (pycodestyle), W (warnings), F (pyflakes), I (isort), B (bugbear), C4 (comprehensions), UP (pyupgrade), ARG (unused args), SIM (simplifications)

**Regras Ignoradas**: E501 (linha muito longa - Black cuida), B008 (função em defaults), C901 (complexidade - pode ajustar)

*   **Estrutura de Código**:

    *   Mantenha a estrutura modular em `src/chatbot_acessibilidade/`.
    *   Separe responsabilidades: `agents/`, `core/`, `backend/`.
    *   Use injeção de dependências quando apropriado.

## 4. Estratégia de Testes (Pirâmide + Playwright)

### 4.1 Testes Unitários (Base da Pirâmide)

*   **Framework**: Pytest com `pytest-asyncio` para testes assíncronos.

*   **Padrão AAA**: Organize os testes em Arrange (preparação), Act (ação) e Assert (verificação).

*   **Cobertura**: A meta é manter a cobertura de código acima de **95%**. A cobertura atual é de **95.60%** e deve ser mantida.

*   **Isolamento**: Testes unitários não devem depender de serviços externos (APIs reais do Google Gemini ou OpenRouter). Use `unittest.mock` ou `pytest-mock` para mockar chamadas externas.

*   **Regra**: Teste a lógica de negócio, parsers e formatadores isoladamente, **mockando chamadas de IA**.

*   **Nomenclatura**: `test_funcionalidade_cenario_resultado` (ex: `test_google_gemini_client_timeout_error`, `test_pipeline_agentes_paralelos_sucesso`).

*   **Estrutura de Testes**:

    *   Testes unitários em `tests/unit/`.
    *   Use fixtures do pytest para setup comum.
    *   Mock todas as dependências externas.

*   **Testes Assíncronos**: Sempre use `@pytest.mark.asyncio` para funções assíncronas.

### 4.2 Testes E2E e Acessibilidade (Playwright)

*   **Ferramenta**: Playwright para testes end-to-end e acessibilidade.

*   **Estratégia de Locators**:

    *   **Primário**: Utilize `page.get_by_test_id("nome-do-elemento")` para interações funcionais. Isso garante que o teste não quebre se o texto do botão mudar de "Enviar" para "Mandar".
    
    *   **Secundário (Validação A11y)**: Use `expect(locator).to_have_attribute("aria-label", ...)` ou `get_by_role` nas asserções para garantir que, além de funcional (via test-id), o elemento está semanticamente correto para leitores de tela.

*   **Testes de A11y Automatizados**:

    *   Integre `axe-core` (axe-playwright) nos testes E2E.
    *   Valide violações de WCAG automaticamente em cada view.
    *   Testes devem fazer skip se `axe-playwright` não estiver disponível, mas devem existir.

*   **Sincronização**:

    *   **NUNCA use `time.sleep()`**. Confie nos `await expect(page.get_by_test_id(...)).to_be_visible()`.
    *   Use `page.wait_for_load_state("networkidle")` quando apropriado.

*   **Independência**: Cada teste cria e limpa seus próprios dados. Use fixtures para setup/teardown.

*   **Estrutura**: Testes E2E em `tests/e2e/playwright/`.

## 5. Git e Versionamento

### Regras Obrigatórias de Branch

⚠️ **REGRA CRÍTICA**: **NUNCA, JAMAIS, SOB NENHUMA CIRCUNSTÂNCIA faça commits diretamente na branch `main`**.

*   **NUNCA faça commits diretamente na branch `main`**.
*   **SEMPRE crie uma branch antes de iniciar qualquer alteração**.
*   **Mesmo para correções pequenas ou documentação, crie uma branch**.
*   **A branch `main` deve ser protegida e receber código apenas via Pull Request/Merge**.

*   Nomenclatura de branches:

    *   `feature/nome-da-funcionalidade` para novas funcionalidades
    *   `fix/nome-do-bug` para correções
    *   `refactor/nome-da-refatoracao` para refatorações
    *   `docs/nome-da-documentacao` para documentação
    *   `test/nome-do-teste` para adição de testes

### Commits Semânticos

*   `feat:`: Nova funcionalidade.
*   `fix:`: Correção de bug.
*   `docs:`: Alterações na documentação.
*   `style:`: Formatação, falta de ponto e vírgula, etc. (sem alteração de código).
*   `refactor:`: Refatoração de código (sem alteração de funcionalidade).
*   `test:`: Adição ou correção de testes.
*   `chore:`: Atualização de tarefas de build, configs, etc.
*   `perf:`: Melhorias de performance.
*   `ci:`: Mudanças em CI/CD.

### Fluxo de Trabalho

⚠️ **IMPORTANTE**: Sempre siga este fluxo, sem exceções:

1. **NUNCA** trabalhe diretamente na `main`. Sempre crie uma branch:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/minha-feature
   ```

2. Faça seus commits na branch criada

3. Execute `make lint` e `make test` antes de fazer push

4. Faça push da sua branch:
   ```bash
   git push origin feature/minha-feature
   ```

5. Abra um Pull Request para a `main` no GitHub/GitLab

6. Aguarde revisão e aprovação

7. Após aprovação e merge, limpe as branches locais e remotas:
   ```bash
   git checkout main
   git pull origin main
   git branch -d feature/minha-feature
   git push origin --delete feature/minha-feature
   ```

*   **Mensagens**: Claras e descritivas, em português.
*   **Violação desta regra**: Se você cometeu diretamente na `main` por engano, use `git reset` para desfazer e crie uma branch corretamente.

## 6. Segurança

*   **Secrets**: NUNCA commite chaves de API, senhas ou tokens. Use variáveis de ambiente e o arquivo `.env` (que deve estar no `.gitignore`).

*   **Validação**: Valide todas as entradas de dados, especialmente as que vêm de usuários ou APIs externas.

*   **Logs**: Não logue informações sensíveis (PII, tokens, chaves API). Use `logger.debug()` para informações detalhadas e `logger.info()` para informações gerais.

*   **Rate Limiting**: O projeto implementa rate limiting no FastAPI. Não remova ou desabilite sem justificativa.

*   **CORS**: Configure CORS adequadamente para produção. Não use `*` em produção.

## 7. Estrutura de Arquivos

*   Mantenha a estrutura definida no `README.md`:

    ```
    chatbotAcessibilidade/
    ├── src/
    │   ├── chatbot_acessibilidade/  # Módulo principal
    │   │   ├── agents/              # Agentes do sistema
    │   │   ├── core/                # Funcionalidades core
    │   │   └── pipeline.py          # Pipeline principal
    │   └── backend/                 # API FastAPI
    ├── tests/                       # Testes
    ├── docs/                        # Documentação
    ├── scripts/                     # Scripts utilitários
    ├── static/                      # Arquivos estáticos
    └── frontend/                    # Frontend HTML/CSS/JS
    ```

*   Novos módulos devem ir para `src/chatbot_acessibilidade/`.
*   Novos testes devem ir para `tests/`.
*   Scripts utilitários em `scripts/`.
*   Documentação em `docs/`.

## 8. Arquitetura e Padrões

### 8.1 Stack de IA (Regra de Ouro)

⚠️ **PROIBIÇÃO ABSOLUTA**: É **estritamente proibido** o uso de frameworks de orquestração pesados.

*   **NÃO UTILIZE**:
    *   LangChain
    *   LangGraph
    *   LlamaIndex
    *   Frameworks similares de orquestração pesados

*   **USE APENAS**:
    *   SDKs nativos/leves (ex: `google-genai`, `openai-python`, `anthropic-sdk`)
    *   Google ADK (Agent Development Kit) - já em uso
    *   Vercel AI SDK (Core) - se necessário para frontend

*   **Controle de Fluxo**: A lógica de estado, memória e ferramentas deve ser implementada com código nativo (Python/TypeScript) simples e explícito.

*   **Prompts**: Devem ser explícitos, versionados e desacoplados da lógica de negócio. Mantenha prompts em `agents/factory.py` ou arquivos dedicados.

### 8.2 Multi-Agent System

*   **Multi-Agent System**: O projeto usa um sistema de múltiplos agentes (Assistant, Validator, Reviewer, Tester, Aprofundador). Mantenha a separação de responsabilidades.

*   **LLM Providers**: O projeto suporta múltiplos provedores de LLM (Google Gemini como primário, OpenRouter como fallback). Novos provedores devem seguir o padrão `LLMClient` em `core/llm_provider.py`.

*   **Fallback Mechanism**: O sistema de fallback automático deve ser mantido e testado. Não remova sem substituir por alternativa.

*   **Cache**: O sistema usa cache em memória para otimizar chamadas. Respeite o TTL e limites de tamanho.

*   **Async/Await**: Use operações assíncronas para todas as chamadas de API e operações I/O.

*   **Error Handling**: Use as exceções customizadas em `core/exceptions.py`. Não use exceções genéricas sem contexto.

## 9. Frontend

### 9.1 Acessibilidade (WCAG 2.2 AA/AAA - Prioridade Zero)

⚠️ **PRIORIDADE ZERO**: Como este é um Chat de Acessibilidade, a aplicação deve ser o **exemplo máximo de conformidade**.

*   **WCAG 2.2 AA/AAA**: Todo componente deve atingir no mínimo o nível **AA**. Prefira **AAA** quando possível.

*   **Semântica HTML**: Use elementos HTML semânticos (`<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<footer>`, `<button>`, `<form>`, etc.).

*   **ARIA Labels**: Adicione `aria-label` ou `aria-labelledby` quando necessário:
    ```html
    <button aria-label="Enviar mensagem">Enviar</button>
    <div role="status" aria-live="polite" id="status-message"></div>
    ```

*   **Screen Readers**: Use `aria-live="polite"` para respostas do bot e `aria-label` quando necessário. Garanta que todas as mudanças dinâmicas sejam anunciadas.

*   **Contraste de Cores**: Garanta contraste mínimo de 4.5:1 para texto normal e 3:1 para texto grande (WCAG AA).

*   **Navegação por Teclado**: Todo o fluxo deve ser operável **apenas com teclado** (Tab, Enter, Esc, setas). Teste sem mouse.

*   **Gerenciamento de Foco**: O foco deve ser lógico e **nunca se perder** após interações (envio de msg, fechamento de modal). Sempre retorne o foco para o elemento apropriado.

*   **Foco Visível**: Sempre forneça indicador visual de foco (`:focus`, `:focus-visible`).

*   **Alt Text**: Todas as imagens devem ter `alt` descritivo:
    ```html
    <img src="logo.png" alt="Logo do Chatbot de Acessibilidade">
    <!-- Se decorativa: -->
    <img src="decoration.png" alt="">
    ```

*   **Formulários**: Associe labels aos inputs:
    ```html
    <label for="pergunta">Sua pergunta:</label>
    <input type="text" id="pergunta" name="pergunta" required>
    ```

*   **Mensagens de Erro**: Associe mensagens de erro aos campos usando `aria-describedby`:
    ```html
    <input aria-invalid="true" aria-describedby="erro-pergunta">
    <span id="erro-pergunta" role="alert">Campo obrigatório</span>
    ```

*   **Skip Links**: Adicione links para pular navegação:
    ```html
    <a href="#main-content" class="skip-link">Pular para conteúdo principal</a>
    ```

*   **Landmarks**: Use landmarks ARIA quando apropriado (`role="banner"`, `role="navigation"`, `role="main"`, etc.).

### 9.2 Mobile First

⚠️ **OBRIGATÓRIO**: Design deve ser pensado primeiro para mobile.

*   **Abordagem Mobile First**: Comece com estilos para telas pequenas, depois adicione media queries para telas maiores:
    ```css
    /* Mobile (padrão) */
    .container {
        padding: 1rem;
        font-size: 14px;
    }
    
    /* Tablet */
    @media (min-width: 768px) {
        .container {
            padding: 2rem;
            font-size: 16px;
        }
    }
    
    /* Desktop */
    @media (min-width: 1024px) {
        .container {
            padding: 3rem;
            font-size: 18px;
        }
    }
    ```

*   **Touch Targets**: Botões e elementos clicáveis devem ter no mínimo 44x44px (recomendação Apple/Google).

*   **Viewport**: Sempre inclua meta viewport:
    ```html
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    ```

*   **Responsividade**: Teste em diferentes tamanhos de tela (320px, 375px, 768px, 1024px, 1920px).

*   **Performance Mobile**: Otimize imagens, use lazy loading, minimize JavaScript.

### 9.3 Test IDs (Obrigatório para Testabilidade)

⚠️ **OBRIGATÓRIO**: Para garantir automação robusta e desacoplada de mudanças visuais, **TODOS** os componentes interativos, containers de layout principais e elementos dinâmicos de resposta **DEVEM** possuir um atributo identificador único.

*   **Obrigatoriedade**: 
    *   Botões, inputs, links (todos os elementos interativos)
    *   Containers de layout principais
    *   Elementos dinâmicos de resposta (mensagens do chat, erros, etc.)

*   **Padrão de Nomenclatura**: 
    *   Use `data-testid="nome-do-elemento"` (preferencial) ou `id="nome-unico"`
    *   Nomes em **kebab-case** e descritivos
    *   Atributos de código em **inglês técnico** (ex: `submit-button`, `chat-input-field`)

*   **Exemplos**:
    ```html
    <button data-testid="send-message-button">Enviar</button>
    <input data-testid="chat-input-field" type="text">
    <div data-testid="bot-response-container">Resposta</div>
    <div data-testid="chat-history-item-0">Mensagem 1</div>
    ```

*   **Estrutura Hierárquica**: Para elementos repetidos, use índices ou IDs:
    ```html
    <div data-testid="chat-mensagem" data-message-id="1">...</div>
    <div data-testid="chat-mensagem" data-message-id="2">...</div>
    ```

*   **Componentes Principais**: Sempre adicione test IDs em:
    - Botões e links
    - Inputs e formulários
    - Mensagens de erro/sucesso
    - Containers principais
    - Elementos de navegação
    - Elementos dinâmicos (respostas do bot, loading states, etc.)

*   **Não use test IDs em**: Elementos puramente decorativos (imagens de fundo, etc.).

*   **Exemplo Completo**:
    ```html
    <form data-testid="form-chat">
        <label for="pergunta">Pergunta:</label>
        <input 
            id="pergunta"
            type="text"
            data-testid="input-pergunta"
            aria-required="true"
        >
        <button 
            type="submit"
            data-testid="btn-enviar"
            aria-label="Enviar pergunta"
        >
            Enviar
        </button>
    </form>
    <div data-testid="chat-respostas" role="log" aria-live="polite">
        <!-- Mensagens -->
    </div>
    ```

*   **Lembrete**: "Testabilidade (IDs únicos) é a garantia da longevidade do código."

### 9.4 Outras Regras Frontend

*   **Tema**: Suporte a tema claro/escuro baseado nas preferências do sistema:
    ```css
    @media (prefers-color-scheme: dark) {
        /* Estilos dark mode */
    }
    ```

*   **Markdown**: Use markdown para renderização de respostas do chatbot.

*   **Timeout**: Implemente timeouts adequados para requisições ao backend.

*   **Loading States**: Sempre forneça feedback visual durante operações assíncronas:
    ```html
    <button data-testid="btn-enviar" aria-busy="true" disabled>
        <span aria-hidden="true">⏳</span>
        <span class="sr-only">Enviando...</span>
    </button>
    ```

## 10. Documentação

*   Mantenha o `README.md` atualizado com instruções de instalação e uso.

*   Adicione docstrings (Google Style) em todas as funções e classes públicas.

*   Documente mudanças significativas no `docs/CHANGELOG.md`.

*   Se uma regra mudar, atualize este arquivo (`docs/REGRAS_REVISAO.md`).

*   Documente configurações de ambiente no `.env.example` (sem valores reais).

## 11. Smoke Test Obrigatório (Manual)

⚠️ **ANTES de qualquer commit**, execute manualmente:

- [ ] **Inspeção de Código**: Verifique se os novos elementos de UI possuem `data-testid`
- [ ] **Navegação por Teclado**: TAB funciona em tudo? Foco visível?
- [ ] **Fluxo Feliz**: Envio de mensagem e recebimento de resposta funcionam?
- [ ] **Leitor de Tela**: O `aria-live` anuncia a resposta?

## 12. Checklist de Revisão e Definição de Pronto (DoD)

Antes de abrir um Pull Request, verifique **TODOS** os itens:

### Qualidade de Código
- [ ] Linters executados sem erros (`make lint`)
- [ ] Código formatado (`make format`)
- [ ] Código simples usando SDK nativo (sem LangChain/LangGraph)
- [ ] Sem dependências de LangChain ou frameworks pesados

### Testes
- [ ] Todos os testes unitários passando (100%) (`make test-unit`)
- [ ] Cobertura de testes acima de 95% (`make test-cov`)
- [ ] Testes E2E (Playwright) usando `get_by_test_id` passaram (`make test-e2e`)
- [ ] Verificação axe-core sem violações críticas (se disponível)

### Acessibilidade e UI
- [ ] Elementos de UI possuem `data-testid` (todos os componentes interativos)
- [ ] Navegação por teclado funciona completamente
- [ ] Gerenciamento de foco correto (foco não se perde)
- [ ] Screen readers anunciam mudanças (`aria-live`)

### Git e Segurança
- [ ] Sem commits de secrets ou informações sensíveis
- [ ] Mensagens de commit semânticas e em português
- [ ] Branch criada a partir da `main` atualizada (nunca commitou na main)
- [ ] Código revisado e sem código comentado desnecessário

### Documentação
- [ ] Documentação atualizada (se necessário)
- [ ] Type hints adicionados em novas funções
- [ ] Tratamento de erros adequado
- [ ] Logs apropriados (sem informações sensíveis)

### Lembrete do Agente
> "Acessibilidade é a alma do projeto. Testabilidade (IDs únicos) é a garantia da longevidade do código."

## 13. Regras Específicas do Projeto

*   **Google Gemini API**: Use o Google ADK (Agent Development Kit) para interação com Gemini. Não use a API REST diretamente.

*   **OpenRouter**: Configure modelos gratuitos como fallback. Documente quais modelos estão sendo usados.

*   **Streamlit**: Mantido como alternativa. Não remova sem consenso da equipe.

*   **FastAPI**: API principal. Mantenha compatibilidade com o frontend HTML.

*   **Configuração**: Use Pydantic Settings para gerenciamento de configurações. Valide todas as configurações na inicialização.

*   **Tratamento de Erros**: Nunca falhe silenciosamente; exiba erros acessíveis com `aria-live="polite"` ou `role="alert"`.

## 14. Performance

*   **Cache**: Use cache para respostas frequentes. Limpe cache quando apropriado.

*   **Timeout**: Configure timeouts adequados para todas as operações assíncronas.

*   **Rate Limiting**: Respeite os limites de rate limiting do FastAPI.

*   **Logging**: Use logging estruturado. Não logue em excesso em produção.

## 15. Manutenção

*   **Dependências**: Mantenha dependências atualizadas, mas teste antes de atualizar versões major.

*   **Python Version**: O projeto usa Python 3.12+ (versão estável mais recente). Mantenha compatibilidade.

*   **Breaking Changes**: Documente breaking changes no CHANGELOG e considere versionamento semântico.

---

**Última atualização**: 2025-11-23

**Versão**: 2.0.0

---

## Changelog de Regras

### Versão 2.0.0 (2025-11-23)
- Adicionada seção 8.1: Stack de IA (proibição de LangChain/LangGraph)
- Atualizada seção 9.1: WCAG 2.2 AA/AAA (Prioridade Zero)
- Expandida seção 9.3: Test IDs com mais detalhes e exemplos
- Atualizada seção 4: Estratégia de Testes (Pirâmide + Playwright)
- Adicionada seção 11: Smoke Test Obrigatório
- Atualizada seção 12: Checklist de Revisão e DoD completo
- Adicionado lembrete do agente sobre acessibilidade e testabilidade

