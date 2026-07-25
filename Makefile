.PHONY: install lint format test security docs dev clean

install:
	uv sync --extra dev

lint:
	uv run ruff check .

format:
	uv run ruff format .

test:
	uv run pytest -q

security:
	uv run pip-audit
	uv run bandit -r packages/ apps/ scripts/ -ll -q

docs:
	uv run mkdocs serve

dev:
	uv run uvicorn core.main:app --reload

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
