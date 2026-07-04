.PHONY: install lint format test docs dev clean

install:
	uv sync

lint:
	ruff check .

format:
	ruff format .

test:
	pytest

docs:
	mkdocs serve

dev:
	uv run python -m packages.core

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
