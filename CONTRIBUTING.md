# Contributing to STARCORE Platform

Thanks for your interest in contributing. This project is pre-alpha and
moves quickly; the rules below keep it reviewable and stable.

## Workflow

1. Fork/branch from `main` (direct pushes to `main` are blocked).
2. Make your change on a focused feature branch (one concern per PR).
3. Run the full quality gate locally (see below) — CI runs the same.
4. Open a PR using the template; describe **what** changed, **why**, and
   how you tested it.
5. A significant change set should add a `docs/changelog/sprint-NNN.md`
   entry; architectural decisions get an ADR in `docs/adr/`.

## Quality gate (must pass before review)

```bash
uv sync --extra dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pip-audit
uv run pytest -q
```

`make lint` / `make format` / `make test` wrap the same commands.

## Ground rules

- **Tests are part of the change.** New behavior needs new tests;
  bug fixes need a regression test that fails without the fix.
- **Type hints everywhere.** Pyright checks `packages/`, `apps/`, and
  `tests/` against Python 3.12.
- **Schema changes go through Alembic** (`uv run alembic revision`);
  keep `packages/core/models_db.py` and migrations in sync — startup
  fails fast on drift by design.
- **No secrets in code, tests, or logs.** Configuration goes through
  Pydantic Settings (`STARCORE_*` env vars) with `.env.example` updated
  in the same PR.
- **Ruff configuration lives in `ruff.toml`** — don't add a
  `[tool.ruff]` section to `pyproject.toml`.
- Keep the README's "What Works Today" table honest: if your PR changes
  the feature surface, update it.

## Reporting bugs and proposing features

Open a GitHub issue with reproduction steps (bugs) or the problem you're
trying to solve (features). For security issues, see [SECURITY.md](SECURITY.md)
— never open a public issue for a vulnerability.
