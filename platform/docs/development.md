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

## Standalone scripts

`scripts/` holds two operator-facing scripts, independent of the CLI:

- `scripts/doctor.py` — runs the same quality gates as `starcore doctor`
  (lockfile, ruff, pyright, pip-audit, Bandit, tests) with plain-text
  PASS/FAIL output and no `typer`/`rich` dependency. Useful in contexts
  where the full `starcore` CLI isn't installed. Run with
  `uv run python scripts/doctor.py`.
- `scripts/health.py` — pings a *running* STARCORE API instance's
  `GET /health` endpoint over HTTP and reports its status; exits 1 if
  unreachable or unhealthy. This is distinct from `starcore health` (which
  checks the local process's own database connectivity directly, no HTTP
  round trip) — use `scripts/health.py` for external monitoring of a
  deployed instance, e.g. `uv run python scripts/health.py --url
  http://myserver:8000`.

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

### Rollback procedure

Every migration in `migrations/versions/` is expected to implement both
`upgrade()` and `downgrade()` (`tests/test_migrations.py` exercises both
directions for the initial schema). To roll a database back one revision:

```bash
uv run alembic downgrade -1
```

or to a specific revision:

```bash
uv run alembic downgrade <revision_id>   # uv run alembic history to list revisions
```

**Back up the database file before downgrading anything that isn't a
throwaway/CI database** — `downgrade()` runs real `DROP`/`ALTER`
statements and Alembic does not snapshot data for you. For the default
SQLite deployment this is just `cp data/starcore.db data/starcore.db.bak`;
for any other backend, use that backend's own backup mechanism. After a
downgrade, restart the STARCORE process: `init_db()`'s startup check
compares the database's revision against the migration head baked into
the *running* code, so a downgraded database will correctly make a
newer-than-downgrade STARCORE build fail fast (`RuntimeError`) rather than
run against a schema it doesn't recognize — that's the same fail-fast
behavior `_ensure_schema_at_head()` applies to a stale-forward database,
applied symmetrically to a stale-backward one. If you need the older code
running against the downgraded schema too, redeploy the matching older
build alongside the downgrade.

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
