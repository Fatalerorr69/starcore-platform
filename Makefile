.PHONY: install lint format test security docs dev clean health copilot-setup copilot-verify

# ============================================================================
# STARCORE Platform - Development Makefile
# ============================================================================
# This Makefile provides convenient shortcuts for common development tasks.
# Run 'make help' to see all available targets.

help:
	@echo "STARCORE Platform - Available Make Targets"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install              Install dependencies (uv sync --extra dev)"
	@echo "  make copilot-setup        Setup GitHub Copilot integration"
	@echo "  make copilot-verify       Verify Copilot integration"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint                 Run Ruff linter (ruff check .)"
	@echo "  make format               Format code (ruff format .)"
	@echo "  make format-check         Check formatting without changes"
	@echo "  make type-check           Run Pyright type checker"
	@echo ""
	@echo "Testing:"
	@echo "  make test                 Run pytest (quick)"
	@echo "  make test-cov             Run pytest with coverage report"
	@echo "  make test-verbose         Run pytest with verbose output"
	@echo ""
	@echo "Security:"
	@echo "  make security             Run security scans (pip-audit, bandit, gitleaks)"
	@echo "  make audit                Dependency vulnerability scan"
	@echo "  make sast                 Run Bandit SAST"
	@echo ""
	@echo "Development:"
	@echo "  make dev                  Start API server with auto-reload"
	@echo "  make health               Local health check"
	@echo "  make doctor               Run full quality gate"
	@echo "  make diagnose             Deep diagnostics"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs                 Build & serve MkDocs"
	@echo "  make docs-build           Build documentation only"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean                Remove cache files"
	@echo "  make migrations           Show migration status"
	@echo ""

# ============================================================================
# Setup & Installation
# ============================================================================

install:
	uv sync --extra dev
	@echo "✓ Dependencies installed"

copilot-setup:
	bash scripts/setup-copilot.sh

copilot-verify:
	bash scripts/verify-integration.sh

# ============================================================================
# Code Quality
# ============================================================================

lint:
	uv run ruff check .

@echo "✓ Linting passed"

format:
	uv run ruff format .
	@echo "✓ Formatting applied"

format-check:
	uv run ruff format --check .

type-check:
	uv run pyright

all-checks: lint format-check type-check
	@echo "✓ All checks passed"

# ============================================================================
# Testing
# ============================================================================

test:
	uv run pytest -q

test-cov:
	uv run pytest -q --cov --cov-report=term-missing --cov-fail-under=100

test-verbose:
	uv run pytest tests/ -v --tb=short

test-watch:
	uv run ptw -- -q

# ============================================================================
# Security
# ============================================================================

security: audit sast
	@echo "✓ Security checks complete"

audit:
	uv run pip-audit

sast:
	uv run bandit -r packages/ apps/ scripts/ -ll -q

# ============================================================================
# Development
# ============================================================================

dev:
	uv run uvicorn core.main:app --reload --port 8000

health:
	uv run starcore health

doctor:
	uv run starcore doctor

diagnose:
	uv run starcore diagnose

# ============================================================================
# Documentation
# ============================================================================

docs:
	uv run mkdocs serve

docs-build:
	uv run mkdocs build --strict

# ============================================================================
# Maintenance
# ============================================================================

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage
	@echo "✓ Cache cleaned"

migrations:
	uv run alembic current

migration-status:
	uv run alembic heads

# ============================================================================
# Pre-commit (CI-like checks locally)
# ============================================================================

pre-commit: lint format-check type-check test
	@echo "✓ All pre-commit checks passed"

ci: pre-commit security
	@echo "✓ Full CI pipeline passed locally"
