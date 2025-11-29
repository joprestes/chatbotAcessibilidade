# Problemas Conhecidos e Soluções (Known Issues)

Este documento registra problemas conhecidos, quirks de bibliotecas externas e suas soluções para evitar retrabalho futuro.

## 🐛 Bibliotecas Externas

### axe-playwright-python

#### Problema: Serialização de Booleanos Python para JavaScript
**Sintoma:** `ReferenceError: True is not defined` ao usar `axe.run()` com opções contendo booleanos Python.

**Causa:** A biblioteca não converte automaticamente booleanos Python (`True`/`False`) para JavaScript (`true`/`false`) ao injetar opções no contexto do navegador.

**Solução:**
```python
# ❌ Errado - causa ReferenceError
results = axe.run(
    page,
    options={
        "rules": {
            "color-contrast": {"enabled": True},  # True do Python
        }
    },
)

# ✅ Correto - use inteiros
results = axe.run(
    page,
    options={
        "rules": {
            "color-contrast": {"enabled": 1},  # 1 é interpretado como truthy em JS
        }
    },
)
```

**Referência:** Corrigido em commits `82ee10a3` e `c8540fea`

---

#### Problema: API do AxeResults
**Sintoma:** `AttributeError: 'AxeResults' object has no attribute 'violations'`

**Causa:** O objeto retornado por `axe.run()` não expõe `violations` como atributo direto.

**Solução:**
```python
# ❌ Errado
results = axe.run(page)
violations = results.violations  # AttributeError

# ✅ Correto - acesse via response
results = axe.run(page)
violations = results.response["violations"]
```

**Referência:** Corrigido em commit `c8540fea`

---

### pytest-asyncio

#### Problema: Event Loop Teardown Errors
**Sintoma:** `ExceptionGroup: errors while tearing down fixture "event_loop"` em testes assíncronos.

**Causa:** Mocks assíncronos (`AsyncMock`) não sendo resetados corretamente ou event loops não sendo gerenciados adequadamente.

**Solução:**
- Sempre use `AsyncMock` para funções assíncronas
- Garanta que fixtures assíncronas sejam corretamente limpas
- Evite compartilhar estado entre testes assíncronos

**Status:** Monitorar - pode ocorrer esporadicamente

---

## 🎨 Frontend

### Contraste de Cores WCAG AAA

#### Problema: Violações de Contraste em Modo de Alto Contraste
**Sintoma:** Testes de acessibilidade AAA falhando com contraste insuficiente (< 7:1).

**Elementos Afetados:**
- `.input-hint`: Contraste 5.58 (necessário 7:1)
- `.char-counter`: Contraste 6.38 (necessário 7:1)
- Modo de alto contraste forçado: Múltiplos elementos com contraste ~1.4

**Solução:**
1. Escurecer cores para `#3B0764` (roxo muito escuro)
2. Remover opacity que reduz contraste
3. Adicionar suporte para `@media (forced-colors: active)`

```css
/* ✅ Correto - AAA compliant */
.input-hint {
    color: #3B0764; /* 7:1 contrast ratio */
    font-weight: 600;
}

.char-counter {
    color: #3B0764;
    opacity: 1; /* Sem opacity */
}

/* Suporte para modo de alto contraste */
@media (forced-colors: active) {
    * {
        color: CanvasText !important;
        background-color: Canvas !important;
    }
}
```

**Referência:** Corrigido em commit `5c1269ab`

---

## 🧪 Testes

### Cobertura de Testes

#### Problema: Cobertura Insuficiente Após Remoção de Código
**Sintoma:** Cobertura cai abaixo de 95% após remover código morto.

**Causa:** Linhas não testadas em cenários de erro e retry ficam expostas quando código de fallback é removido.

**Prevenção:**
1. Sempre verificar cobertura ANTES e DEPOIS de remover código
2. Adicionar testes para cenários de erro não cobertos
3. Usar `make pre-commit` antes de commitar

**Checklist de Remoção de Código:**
- [ ] Verificar cobertura atual
- [ ] Identificar código não testado
- [ ] Adicionar testes para código não coberto
- [ ] Remover código morto
- [ ] Verificar cobertura final (deve ser >= 95%)
- [ ] Rodar suite completa de testes

**Referência:** Corrigido em commits adicionando `test_llm_provider_coverage_fix.py` e `test_orquestrador_commands.py`

---

## 📋 Processo

### Pipeline CI/CD

#### Problema: Múltiplos Ciclos de CI Falhados
**Causa Raiz:** Falta de validação local completa antes do push.

**Solução Implementada:** Comando `make pre-commit`

```bash
make pre-commit
```

**O que verifica:**
1. Formatação (black)
2. Linting (ruff)
3. Testes unitários
4. Cobertura (>95%)

**Uso Recomendado:** Execute SEMPRE antes de fazer commit/push.

---

## 🔄 Atualizações

**Última atualização:** 2025-11-29  
**Responsável:** Equipe de QA

---

## 📝 Como Contribuir

Se você encontrar um novo problema ou quirk de biblioteca:

1. Documente aqui seguindo o formato:
   - **Sintoma:** O que você vê
   - **Causa:** Por que acontece
   - **Solução:** Como resolver
   - **Referência:** Commit ou PR que corrigiu

2. Adicione testes que validem a solução
3. Atualize a data de "Última atualização"
