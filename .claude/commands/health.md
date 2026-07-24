Run a full repo health check and summarise the results:

1. `uv lock --check` — verify lockfile is consistent with pyproject.toml
2. `uv run ruff check .` — lint
3. `uv run ruff format --check .` — format check
4. `uv run pyright` — type check
5. `uv run pytest -q --cov --cov-report=term-missing` — tests with coverage
6. `uv run pip-audit` — dependency vulnerability scan
7. `STARCORE_DATABASE_URL=sqlite:///./data/ci-check.db uv run alembic upgrade head && STARCORE_DATABASE_URL=sqlite:///./data/ci-check.db uv run alembic check` — verify no un-migrated ORM model changes
8. `docker compose config` — validate docker-compose.yml syntax

Report each check as PASS or FAIL with the key output. If anything fails, suggest the fix.
