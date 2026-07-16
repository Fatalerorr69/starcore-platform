.PHONY: install lint format test docs dev clean

install:
	uv sync

lint:
	uv run ruff check .

format:
	uv run ruff format .

test:
	uv run pytest -q

docs:
	uv run mkdocs serve

dev:
	uv run uvicorn core.main:app --reload

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
