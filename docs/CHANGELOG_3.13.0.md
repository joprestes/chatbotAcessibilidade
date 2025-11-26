# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [3.13.0] - 2025-11-26

### Adicionado
- **Suite de Testes de Classe Mundial**: Implementadas 5 novas ferramentas de teste profissionais
  - **Locust** (v2.42.5): Testes de carga com 4 cenários (ChatbotUser, HealthCheckUser, MixedUser, StressTestUser)
  - **pytest-benchmark** (v5.2.0): 6 benchmarks de performance (pipeline, cache, validation, formatter, metrics, concurrent)
  - **Hypothesis** (v6.148.2): 10 property-based tests para validators, cache e formatter
  - **mutmut** (v3.4.0): Mutation testing configurado para validar qualidade dos testes
  - **Allure** (v2.15.0): Relatórios visuais profissionais com dashboards interativos

- **Documentação Completa de Testes**:
  - `docs/INDICE_TESTES.md`: Índice completo de toda documentação de testes
  - `docs/TESTES_CARGA.md`: Guia completo de Locust e pytest-benchmark (206 linhas)
  - `docs/MUTATION_TESTING.md`: Guia completo de mutation testing (247 linhas)
  - `docs/ALLURE_REPORTS.md`: Guia completo de relatórios visuais (230 linhas)

- **Novos Comandos Makefile** (14 comandos):
  - `make test-load`: Testes de carga headless (50 users, 60s)
  - `make test-load-ui`: Testes de carga com interface web
  - `make test-benchmark`: Benchmarks de performance
  - `make test-benchmark-compare`: Benchmarks com comparação
  - `make test-property`: Property-based tests
  - `make test-mutation`: Mutation testing
  - `make mutation-results`: Ver resultados do mutation testing
  - `make mutation-show-survived`: Ver mutantes que sobreviveram
  - `make mutation-html`: Gerar relatório HTML do mutation testing
  - `make mutation-clean`: Limpar resultados do mutation testing
  - `make test-allure`: Executar testes e gerar dados Allure
  - `make allure-serve`: Gerar e abrir dashboard Allure
  - `make allure-generate`: Gerar relatório HTML estático
  - `make allure-clean`: Limpar relatórios Allure

- **Estrutura de Testes Expandida**:
  - `tests/load/locustfile.py`: 4 cenários de carga (200+ linhas)
  - `tests/performance/test_benchmarks.py`: 6 benchmarks (150+ linhas)
  - `tests/property/test_validators_property.py`: 10 property tests (150+ linhas)
  - `.mutmut-config.py`: Configuração do mutation testing

### Modificado
- **README.md**: Atualizada seção de testes com novas ferramentas e métricas
- **.gitignore**: Adicionadas entradas para `.mutmut-cache`, `html/`, `allure-results/`, `allure-report/`
- **requirements.txt**: Adicionadas 5 novas dependências de teste

### Melhorado
- **Cobertura de Testes**: Mantida em 98.77% (acima da meta de 95%)
- **Qualidade de Código**: 0 erros de lint (Ruff) e type checking (MyPy)
- **Performance**: Cache operando em 2.7μs (367x mais rápido que meta de 10ms)
- **Documentação**: 3 novos guias completos + índice centralizado

### Corrigido
- Import não utilizado `AsyncMock` em `tests/performance/test_benchmarks.py`
- Sintaxe do mutmut atualizada para v3.4.0 (não usa mais `--paths-to-mutate`)

### Notas Técnicas
- Total de ferramentas de teste: 8 (pytest, pytest-cov, Playwright, Locust, pytest-benchmark, Hypothesis, mutmut, Allure)
- Total de testes: 384 (100% passando)
- Total de arquivos criados: 14 (~2,000 linhas de código)
- Total de comandos Makefile: 14 novos
- Tempo de implementação: ~2 horas
- Projeto agora serve como referência de qualidade para QAs profissionais

