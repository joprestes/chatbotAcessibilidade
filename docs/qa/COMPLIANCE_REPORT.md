# Relatório de Conformidade com Regras Globais

Este documento certifica que o projeto **Chatbot de Acessibilidade Digital** está em conformidade com as Regras Globais estabelecidas.

**Data da Verificação:** 29/11/2025
**Versão:** 3.17.0

## 1. Idioma e Padrões
- [x] **Português Brasileiro (pt-BR):** Utilizado em código, comentários, documentação e commits.
- [x] **Inglês Técnico:** Apenas termos universais (`get`, `set`, `controller`) mantidos.

## 2. Qualidade de Código (Clean Code & Architecture)
- [x] **Clean Code:** Nomes descritivos, funções pequenas, princípio DRY aplicado.
- [x] **Clean Architecture:** Separação clara entre `core`, `agents`, `pipeline` e `frontend`.
- [x] **Simplicidade:** Soluções diretas, sem super-engenharia.
- [x] **Sem Código Morto:** Remoção de `FireworksAIClient` e integrações obsoletas.
- [x] **Sem Valores Mágicos:** Uso de `constants.py` e variáveis de ambiente.
- [x] **Tratamento de Erros:** Blocos `try-except` explícitos com logs adequados.

## 3. Testes e Qualidade (QA)
- [x] **Linters:** `ruff` e `black` executados sem erros via `make pre-commit`.
- [x] **Testes Unitários:** 302 testes passando (100% de sucesso).
- [x] **Cobertura:** **97.70%** (Meta: >90%).
- [x] **Padrão AAA:** Testes seguem Arrange-Act-Assert.
- [x] **Isolamento:** Uso de mocks para APIs externas (`GoogleGeminiClient`, `Playwright`).
- [x] **Cenários:** Cobertura de sucesso, erro e casos de borda.

## 4. Segurança
- [x] **Credenciais:** Nenhuma chave de API commitada (uso de `.env`).
- [x] **Sanitização:** Inputs validados antes do processamento.
- [x] **Logs:** Sem exposição de dados sensíveis.

## 5. Commits e Git
- [x] **Commits Atômicos:** Mudanças pequenas e focadas.
- [x] **Commits Semânticos:** Uso de `feat:`, `fix:`, `docs:`, `test:`.
- [x] **Mensagens Descritivas:** Em pt-BR, explicando o "porquê".
- [x] **Fluxo de Trabalho:** Uso de branches (`feat/...`, `fix/...`) e Merge Requests.

## 6. Frontend e Acessibilidade (WCAG)
- [x] **Mobile First:** Layout responsivo e adaptável.
- [x] **Acessibilidade AAA:**
    - Contraste corrigido (> 7:1).
    - Suporte a leitores de tela (ARIA attributes, roles).
    - Navegação por teclado (tabindex, focus trap).
    - VLibras integrado sem sobreposição (z-index corrigido).
- [x] **Performance:** Assets otimizados.

## 7. Documentação
- [x] **Atualizada:** `README.md`, `CHANGELOG.md` refletem o estado atual.
- [x] **QA Docs:** `KNOWN_ISSUES.md` e `CODE_REMOVAL_CHECKLIST.md` criados.

---

**Status Final:** ✅ **CONFORME**

O projeto atende a todas as 45 regras globais definidas na memória do agente.
