# Checklist de Remoção de Código

Este documento fornece um processo estruturado para remover código morto ou funcionalidades descontinuadas de forma segura, minimizando riscos e garantindo qualidade.

## 🎯 Objetivo

Remover código de forma segura requer planejamento e validação cuidadosa. Este checklist garante que:
- Nenhuma funcionalidade ativa seja quebrada
- A cobertura de testes seja mantida ou melhorada
- Dependências sejam corretamente atualizadas
- A documentação reflita as mudanças

## 📋 Checklist Completo

### Fase 1: Planejamento e Análise

- [ ] **Identificar o código a ser removido**
  - Listar arquivos, funções, classes e módulos
  - Documentar o motivo da remoção
  - Verificar se há alternativas implementadas

- [ ] **Analisar dependências**
  - Usar `grep` ou IDE para encontrar todas as referências
  - Identificar código que depende do que será removido
  - Verificar imports e chamadas de função

- [ ] **Verificar impacto em testes**
  - Identificar testes que cobrem o código a ser removido
  - Verificar se há testes que dependem indiretamente

- [ ] **Documentar estado atual**
  - Registrar cobertura de testes atual: `pytest --cov --cov-report=term`
  - Fazer screenshot ou salvar relatório de cobertura
  - Anotar percentual total e por arquivo

### Fase 2: Preparação

- [ ] **Criar branch específica**
  ```bash
  git checkout -b refactor/remove-<feature-name>
  ```

- [ ] **Backup de segurança**
  - Commitar qualquer trabalho em andamento
  - Garantir que a branch está atualizada com `main`

- [ ] **Identificar código não testado**
  - Executar `pytest --cov --cov-report=html`
  - Abrir `htmlcov/index.html` e identificar linhas não cobertas
  - Priorizar adicionar testes ANTES de remover código

### Fase 3: Adicionar Testes (se necessário)

- [ ] **Cobrir cenários não testados**
  - Criar testes para código que ficará exposto após remoção
  - Focar em cenários de erro e edge cases
  - Garantir cobertura >= 95%

- [ ] **Validar testes adicionados**
  ```bash
  pytest tests/unit/ tests/integration/ -v
  pytest --cov --cov-fail-under=95
  ```

- [ ] **Commitar testes separadamente**
  ```bash
  git add tests/
  git commit -m "test: add coverage for <module> before removal"
  ```

### Fase 4: Remoção de Código

- [ ] **Remover imports não utilizados**
  - Remover imports do código a ser deletado
  - Executar `ruff check` para identificar imports órfãos

- [ ] **Remover código principal**
  - Deletar arquivos completos OU
  - Remover funções/classes específicas
  - Atualizar `__init__.py` se necessário

- [ ] **Remover testes relacionados**
  - Deletar testes que testam apenas o código removido
  - Atualizar testes que tinham dependências

- [ ] **Atualizar configurações**
  - Remover variáveis de ambiente obsoletas (`.env`, `config.py`)
  - Atualizar `requirements.txt` se bibliotecas não são mais necessárias
  - Atualizar `pyproject.toml` se configurações mudaram

- [ ] **Atualizar constantes e mensagens**
  - Remover constantes não utilizadas de `constants.py`
  - Remover mensagens de erro obsoletas

### Fase 5: Validação

- [ ] **Executar linters**
  ```bash
  ruff check .
  black --check .
  ```

- [ ] **Corrigir erros de linting**
  ```bash
  ruff check --fix .
  black .
  ```

- [ ] **Executar suite completa de testes**
  ```bash
  pytest tests/unit/ tests/integration/ -v
  ```

- [ ] **Verificar cobertura de testes**
  ```bash
  pytest --cov --cov-report=term --cov-fail-under=95
  ```
  - ⚠️ **CRÍTICO**: Cobertura deve ser >= 95%
  - Se caiu, adicione testes antes de prosseguir

- [ ] **Executar testes E2E (se aplicável)**
  ```bash
  pytest tests/e2e/playwright/ -v -m "playwright"
  ```

### Fase 6: Documentação

- [ ] **Atualizar README.md**
  - Remover menções à funcionalidade removida
  - Atualizar exemplos de uso
  - Atualizar lista de features

- [ ] **Atualizar CHANGELOG.md**
  - Adicionar entrada na seção `[Unreleased]` ou próxima versão
  - Usar categoria `### Removed`
  - Explicar o que foi removido e por quê

- [ ] **Atualizar documentação técnica**
  - Atualizar guias em `docs/`
  - Remover referências obsoletas
  - Atualizar diagramas se necessário

- [ ] **Atualizar comentários de código**
  - Remover TODOs relacionados
  - Atualizar docstrings que mencionavam o código removido

### Fase 7: Commit e Push

- [ ] **Revisar mudanças**
  ```bash
  git status
  git diff
  ```

- [ ] **Commitar mudanças**
  ```bash
  git add .
  git commit -m "refactor: remove <feature-name>

  - Remove <list of removed files/classes>
  - Update tests and documentation
  - Maintain test coverage at XX%"
  ```

- [ ] **Executar validação pré-commit**
  ```bash
  make pre-commit
  ```

- [ ] **Push para repositório**
  ```bash
  git push origin refactor/remove-<feature-name>
  ```

### Fase 8: Code Review

- [ ] **Criar Pull Request**
  - Descrever o que foi removido
  - Explicar o motivo
  - Listar arquivos afetados
  - Incluir antes/depois da cobertura

- [ ] **Solicitar revisão**
  - Marcar reviewers apropriados
  - Aguardar aprovação

- [ ] **Validar CI/CD**
  - Garantir que pipeline passa
  - Verificar cobertura no CI
  - Verificar testes E2E no CI

## 🚨 Sinais de Alerta

**PARE e revise se:**
- ❌ Cobertura de testes caiu abaixo de 95%
- ❌ Mais de 5 testes falharam
- ❌ Linters reportam erros não relacionados
- ❌ Você não tem certeza do impacto da remoção

**Ações corretivas:**
1. Reverter mudanças: `git reset --hard HEAD`
2. Re-analisar dependências
3. Adicionar mais testes
4. Pedir ajuda de outro desenvolvedor

## 📊 Exemplo de Remoção Bem-Sucedida

**Contexto:** Remoção de `FireworksAIClient` e `generate_with_fallback`

**Antes:**
- Cobertura: 88.90%
- Arquivos: 15 arquivos com referências

**Processo:**
1. ✅ Identificadas todas as referências (grep, IDE)
2. ✅ Adicionados testes de cobertura para `llm_provider.py` e `orquestrador.py`
3. ✅ Removidos arquivos e funções
4. ✅ Atualizados testes e configurações
5. ✅ Executados linters e testes

**Depois:**
- Cobertura: 97.70% ⬆️
- Commits: 3 (testes, remoção, documentação)
- CI: ✅ Passou

**Referência:** Commits `4099100c` a `5c1269ab`

## 🔗 Recursos Relacionados

- [KNOWN_ISSUES.md](./KNOWN_ISSUES.md) - Problemas conhecidos e soluções
- [GUIA_CODE_REVIEW.md](./guides/GUIA_CODE_REVIEW.md) - Guia de code review
- [Makefile](../../Makefile) - Comando `make pre-commit`

## 📝 Histórico de Revisões

| Data       | Autor | Mudança                          |
|------------|-------|----------------------------------|
| 2025-11-29 | QA    | Criação inicial do documento     |

---

**Lembre-se:** Remover código é tão importante quanto adicionar. Faça com cuidado e atenção! 🧹
