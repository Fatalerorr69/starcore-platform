# Sprint 006 — Observability, CLI Automation & Dependency Hygiene

**Date:** 2026-07-25
**Branch:** `claude/new-session-s52x55` → merged as PR #72 + PR #73
**Mode:** MODE 5 — CONTROLLED AUTONOMY

## Changes

### A01 — Dockerfile Python version
`FROM python:3.14-slim` → `FROM python:3.12-slim`. 3.14 is pre-release
beta; pyproject.toml, pyrightconfig.json, ruff.toml, and CI all target 3.12.

### A02 — pyright pre-commit hook
Added `RobertCraigie/pyright-python` rev `v1.1.400` to
`.pre-commit-config.yaml`. Pyright was CI-only; type errors could now be
caught locally before push.

### B01 — `scripts/` automation directory
- `scripts/doctor.py` — standalone runner for all CI gates (lockfile, ruff,
  pyright, pip-audit, pytest) with Rich table output and exit 1 on failure.
- `scripts/health.py` — runtime probe for the `/health` endpoint with `--url`
  flag.

### B02 — `starcore doctor` / `starcore audit` CLI commands
- `starcore doctor [--fast]` — runs all quality gates; `--fast` skips tests.
- `starcore audit` — shows git branch/SHA/tree state, recent commits, Python
  and test file counts.
- 8 new tests in `tests/test_cli.py`.

### C01 — Prometheus metrics endpoint & structured logging
- `packages/core/metrics.py`: authenticated `GET /metrics` endpoint
  (`X-API-Key`), Prometheus text format, dedicated `CollectorRegistry`.
  Metrics: `starcore_http_requests_total{method,path,status}`,
  `starcore_http_request_duration_seconds{method,path}`,
  `starcore_blueprint_tasks_total{provider,status}`.
- `packages/core/logger.py`: loguru sink configuration was never imported;
  now wired at startup in `core/main.py` and `apps/cli/main.py`.
- New env var `STARCORE_LOG_JSON` (`false` by default) switches to
  JSON-per-line output via loguru `serialize=True`, suited for Loki/ELK.
- 9 new tests in `tests/test_metrics.py`.
- New dependency: `prometheus-client>=0.21.0`.

### C02 — Snapshot/Rollback (verified — no action needed)
`starcore snapshot create/list/delete/rollback` was found to be already
fully implemented end-to-end (CLI → core → Proxmox provider → proxmoxer).
The prior session's recommendation was stale; no code change was made.

### C03 — Remove unused dependencies
`redis>=6.2.0` and `nats-py>=2.11.0` removed from `pyproject.toml` /
`uv.lock`. Dead `redis_url`/`nats_url` fields removed from `Settings`.

### TD-C05 — Alembic check documentation
Added runbook for `alembic check`'s throwaway-DB requirement to
`docs/development.md` and `CONTRIBUTING.md`, eliminating the confusing
"Target database is not up to date" error for contributors.

### TD-C06 — MkDocs version pin
Pinned `mkdocs<2.0.0` and `mkdocs-material<10.0.0` in `pyproject.toml`
to avoid unintended adoption of the breaking MkDocs 2.0 release.
Rationale added to `docs/development.md`.

### Audit finding fixes (PR #73 post-review)
- F-03: `@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])`
  on the repository vmid property test.
- F-04: `# noqa: S603` on `subprocess.run` calls with hardcoded cmd lists.
- F-05: `status=str(response.status_code)` in metrics middleware label.
- F-06: Corrected `_metrics_middleware` docstring.
- F-07: Removed dead `postgres_url` from `Settings`; removed stale
  `POSTGRES_URL`/`REDIS_URL`/`NATS_URL` from `.env.example`.

## Test counts
| Before | After |
|--------|-------|
| 338 passed | 355 passed |
| 100% coverage | 100% coverage |
