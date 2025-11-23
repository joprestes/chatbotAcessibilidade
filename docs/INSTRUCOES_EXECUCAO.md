# Instruções de Execução - Frontend Web

## Pré-requisitos

- Python 3.12 ou superior (recomendado 3.12.x)
- Arquivo `.env` com a chave `GOOGLE_API_KEY` (obrigatória)
- Chave `OPENROUTER_API_KEY` (opcional, necessária apenas se quiser usar fallback automático)

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Execução

### Opção 1: Frontend Web (Recomendado)

Execute o servidor FastAPI:
```bash
uvicorn src.backend.api:app --reload --port 8000
```

Acesse no navegador:
```
http://localhost:8000
```

### Opção 2: Interface Streamlit (Alternativa)

Execute o Streamlit:
```bash
streamlit run scripts/streamlit/app.py
```

Acesse no navegador:
```
http://localhost:8501
```

## Estrutura de Arquivos

- `src/backend/api.py` - API FastAPI que processa as perguntas
- `frontend/index.html` - Interface HTML principal
- `frontend/styles.css` - Estilos acessíveis
- `frontend/app.js` - Lógica JavaScript do chat
- `static/images/` - Imagens (banner, avatar)

## Funcionalidades

- Chat interativo com histórico persistente (localStorage)
- Respostas formatadas em seções expansíveis
- Suporte a tema claro/escuro
- Totalmente acessível (WCAG AA)
- Navegação por teclado
- Contraste adequado

## Configuração do Fallback Automático (Opcional)

O chatbot suporta fallback automático para múltiplos LLMs quando o Google Gemini esgota suas utilizações:

1. **Obtenha uma chave API do OpenRouter:**
   - Acesse [https://openrouter.ai/](https://openrouter.ai/)
   - Crie uma conta e gere uma chave API

2. **Configure no `.env`:**
   ```env
   OPENROUTER_API_KEY="sua_chave_openrouter"
   FALLBACK_ENABLED=true
   OPENROUTER_MODELS=meta-llama/llama-3.3-70b-instruct:free,google/gemini-flash-1.5:free
   ```

3. **Como funciona:**
   - O sistema tenta usar Google Gemini primeiro
   - Se falhar ou esgotar quota, tenta automaticamente modelos OpenRouter
   - Itera pelos modelos configurados até encontrar um disponível

## Troubleshooting

### Erro: "GOOGLE_API_KEY não encontrada"
- Verifique se o arquivo `.env` existe na raiz do projeto
- Certifique-se de que contém: `GOOGLE_API_KEY="sua_chave_aqui"`

### Erro: "fallback_enabled=True requer openrouter_api_key configurada"
- Se você habilitou o fallback, configure `OPENROUTER_API_KEY` no `.env`
- Ou desabilite o fallback: `FALLBACK_ENABLED=false`

### Erro: "Frontend não encontrado"
- Verifique se a pasta `frontend/` existe com os arquivos `index.html`, `styles.css` e `app.js`

### Erro: "Assets não encontrados"
- Verifique se a pasta `assets/` existe com as imagens `banner.webp` e `avatar.webp`

### Porta já em uso
- Use outra porta: `uvicorn backend.api:app --reload --port 8001`

