MAKEFLAGS += --no-print-directory

# Standard Makefile for UV Python Projects
# Provides consistent development workflows

.PHONY: help sync-check ensure-sync dev-shell format lint type-check test test-cov clean clean-venv install build pre-commit-install pre-commit-run all-checks

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

sync-check: ## Check if environment sync is needed
	@if ! uv run python -c "import sys; sys.exit(0)" 2>/dev/null; then \
		echo "❌ Package not installed - sync needed"; \
		exit 1; \
	elif [ uv.lock -nt .venv/pyvenv.cfg ] 2>/dev/null; then \
		echo "❌ Lock file newer than venv - sync needed"; \
		exit 1; \
	elif [ pyproject.toml -nt .venv/pyvenv.cfg ] 2>/dev/null; then \
		echo "❌ pyproject.toml newer than venv - sync needed"; \
		exit 1; \
	else \
		echo "✅ Environment is up to date"; \
	fi

ensure-sync: ## Ensure environment is synced
	@$(MAKE) sync-check || (echo "Syncing environment..." && uv sync)

dev-shell: ensure-sync ## Activate development shell
	@echo "Activating virtual environment..."
	@echo "You can leave the dev shell by typing 'exit'"
	@bash -c "source .venv/bin/activate && exec bash"

format: ensure-sync ## Format code with black and isort
	@echo "Formatting code..."
	@uv run black .
	@uv run isort .
	@echo "✅ Formatting complete"

lint: ensure-sync ## Lint code with ruff
	@echo "Linting code..."
	@uv run ruff check --fix .
	@echo "✅ Linting complete"

type-check: ensure-sync ## Type check with mypy
	@echo "Type checking..."
	@uv run mypy .
	@echo "✅ Type checking complete"

test: ensure-sync ## Run tests
	@echo "Running tests..."
	@uv run pytest -v
	@echo "✅ Tests complete"

test-cov: ensure-sync ## Run tests with coverage
	@echo "Running tests with coverage..."
	@uv run pytest --cov --cov-report=html --cov-report=term
	@echo "✅ Coverage report generated in htmlcov/"

clean: ## Clean cache files and build artifacts
	@echo "Cleaning cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf build/ dist/ htmlcov/ .coverage 2>/dev/null || true
	@echo "✅ Cleanup complete"

clean-venv: ## Remove virtual environment
	@echo "Removing virtual environment..."
	@rm -rf .venv
	@echo "✅ Virtual environment removed"
	@echo "Run 'make install' or 'uv sync' to recreate"

install: ## Install project in editable mode
	@echo "Installing project..."
	@uv sync
	@echo "✅ Installation complete"

build: ensure-sync ## Build the package
	@echo "Building package..."
	@uv build
	@echo "✅ Build complete"

pre-commit-install: ensure-sync ## Install pre-commit hooks
	@echo "Installing pre-commit hooks..."
	@uv run pre-commit install
	@echo "✅ Pre-commit hooks installed"

pre-commit-run: ensure-sync ## Run pre-commit on all files
	@echo "Running pre-commit on all files..."
	@uv run pre-commit run --all-files
	@echo "✅ Pre-commit checks complete"

all-checks: format lint type-check test ## Run all checks (format, lint, type-check, test)
	@echo "✅ All checks passed!"
