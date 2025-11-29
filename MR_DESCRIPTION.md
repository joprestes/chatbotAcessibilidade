# 🚀 Pull Request: Acessibilidade Avançada e Resiliência

Este PR consolida uma série de melhorias focadas em acessibilidade, robustez da API e qualidade de código.

## ✨ Principais Funcionalidades

### 1. Acessibilidade & UI (Frontend)
- **VLibras**: Integração do widget de tradução para Libras.
- **Controles de Acessibilidade**:
  - **Filtros de Cor**: Daltonismo (Protanopia, Deuteranopia, Tritanopia), Alto Contraste, Monocromático.
  - **Controle de Fonte**: Aumento/diminuição de tamanho e troca para fonte disléxica.
  - **Feedback Sonoro/Voz**: Opções para ativar/desativar leitura de tela e sons de interface.
- **Foco e Navegação**: Correção de bug onde o foco não retornava ao input após envio (WCAG 2.4.3).

### 2. Resiliência de API (Backend)
- **Fallback de Múltiplas Chaves**: Suporte nativo para `GOOGLE_API_KEY_SECOND` para dobrar a quota disponível.
- **Graceful Shutdown**: Implementação de mensagem amigável ("Sistema em Manutenção") quando **todas** as chaves atingem o limite, evitando erros 500/429 para o usuário.
- **Retry Logic**: Melhoria na lógica de tentativas automáticas antes de falhar.

### 3. Planejamento
- **Roadmap**: Adição de `docs/project/ROADMAP.md` detalhando as próximas fases (Multimodalidade, Design, PWA).

## � Correções e Melhorias Técnicas
- **Testes E2E**: Refatoração para maior estabilidade (remoção de `try/except` desnecessários, suporte a permissões de microfone).
- **Testes Unitários**: Atualização para suportar nova lógica de fallback e async/await.
- **Linting**: Correção de diversos erros de linting e tipagem (`mypy`, `ruff`).
- **Configuração**: Remoção de dependências legadas (HuggingFace/OpenRouter) da documentação e código.

## 📚 Documentação
- Atualização completa do `README.md` e `CHANGELOG.md`.
- Revisão dos guias de QA (`GUIA_CODE_REVIEW.md`, `GUIA_DESENVOLVEDOR_TESTES.md`).

## ✅ Checklist de Qualidade
- [x] Linters (Ruff, Black, MyPy) passando.
- [x] Testes Unitários e E2E passando.
- [x] Cobertura de testes > 95%.
- [x] Acessibilidade validada (WCAG AAA).
