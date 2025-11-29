# Guia Completo de Integração do VLibras

Este guia documenta o processo completo de integração do widget VLibras em uma aplicação web, incluindo todos os desafios encontrados e soluções aplicadas.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Método de Integração](#método-de-integração)
- [Configuração de CSP](#configuração-de-csp)
- [Problemas Comuns e Soluções](#problemas-comuns-e-soluções)
- [Validação](#validação)
- [Referências](#referências)

## 🎯 Visão Geral

O VLibras é um widget de acessibilidade que traduz conteúdo em português para Língua Brasileira de Sinais (Libras). A integração requer atenção especial a políticas de segurança (CSP) devido ao uso de WebAssembly e Unity.

## 🔧 Método de Integração

### Opção Recomendada: Carregamento Dinâmico

Ao invés de adicionar scripts estáticos no HTML, recomendamos o **carregamento dinâmico via JavaScript** para evitar condições de corrida e garantir inicialização correta.

#### 1. JavaScript (app.js)

```javascript
/**
 * Inicializa o widget VLibras carregando o script dinamicamente
 * Baseado em: https://pt.stackoverflow.com/questions/511562
 */
function initVLibras() {
    // Verifica se já existe para evitar duplicidade
    if (document.querySelector('[vw]')) return;

    // Injeta a estrutura HTML necessária
    const vlibrasDOM = `
        <aside aria-label="Ferramenta de tradução para Libras">
            <div vw class="enabled">
                <div vw-access-button class="active"></div>
                <div vw-plugin-wrapper>
                    <div class="vw-plugin-top-wrapper"></div>
                </div>
            </div>
        </aside>
    `;
    document.body.insertAdjacentHTML('beforeend', vlibrasDOM);

    // Carrega o script
    const script = document.createElement('script');
    script.src = 'https://vlibras.gov.br/app/vlibras-plugin.js';
    script.async = true;
    
    script.onload = () => {
        if (window.VLibras && window.VLibras.Widget) {
            new window.VLibras.Widget('https://vlibras.gov.br/app');
            console.log('VLibras widget initialized successfully');
        }
    };
    
    script.onerror = () => {
        console.warn('Falha ao carregar widget VLibras');
    };
    
    document.body.appendChild(script);
}

// Chamar após o DOM estar pronto
document.addEventListener('DOMContentLoaded', () => {
    // ... outras inicializações
    initVLibras();
});
```

#### 2. CSS (styles.css)

Garanta que modais e overlays tenham z-index suficiente para sobrepor o widget:

```css
.modal-overlay {
    z-index: 2147483647; /* Máximo z-index seguro (32-bit int) */
}
```

## 🔒 Configuração de CSP

**CRÍTICO:** O VLibras usa Unity WebAssembly e requer configurações específicas de Content Security Policy.

### CSP Completo Necessário

```python
# Backend (middleware.py ou equivalente)
csp_policy = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: "
        "https://vlibras.gov.br https://www.vlibras.gov.br https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' "
        "https://fonts.googleapis.com https://cdn.jsdelivr.net; "
    "img-src 'self' data: https:; "
    "font-src 'self' data: "
        "https://fonts.gstatic.com https://cdn.jsdelivr.net "
        "https://vlibras.gov.br https://www.vlibras.gov.br; "
    "connect-src 'self' "
        "https://vlibras.gov.br https://www.vlibras.gov.br "
        "https://dicionario2.vlibras.gov.br https://cdn.jsdelivr.net; "
    "worker-src 'self' blob:; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'self'"
)
```

### Detalhamento das Diretivas CSP

| Diretiva | Valores Necessários | Motivo |
|----------|-------------------|--------|
| `script-src` | `'unsafe-inline'` | Scripts inline do VLibras |
| `script-src` | `'unsafe-eval'` | **WebAssembly** (Unity) |
| `script-src` | `blob:` | Unity WebAssembly loader |
| `script-src` | `https://vlibras.gov.br` | Script principal |
| `script-src` | `https://www.vlibras.gov.br` | Chunks do plugin |
| `script-src` | `https://cdn.jsdelivr.net` | Fallback CDN |
| `connect-src` | `https://dicionario2.vlibras.gov.br` | API de dicionário |
| `connect-src` | `https://vlibras.gov.br` | Recursos do player |
| `connect-src` | `https://cdn.jsdelivr.net` | Recursos CDN |
| `font-src` | `https://vlibras.gov.br` | Fontes do widget |
| `font-src` | `https://www.vlibras.gov.br` | Fontes do widget |
| `worker-src` | `blob:` | Web Workers do Unity |

## ⚠️ Problemas Comuns e Soluções

### 1. Widget não aparece na tela

**Sintoma:** Console mostra "VLibras widget initialized successfully" mas o botão não está visível.

**Causa:** Estrutura HTML não foi criada antes do script carregar.

**Solução:** Use carregamento dinâmico (método acima) que injeta o HTML antes do script.

---

### 2. Erro: "ChunkLoadError: Loading chunk failed"

**Sintoma:**
```
Loading the script 'https://www.vlibras.gov.br/app/vlibras-plugin.chunk.js' 
violates the following Content Security Policy directive
```

**Causa:** CSP bloqueando `www.vlibras.gov.br`.

**Solução:** Adicione `https://www.vlibras.gov.br` ao `script-src`.

---

### 3. Erro: "Connecting to 'https://dicionario2.vlibras.gov.br/bundles' violates CSP"

**Sintoma:**
```
Connecting to 'https://dicionario2.vlibras.gov.br/bundles' violates the 
following Content Security Policy directive: "connect-src 'self'"
```

**Causa:** CSP bloqueando conexões à API do dicionário.

**Solução:** Adicione `https://dicionario2.vlibras.gov.br` ao `connect-src`.

---

### 4. Erro: "Loading the font violates CSP"

**Sintoma:**
```
Loading the font '<URL>' violates the following Content Security Policy 
directive: "font-src 'self' data:"
```

**Causa:** CSP bloqueando fontes do VLibras.

**Solução:** Adicione domínios VLibras ao `font-src`.

---

### 5. Erro: "Creating a worker from 'blob:...' violates CSP"

**Sintoma:**
```
Creating a worker from 'blob:http://localhost:8000/...' violates the 
following Content Security Policy directive: "script-src 'self'"
```

**Causa:** CSP bloqueando Web Workers criados a partir de blobs.

**Solução:** Adicione `worker-src 'self' blob:` ao CSP.

---

### 6. Erro: "Loading the script 'blob:...' violates CSP"

**Sintoma:**
```
Loading the script 'blob:http://localhost:8000/...' violates the following 
Content Security Policy directive: "script-src 'self' 'unsafe-inline'"
```

**Causa:** Unity WebAssembly loader cria scripts a partir de blobs.

**Solução:** Adicione `blob:` ao `script-src`.

---

### 7. Erro: "WebAssembly.instantiate() violates CSP"

**Sintoma:**
```
CompileError: WebAssembly.instantiate(): Compiling or instantiating 
WebAssembly module violates the following Content Security policy directive 
because 'unsafe-eval' is not an allowed source of script
```

**Causa:** WebAssembly requer `'unsafe-eval'` para compilar módulos WASM.

**Solução:** Adicione `'unsafe-eval'` ao `script-src`.

> **⚠️ IMPORTANTE:** `'unsafe-eval'` reduz a segurança do CSP, mas é **obrigatório** para WebAssembly. Considere usar CSP com nonce ou hash para outros scripts se possível.

---

### 8. Modal fica atrás do widget

**Sintoma:** Ao abrir um modal, o widget VLibras aparece por cima.

**Causa:** Z-index do modal menor que o do widget.

**Solução:** Defina `z-index: 2147483647` (máximo seguro) para modais.

## ✅ Validação

### Console do Navegador

Após a integração correta, você deve ver:

```
✅ VLibras widget initialized successfully
✅ [UnityCache] '...playerweb.wasm.framework.unityweb' successfully downloaded
✅ [UnityCache] '...playerweb.wasm.code.unityweb' successfully downloaded
✅ [UnityCache] '...playerweb.data.unityweb' successfully downloaded
✅ Initialize engine version: 2018.4.36f1
✅ Creating WebGL 2.0 context
✅ [BundleLoader]: BUNDLE (...) CARREGADO COM SUCESSO
```

### Erros Esperados (Não Críticos)

Estes avisos são **normais** e **não afetam** o funcionamento:

```
⚠️ Permissions policy violation: gyroscope is not allowed
⚠️ The devicemotion events are blocked by permissions policy
⚠️ The deviceorientation events are blocked by permissions policy
```

Esses são recursos opcionais de sensores que o Unity tenta usar mas não são essenciais para o VLibras.

## 📚 Referências

- [Documentação Oficial VLibras](https://vlibras.gov.br/doc/widget/installation/webpageintegration.html)
- [StackOverflow - Dificuldade para implementar VLibras usando JavaScript](https://pt.stackoverflow.com/questions/511562)
- [PDF de Desenvolvimento VLibras](https://vlibras.gov.br/files/Dev_VLibras_Plugin_Widget.pdf)
- [WebAssembly e CSP](https://developer.mozilla.org/en-US/docs/WebAssembly/Loading_and_running)
- [Content Security Policy (CSP)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)

## 🎯 Checklist de Integração

- [ ] Implementar carregamento dinâmico via JavaScript
- [ ] Configurar CSP com `'unsafe-eval'` para WebAssembly
- [ ] Adicionar `blob:` ao `script-src` e `worker-src`
- [ ] Adicionar todos os domínios VLibras ao CSP
- [ ] Configurar z-index de modais (se aplicável)
- [ ] Testar em diferentes navegadores
- [ ] Verificar console para erros de CSP
- [ ] Validar funcionamento do widget (clicar e traduzir)

## 💡 Dicas Finais

1. **Sempre use HTTPS** em produção para o VLibras funcionar corretamente
2. **Teste em modo anônimo** para garantir que não há cache interferindo
3. **Monitore o console** durante a integração para identificar bloqueios de CSP rapidamente
4. **Documente** quaisquer configurações específicas do seu ambiente
5. **Considere** criar um ambiente de staging para testar antes de produção

---

**Última atualização:** 2025-11-29  
**Versão do VLibras testada:** 2018.4.36f1  
**Status:** ✅ Totalmente funcional
