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

test: ## Executa testes
	pytest -v

test-cov: ## Executa testes com cobertura
	pytest --cov=src.chatbot_acessibilidade --cov=src.backend --cov-report=html --cov-report=term

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

