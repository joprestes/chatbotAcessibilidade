# 📁 Reorganização do Projeto

**Data:** 2025-11-22  
**Versão:** 3.0.0

## 🎯 Objetivo

Reorganizar a estrutura do projeto para torná-lo mais profissional, seguindo as melhores práticas de organização de projetos Python modernos.

## 📊 Mudanças Realizadas

### Estrutura Anterior vs Nova

#### ❌ Antes
```
chatbot-acessibilidade/
├── app.py (raiz)
├── backend/
├── chatbot_acessibilidade/
├── assets/
├── tests/
├── CHANGELOG.md (raiz)
├── INSTRUCOES_EXECUCAO.md (raiz)
└── ... (muitos arquivos na raiz)
```

#### ✅ Agora
```
chatbot-acessibilidade/
├── docs/                    # Toda documentação organizada
├── src/                     # Todo código fonte
│   ├── chatbot_acessibilidade/
│   └── backend/
├── frontend/                # Interface web
├── static/                  # Recursos estáticos
│   └── images/
├── scripts/                 # Scripts auxiliares
│   ├── streamlit/
│   └── setup/
├── tests/                   # Testes organizados
│   ├── unit/
│   ├── integration/
│   └── reports/
└── ... (arquivos de configuração na raiz)
```

## 📝 Detalhes das Mudanças

### 1. Documentação (`docs/`)
- ✅ `CHANGELOG.md` → `docs/CHANGELOG.md`
- ✅ `INSTRUCOES_EXECUCAO.md` → `docs/INSTRUCOES_EXECUCAO.md`
- ✅ `LINTERS.md` → `docs/LINTERS.md`
- ✅ `MELHORIAS_IMPLEMENTADAS.md` → `docs/MELHORIAS_IMPLEMENTADAS.md`
- ✅ `ANALISE_PROJETO.md` → `docs/ANALISE_PROJETO.md`
- ✅ `LICENSE.pt-BR.md` → `docs/LICENSE.pt-BR.md`
- ✅ Criadas pastas `docs/guides/`, `docs/api/`, `docs/development/` para organização futura

### 2. Código Fonte (`src/`)
- ✅ `chatbot_acessibilidade/` → `src/chatbot_acessibilidade/`
- ✅ `backend/` → `src/backend/`
- ✅ Criado `src/__init__.py` para tornar src um pacote Python

### 3. Scripts (`scripts/`)
- ✅ `app.py` → `scripts/streamlit/app.py`
- ✅ `setup.sh` → `scripts/setup/setup.sh`

### 4. Recursos Estáticos (`static/`)
- ✅ `assets/` → `static/images/`
- ✅ Imagens (banner.webp, avatar.webp) agora em `static/images/`

### 5. Testes (`tests/`)
- ✅ `conftest.py` movido para `tests/` (já estava lá)
- ✅ `relatorio_testes.html` → `tests/reports/relatorio_testes.html`
- ✅ Criadas pastas `tests/unit/` e `tests/integration/` para organização futura

## 🔧 Ajustes Técnicos

### Imports Atualizados
- ✅ `src/backend/api.py` - Ajustado para importar de `src.chatbot_acessibilidade`
- ✅ `scripts/streamlit/app.py` - Ajustado para importar de `src.chatbot_acessibilidade`
- ✅ `tests/conftest.py` - Adicionado path de `src/` ao sys.path
- ✅ `tests/test_api.py` - Atualizado para importar de `src.backend.api`

### Caminhos de Arquivos
- ✅ `src/backend/api.py` - Ajustado para servir arquivos estáticos da nova localização
- ✅ `scripts/streamlit/app.py` - Atualizado caminhos de imagens para `static/images/`
- ✅ Frontend continua funcionando (caminhos relativos mantidos)

### Documentação Atualizada
- ✅ `README.md` - Nova estrutura de arquitetura
- ✅ `docs/INSTRUCOES_EXECUCAO.md` - Comandos atualizados
- ✅ `Makefile` - Caminhos atualizados para `src/`
- ✅ `.gitignore` - Adicionado `tests/reports/*.html`

## 🚀 Comandos Atualizados

### Executar API
```bash
# Antes
uvicorn backend.api:app --reload

# Agora
uvicorn src.backend.api:app --reload
```

### Executar Streamlit
```bash
# Antes
streamlit run app.py

# Agora
streamlit run scripts/streamlit/app.py
```

### Testes
```bash
# Comandos permanecem os mesmos
pytest -v
pytest --cov=src.chatbot_acessibilidade --cov=src.backend
```

### Linters
```bash
# Makefile atualizado automaticamente
make lint
make format
make type-check
```

## ✅ Benefícios

1. **Organização Profissional**: Estrutura clara e padronizada
2. **Separação de Responsabilidades**: Código, docs, scripts, testes separados
3. **Facilita Manutenção**: Mais fácil encontrar arquivos
4. **Escalabilidade**: Estrutura preparada para crescimento
5. **Padrão da Indústria**: Segue convenções Python modernas

## 📌 Notas Importantes

- ⚠️ **Imports**: Alguns arquivos precisam adicionar `src/` ao `sys.path` para funcionar
- ⚠️ **Caminhos Relativos**: Todos os caminhos foram ajustados para funcionar da nova estrutura
- ✅ **Compatibilidade**: Toda funcionalidade existente foi mantida
- ✅ **Testes**: Todos os testes continuam funcionando

## 🔄 Próximos Passos Sugeridos

1. Mover testes para `tests/unit/` e `tests/integration/` conforme apropriado
2. Adicionar documentação em `docs/guides/` e `docs/api/`
3. Considerar criar `setup.py` ou usar `pyproject.toml` para instalação como pacote
4. Adicionar GitHub Actions para CI/CD usando a nova estrutura

---

**Status**: ✅ Reorganização completa e funcional

