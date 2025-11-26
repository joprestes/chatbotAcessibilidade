# 📊 Guia de Relatórios Visuais com Allure

## 🎯 O que é Allure?

Allure é um framework de relatórios que transforma resultados de testes em **dashboards visuais interativos** e profissionais.

---

## 🚀 Como Usar

### Opção 1: Com Allure CLI (Recomendado)

#### 1. Instalar Allure CLI

```bash
# macOS
brew install allure

# Linux
sudo apt-add-repository ppa:qameta/allure
sudo apt-get update
sudo apt-get install allure

# Windows
scoop install allure
```

#### 2. Executar Testes e Gerar Relatório

```bash
# Executar testes e coletar dados
make test-allure

# Gerar e abrir relatório (abre no navegador)
make allure-serve

# OU gerar relatório HTML estático
make allure-generate
open allure-report/index.html
```

### Opção 2: Sem Allure CLI (Apenas pytest-html)

Se não quiser instalar Allure CLI, continue usando pytest-html:

```bash
# Relatório HTML básico (já funciona)
make test-cov
open htmlcov/index.html
```

---

## 📊 O que Você Verá no Dashboard

### 1. Overview
- 📈 Gráfico de pizza (passed/failed/skipped)
- ⏱️ Duração total e média
- 📊 Taxa de sucesso
- 🎯 Estatísticas gerais

### 2. Suites
- 📁 Organização por diretório
  - `tests/unit/` (145 testes)
  - `tests/integration/` (55 testes)
  - `tests/contract/` (13 testes)

### 3. Graphs
- 📈 Gráfico de duração
- 📊 Distribuição por status
- ⏱️ Testes mais lentos

### 4. Timeline
- ⏰ Linha do tempo de execução
- 🔄 Testes paralelos visualizados

---

## 🎨 Recursos Visuais

### Sem Decorators (Configuração Atual)
Allure já funciona **automaticamente** com seus testes existentes:

```python
# Seu teste atual (sem mudanças!)
def test_chat_endpoint():
    response = client.post('/api/chat', json={'pergunta': 'teste'})
    assert response.status_code == 200
```

✅ Já aparece no dashboard Allure!

### Com Decorators (Opcional - Para Melhorar)
Se quiser deixar ainda mais bonito, pode adicionar:

```python
import allure

@allure.feature('Chat API')
@allure.story('Validação de Entrada')
@allure.severity(allure.severity_level.CRITICAL)
def test_chat_endpoint():
    with allure.step('Enviar pergunta'):
        response = client.post('/api/chat', json={'pergunta': 'teste'})
    
    with allure.step('Verificar resposta'):
        assert response.status_code == 200
```

**Mas isso é OPCIONAL!** O dashboard já funciona sem decorators.

---

## 📁 Estrutura de Arquivos

```
allure-results/        # Dados brutos (gerados por pytest)
allure-report/         # Relatório HTML (gerado por allure CLI)
  ├── index.html       # Dashboard principal
  ├── data/
  ├── plugins/
  └── widgets/
```

---

## 🔄 Workflow Recomendado

### Desenvolvimento Diário
```bash
# Executar testes normalmente
make test

# Ver cobertura (pytest-html)
make test-cov
open htmlcov/index.html
```

### Apresentações / Demos
```bash
# Gerar dashboard bonito
make test-allure
make allure-serve
```

### CI/CD
```bash
# Gerar relatório estático
make test-allure
make allure-generate
# Publicar allure-report/ como artifact
```

---

## 🎯 Comandos Disponíveis

```bash
make test-allure       # Executar testes + coletar dados Allure
make allure-serve      # Gerar e abrir dashboard (requer allure CLI)
make allure-generate   # Gerar HTML estático (requer allure CLI)
make allure-clean      # Limpar resultados
```

---

## 💡 Dicas

### 1. Primeira Vez
```bash
# Instalar Allure CLI
brew install allure

# Testar
make test-allure
make allure-serve
```

### 2. Sem Allure CLI
Se não quiser instalar, use pytest-html:
```bash
make test-cov  # Já funciona!
```

### 3. CI/CD
No GitHub Actions, use:
```yaml
- name: Generate Allure Report
  run: |
    make test-allure
    make allure-generate
    
- name: Publish Report
  uses: actions/upload-artifact@v3
  with:
    name: allure-report
    path: allure-report/
```

---

## 🆚 Comparação

| Recurso | pytest-html | Allure |
|:---|:---:|:---:|
| **Instalação** | ✅ Já instalado | ⚠️ Requer CLI |
| **Simplicidade** | ✅ Muito simples | ⚠️ Mais complexo |
| **Visual** | ⚠️ Básico | ✅ Profissional |
| **Interatividade** | ❌ Estático | ✅ Interativo |
| **Gráficos** | ❌ Poucos | ✅ Muitos |
| **Histórico** | ❌ Não | ✅ Sim |

---

## 🎉 Resumo

**Allure está configurado!** Você pode:

1. ✅ **Usar pytest-html** (já funciona, simples)
2. ✅ **Instalar Allure CLI** e ter dashboards incríveis
3. ✅ **Escolher quando usar cada um**

**Recomendação**: 
- Dia a dia: `make test-cov` (pytest-html)
- Apresentações: `make allure-serve` (Allure)

---

**Última atualização**: 2025-11-26
