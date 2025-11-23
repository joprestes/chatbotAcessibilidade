# 📋 Plano de Expansão de Testes Automatizados

## Objetivo

Expandir a cobertura de testes automatizados identificando gaps e adicionando novos casos de teste para melhorar a qualidade e confiabilidade do sistema.

---

## 📊 Análise da Cobertura Atual

### ✅ O que já está coberto

- **Testes Unitários**: ~161 testes cobrindo módulos core, agents e backend
- **Testes de Integração**: Fluxo básico do usuário, cache, métricas
- **Testes E2E Playwright**: 
  - Frontend: 12 testes (carregamento, interface, fluxo de chat, tema, sugestões, busca, responsividade)
  - API: 7 testes (health, config, chat, validação, CORS, estáticos, métricas)
  - Acessibilidade: 7 testes (WCAG, navegação por teclado, ARIA, contraste, foco)

### ❌ Gaps Identificados

1. **Tratamento de Erros**: Alguns cenários de erro não testados
2. **Performance**: Testes de carga e stress ausentes
3. **Segurança**: Alguns vetores de ataque não testados
4. **Edge Cases**: Casos extremos não cobertos
5. **Integração Avançada**: Fallback, retry, timeout não testados completamente
6. **UI/UX**: Algumas interações não testadas

---

## 🎯 Novos Casos de Teste Propostos

### 1. Testes de Tratamento de Erros (Frontend)

#### 1.1 Timeout de Requisição
- **Arquivo**: `tests/e2e/playwright/test_error_handling.py`
- **Casos**:
  - Testa timeout quando requisição demora mais que `request_timeout_ms`
  - Verifica mensagem de erro apropriada
  - Verifica que indicador de digitação é removido
  - Verifica que botão cancelar funciona durante timeout

#### 1.2 Erro de Rede (Offline)
- **Casos**:
  - Simula perda de conexão durante requisição
  - Verifica mensagem "Você está offline"
  - Verifica que reconexão é detectada
  - Testa envio após reconexão

#### 1.3 Rate Limit (429)
- **Casos**:
  - Simula resposta 429 do servidor
  - Verifica mensagem "Muitas requisições"
  - Verifica que usuário pode tentar novamente após espera

#### 1.4 Erro do Servidor (500+)
- **Casos**:
  - Simula erro 500 do servidor
  - Verifica mensagem "Erro no servidor"
  - Verifica que erro é exibido corretamente

#### 1.5 Cancelamento Manual
- **Casos**:
  - Testa botão cancelar durante requisição
  - Verifica que requisição é abortada
  - Verifica que não há mensagem de erro
  - Verifica que indicador é removido

#### 1.6 Erro de Parsing de Resposta
- **Casos**:
  - Simula resposta malformada do servidor
  - Verifica tratamento gracioso do erro
  - Verifica mensagem de erro apropriada

---

### 2. Testes de Performance e Stress

#### 2.1 Múltiplas Requisições Sequenciais
- **Arquivo**: `tests/e2e/playwright/test_performance.py`
- **Casos**:
  - Envia 10 requisições sequenciais
  - Verifica que todas são processadas
  - Verifica que não há vazamento de memória
  - Verifica que cache funciona corretamente

#### 2.2 Requisições Paralelas
- **Casos**:
  - Envia 5 requisições simultâneas
  - Verifica que apenas uma é processada por vez (frontend)
  - Verifica que outras são bloqueadas corretamente

#### 2.3 Mensagens Longas
- **Casos**:
  - Envia mensagem com 2000 caracteres (limite máximo)
  - Verifica que é aceita
  - Envia mensagem com 2001 caracteres
  - Verifica que é rejeitada

#### 2.4 Histórico Grande
- **Casos**:
  - Cria 100 mensagens no histórico
  - Verifica performance de renderização
  - Verifica que busca funciona
  - Verifica que scroll funciona

---

### 3. Testes de Segurança

#### 3.1 Injeção de Script (XSS)
- **Arquivo**: `tests/e2e/playwright/test_security.py`
- **Casos**:
  - Tenta enviar `<script>alert('XSS')</script>`
  - Verifica que é sanitizado
  - Verifica que não executa no DOM
  - Testa múltiplos padrões de XSS

#### 3.2 SQL Injection (Prevenção)
- **Casos**:
  - Tenta enviar padrões SQL injection
  - Verifica que são detectados e rejeitados
  - Verifica mensagem de erro apropriada

#### 3.3 CSRF Protection
- **Casos**:
  - Verifica headers de segurança
  - Testa requisições cross-origin
  - Verifica CORS configurado corretamente

#### 3.4 Rate Limiting Real
- **Casos**:
  - Envia requisições rápidas até atingir limite
  - Verifica que rate limit é acionado
  - Verifica mensagem 429
  - Verifica que após espera, funciona novamente

---

### 4. Testes de Fallback e Retry

#### 4.1 Fallback Automático
- **Arquivo**: `tests/integration/test_fallback.py`
- **Casos**:
  - Simula falha do Google Gemini
  - Verifica que fallback para OpenRouter é acionado
  - Verifica que resposta é retornada
  - Verifica logs de fallback

#### 4.2 Retry Automático
- **Casos**:
  - Simula erro temporário (ResourceExhausted)
  - Verifica que retry é executado
  - Verifica número máximo de tentativas
  - Verifica backoff exponencial

#### 4.3 Todos os Provedores Falham
- **Casos**:
  - Simula falha de todos os provedores
  - Verifica mensagem de erro apropriada
  - Verifica que erro é tratado graciosamente

---

### 5. Testes de Acessibilidade Avançados

#### 5.1 Screen Reader Compatibility
- **Arquivo**: `tests/e2e/playwright/test_accessibility_advanced.py`
- **Casos**:
  - Testa com NVDA (via Playwright)
  - Verifica anúncios de mudanças de estado
  - Verifica labels ARIA
  - Verifica landmarks

#### 5.2 Navegação por Teclado Completa
- **Casos**:
  - Testa Tab em todos os elementos interativos
  - Verifica ordem de foco lógica
  - Testa Shift+Tab (navegação reversa)
  - Testa Enter e Space em botões

#### 5.3 Modo de Alto Contraste
- **Casos**:
  - Simula modo de alto contraste do sistema
  - Verifica que interface se adapta
  - Verifica contraste mínimo 4.5:1

#### 5.4 Zoom de Tela
- **Casos**:
  - Testa zoom 200% (WCAG requerido)
  - Verifica que layout não quebra
  - Verifica que texto permanece legível
  - Verifica que não há scroll horizontal

#### 5.5 Redução de Movimento
- **Casos**:
  - Testa `prefers-reduced-motion`
  - Verifica que animações são desabilitadas
  - Verifica que transições são instantâneas

---

### 6. Testes de UI/UX Detalhados

#### 6.1 Expansão de Expanders
- **Arquivo**: `tests/e2e/playwright/test_ui_interactions.py`
- **Casos**:
  - Testa clique em expander
  - Verifica que conteúdo é exibido
  - Testa clique novamente para fechar
  - Verifica animação suave
  - Testa navegação por teclado em expanders

#### 6.2 Toast Notifications
- **Casos**:
  - Testa exibição de toast
  - Verifica que desaparece automaticamente
  - Verifica que múltiplos toasts funcionam
  - Verifica acessibilidade de toasts

#### 6.3 Auto-resize do Textarea
- **Casos**:
  - Digita texto longo
  - Verifica que textarea expande
  - Verifica que não ultrapassa limite
  - Verifica que scroll funciona se necessário

#### 6.4 Persistência de Tema
- **Casos**:
  - Muda tema
  - Recarrega página
  - Verifica que tema é mantido
  - Testa em modo privado (sem localStorage)

#### 6.5 Histórico de Mensagens
- **Casos**:
  - Envia mensagens
  - Recarrega página
  - Verifica que mensagens são restauradas
  - Testa limpeza de histórico
  - Testa busca no histórico

---

### 7. Testes de Integração Avançados

#### 7.1 Cache com TTL
- **Arquivo**: `tests/integration/test_cache_advanced.py`
- **Casos**:
  - Envia pergunta
  - Aguarda TTL expirar
  - Envia mesma pergunta
  - Verifica que cache foi invalidado

#### 7.2 Métricas Detalhadas
- **Casos**:
  - Faz múltiplas requisições
  - Verifica métricas de tempo de resposta
  - Verifica métricas de cache
  - Verifica métricas de fallback

#### 7.3 Pipeline Completo com Falhas Parciais
- **Casos**:
  - Simula falha de agente paralelo
  - Verifica que outros agentes continuam
  - Verifica que resposta é montada corretamente

---

### 8. Testes de Validação de Entrada

#### 8.1 Validação de Pergunta
- **Arquivo**: `tests/unit/backend/test_validation.py`
- **Casos**:
  - Pergunta muito curta (< 3 caracteres)
  - Pergunta muito longa (> 2000 caracteres)
  - Pergunta com apenas espaços
  - Pergunta com caracteres especiais
  - Pergunta com emojis
  - Pergunta com HTML

#### 8.2 Sanitização de Entrada
- **Casos**:
  - Testa múltiplos padrões de injeção
  - Verifica que são sanitizados
  - Verifica que conteúdo válido não é alterado

---

### 9. Testes de Responsividade Detalhados

#### 9.1 Breakpoints Específicos
- **Arquivo**: `tests/e2e/playwright/test_responsive_detailed.py`
- **Casos**:
  - Mobile: 320px, 375px, 414px
  - Tablet: 768px, 1024px
  - Desktop: 1280px, 1920px
  - Verifica layout em cada breakpoint
  - Verifica que elementos não se sobrepõem

#### 9.2 Orientação (Portrait/Landscape)
- **Casos**:
  - Testa rotação de tela
  - Verifica que layout se adapta
  - Verifica que funcionalidade não quebra

---

### 10. Testes de Compatibilidade de Navegadores

#### 10.1 Funcionalidades Específicas
- **Arquivo**: `tests/e2e/playwright/test_browser_compatibility.py`
- **Casos**:
  - Testa localStorage em todos os navegadores
  - Testa fetch API
  - Testa AbortController
  - Testa CSS Grid/Flexbox

---

## 📁 Estrutura de Arquivos Propostos

```
tests/
├── e2e/
│   └── playwright/
│       ├── test_error_handling.py          # Novo
│       ├── test_performance.py             # Novo
│       ├── test_security.py                # Novo
│       ├── test_accessibility_advanced.py  # Novo
│       ├── test_ui_interactions.py         # Novo
│       ├── test_responsive_detailed.py     # Novo
│       └── test_browser_compatibility.py   # Novo
│
├── integration/
│   ├── test_fallback.py                    # Novo
│   └── test_cache_advanced.py              # Novo
│
└── unit/
    └── backend/
        └── test_validation.py              # Novo
```

---

## 🎯 Priorização

### Alta Prioridade (Implementar Primeiro)
1. ✅ Testes de Tratamento de Erros (Frontend)
2. ✅ Testes de Fallback e Retry
3. ✅ Testes de Segurança Básicos
4. ✅ Testes de Acessibilidade Avançados

### Média Prioridade
5. ✅ Testes de Performance
6. ✅ Testes de UI/UX Detalhados
7. ✅ Testes de Validação de Entrada

### Baixa Prioridade (Opcional)
8. ✅ Testes de Responsividade Detalhados
9. ✅ Testes de Compatibilidade de Navegadores

---

## 📊 Estimativa

- **Total de novos testes**: ~80-100 testes
- **Tempo estimado**: 2-3 semanas
- **Impacto na cobertura**: +5-10% (já está em 98.93%)

---

## ✅ Checklist de Implementação

- [ ] Criar arquivo `test_error_handling.py`
- [ ] Criar arquivo `test_performance.py`
- [ ] Criar arquivo `test_security.py`
- [ ] Criar arquivo `test_accessibility_advanced.py`
- [ ] Criar arquivo `test_ui_interactions.py`
- [ ] Criar arquivo `test_fallback.py`
- [ ] Criar arquivo `test_cache_advanced.py`
- [ ] Criar arquivo `test_validation.py`
- [ ] Atualizar documentação de testes
- [ ] Adicionar novos comandos ao Makefile se necessário

---

## 📝 Notas

- Todos os testes devem seguir padrão AAA (Arrange, Act, Assert)
- Usar fixtures do conftest.py quando possível
- Adicionar marcadores pytest apropriados
- Documentar casos de teste complexos
- Manter cobertura acima de 95%

