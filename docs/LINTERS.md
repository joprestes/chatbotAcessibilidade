# Guia de Linters e Formatação

Este projeto usa várias ferramentas para garantir qualidade e consistência do código.

## 🛠️ Ferramentas Configuradas

### 1. **Black** - Formatação de Código
Formata automaticamente o código Python seguindo o estilo PEP 8.

### 2. **Ruff** - Linter Rápido
Linter moderno e rápido que substitui múltiplas ferramentas:
- pycodestyle (E, W)
- pyflakes (F)
- isort (I)
- flake8-bugbear (B)
- E mais...

### 3. **MyPy** - Verificação de Tipos
Verifica type hints e detecta erros de tipo.

### 4. **Pre-commit** - Hooks Automáticos
Executa verificações automaticamente antes de cada commit.

## 📦 Instalação

```bash
# Instalar dependências
pip install -r requirements.txt

# Instalar pre-commit hooks
pre-commit install
```

Ou use o Makefile:

```bash
make install
```

## 🚀 Uso

### Formatação Automática

```bash
# Formata todo o código
make format

# Ou manualmente
black chatbot_acessibilidade/ backend/ tests/
ruff format chatbot_acessibilidade/ backend/ tests/
```

### Verificação de Lint

```bash
# Verifica problemas de lint
make lint

# Ou manualmente
ruff check chatbot_acessibilidade/ backend/ tests/
```

### Verificação de Tipos

```bash
# Verifica tipos
make type-check

# Ou manualmente
mypy chatbot_acessibilidade/ backend/
```

### Executar Tudo

```bash
# Executa lint, type-check e testes
make check

# Ou individualmente
make lint
make type-check
make test
```

### Correção Automática

```bash
# Formata e corrige problemas automaticamente
make fix
```

## 📋 Comandos Disponíveis (Makefile)

```bash
make help          # Mostra todos os comandos
make install       # Instala dependências e hooks
make lint          # Executa linters
make format        # Formata código
make type-check    # Verifica tipos
make test          # Executa testes
make test-cov      # Testes com cobertura
make check         # Executa todas as verificações
make clean         # Limpa arquivos temporários
make fix           # Formata e corrige automaticamente
```

## 🔧 Configuração

### Black
Configurado em `pyproject.toml`:
- Line length: 100 caracteres
- Target: Python 3.10+

### Ruff
Configurado em `pyproject.toml`:
- Line length: 100 caracteres
- Regras selecionadas: E, W, F, I, B, C4, UP, ARG, SIM
- Ignora E501 (linha muito longa - tratado pelo Black)

### MyPy
Configurado em `pyproject.toml`:
- Python 3.10+
- Ignora imports faltantes de bibliotecas externas (google.*, streamlit, etc)

## 🎯 Pre-commit Hooks

Os hooks são executados automaticamente antes de cada commit:

1. **Trailing whitespace** - Remove espaços no final das linhas
2. **End of file fixer** - Adiciona nova linha no final do arquivo
3. **YAML/JSON/TOML checker** - Valida sintaxe
4. **Black** - Formata código Python
5. **Ruff** - Verifica e corrige problemas de lint
6. **MyPy** - Verifica tipos

### Pular Hooks (não recomendado)

```bash
git commit --no-verify -m "mensagem"
```

## 📝 Regras de Lint

### Regras Habilitadas

- **E** - Erros do pycodestyle
- **W** - Avisos do pycodestyle
- **F** - Pyflakes (detecção de erros)
- **I** - isort (ordenação de imports)
- **B** - Bugbear (detecção de bugs comuns)
- **C4** - Comprehensions (melhorias em list/dict comprehensions)
- **UP** - Pyupgrade (atualiza sintaxe para versões mais novas)
- **ARG** - Unused arguments
- **SIM** - Simplifications

### Regras Ignoradas

- **E501** - Linha muito longa (Black cuida disso)
- **B008** - Chamadas de função em defaults de argumentos
- **C901** - Complexidade muito alta (pode ser ajustado)

## 🐛 Resolução de Problemas

### Ruff encontra muitos problemas

```bash
# Ver quais problemas existem
ruff check chatbot_acessibilidade/ backend/ tests/

# Corrigir automaticamente o que for possível
ruff check --fix chatbot_acessibilidade/ backend/ tests/
```

### MyPy encontra erros de tipo

Alguns erros podem ser ignorados adicionando comentários:

```python
# type: ignore[erro-especifico]
```

Ou configurando no `pyproject.toml` para módulos específicos.

### Pre-commit falha

```bash
# Executar manualmente
pre-commit run --all-files

# Ou para um hook específico
pre-commit run black --all-files
```

## 📚 Recursos

- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Pre-commit Documentation](https://pre-commit.com/)

