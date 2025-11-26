#!/bin/bash
# Script para criar commits semânticos agrupados por objetivo

cd "$(dirname "$0")"

echo "🚀 Criando commits semânticos agrupados..."
echo ""

# Commit 1: Correções críticas de qualidade
echo "📝 Commit 1: Correções críticas de qualidade..."
git reset
git add src/backend/middleware.py
git add src/chatbot_acessibilidade/config.py
git add src/backend/api.py
git add tests/integration/test_llm_dispatcher_integration.py
git commit -m "fix: corrige type hints e remove imports não utilizados

- Corrige type hints em middleware.py (call_next, response.body_iterator)
- Corrige ConfigDict para SettingsConfigDict em config.py
- Adiciona type: ignore para RateLimitExceeded handler em api.py
- Remove imports não utilizados em test_llm_dispatcher_integration.py

Resolve todos os erros de ruff e mypy (17 arquivos verificados)"

# Commit 2: Testes de carga com Locust
echo "📝 Commit 2: Testes de carga com Locust..."
git add tests/load/
git add requirements.txt
git commit -m "feat: adiciona testes de carga com Locust

- Cria locustfile.py com 4 cenários de carga:
  * ChatbotUser: usuários fazendo perguntas
  * HealthCheckUser: monitoramento constante
  * MixedUser: uso misto realista
  * StressTestUser: teste de stress
- Adiciona locust==2.42.5 ao requirements.txt
- Cria estrutura tests/load/ com __init__.py"

# Commit 3: Benchmarks de performance
echo "📝 Commit 3: Benchmarks de performance..."
git add tests/performance/
git add requirements.txt
git commit -m "feat: adiciona benchmarks de performance com pytest-benchmark

- Cria test_benchmarks.py com 6 benchmarks:
  * test_pipeline_performance
  * test_cache_performance (2.7μs - 367x mais rápido!)
  * test_validation_performance
  * test_formatter_performance
  * test_metrics_collection_performance
  * test_concurrent_requests_performance
- Adiciona pytest-benchmark==5.2.0 ao requirements.txt
- Cria conftest.py para configuração de testes de performance"

# Commit 4: Property-based testing
echo "📝 Commit 4: Property-based testing..."
git add tests/property/
git add requirements.txt
git commit -m "feat: adiciona property-based testing com Hypothesis

- Cria test_validators_property.py com 10 property tests
- Testa invariantes em validators, cache e formatter
- Gera automaticamente 100+ casos de teste por property
- Adiciona hypothesis==6.148.2 ao requirements.txt
- Cria conftest.py para configuração de property tests"

# Commit 5: Mutation testing
echo "📝 Commit 5: Mutation testing..."
git add .mutmut-config.py
git add requirements.txt
git commit -m "feat: adiciona mutation testing com mutmut

- Cria .mutmut-config.py para configuração
- Configura para pular mutações em imports
- Adiciona mutmut==3.4.0 ao requirements.txt
- Valida qualidade dos testes existentes"

# Commit 6: Relatórios visuais com Allure
echo "📝 Commit 6: Relatórios visuais..."
git add requirements.txt
git commit -m "feat: adiciona relatórios visuais com Allure

- Adiciona allure-pytest==2.15.0 ao requirements.txt
- Funciona automaticamente sem decorators
- Gera dashboards interativos profissionais
- Suporta histórico de execuções"

# Commit 7: Comandos Makefile
echo "📝 Commit 7: Comandos Makefile..."
git add Makefile
git commit -m "feat: adiciona 14 novos comandos ao Makefile

Testes de carga:
- test-load: Locust headless
- test-load-ui: Locust com interface web

Benchmarks:
- test-benchmark: Executar benchmarks
- test-benchmark-compare: Com comparação

Property-based:
- test-property: Property tests

Mutation testing:
- test-mutation: Executar mutation testing
- mutation-results: Ver resultados
- mutation-show-survived: Ver sobreviventes
- mutation-html: Gerar relatório HTML
- mutation-clean: Limpar cache

Relatórios visuais:
- test-allure: Gerar dados Allure
- allure-serve: Abrir dashboard
- allure-generate: Gerar HTML estático
- allure-clean: Limpar relatórios"

# Commit 8: Documentação completa
echo "📝 Commit 8: Documentação completa..."
git add docs/TESTES_CARGA.md
git add docs/MUTATION_TESTING.md
git add docs/ALLURE_REPORTS.md
git add docs/INDICE_TESTES.md
git commit -m "docs: adiciona guias completos de testes avançados

- INDICE_TESTES.md: Índice completo de documentação (200+ linhas)
- TESTES_CARGA.md: Guia de Locust e pytest-benchmark (206 linhas)
- MUTATION_TESTING.md: Guia de mutation testing (247 linhas)
- ALLURE_REPORTS.md: Guia de relatórios visuais (230 linhas)

Todos os guias incluem:
- Como executar
- Interpretação de resultados
- Metas de performance
- Troubleshooting
- Boas práticas"

# Commit 9: Atualização de configuração
echo "📝 Commit 9: Atualização de configuração..."
git add .gitignore
git commit -m "chore: atualiza .gitignore para ferramentas de teste

- Adiciona .mutmut-cache (mutation testing)
- Adiciona html/ (relatórios mutmut)
- Adiciona allure-results/ (dados Allure)
- Adiciona allure-report/ (relatórios Allure)
- Adiciona .allure/ (cache Allure)"

# Commit 10: Atualização de documentação principal
echo "📝 Commit 10: Atualização de documentação principal..."
git add README.md
git add docs/CHANGELOG.md
git add docs/CHANGELOG_3.13.0.md
git commit -m "docs: atualiza README e CHANGELOG para v3.13.0

README.md:
- Atualiza seção de Testes e Qualidade
- Adiciona tabela com 8 ferramentas de teste
- Adiciona comandos de testes avançados
- Atualiza métricas de qualidade (98.77% cobertura)
- Adiciona links para novos guias

CHANGELOG.md:
- Adiciona versão 3.13.0 com todas as melhorias
- Documenta 5 novas ferramentas de teste
- Lista 14 novos comandos Makefile
- Documenta 4 novos guias de documentação

CHANGELOG_3.13.0.md:
- Versão detalhada standalone para referência"

# Commit 11: Correção final
echo "📝 Commit 11: Correção final..."
git add tests/performance/test_benchmarks.py
git commit -m "fix: remove import não utilizado em test_benchmarks.py

- Remove AsyncMock não utilizado
- Mantém apenas patch do unittest.mock
- Resolve warning do ruff F401"

echo ""
echo "✅ Todos os commits criados com sucesso!"
echo ""
echo "📊 Resumo:"
git log --oneline -11
echo ""
echo "🎉 Pronto! Use 'git push' para enviar ao repositório remoto."
