# Instruções de Execução - Frontend Web

## Pré-requisitos

- Python 3.10 ou superior
- Arquivo `.env` com a chave `GOOGLE_API_KEY`

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Execução

### Opção 1: Frontend Web (Recomendado)

Execute o servidor FastAPI:
```bash
uvicorn backend.api:app --reload --port 8000
```

Acesse no navegador:
```
http://localhost:8000
```

### Opção 2: Interface Streamlit (Alternativa)

Execute o Streamlit:
```bash
streamlit run app.py
```

Acesse no navegador:
```
http://localhost:8501
```

## Estrutura de Arquivos

- `backend/api.py` - API FastAPI que processa as perguntas
- `frontend/index.html` - Interface HTML principal
- `frontend/styles.css` - Estilos acessíveis
- `frontend/app.js` - Lógica JavaScript do chat
- `assets/` - Imagens (banner, avatar)

## Funcionalidades

- Chat interativo com histórico persistente (localStorage)
- Respostas formatadas em seções expansíveis
- Suporte a tema claro/escuro
- Totalmente acessível (WCAG AA)
- Navegação por teclado
- Contraste adequado

## Troubleshooting

### Erro: "GOOGLE_API_KEY não encontrada"
- Verifique se o arquivo `.env` existe na raiz do projeto
- Certifique-se de que contém: `GOOGLE_API_KEY="sua_chave_aqui"`

### Erro: "Frontend não encontrado"
- Verifique se a pasta `frontend/` existe com os arquivos `index.html`, `styles.css` e `app.js`

### Erro: "Assets não encontrados"
- Verifique se a pasta `assets/` existe com as imagens `banner.webp` e `avatar.webp`

### Porta já em uso
- Use outra porta: `uvicorn backend.api:app --reload --port 8001`

