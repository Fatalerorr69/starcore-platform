# Development

## Quality gates

Every pull request must pass the same checks CI runs:

```bash
uv sync --extra dev
uv lock --check
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pip-audit
uv run bandit -r packages/ apps/ scripts/ -ll -q
# gitleaks secret scanning runs via gitleaks/gitleaks-action in CI, not a local uv command
uv run pytest -q --cov --cov-report=term-missing --cov-fail-under=100
```

`make lint`, `make format`, `make test`, and `make security` (pip-audit +
Bandit) wrap the same commands. Pre-commit hooks are available via
`uv run pre-commit run --all-files`.

- **Ruff** is configured in `ruff.toml` (the single source of truth for
  lint/format settings).
- **Pyright** (`pyrightconfig.json`) type-checks `packages/`, `apps/`,
  and `tests/` against Python 3.12.
- **pip-audit** scans the locked dependency set (`uv.lock`) for known
  CVEs and blocks CI on findings.
- **Bandit** (medium+ severity, `-ll`) statically scans for insecure code
  patterns; low-severity findings (e.g. `assert` usage) don't fail CI.
- **gitleaks** scans the full commit history for secrets on every PR and
  push to `main`; `.gitleaks.toml` allowlists known-safe test fixtures.
- **pytest** runs with per-test isolation fixtures (fresh SQLite database,
  injected test API key, event-bus reset, rate-limiter counter reset) —
  see `tests/conftest.py`. Coverage is enforced at 100%.

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

`uv run alembic check` (used by CI to catch model/migration drift) needs
a database that's already at the migration head — it fails with "Target
database is not up to date" against a fresh or stale one, which is not a
drift bug, just an unmigrated DB. Point it at a throwaway file rather
than your dev DB, matching what CI does (`.github/workflows/ci.yml`):

```bash
STARCORE_DATABASE_URL=sqlite:///./ci-check.db uv run alembic upgrade head
STARCORE_DATABASE_URL=sqlite:///./ci-check.db uv run alembic check
rm ci-check.db
```

## Documentation

This site is built with MkDocs Material:

```bash
make docs         # uv run mkdocs serve
```

Sprint changelogs live in `docs/changelog/`; long-term vision documents
live in `docs/ses/`.

`mkdocs`/`mkdocs-material` are pinned below their next major (`<2.0.0` /
`<10.0.0`) in `pyproject.toml`. The Material for MkDocs team has flagged
the upcoming MkDocs 2.0 as a breaking rewrite with no migration path
(plugin system removed, theming rewritten) and currently unlicensed for
production use — see the notice printed on every `mkdocs build`/`serve`.
The cap stops a routine dependency bump from landing on it silently;
lift it only after evaluating 2.0 deliberately.
