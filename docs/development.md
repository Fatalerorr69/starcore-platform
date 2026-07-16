# Development

## Quality gates

Every pull request must pass the same checks CI runs:

```bash
uv sync --extra dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pip-audit
uv run pytest -q
```

`make lint`, `make format`, and `make test` wrap the same commands.
Pre-commit hooks are available via `uv run pre-commit run --all-files`.

- **Ruff** is configured in `ruff.toml` (the single source of truth for
  lint/format settings).
- **Pyright** (`pyrightconfig.json`) type-checks `packages/`, `apps/`,
  and `tests/` against Python 3.12.
- **pip-audit** scans the locked dependency set (`uv.lock`) for known
  CVEs and blocks CI on findings.
- **pytest** runs with per-test isolation fixtures (fresh SQLite database,
  injected test API key, event-bus reset, rate-limiter counter reset) —
  see `tests/conftest.py`.

## Development workflow

Work happens on feature branches merged to `main` via pull request;
`main` is protected against direct pushes. Each significant change set is
documented in `docs/changelog/sprint-NNN.md`.

Run the API with auto-reload during development:

```bash
make dev          # uv run uvicorn core.main:app --reload
```

## Database migrations

Schema is managed exclusively by Alembic (`migrations/versions/`). To add
a migration:

```bash
uv run alembic revision -m "describe the change"
# edit the generated file, then:
uv run alembic upgrade head
uv run pytest tests/test_migrations.py tests/test_schema_management.py -q
```

Keep ORM models (`packages/core/models_db.py`) and migrations in sync —
`init_db()` fails fast if a database's recorded revision doesn't match
the migration head.

## Documentation

This site is built with MkDocs Material:

```bash
make docs         # uv run mkdocs serve
```

Sprint changelogs live in `docs/changelog/`; long-term vision documents
live in `docs/ses/`.
