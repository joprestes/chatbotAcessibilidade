# 🥒 Cenários de Teste em Gherkin (BDD)

**Projeto:** Chatbot de Acessibilidade Digital (Ada)
**Idioma:** Português (pt-BR)
**Referência:** Plano Mestre de Testes QA

---

## 1. Smoke Tests (Verificação de Sanidade)

### Funcionalidade: Chat Básico
  **Como** usuário do chatbot
  **Quero** enviar mensagens e receber respostas
  **Para** obter informações sobre acessibilidade

  **Cenário:** Envio de mensagem simples com sucesso
    **Dado** que a aplicação está carregada na URL raiz
    **E** o serviço de backend está operacional
    **Quando** eu digito "Olá" no campo de entrada
    **E** clico no botão "Enviar"
    **Então** a mensagem "Olá" deve aparecer no histórico do chat
    **E** um indicador de digitação deve ser exibido
    **E** eu devo receber uma resposta da Ada em menos de 5 segundos

  **Cenário:** Verificação de Saúde da API
    **Dado** que o servidor está rodando
    **Quando** eu faço uma requisição GET para "/api/health"
    **Então** o status da resposta deve ser 200
    **E** o corpo da resposta deve conter o status "ok"

---

## 2. Casos de Borda (Edge Cases)

### Funcionalidade: Validação de Entrada
  **Como** sistema
  **Quero** validar as entradas do usuário
  **Para** garantir a segurança e integridade do processamento

  **Cenário:** Tentativa de envio de input vazio
    **Dado** que estou na tela de chat
    **Quando** eu deixo o campo de mensagem vazio
    **Ou** digito apenas espaços em branco
    **Então** o botão "Enviar" deve permanecer desabilitado
    **E** nenhuma requisição deve ser enviada ao servidor

  **Cenário:** Envio de texto no limite máximo de caracteres
    **Dado** que o limite de caracteres é 2000
    **Quando** eu colo um texto com exatos 2000 caracteres
    **E** clico em enviar
    **Então** a mensagem deve ser enviada com sucesso

  **Cenário:** Tentativa de injeção de XSS
    **Dado** que estou na tela de chat
    **Quando** eu envio a mensagem "<script>alert('XSS')</script>"
    **Então** a mensagem deve ser exibida no chat como texto plano
    **E** nenhum script deve ser executado no navegador

---

## 3. Testes de Exceção (Resiliência)

### Funcionalidade: Tratamento de Erros
  **Como** usuário
  **Quero** ser informado sobre problemas técnicos
  **Para** não ficar confuso sobre o estado do sistema

  **Cenário:** Perda de conexão (Offline)
    **Dado** que estou utilizando o chat
    **E** minha conexão com a internet cai
    **Quando** eu tento enviar uma mensagem
    **Então** um toast deve aparecer com a mensagem "Você está offline"
    **E** minha mensagem não deve ser perdida do campo de entrada

  **Cenário:** Erro interno do servidor
    **Dado** que o servidor está enfrentando problemas internos
    **Quando** eu envio uma mensagem válida
    **Então** eu devo ver um toast de erro informando "Erro no servidor"
    **E** a interface não deve travar em estado de carregamento

  **Cenário:** Cancelamento manual de requisição
    **Dado** que enviei uma pergunta complexa
    **E** o bot está "digitando" (processando)
    **Quando** eu clico no botão "Cancelar"
    **Então** a requisição deve ser abortada imediatamente
    **E** o indicador de digitação deve desaparecer
    **E** uma mensagem "Requisição cancelada pelo usuário" deve ser registrada

---

## 4. Acessibilidade (WCAG AAA)

### Funcionalidade: Navegação e Leitura
  **Como** usuário com deficiência visual ou motora
  **Quero** navegar e interagir com o chat usando tecnologias assistivas
  **Para** utilizar o serviço com autonomia

  **Cenário:** Navegação via Teclado
    **Dado** que estou na página inicial
    **Quando** eu pressiono a tecla TAB sequencialmente
    **Então** o foco deve passar por todos os elementos interativos (links, inputs, botões)
    **E** o elemento focado deve ter um indicador visual claro (outline)

  **Cenário:** Gerenciamento de Foco no Modal
    **Dado** que abri o modal de "Limpar Chat"
    **Quando** o modal é exibido
    **Então** o foco do teclado deve ser movido automaticamente para dentro do modal
    **E** ao fechar o modal, o foco deve retornar ao botão que o abriu

  **Cenário:** Compatibilidade com Leitor de Tela
    **Dado** que estou usando um leitor de tela (NVDA/VoiceOver)
    **Quando** eu foco no botão de "Enviar"
    **Então** o leitor deve anunciar "Enviar mensagem, botão"
    **E** não apenas "botão" ou "ícone"

---

## 5. Performance (Não-Funcional)

### Funcionalidade: Capacidade de Carga
  **Como** arquiteto de sistema
  **Quero** que a aplicação suporte múltiplos usuários simultâneos
  **Para** garantir a disponibilidade do serviço em horários de pico

  **Cenário:** Teste de Carga (Load Test)
    **Dado** que o sistema está operando em condições normais
    **Quando** 50 usuários virtuais acessam o chat simultaneamente
    **E** enviam mensagens a uma taxa de 1 requisição por segundo
    **Então** o tempo de resposta (p95) deve permanecer abaixo de 500ms
    **E** a taxa de erro deve ser inferior a 1%

  **Cenário:** Teste de Stress (Ponto de Quebra)
    **Dado** que o sistema está sob carga crescente
    **Quando** o número de usuários virtuais aumenta progressivamente até 200
    **Então** o sistema não deve sofrer falha catastrófica (crash)
    **E** deve se recuperar automaticamente após a redução da carga

---

## 6. Segurança (AppSec)

### Funcionalidade: Proteção contra Ataques
  **Como** especialista em segurança
  **Quero** que o sistema bloqueie tentativas de exploração maliciosa
  **Para** proteger os dados dos usuários e a infraestrutura

  **Cenário:** Prevenção de Injeção SQL
    **Dado** que um atacante tenta manipular o banco de dados
    **Quando** ele envia o payload "SELECT * FROM users" no campo de chat
    **Então** a API deve rejeitar a entrada ou sanitizá-la
    **E** nenhuma informação sensível do banco de dados deve ser exposta

  **Cenário:** Proteção contra Rate Limiting (DoS)
    **Dado** que um usuário mal-intencionado tenta sobrecarregar a API
    **Quando** ele envia mais de 10 requisições em menos de 1 minuto
    **Então** o sistema deve bloquear temporariamente o IP de origem
    **E** retornar um código de erro 429 (Too Many Requests)
