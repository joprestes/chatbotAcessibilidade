# Regras do Workspace - Chatbot Acessibilidade

Este documento define as regras, padrões e convenções que devem ser seguidos por todos os desenvolvedores e agentes trabalhando no projeto Chatbot Acessibilidade.

## 1. Princípios Gerais

⚠️ **REGRA FUNDAMENTAL**: **NUNCA faça commits diretamente na branch `main`**. Sempre crie uma branch para qualquer alteração, por menor que seja.

*   **Idioma**: Todo o código, comentários, documentação e mensagens de commit devem ser em **Português Brasileiro (pt-BR)**. Termos técnicos universais (ex: *controller*, *service*, *payload*, *API*, *LLM*) podem ser mantidos em inglês.

*   **Clean Code**: O código deve ser legível, simples e autoexplicativo. Funções devem ser pequenas e ter uma única responsabilidade.

*   **SOLID**: Aplique os princípios SOLID onde fizer sentido, especialmente a separação de responsabilidades e injeção de dependências.

*   **KISS (Keep It Simple, Stupid)**: Evite complexidade acidental. A solução mais simples que resolve o problema é geralmente a melhor.

*   **YAGNI (You Aren't Gonna Need It)**: Não implemente funcionalidades pensando no futuro. Implemente apenas o necessário para os requisitos atuais.

*   **Acessibilidade**: Este é um projeto focado em acessibilidade. Sempre considere a experiência do usuário e garanta que todas as funcionalidades sejam acessíveis.

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

*   **Linting**: O projeto usa **Ruff**. Nenhum erro de lint deve ser ignorado sem uma justificativa forte (use `# noqa: EXXX` com o código do erro e explicação).

*   **Formatação**: O projeto usa **Black** e **Ruff format**. Todo código deve ser formatado automaticamente antes do commit.

*   **Type Checking**: Utilize type hints em todas as assinaturas de função. O projeto usa **MyPy** para verificação estática de tipos.

*   **Estrutura de Código**:

    *   Mantenha a estrutura modular em `src/chatbot_acessibilidade/`.
    *   Separe responsabilidades: `agents/`, `core/`, `backend/`.
    *   Use injeção de dependências quando apropriado.

## 4. Testes

*   **Framework**: Pytest com `pytest-asyncio` para testes assíncronos.

*   **Padrão AAA**: Organize os testes em Arrange (preparação), Act (ação) e Assert (verificação).

*   **Cobertura**: A meta é manter a cobertura de código acima de **95%**. A cobertura atual é de **98.93%** e deve ser mantida.

*   **Isolamento**: Testes unitários não devem depender de serviços externos (APIs reais do Google Gemini ou OpenRouter). Use `unittest.mock` ou `pytest-mock` para mockar chamadas externas.

*   **Nomenclatura**: `test_funcionalidade_cenario_resultado` (ex: `test_google_gemini_client_timeout_error`, `test_pipeline_agentes_paralelos_sucesso`).

*   **Estrutura de Testes**:

    *   Testes unitários em `tests/test_*.py`.
    *   Use fixtures do pytest para setup comum.
    *   Mock todas as dependências externas.

*   **Testes Assíncronos**: Sempre use `@pytest.mark.asyncio` para funções assíncronas.

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

*   **Multi-Agent System**: O projeto usa um sistema de múltiplos agentes (Assistant, Validator, Reviewer, Tester, Aprofundador). Mantenha a separação de responsabilidades.

*   **LLM Providers**: O projeto suporta múltiplos provedores de LLM (Google Gemini como primário, OpenRouter como fallback). Novos provedores devem seguir o padrão `LLMClient` em `core/llm_provider.py`.

*   **Fallback Mechanism**: O sistema de fallback automático deve ser mantido e testado. Não remova sem substituir por alternativa.

*   **Cache**: O sistema usa cache em memória para otimizar chamadas. Respeite o TTL e limites de tamanho.

*   **Async/Await**: Use operações assíncronas para todas as chamadas de API e operações I/O.

*   **Error Handling**: Use as exceções customizadas em `core/exceptions.py`. Não use exceções genéricas sem contexto.

## 9. Frontend

*   **Acessibilidade**: O frontend deve ser acessível (WCAG 2.1 AA mínimo).

*   **Responsividade**: Deve funcionar em desktop e mobile.

*   **Tema**: Suporte a tema claro/escuro baseado nas preferências do sistema.

*   **Markdown**: Use markdown para renderização de respostas do chatbot.

*   **Timeout**: Implemente timeouts adequados para requisições ao backend.

## 10. Documentação

*   Mantenha o `README.md` atualizado com instruções de instalação e uso.

*   Adicione docstrings (Google Style) em todas as funções e classes públicas.

*   Documente mudanças significativas no `docs/CHANGELOG.md`.

*   Se uma regra mudar, atualize este arquivo (`docs/REGRAS_REVISAO.md`).

*   Documente configurações de ambiente no `.env.example` (sem valores reais).

## 11. Checklist de Revisão

Antes de abrir um Pull Request, verifique:

- [ ] Todos os testes passam (`make test`)
- [ ] Cobertura de testes acima de 95% (`make test-cov`)
- [ ] Linters passam sem erros (`make lint`)
- [ ] Código formatado (`make format`)
- [ ] Sem commits de secrets ou informações sensíveis
- [ ] Documentação atualizada (se necessário)
- [ ] Mensagens de commit semânticas e em português
- [ ] Branch criada a partir da `main` atualizada
- [ ] Código revisado e sem código comentado desnecessário
- [ ] Type hints adicionados em novas funções
- [ ] Tratamento de erros adequado
- [ ] Logs apropriados (sem informações sensíveis)

## 12. Regras Específicas do Projeto

*   **Google Gemini API**: Use o Google ADK (Agent Development Kit) para interação com Gemini. Não use a API REST diretamente.

*   **OpenRouter**: Configure modelos gratuitos como fallback. Documente quais modelos estão sendo usados.

*   **Streamlit**: Mantido como alternativa. Não remova sem consenso da equipe.

*   **FastAPI**: API principal. Mantenha compatibilidade com o frontend HTML.

*   **Configuração**: Use Pydantic Settings para gerenciamento de configurações. Valide todas as configurações na inicialização.

## 13. Performance

*   **Cache**: Use cache para respostas frequentes. Limpe cache quando apropriado.

*   **Timeout**: Configure timeouts adequados para todas as operações assíncronas.

*   **Rate Limiting**: Respeite os limites de rate limiting do FastAPI.

*   **Logging**: Use logging estruturado. Não logue em excesso em produção.

## 14. Manutenção

*   **Dependências**: Mantenha dependências atualizadas, mas teste antes de atualizar versões major.

*   **Python Version**: O projeto usa Python 3.9+. Mantenha compatibilidade.

*   **Breaking Changes**: Documente breaking changes no CHANGELOG e considere versionamento semântico.

---

**Última atualização**: 2025-01-22

**Versão**: 1.0.0

