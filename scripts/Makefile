.PHONY: help clean lint format test test-unit test-integration coverage install dev-install

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

clean: ## Clean up build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf coverage_html/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint: ## Run linting tools
	ruff src tests
	black --check src tests
	isort --check src tests
	mypy src tests

format: ## Format code with black, isort and ruff
	black src tests
	isort src tests
	ruff check --fix src tests

test: ## Run all tests
	pytest

test-unit: ## Run unit tests only
	pytest tests/unit

test-integration: ## Run integration tests only
	pytest tests/integration

coverage: ## Generate coverage report
	pytest --cov=src --cov-report=term --cov-report=html:coverage_html tests/

install: ## Install the package
	pip install -e .

dev-install: ## Install the package with development dependencies
	pip install -e ".[dev]"

docker-build: ## Build Docker image
	docker compose build

docker-up: ## Start Docker services
	docker compose up -d

docker-down: ## Stop Docker services
	docker compose down

docker-logs: ## View Docker logs
	docker compose logs -f

pre-commit: ## Install pre-commit hooks
	pre-commit install