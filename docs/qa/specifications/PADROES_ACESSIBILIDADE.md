# Padrões de Acessibilidade - Chatbot Acessibilidade

Este documento define os padrões de acessibilidade que devem ser seguidos no projeto, com foco especial em gerenciamento de foco e navegação por teclado.

## Gerenciamento de Foco

### Princípios Gerais

1. **Foco nunca deve se perder**: Após qualquer interação, o foco deve retornar para um elemento lógico e acessível
2. **Foco visível**: O elemento com foco deve ter um indicador visual claro (outline, border, etc.)
3. **Ordem lógica**: A ordem de tabulação deve seguir a ordem visual e semântica da página

### Padrões Específicos

#### 1. Após Envio de Mensagem

**Padrão Implementado:**
```javascript
// frontend/app.js - linha ~538
async function sendMessage(pergunta) {
    // ... código de envio ...
    
    // Após envio bem-sucedido, foco retorna ao input
    userInput.focus();
}
```

**Justificativa**: Permite que o usuário continue digitando sem precisar clicar novamente no campo.

**Teste**: `test_focus_returns_to_input_after_send()` em `test_focus_management.py`

#### 2. Após Abrir/Fechar Busca

**Padrão Implementado:**
```javascript
// frontend/app.js - linha ~389
function toggleSearch() {
    // ... código de toggle ...
    
    if (searchWrapper.classList.contains('hidden')) {
        // Fecha busca
    } else {
        // Abre busca e foca no input
        searchInput?.focus();
    }
}
```

**Justificativa**: Quando o campo de busca é aberto, o foco deve ir diretamente para ele.

**Teste**: `test_focus_after_search_toggle()` em `test_focus_management.py`

#### 3. Após Limpar Chat

**Padrão Recomendado:**
```javascript
function clearMessages() {
    // ... código de limpeza ...
    
    // Após limpar, foco retorna ao input
    userInput.focus();
}
```

**Status**: A ser implementado se necessário.

**Teste**: `test_focus_after_clear_chat()` em `test_focus_management.py`

#### 4. Após Fechamento de Modais (Futuro)

**Padrão Recomendado:**
```javascript
function closeModal() {
    // ... código de fechamento ...
    
    // Retorna foco para o elemento que abriu o modal
    // ou para o primeiro elemento focável da página
    previousFocusedElement?.focus() || firstFocusableElement.focus();
}
```

**Status**: Não há modais no projeto atual, mas este padrão deve ser seguido se modais forem adicionados.

**Justificativa**: Retornar o foco para o elemento que abriu o modal mantém o contexto do usuário.

### Navegação por Teclado

#### Ordem de Tabulação

A ordem de tabulação deve seguir esta sequência:

1. Skip link (se visível)
2. Botão de busca (header)
3. Botão de limpar chat (header)
4. Botão de toggle de tema (header)
5. Input de pergunta (footer)
6. Botão de enviar (footer)
7. Mensagens do chat (se interativas)

#### Atalhos de Teclado

- **Enter**: Envia mensagem (quando foco está no input)
- **Shift + Enter**: Nova linha no input
- **Escape**: Cancela requisição em andamento (se aplicável)
- **Tab**: Navega para próximo elemento focável
- **Shift + Tab**: Navega para elemento anterior

### Screen Readers

#### ARIA Live Regions

**Chat Container:**
```html
<div id="chat-container" 
     role="log" 
     aria-live="polite" 
     aria-label="Histórico de mensagens">
```

**Toast Container:**
```html
<div id="toast-container" 
     role="region" 
     aria-live="assertive" 
     aria-label="Notificações">
```

**Justificativa**: 
- `aria-live="polite"` para mensagens do chat (não interrompe o usuário)
- `aria-live="assertive"` para toasts/erros (prioridade alta)

#### ARIA Labels

Todos os botões sem texto visível devem ter `aria-label`:

```html
<button 
    data-testid="btn-buscar"
    aria-label="Buscar no histórico"
    aria-expanded="false">
    <!-- Ícone SVG -->
</button>
```

### Indicadores Visuais de Foco

O CSS deve garantir que elementos focáveis tenham indicador visível:

```css
/* Exemplo mínimo */
button:focus,
input:focus,
textarea:focus {
    outline: 2px solid var(--focus-color);
    outline-offset: 2px;
}
```

## Checklist de Implementação

Ao adicionar novos componentes interativos:

- [ ] Elemento tem `data-testid` único
- [ ] Elemento é focável via teclado (Tab)
- [ ] Elemento tem indicador visual de foco
- [ ] Elemento tem `aria-label` ou texto visível
- [ ] Foco é gerenciado corretamente após interação
- [ ] Ordem de tabulação é lógica
- [ ] Screen reader anuncia mudanças relevantes (`aria-live`)

## Referências

- [WCAG 2.2 - Focus Management](https://www.w3.org/WAI/WCAG22/Understanding/focus-order.html)
- [ARIA Authoring Practices - Focus Management](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/)
- [MDN - Keyboard Navigation](https://developer.mozilla.org/en-US/docs/Web/Accessibility/Keyboard-navigable_JavaScript_widgets)

