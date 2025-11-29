# Roadmap - Chatbot de Acessibilidade

Este documento descreve o planejamento estratégico de funcionalidades para o projeto, focado em transformar a Ada em uma assistente completa de acessibilidade digital.

## 🎯 Fase 1: A Ada "Olhos de Águia" (Multimodalidade e Análise)
*Foco: Expandir a capacidade da IA de ver e analisar além do texto.*

- [ ] **Transformação de Imagem para Texto (Vision/OCR)**
  - **Descrição**: Permitir upload de imagens para descrição e análise de acessibilidade.
  - **Tecnologia**: Google Gemini Pro Vision.
  
- [ ] **Analisador de Acessibilidade em Tempo Real (URL)**
  - **Descrição**: Usuário envia uma URL e a Ada retorna um relatório simplificado de erros (contraste, ARIA, estrutura).
  - **Tecnologia**: Integração com `axe-core` ou `Pa11y` via backend.

## 🎨 Fase 2: A Ada "Designer" (Ferramentas Criativas)
*Foco: Auxiliar na criação de interfaces acessíveis desde o design.*

- [ ] **Gerador de Paletas Acessíveis (AAA)**
  - **Descrição**: Geração de paletas de cores harmônicas que garantem contraste WCAG AAA.
  - **Tecnologia**: Algoritmos de cor (Chroma.js) integrados ao prompt.

- [ ] **Templates de Componentes Acessíveis**
  - **Descrição**: A Ada fornece código pronto (React/Vue/HTML) de componentes comuns (Modais, Tabs) 100% acessíveis.
  - **Tecnologia**: Base de conhecimento vetorial (RAG) com exemplos curados.

## 🤖 Fase 2: Evolução dos Agentes (IA Especialista)
*Foco: Aprofundar a especialização técnica e empatia dos agentes.*

- [ ] **Agente Assistente 2.0**
  - Validação automática de contraste (cálculo de razão).
  - Templates de Loading States (ARIA live regions).
  - Seção de "Armadilhas Comuns" nas respostas.

- [ ] **Novos Agentes Especialistas**
  - **Design System Agent**: Sugestão de tokens (cores, espaçamento, tipografia) acessíveis.
  - **Metrics Agent**: Scorecard quantitativo de acessibilidade e impacto estimado.

- [ ] **Orquestração Inteligente**
  - Modos de execução: Rápido (Assistente+Validador), Padrão e Profundo (Todos + Métricas).

## 🛠️ Fase 3: Ferramentas de Produtividade & Técnica
*Foco: Melhorar a experiência de uso e alcance da ferramenta.*

- [ ] **Progressive Web App (PWA)**
  - **Descrição**: Tornar o chatbot instalável em desktop/mobile com funcionamento offline básico.
  - **Impacto**: Acessibilidade nativa e maior engajamento.

- [ ] **Gerador de Documentação (VPAT/ACR)**
  - **Descrição**: Auxiliar na redação de relatórios formais de conformidade baseados nas análises feitas.

## 📊 Fase 4: Inteligência e Métricas
- [ ] **Dashboard de Analytics**
  - **Descrição**: Métricas anônimas sobre dúvidas mais frequentes para melhorar o treinamento da IA.

---
> **Nota:** Funcionalidades como LMS (Cursos), Redes Sociais ou Integrações CI/CD complexas foram consideradas mas priorizadas para um momento futuro para manter o foco na essência de "Assistente Virtual".
