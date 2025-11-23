.PHONY: help install lint format type-check test clean

help: ## Mostra esta mensagem de ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instala dependências e pre-commit hooks
	pip install -r requirements.txt
	pip install pre-commit black ruff mypy
	pre-commit install

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

check: lint type-check test ## Executa todas as verificações

clean: ## Limpa arquivos temporários
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	rm -rf .coverage htmlcov/

fix: format lint ## Formata e corrige problemas de lint automaticamente

