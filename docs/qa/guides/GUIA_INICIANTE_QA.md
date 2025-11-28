# 🎓 Guia do Iniciante em QA (Onboarding)

Bem-vindo ao time de Qualidade do Chatbot Ada! Este guia foi criado para te ajudar a começar com o pé direito.

---

## 1. O que é este projeto?
O **Chatbot Ada** é uma aplicação focada em acessibilidade digital. Nosso objetivo principal é garantir que **TODAS** as pessoas, independentemente de suas limitações, consigam interagir com a tecnologia.
*   **Frontend:** HTML/JS Vanilla (Simples e acessível).
*   **Backend:** Python (FastAPI).
*   **Foco de QA:** Acessibilidade (WCAG AAA), Usabilidade e Robustez.

---

## 2. Configurando seu Ambiente

### Pré-requisitos
1.  **Git:** Para baixar o código.
2.  **Python 3.12+:** Para rodar o backend e testes.
3.  **Node.js:** Para ferramentas de linting (opcional, mas recomendado).
4.  **VS Code:** Editor recomendado.

### Passo a Passo
1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/chatbotAcessibilidade.git
    cd chatbotAcessibilidade
    ```
2.  **Crie o ambiente virtual e instale dependências:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # No Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  **Instale os navegadores do Playwright:**
    ```bash
    playwright install
    ```

---

## 3. Como Rodar os Testes?

### 🧪 Testes Automatizados (O "Robô")
Nós usamos o **Pytest** e o **Playwright**.
*   **Rodar tudo:** `pytest`
*   **Rodar apenas testes unitários (rápidos):** `pytest tests/unit`
*   **Rodar testes de interface (abre o navegador):** `pytest tests/e2e --headed`

### 🖐️ Testes Manuais (Você)
1.  Inicie o servidor: `uvicorn src.backend.api:app --reload`
2.  Acesse: `http://localhost:8000`
3.  Siga o roteiro em: `docs/qa/specifications/CENARIOS_BDD.md`

---

## 4. Ferramentas que Usamos

| Ferramenta | Para que serve? |
|:---|:---|
| **Pytest** | Executor de testes (nossa base). |
| **Playwright** | Simula um usuário clicando no navegador. |
| **Axe-core** | Verifica acessibilidade automaticamente. |
| **Locust** | Testa se o sistema aguenta muitos usuários. |
| **Allure** | Gera relatórios bonitos dos testes. |

---

## 5. Seu Fluxo de Trabalho (Dia a Dia)
1.  **Pegue uma tarefa** (ex: "Testar nova funcionalidade de busca").
2.  **Leia a especificação** em `docs/qa/specifications/`.
3.  **Crie casos de teste** (se não existirem).
4.  **Execute os testes** (Manuais e Automatizados).
5.  **Achou um bug?**
    *   Verifique se é reproduzível.
    *   Abra um ticket com "Passos para Reproduzir".
    *   Classifique a severidade (Crítico, Alto, Médio, Baixo).
6.  **Documente** seus resultados em `docs/qa/reports/`.

---

## 🆘 Precisa de Ajuda?
*   Consulte o [Índice Geral de Testes](./INDICE_GERAL_TESTES.md).
*   Fale com o Tech Lead ou QA Senior.
*   Lembre-se: **Não existe pergunta boba!** Qualidade é um trabalho em equipe.
