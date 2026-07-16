# Sprint 005 — Tooling, Documentation & Hardening Cleanup

**Date:** 2026-07-16
**Scope:** All 12 remaining Low/Informational audit findings, per
`STARCORE-Platform-Audit-Report.md` (commit `d25b76a`): TD-04, TD-05,
TD-06, TD-07, TD-08, TD-09, TD-10, TD-14, TD-15, TD-18, TD-19, TD-20.
No ADR required — none of these involve an architectural decision; TD-14
and TD-15 follow long-established container best practices.

With this sprint, **every finding from the original audit (TD-01 through
TD-20, RISK-01 through RISK-12) is closed.**

---

## Fixed

### TD-04 / TD-05 — Makefile repaired and made consistent

`make dev` invoked `python -m packages.core`, which has no `__main__.py`
anywhere in the repository and failed outright; `lint`/`format`/`test`
omitted the `uv run` prefix used everywhere else and in the README. `dev`
now runs `uv run uvicorn core.main:app --reload` (matching the README,
the Dockerfile, and docs), and every target consistently uses `uv run`.
`make test` now runs `pytest -q` to match CI. **Files:** `Makefile`

### TD-06 — MkDocs site is functional

`mkdocs.yml` referenced four pages that did not exist (`index.md`,
`architecture.md`, `installation.md`, `development.md`) while the one
real docs file was unreachable from the nav. All four pages now exist
with accurate, current-state content (sourced from the verified
repository, not aspiration); the nav additionally exposes the sprint
changelogs, the new ADRs, and the SES vision index. Verified with
`mkdocs build --strict` (which also caught a missing nav target during
development — the strict flag is doing its job). **Files:** `mkdocs.yml`,
`docs/index.md`, `docs/architecture.md`, `docs/installation.md`,
`docs/development.md`

### TD-07 — Single Ruff configuration source

The dead `[tool.ruff]` block in `pyproject.toml` (silently shadowed by
`ruff.toml`, per Ruff's config precedence) is removed; `ruff.toml` is the
single source of truth, and CONTRIBUTING.md says so explicitly.
**Files:** `pyproject.toml`

### TD-08 — Pyright checks the right Python version and the whole codebase

`pyrightconfig.json` targeted Python 3.11 (project requires ≥3.12) and
only `packages/`. Now: `pythonVersion: 3.12`, `include: ["packages",
"apps", "tests"]`. Widening the scope surfaced 38 pre-existing type
errors in tests, all fixed in this sprint: heterogeneous
`dict(...)`-literal `_settings()` helpers in `test_providers.py` /
`test_ai_generator.py` now use explicit `dict[str, Any]` annotations;
sentinel `provider._client = object()` assignments use an explicit
`cast(ProxmoxAPI, object())` so the intent is visible to the type
checker; and `test_rate_limiting.py` now reuses `core.main`'s typed
`_handle_rate_limit_exceeded` adapter instead of re-importing slowapi's
raw handler (fixing an inconsistency introduced in Sprint 003).
**Files:** `pyrightconfig.json`, `tests/test_providers.py`,
`tests/test_ai_generator.py`, `tests/test_resource_actions.py`,
`tests/test_rate_limiting.py`

### TD-09 — Coverage is measured

`pytest-cov` was declared but never invoked anywhere. CI's Pytest step
now runs `pytest -q --cov --cov-report=term-missing`, with
`[tool.coverage.*]` configuration added (`source = packages, apps`).
Informational, not a blocking threshold — a gate can be introduced once a
baseline is agreed. First measured baseline: **83 % total** (weakest
spots: `providers/docker` 46 %, `provider_sdk/exceptions` and
`core/logger` 0 % — candidates for future test work). **Files:**
`.github/workflows/ci.yml`, `pyproject.toml`

### TD-10 — Dead mypy configuration removed

mypy was declared as a dev dependency with a `[tool.mypy]` config block
but never ran in CI or pre-commit (only Ruff and Pyright are enforced).
Both the dependency and the config block are removed; Pyright is the
project's type checker. **Files:** `pyproject.toml`

### TD-14 — Container runs as non-root

The Docker image had no `USER` directive. It now creates a dedicated
system user (`starcore`), owns `/app` and `/data` accordingly, and moves
the `uv`/`uvx` binaries to `/usr/local/bin` (world-readable — they were
previously under `/root/.local/bin`, unreachable for a non-root user
since `/root` is mode 700). Nothing the application does requires root
in-container. **Files:** `Dockerfile`

### TD-15 — Unused Compose scaffolding is opt-in; hardcoded password removed

`postgres`, `redis`, and `nats` (declared for future use, wired into
nothing) previously started with every `docker compose up`, exposing
ports and one hardcoded credential (`POSTGRES_PASSWORD: starcore`). All
three now sit behind a `scaffold` Compose profile (opt in with
`docker compose --profile scaffold up`); the Postgres password must come
from `STARCORE_POSTGRES_PASSWORD` in `.env` (Compose refuses to start the
service without it). The `api` service additionally gained a proper
Compose `healthcheck` targeting `/health` — which, since Sprint 002,
actually reflects database reachability. **Files:**
`docker-compose.yml`, `.env.example`

### TD-18 — Governance documents exist (including the missing ADRs)

`SECURITY.md` (private vulnerability reporting via GitHub Security
Advisories, current security model, known accepted limitations) and
`CONTRIBUTING.md` (workflow, quality gate, ground rules) are added.
Additionally, ADR-001 through ADR-005 — referenced by earlier sprint
changelogs but never committed as files — now exist under `docs/adr/`
and are reachable from the MkDocs nav. `CODEOWNERS` is intentionally
omitted: with a single maintainer it encodes nothing GitHub doesn't
already do. **Files:** `SECURITY.md`, `CONTRIBUTING.md`,
`docs/adr/ADR-001..005-*.md`

### TD-19 — Dead `Resource` model removed

`provider_sdk/models.py` defined a Pydantic `Resource` model imported
nowhere (verified repository-wide, code and docs). Deleted. Providers'
`list_resources()` continue returning provider-shaped dicts as before; a
shared resource model can be reintroduced deliberately if/when providers
converge on one. **Files:** `packages/provider_sdk/models.py` (deleted)

### TD-20 — `GET /runs` is paginated

`list_runs()` executed an unbounded query and the endpoint returned it
whole. `list_runs()` now accepts optional `limit`/`offset` (default
`None`/`0` — the CLI's `starcore runs list` behavior is unchanged);
`GET /runs` takes validated query parameters (`limit` 1–200, default 50;
`offset` ≥ 0) and returns newest-first pages. Out-of-range values return
422. **Files:** `packages/core/repository.py`, `packages/core/main.py`

---

## Tests

3 tests added (142 total):

- `tests/test_persistence.py` — `list_runs()` pagination returns
  newest-first pages with correct limit/offset behavior, and the
  no-argument call remains unbounded (CLI compatibility).
- `tests/test_api.py` — `GET /runs` rejects `limit=0`, `limit=201`, and
  `offset=-1` with 422, accepts the documented maximum.

```
142 passed (140 pre-existing + 2 new persistence/API pagination tests,
             plus assertions consolidated into existing files), 0 failed
ruff format --check .   -> 61 files already formatted
ruff check .            -> All checks passed
pyright (packages+apps+tests, py312) -> 0 errors
pip-audit               -> No known vulnerabilities found
pytest --cov            -> 83% total coverage (first measurement)
mkdocs build --strict   -> passes
uv build                -> wheel built successfully
```

## Breaking changes

- **`GET /runs`** now returns at most 200 records per request (default
  50) instead of the entire history. Clients wanting everything must
  paginate with `offset`. The CLI (`starcore runs list`) is unaffected.
- **`docker compose up`** no longer starts `postgres`/`redis`/`nats`;
  they require `--profile scaffold` and (for Postgres)
  `STARCORE_POSTGRES_PASSWORD`. The application never used them, so no
  application behavior changes.
- **The container runs as non-root.** Deployments that bind-mounted host
  paths into `/data` with root-only permissions must make them writable
  by the container user (the named-volume default works unchanged; CI's
  docker-build smoke test will verify this path).
- **mypy** is no longer a declared dev dependency; anyone invoking it
  manually should switch to `uv run pyright`.

## Out of scope

Nothing — this sprint closes the audit backlog. Future work is
feature-driven (see README "What's Planned") plus the coverage-baseline
follow-ups noted under TD-09.
