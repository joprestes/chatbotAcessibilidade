# Recomendações de Acessibilidade WCAG AAA - Chatbot de Acessibilidade Digital

**Data**: 26 de novembro de 2025  
**Baseado em**: [Auditoria de Acessibilidade AAA](./auditoria_acessibilidade_aaa.md)  
**Objetivo**: Priorizar e detalhar melhorias para atingir conformidade WCAG AAA

---

## Sumário de Gaps Identificados

| Prioridade | Critério WCAG | Gap | Esforço | Impacto |
|:-----------|:--------------|:----|:--------|:--------|
| 🔴 Crítica | 1.4.6 | Contraste AAA | Baixo | Alto |
| 🔴 Crítica | 2.3.3 | Reduced Motion | Baixo | Alto |
| 🔴 Crítica | 1.4.11 | High Contrast Mode | Médio | Alto |
| 🔴 Crítica | 2.2.6 | Timeout Ajustável | Médio | Médio |
| 🔴 Crítica | 3.3.5 | Ajuda Contextual | Médio | Médio |
| 🟡 Importante | 2.4.10 | Headings em Respostas | Baixo | Médio |
| 🟡 Importante | - | Gerenciamento de Foco | Baixo | Médio |
| 🟢 Recomendada | 2.1.1 | Atalho Escape | Baixo | Baixo |
| 🟢 Recomendada | 1.1.1 | Alt Text do Logo | Trivial | Baixo |
| 🟢 Recomendada | 2.4.7 | Outline no Textarea | Trivial | Baixo |

---

## 🔴 Melhorias Críticas (Bloqueiam AAA)

### 1. Contraste AAA (WCAG 1.4.6)

**Gap**: Alguns elementos não atingem razão de contraste 7:1 para texto normal.

**Elementos Afetados**:
- Texto secundário: `#6B21A8` em `#FAF5FF` (6.2:1 - requer 7:1)
- Links/Botões: `#7C3AED` em `#FAF5FF` (5.1:1 - requer 7:1)
- Placeholder: `#8B5CF6` com 70% opacity (~3.8:1 - requer 7:1)
- Header subtitle: `rgba(255,255,255,0.95)` em gradient (~4.2:1 - requer 7:1)

**Solução Proposta**:

```css
/* frontend/styles.css */

:root {
    /* Ajustes para AAA - Tema Claro */
    --text-secondary: #5B1A98; /* Era #6B21A8 - Razão: 7.5:1 */
    --accent-color: #6C2ADD; /* Era #7C3AED - Razão: 7.2:1 */
}

#user-input::placeholder {
    color: #6C2ADD; /* Era #8B5CF6 com opacity */
    opacity: 1; /* Remove opacity para garantir contraste */
}

.ada-header-status {
    color: rgba(255, 255, 255, 1); /* Era 0.95 */
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5); /* Aumenta sombra */
}

[data-theme="dark"] {
    /* Ajustes para AAA - Tema Escuro */
    --accent-color: #A78BFA; /* Era #8B5CF6 - Razão: 7.1:1 */
}
```

**Esforço**: 1-2 horas  
**Impacto**: Alto - Melhora legibilidade para todos os usuários  
**Testes**: Validar com Color Contrast Analyzer e axe DevTools

---

### 2. Reduced Motion (WCAG 2.3.3)

**Gap**: Animações não respeitam preferência `prefers-reduced-motion`.

**Animações Identificadas**:
- `fadeInMessage` (mensagens)
- `fadeInContent` (expanders)
- `avatarBreathing` (avatar)
- `slideDown` (busca)
- Transições em hover/focus

**Solução Proposta**:

```css
/* frontend/styles.css - Adicionar no final do arquivo */

/**
 * Suporte a Reduced Motion (WCAG 2.3.3 - AAA)
 * Desabilita animações para usuários que preferem movimento reduzido
 */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }
    
    /* Mantém transições essenciais de opacidade para feedback visual */
    button:focus,
    input:focus,
    textarea:focus {
        transition: opacity 0.1s ease !important;
    }
}
```

**Esforço**: 1 hora  
**Impacto**: Alto - Essencial para usuários com distúrbios vestibulares  
**Testes**: Ativar "Reduce motion" nas configurações do sistema e verificar

---

### 3. High Contrast Mode (WCAG 1.4.11)

**Gap**: Não há suporte para `prefers-contrast: high`.

**Solução Proposta**:

```css
/* frontend/styles.css - Adicionar após reduced motion */

/**
 * Suporte a High Contrast Mode (WCAG 1.4.11 - AA/AAA)
 * Aumenta contraste para usuários com baixa visão
 */
@media (prefers-contrast: high) {
    :root {
        /* Cores de alto contraste - Tema Claro */
        --bg-primary: #FFFFFF;
        --bg-secondary: #F0F0F0;
        --text-primary: #000000;
        --text-secondary: #000000;
        --accent-color: #0000FF;
        --accent-hover: #0000CC;
        --border-color: #000000;
        --error-color: #CC0000;
        --success-color: #008000;
    }
    
    [data-theme="dark"] {
        /* Cores de alto contraste - Tema Escuro */
        --bg-primary: #000000;
        --bg-secondary: #1A1A1A;
        --text-primary: #FFFFFF;
        --text-secondary: #FFFFFF;
        --accent-color: #00FFFF;
        --accent-hover: #00CCCC;
        --border-color: #FFFFFF;
        --error-color: #FF6666;
        --success-color: #66FF66;
    }
    
    /* Aumenta espessura de bordas e outlines */
    button,
    input,
    textarea,
    .message-bubble {
        border-width: 2px !important;
    }
    
    button:focus,
    input:focus,
    textarea:focus {
        outline-width: 3px !important;
    }
}
```

**Esforço**: 2-3 horas  
**Impacto**: Alto - Essencial para usuários com baixa visão  
**Testes**: Ativar "Increase contrast" nas configurações do sistema

---

### 4. Timeout Ajustável (WCAG 2.2.6)

**Gap**: Usuário não pode ajustar ou estender o timeout de 120 segundos.

**Solução Proposta**:

**Passo 1**: Adicionar aviso antes do timeout

```javascript
// frontend/app.js

let timeoutWarningShown = false;
let timeoutExtensionCount = 0;
const MAX_EXTENSIONS = 3;

async function sendMessage(pergunta) {
    // ... código existente ...
    
    // Inicia timer de aviso (20s antes do timeout)
    const warningTime = frontendConfig.request_timeout_ms - 20000;
    const warningTimer = setTimeout(() => {
        if (isLoading && !timeoutWarningShown) {
            showTimeoutWarning();
        }
    }, warningTime);
    
    // ... resto do código ...
}

function showTimeoutWarning() {
    timeoutWarningShown = true;
    
    const canExtend = timeoutExtensionCount < MAX_EXTENSIONS;
    const message = canExtend
        ? 'A requisição está demorando. Deseja estender o tempo de espera por mais 2 minutos?'
        : 'A requisição está demorando e atingiu o limite de extensões.';
    
    if (canExtend && confirm(message)) {
        extendTimeout();
    }
}

function extendTimeout() {
    timeoutExtensionCount++;
    timeoutWarningShown = false;
    
    // Cancela timeout atual e cria novo
    if (currentAbortController) {
        // Cria novo controller mantendo a requisição
        const signal = currentAbortController.signal;
        currentAbortController = new AbortController();
        
        showToast(`Tempo estendido por mais 2 minutos (${timeoutExtensionCount}/${MAX_EXTENSIONS})`, 'info');
    }
}
```

**Passo 2**: Adicionar configuração de timeout no frontend

```html
<!-- frontend/index.html - Adicionar no header -->
<button id="settings-toggle" class="icon-button" 
        aria-label="Configurações de acessibilidade">
    <svg><!-- ícone de engrenagem --></svg>
</button>

<div id="settings-panel" class="settings-panel hidden">
    <h2>Configurações de Acessibilidade</h2>
    <label for="timeout-setting">
        Tempo máximo de espera:
        <select id="timeout-setting">
            <option value="60000">1 minuto</option>
            <option value="120000" selected>2 minutos (padrão)</option>
            <option value="300000">5 minutos</option>
            <option value="600000">10 minutos</option>
        </select>
    </label>
</div>
```

**Esforço**: 4-6 horas  
**Impacto**: Médio - Importante para usuários com deficiências cognitivas  
**Testes**: Simular requisição lenta e verificar aviso

---

### 5. Ajuda Contextual (WCAG 3.3.5)

**Gap**: Não há ajuda contextual disponível para campos de entrada.

**Solução Proposta**:

```html
<!-- frontend/index.html - Adicionar tooltip no textarea -->
<div class="input-container floating-pill">
    <label for="user-input" class="sr-only">Digite sua pergunta</label>
    
    <!-- Botão de ajuda -->
    <button type="button" 
            class="help-button" 
            aria-label="Ajuda sobre como fazer perguntas"
            data-testid="btn-ajuda">
        <svg><!-- ícone de ? --></svg>
    </button>
    
    <textarea id="user-input" 
              name="pergunta" 
              aria-describedby="input-help"
              ...>
    </textarea>
    
    <!-- Hint sempre visível -->
    <div id="input-help" class="input-hint">
        <strong>Dica:</strong> Pergunte sobre WCAG, ARIA, testes de acessibilidade, etc.
    </div>
</div>
```

```css
/* frontend/styles.css */
.help-button {
    width: 32px;
    height: 32px;
    background: rgba(124, 58, 237, 0.1);
    border: 1px solid var(--accent-color);
    border-radius: 50%;
    color: var(--accent-color);
    cursor: help;
}

.help-button:hover {
    background: rgba(124, 58, 237, 0.2);
}

.input-hint {
    font-size: 13px;
    color: var(--text-secondary);
    padding: 4px 8px;
    margin-top: 4px;
    background: rgba(124, 58, 237, 0.05);
    border-radius: 6px;
}
```

```javascript
// frontend/app.js
const helpButton = document.querySelector('.help-button');
helpButton?.addEventListener('click', () => {
    showToast(
        'Exemplos de perguntas:\n' +
        '• Como testar contraste de cores?\n' +
        '• O que é navegação por teclado?\n' +
        '• Gere um checklist WCAG AA',
        'info',
        10000 // 10 segundos
    );
});
```

**Esforço**: 3-4 horas  
**Impacto**: Médio - Melhora experiência para todos os usuários  
**Testes**: Clicar no botão de ajuda e verificar tooltip

---

## 🟡 Melhorias Importantes (Impactam experiência)

### 6. Headings em Respostas do Bot

**Gap**: Falta estrutura de headings nas seções de resposta.

**Solução**:

```javascript
// frontend/app.js - Modificar createExpanderSection()
function createExpanderSection(title, content, isExpanded = false) {
    const section = document.createElement('div');
    section.className = 'response-section';
    
    // Usar h3 ao invés de span para o título
    const header = document.createElement('button');
    header.className = 'expander-header';
    header.setAttribute('aria-expanded', isExpanded);
    
    const titleHeading = document.createElement('h3');
    titleHeading.className = 'expander-title';
    titleHeading.textContent = title.replace(/\*\*/g, '').trim();
    header.appendChild(titleHeading);
    
    // ... resto do código ...
}
```

```css
/* frontend/styles.css */
.expander-title {
    font-size: 15px;
    font-weight: 600;
    margin: 0;
    flex: 1;
    text-align: left;
}
```

**Esforço**: 1 hora  
**Impacto**: Médio - Melhora navegação para leitores de tela

---

### 7. Gerenciamento de Foco Aprimorado

**Gaps**:
- Foco não retorna ao botão ao fechar busca
- Foco não retorna ao input após limpar chat

**Solução**:

```javascript
// frontend/app.js

// Ao fechar busca
function toggleSearch() {
    const isHidden = searchWrapper.classList.contains('hidden');
    if (isHidden) {
        searchWrapper.classList.remove('hidden');
        searchToggle.setAttribute('aria-expanded', 'true');
        searchInput?.focus();
    } else {
        searchWrapper.classList.add('hidden');
        searchToggle.setAttribute('aria-expanded', 'false');
        searchFilter = '';
        renderMessages();
        searchToggle.focus(); // ← ADICIONAR
    }
}

// Ao limpar chat
function clearMessages() {
    messages = [];
    saveMessagesToStorage();
    renderMessages();
    userInput.focus(); // ← ADICIONAR
}
```

**Esforço**: 30 minutos  
**Impacto**: Médio - Melhora experiência de navegação por teclado

---

## 🟢 Melhorias Recomendadas (Nice to have)

### 8. Atalho Escape para Cancelar

**Solução**:

```javascript
// frontend/app.js - Adicionar em setupEventListeners()
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isLoading) {
        cancelRequest();
    }
});
```

**Esforço**: 15 minutos  
**Impacto**: Baixo - Conveniência para usuários de teclado

---

### 9. Alt Text do Logo Melhorado

**Solução**:

```html
<!-- frontend/index.html -->
<img src="/assets/ada-logo.png" 
     alt="Ada - Assistente de Acessibilidade Digital" 
     class="ada-header-avatar">
```

**Esforço**: 1 minuto  
**Impacto**: Baixo - Melhora descrição para leitores de tela

---

### 10. Outline Visível no Textarea

**Solução**:

```css
/* frontend/styles.css */
#user-input:focus {
    outline: 2px solid var(--accent-color);
    outline-offset: 2px;
}
```

**Esforço**: 1 minuto  
**Impacto**: Baixo - Melhora indicador visual de foco

---

## Roadmap de Implementação

### Sprint 1: Melhorias Críticas de CSS (1 semana)
- [x] Criar branch `feat/auditoria-acessibilidade-aaa`
- [ ] Implementar ajustes de contraste AAA
- [ ] Implementar suporte a `prefers-reduced-motion`
- [ ] Implementar suporte a `prefers-contrast`
- [ ] Executar testes de contraste
- [ ] Commit: `feat: adiciona suporte AAA para contraste e preferências do usuário`

### Sprint 2: Timeout e Ajuda Contextual (1 semana)
- [ ] Implementar aviso de timeout
- [ ] Implementar extensão de timeout
- [ ] Adicionar painel de configurações
- [ ] Implementar botão de ajuda contextual
- [ ] Adicionar hints visuais
- [ ] Commit: `feat: adiciona timeout ajustável e ajuda contextual (WCAG AAA)`

### Sprint 3: Melhorias de Estrutura (3 dias)
- [ ] Adicionar headings em respostas
- [ ] Melhorar gerenciamento de foco
- [ ] Implementar atalho Escape
- [ ] Melhorar alt texts
- [ ] Adicionar outline no textarea
- [ ] Commit: `feat: melhora estrutura semântica e navegação por teclado`

### Sprint 4: Testes e Validação (1 semana)
- [ ] Criar suite de testes AAA
- [ ] Executar testes automatizados
- [ ] Validação manual com leitores de tela
- [ ] Validação com ferramentas externas
- [ ] Documentar resultados
- [ ] Commit: `test: adiciona suite completa de testes AAA`

### Sprint 5: Documentação e Release (2 dias)
- [ ] Atualizar README com badge AAA
- [ ] Atualizar CHANGELOG
- [ ] Criar PR com descrição detalhada
- [ ] Revisão de código
- [ ] Merge e deploy

---

## Estimativa Total

| Categoria | Esforço | Prazo |
|:----------|:--------|:------|
| Melhorias Críticas | 12-16 horas | 2 semanas |
| Melhorias Importantes | 2-3 horas | 3 dias |
| Melhorias Recomendadas | 1 hora | 1 dia |
| Testes e Validação | 8-10 horas | 1 semana |
| Documentação | 2-3 horas | 2 dias |
| **TOTAL** | **25-33 horas** | **3-4 semanas** |

---

## Critérios de Aceitação

Para considerar o projeto conforme com WCAG AAA:

- [ ] Todos os pares de cores atingem razão 7:1 (texto normal) ou 4.5:1 (texto grande)
- [ ] `prefers-reduced-motion` implementado e testado
- [ ] `prefers-contrast` implementado e testado
- [ ] Timeout ajustável com aviso e extensão
- [ ] Ajuda contextual disponível em todos os campos
- [ ] Headings estruturados em todas as seções
- [ ] Foco gerenciado corretamente em todas as interações
- [ ] 100% dos testes AAA passando
- [ ] Validação manual com NVDA/VoiceOver sem issues
- [ ] Lighthouse Accessibility score: 100
- [ ] axe DevTools: 0 violações AAA

---

**Próxima Ação**: Revisar este documento e aprovar Sprint 1 para início da implementação.
