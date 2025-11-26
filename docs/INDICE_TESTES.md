# 📚 Índice de Documentação de Testes

Este documento serve como índice para toda a documentação de testes e qualidade do projeto.

---

## 🎯 Guias Principais

### 1. [📋 TESTES.md](./TESTES.md)
**Estratégia geral de testes do projeto**
- Pirâmide de testes
- Como executar testes
- Cobertura por módulo
- Testes E2E com Playwright

### 2. [🔥 TESTES_CARGA.md](./TESTES_CARGA.md)
**Testes de carga e performance**
- Locust (4 cenários de carga)
- pytest-benchmark (6 benchmarks)
- Metas de performance
- Como executar e interpretar

### 3. [🧬 MUTATION_TESTING.md](./MUTATION_TESTING.md)
**Validação da qualidade dos testes**
- O que é mutation testing
- Como executar mutmut
- Módulos prioritários
- Interpretação de resultados

### 4. [📊 ALLURE_REPORTS.md](./ALLURE_REPORTS.md)
**Relatórios visuais profissionais**
- Dashboards interativos
- Como instalar e usar
- Comparação com pytest-html
- Workflow recomendado

---

## 🚀 Quick Start

### Testes Básicos
```bash
# Todos os testes
make test

# Com cobertura
make test-cov
```

### Testes de Performance
```bash
# Benchmarks
make test-benchmark

# Testes de carga (requer servidor rodando)
make test-load-ui
```

### Testes Avançados
```bash
# Property-based tests
make test-property

# Mutation testing
make test-mutation
make mutation-results
```

### Relatórios Visuais
```bash
# Gerar dados Allure
make test-allure

# Ver dashboard (requer: brew install allure)
make allure-serve
```

---

## 📊 Ferramentas Disponíveis

| Ferramenta | Propósito | Comando |
|:---|:---|:---|
| **pytest** | Testes unitários/integração | `make test` |
| **pytest-cov** | Cobertura de código | `make test-cov` |
| **Playwright** | Testes E2E | `make test-playwright` |
| **Locust** | Testes de carga | `make test-load-ui` |
| **pytest-benchmark** | Benchmarks | `make test-benchmark` |
| **Hypothesis** | Property-based | `make test-property` |
| **mutmut** | Mutation testing | `make test-mutation` |
| **Allure** | Relatórios visuais | `make allure-serve` |

---

## 📈 Métricas de Qualidade

| Métrica | Valor Atual | Meta |
|:---|:---:|:---:|
| **Testes Passando** | 384/384 | 100% |
| **Cobertura** | 98.77% | ≥ 95% |
| **Ruff (Linter)** | 0 erros | 0 |
| **MyPy (Type Check)** | 0 erros | 0 |

---

## 🎓 Para QAs Novos no Projeto

### 1. Leia Primeiro
1. [TESTES.md](./TESTES.md) - Visão geral
2. [ESTRATEGIA_TESTES.md](./ESTRATEGIA_TESTES.md) - Estratégia detalhada

### 2. Execute os Testes
```bash
# Instalar dependências
make install

# Executar testes
make test

# Ver cobertura
make test-cov
open htmlcov/index.html
```

### 3. Explore Ferramentas Avançadas
- [TESTES_CARGA.md](./TESTES_CARGA.md) - Performance
- [MUTATION_TESTING.md](./MUTATION_TESTING.md) - Qualidade dos testes
- [ALLURE_REPORTS.md](./ALLURE_REPORTS.md) - Relatórios visuais

---

## 🔍 Encontrando Informações

### Preciso testar performance?
→ [TESTES_CARGA.md](./TESTES_CARGA.md)

### Meus testes são bons o suficiente?
→ [MUTATION_TESTING.md](./MUTATION_TESTING.md)

### Quero relatórios bonitos?
→ [ALLURE_REPORTS.md](./ALLURE_REPORTS.md)

### Como executar testes E2E?
→ [TESTES.md](./TESTES.md#testes-e2e-com-playwright)

### Quais são os padrões de acessibilidade?
→ [PADROES_ACESSIBILIDADE.md](./PADROES_ACESSIBILIDADE.md)

---

## 📝 Comandos Mais Usados

```bash
# Desenvolvimento diário
make test                    # Executar testes
make test-cov                # Com cobertura
make lint                    # Linters
make type-check              # Type checking

# Antes de commit
make check                   # Todas as verificações

# Testes específicos
make test-unit               # Apenas unitários
make test-integration        # Apenas integração
make test-playwright         # E2E com Playwright

# Performance
make test-benchmark          # Benchmarks
make test-load-ui            # Testes de carga

# Qualidade avançada
make test-property           # Property-based
make test-mutation           # Mutation testing
make allure-serve            # Relatórios visuais
```

---

## 🆘 Precisa de Ajuda?

1. **Erro nos testes?** → Veja logs detalhados com `pytest -v`
2. **Cobertura baixa?** → Execute `make test-cov` e veja `htmlcov/index.html`
3. **Performance ruim?** → Execute `make test-benchmark`
4. **Testes fracos?** → Execute `make test-mutation`

---

**Última atualização**: 2025-11-26
