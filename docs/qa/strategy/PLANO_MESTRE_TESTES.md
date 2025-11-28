# 📋 Plano Mestre de Testes (Master Test Plan)

**Projeto:** Chatbot de Acessibilidade Digital (Ada)
**Versão do Documento:** 1.1
**Status:** Aprovado para Execução
**Classificação:** Uso Interno / Confidencial

---

## 0. Controle de Documento (Rastreabilidade)

| Versão | Data | Autor | Descrição da Mudança | Aprovado Por |
|:---:|:---:|:---|:---|:---|
| 1.0 | 28/11/2025 | Antigravity (QA) | Criação inicial do plano. | Tech Lead |
| 1.1 | 28/11/2025 | Antigravity (QA) | Inclusão de controle de versão e referências normativas. | QA Manager |

## 1. Introdução e Objetivos
Este documento define a estratégia abrangente de garantia de qualidade (QA) para o Chatbot Ada. O objetivo é ir além do "caminho feliz", assegurando que o sistema seja robusto, resiliente a falhas e acessível em cenários extremos, em conformidade com a **ISO/IEC 25010** (Qualidade de Software) e **WCAG 2.2** (Acessibilidade).

### 1.1 Referências Normativas
*   **ISO/IEC 25010:** Modelo de Qualidade de Produto de Software.
*   **IEEE 829:** Padrão para Documentação de Teste de Software.
*   **WCAG 2.2:** Diretrizes de Acessibilidade para Conteúdo Web (Nível AAA).
*   **LGPD (Lei 13.709/2018):** Proteção de Dados Pessoais (Sanitização de Inputs).

### 1.2 Escopo de Teste
*   **Frontend:** Interface do usuário, interações, acessibilidade (WCAG AAA).
*   **Backend:** API Endpoints, tratamento de erros, validações de segurança.
*   **Integração:** Fluxo completo (UI -> API -> LLM).

---

## 2. Estratégia de Testes

### 2.1 Níveis de Teste
1.  **Smoke Testing (Teste de Fumaça):** Verificação rápida das funcionalidades críticas para validar o build.
2.  **Testes Funcionais:** Validação detalhada dos requisitos de negócio.
3.  **Testes de Borda (Edge Cases):** Entradas nos limites aceitáveis e inaceitáveis.
4.  **Testes de Exceção (Negative Testing):** Comportamento do sistema sob falha.
5.  **Testes de Acessibilidade:** Validação manual e automatizada de conformidade WCAG.

---

## 3. Suíte de Smoke Tests (Sanity Check)
*Executar a cada novo deploy ou build.*

| ID | Cenário | Passos | Resultado Esperado | Prioridade |
|:---|:---|:---|:---|:---:|
| **SMK-01** | **Carregamento da Aplicação** | Acessar a URL raiz. | Página carrega sem erros 404/500 no console. Título "Ada" visível. | **Crítica** |
| **SMK-02** | **Envio de Mensagem Simples** | Enviar "Olá". | Bot responde em < 5s. Indicador de digitação aparece. | **Crítica** |
| **SMK-03** | **Health Check da API** | Acessar `/api/health`. | Retorna JSON `{ "status": "ok" }`. | **Alta** |
| **SMK-04** | **Renderização de Markdown** | Solicitar "Exemplo de código". | Resposta contém bloco de código formatado corretamente. | **Alta** |

---

## 4. Testes de Borda e Limites (Edge Cases)
*Focados em quebrar a validação de entrada e renderização.*

| ID | Cenário | Dados de Entrada | Resultado Esperado |
|:---|:---|:---|:---|
| **EDG-01** | **Input Vazio** | String vazia, apenas espaços, apenas quebras de linha. | Botão enviar desabilitado ou validação impede envio. Não deve haver requisição. |
| **EDG-02** | **Input Máximo (Limites)** | Texto com exatos 2000 caracteres (limite) e 2001 caracteres. | 2000: Envia com sucesso. 2001: Trunca ou exibe erro de validação amigável. |
| **EDG-03** | **Caracteres Especiais e Emojis** | String complexa: `Testing 🚀 with <script> & "quotes" @#%¨&*()`. | Sistema sanitiza HTML (previne XSS), mas preserva emojis e texto seguro. |
| **EDG-04** | **Injeção de Código (Simulação)** | `SELECT * FROM users;` ou `alert('XSS')`. | Backend detecta padrão ou sanitiza. Resposta do bot deve ser segura (ex: "Não posso executar comandos"). |
| **EDG-05** | **Interação Rápida (Flood)** | Clicar em "Enviar" 10x rapidamente. | Frontend bloqueia múltiplos envios (debounce/disable). Apenas 1 requisição processada. |

---

## 5. Testes de Exceção e Resiliência (Negative Testing)
*Como o sistema se comporta quando algo dá errado.*

| ID | Cenário | Simulação | Comportamento Esperado |
|:---|:---|:---|:---|
| **EXC-01** | **Falha de Rede (Offline)** | Desconectar internet/simular "Offline" no DevTools e tentar enviar. | Toast/Alerta: "Você está offline". Mensagem não é perdida (retém no input). |
| **EXC-02** | **Timeout do Servidor** | Simular latência > 30s na API. | Frontend exibe mensagem de "O servidor demorou para responder". Botão "Cancelar" funciona. |
| **EXC-03** | **Erro Interno (500)** | Mockar resposta 500 na rota `/api/chat`. | Toast de erro: "Erro no servidor". Interface não quebra (não fica em loading eterno). |
| **EXC-04** | **Rate Limiting (429)** | Enviar > 10 req/min (via script ou manual rápido). | Toast/Alerta: "Muitas requisições. Tente novamente em instantes". |
| **EXC-05** | **API Indisponível (404/Connection Refused)** | Parar o backend e tentar usar o chat. | Mensagem amigável de "Serviço indisponível". |

---

## 6. Testes de Acessibilidade e Usabilidade (WCAG AAA)
*Validação manual focada em tecnologias assistivas.*

| ID | Cenário | Critério WCAG | Procedimento |
|:---|:---|:---|:---|
| **ACC-01** | **Navegação via Teclado** | 2.1.1 (Keyboard) | Navegar por TODO o app usando apenas `Tab`, `Enter`, `Space`, `Esc`. Foco deve ser visível sempre. |
| **ACC-02** | **Gerenciamento de Foco** | 2.4.3 (Focus Order) | Ao abrir Modal: foco vai para dentro. Ao fechar: foco volta ao botão que abriu. |
| **ACC-03** | **Zoom de 200%** | 1.4.4 (Resize Text) | Aumentar zoom do navegador para 200%. Layout não deve quebrar ou sobrepor texto. |
| **ACC-04** | **Leitor de Tela (VoiceOver/NVDA)** | 4.1.2 (Name, Role, Value) | Ouvir se botões têm labels (ex: "Enviar mensagem", não apenas "botão"). |
| **ACC-05** | **Contraste em Modo Escuro** | 1.4.6 (Contrast AAA) | Validar se texto cinza sobre fundo preto atende 7:1. |

---

## 7. Matriz de Risco e Priorização

| Funcionalidade | Impacto no Negócio | Probabilidade de Falha | Prioridade de Teste |
|:---|:---:|:---:|:---:|
| **Core Chat** | Crítico | Baixa (Estável) | P0 (Smoke) |
| **Acessibilidade** | Crítico (Diferencial) | Média (Regressão visual) | P0 (Manual) |
| **Tratamento de Erros** | Alto | Alta (Rede/API) | P1 (Exception) |
| **Personas** | Médio | Baixa | P2 (Funcional) |
| **Histórico** | Baixo | Média (LocalStorage) | P3 (Funcional) |

---
*Documento elaborado para garantir a excelência técnica e a conformidade com os mais altos padrões de QA.*
