.PHONY: help install lint format type-check test clean

help: ## Mostra esta mensagem de ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instala dependências e pre-commit hooks
	pip install -r requirements.txt
	pip install pre-commit black ruff mypy
	pre-commit install

run: ## Inicia o servidor de desenvolvimento
	uvicorn src.backend.api:app --reload --port 8000

lint: ## Executa linters (ruff)
	ruff check src/ tests/

format: ## Formata código (black + ruff)
	black src/ tests/
	ruff format src/ tests/

type-check: ## Verifica tipos (mypy)
	mypy src/

test: ## Executa todos os testes
	pytest tests/ -v

test-unit: ## Executa apenas testes unitários
	pytest tests/unit/ -v -m "unit"

test-integration: ## Executa apenas testes de integração
	pytest tests/integration/ -v -m "integration"

test-e2e: ## Executa apenas testes E2E
	pytest tests/e2e/ -v -m "e2e"

test-fast: ## Executa testes rápidos (unit + integration)
	pytest tests/unit/ tests/integration/ -v

test-cov: ## Executa testes com cobertura
	pytest --cov=src.chatbot_acessibilidade --cov=src.backend --cov-report=html --cov-report=term

test-playwright: ## Executa testes Playwright (requer servidor rodando)
	pytest tests/e2e/playwright/ -v -m "playwright"

test-ci-local: ## Testa pipeline CI/CD localmente
	@echo "🚀 Executando pipeline CI/CD localmente..."
	@bash scripts/test_ci_local.sh

test-e2e-server: ## Inicia servidor e executa testes E2E
	@echo "🚀 Iniciando servidor para testes E2E..."
	@echo "⚠️  Pressione Ctrl+C para parar o servidor após os testes"
	@uvicorn src.backend.api:app --host 0.0.0.0 --port 8000 &
	@sleep 5
	@echo "✅ Servidor iniciado. Executando testes..."
	@PLAYWRIGHT_BASE_URL=http://localhost:8000 PLAYWRIGHT_HEADLESS=true pytest tests/e2e/ -v -m "e2e" || true
	@pkill -f "uvicorn src.backend.api:app" || true

test-playwright-ui: ## Executa testes Playwright com UI (headed mode)
	pytest tests/e2e/playwright/ -v --headed

test-playwright-api: ## Executa apenas testes de API com Playwright
	pytest tests/e2e/playwright/test_api_playwright.py -v

test-playwright-frontend: ## Executa apenas testes de frontend com Playwright
	pytest tests/e2e/playwright/test_frontend_playwright.py -v

test-playwright-accessibility: ## Executa apenas testes de acessibilidade
	pytest tests/e2e/playwright/test_accessibility.py -v

test-error-handling: ## Executa testes de tratamento de erros
	pytest tests/e2e/playwright/test_error_handling.py -v

test-security: ## Executa testes de segurança
	pytest tests/e2e/playwright/test_security.py -v -m "security"

test-performance: ## Executa testes de performance
	pytest tests/e2e/playwright/test_performance.py -v -m "performance"

test-fallback: ## Executa testes de fallback e retry
	pytest tests/integration/test_fallback.py -v

test-playwright-report: ## Executa testes Playwright e gera relatório HTML
	pytest tests/e2e/playwright/ -v -m "playwright" --html=tests/reports/html/report.html --self-contained-html

playwright-install: ## Instala navegadores do Playwright
	playwright install chromium firefox webkit

playwright-trace: ## Abre trace viewer do Playwright (usa o trace mais recente)
	@if [ -z "$$(ls -A tests/reports/traces/*.zip 2>/dev/null)" ]; then \
		echo "❌ Nenhum trace encontrado em tests/reports/traces/"; \
		exit 1; \
	fi; \
	LATEST_TRACE=$$(ls -t tests/reports/traces/*.zip | head -1); \
	echo "🔍 Abrindo trace: $$LATEST_TRACE"; \
	playwright show-trace "$$LATEST_TRACE"

test-playwright-chromium: ## Executa testes Playwright no Chromium
	PLAYWRIGHT_BROWSER=chromium pytest tests/e2e/playwright/ -v -m "playwright"

test-playwright-firefox: ## Executa testes Playwright no Firefox
	PLAYWRIGHT_BROWSER=firefox pytest tests/e2e/playwright/ -v -m "playwright"

test-playwright-webkit: ## Executa testes Playwright no WebKit
	PLAYWRIGHT_BROWSER=webkit pytest tests/e2e/playwright/ -v -m "playwright"

test-playwright-all-browsers: ## Executa testes em todos os navegadores
	@echo "🌐 Testando Chromium..."
	@$(MAKE) test-playwright-chromium || true
	@echo "🌐 Testando Firefox..."
	@$(MAKE) test-playwright-firefox || true
	@echo "🌐 Testando WebKit..."
	@$(MAKE) test-playwright-webkit || true

test-load: ## Executa testes de carga com Locust (modo headless)
	@echo "🔥 Executando testes de carga (headless)..."
	@echo "⚠️  Certifique-se de que o servidor está rodando em http://localhost:8000"
	locust -f tests/load/locustfile.py --host=http://localhost:8000 \
		--users 50 --spawn-rate 5 --run-time 60s --headless

test-load-ui: ## Executa testes de carga com Locust (interface web)
	@echo "🔥 Iniciando Locust com interface web..."
	@echo "📊 Acesse http://localhost:8089 para configurar e executar os testes"
	@echo "⚠️  Certifique-se de que o servidor está rodando em http://localhost:8000"
	locust -f tests/load/locustfile.py --host=http://localhost:8000

test-benchmark: ## Executa benchmarks de performance
	@echo "⚡ Executando benchmarks de performance..."
	pytest tests/performance/ --benchmark-only -v

test-benchmark-compare: ## Executa benchmarks e compara com execuções anteriores
	@echo "⚡ Executando benchmarks com comparação..."
	pytest tests/performance/ --benchmark-autosave --benchmark-compare -v

test-property: ## Executa property-based tests com Hypothesis
	@echo "🔍 Executando property-based tests..."
	pytest tests/property/ -v -m property

test-mutation: ## Executa mutation testing com mutmut
	@echo "🧬 Executando mutation testing..."
	@echo "⚠️  Isso pode demorar alguns minutos..."
	mutmut run src/chatbot_acessibilidade/core/

mutation-results: ## Mostra resultados do mutation testing
	@echo "📊 Resultados do mutation testing:"
	mutmut results

mutation-show-survived: ## Mostra mutantes que sobreviveram
	@echo "🙁 Mutantes que sobreviveram:"
	mutmut show survived

mutation-html: ## Gera relatório HTML do mutation testing
	@echo "📄 Gerando relatório HTML..."
	mutmut html
	@echo "✅ Relatório gerado em html/index.html"

mutation-clean: ## Limpa resultados do mutation testing
	@echo "🧹 Limpando resultados do mutation testing..."
	rm -rf .mutmut-cache html/
	@echo "✅ Resultados limpos"

test-allure: ## Executa testes e gera dados para Allure
	@echo "📊 Executando testes com Allure..."
	pytest tests/unit tests/integration tests/contract --alluredir=allure-results -v

allure-serve: ## Gera e abre relatório Allure (requer allure CLI)
	@echo "🚀 Gerando e abrindo relatório Allure..."
	@if command -v allure \u003e/dev/null 2\u003e\u00261; then \
		allure serve allure-results; \
	else \
		echo "❌ Allure CLI não instalado. Instale com: brew install allure"; \
		echo "   Ou use: make allure-open-python"; \
	fi

allure-generate: ## Gera relatório Allure HTML (requer allure CLI)
	@echo "📄 Gerando relatório Allure..."
	@if command -v allure \u003e/dev/null 2\u003e\u00261; then \
		allure generate allure-results -o allure-report --clean; \
		echo "✅ Relatório gerado em allure-report/index.html"; \
	else \
		echo "❌ Allure CLI não instalado. Instale com: brew install allure"; \
	fi

allure-clean: ## Limpa resultados e relatórios do Allure
	@echo "🧹 Limpando relatórios Allure..."
	rm -rf allure-results allure-report .allure
	@echo "✅ Relatórios limpos"

check: lint type-check test ## Executa todas as verificações

clean: ## Limpa arquivos temporários
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	rm -rf .coverage htmlcov/

pre-commit: ## Executa verificações pré-commit (linters, formatação, testes, cobertura)
	@echo "🔍 Executando verificações pré-commit..."
	@echo ""
	@echo "1️⃣  Verificando formatação com Black..."
	@black --check src/ tests/ || (echo "❌ Black falhou. Execute 'make format' para corrigir." && exit 1)
	@echo "✅ Black passou!"
	@echo ""
	@echo "2️⃣  Verificando linting com Ruff..."
	@ruff check src/ tests/ || (echo "❌ Ruff falhou. Execute 'make lint' para ver detalhes." && exit 1)
	@echo "✅ Ruff passou!"
	@echo ""
	@echo "3️⃣  Executando testes unitários..."
	@pytest tests/unit/ -v -m "unit" --tb=short || (echo "❌ Testes unitários falharam." && exit 1)
	@echo "✅ Testes unitários passaram!"
	@echo ""
	@echo "4️⃣  Verificando cobertura de testes (>95%)..."
	@pytest --cov=chatbot_acessibilidade --cov-report=term --cov-fail-under=95 tests/unit/ tests/integration/ -q || (echo "❌ Cobertura insuficiente (< 95%)." && exit 1)
	@echo "✅ Cobertura adequada!"
	@echo ""
	@echo "🎉 Todas as verificações passaram! Você pode fazer o commit com segurança."

fix: format lint ## Formata e corrige problemas de lint automaticamente
