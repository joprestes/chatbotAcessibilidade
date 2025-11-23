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

test-playwright-ui: ## Executa testes Playwright com UI (headed mode)
	pytest tests/e2e/playwright/ -v --headed

test-playwright-api: ## Executa apenas testes de API com Playwright
	pytest tests/e2e/playwright/test_api_playwright.py -v

test-playwright-frontend: ## Executa apenas testes de frontend com Playwright
	pytest tests/e2e/playwright/test_frontend_playwright.py -v

test-playwright-accessibility: ## Executa apenas testes de acessibilidade
	pytest tests/e2e/playwright/test_accessibility.py -v

playwright-install: ## Instala navegadores do Playwright
	playwright install chromium firefox webkit

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

