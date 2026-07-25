# Sprint 007 — Ruff PERF/N/FAST Rules, Test Warning Filter & ADR-006

**Date:** 2026-07-25
**Branch:** `claude/new-session-d94909` → merged as PR #75
**Mode:** MODE 5 — CONTROLLED AUTONOMY

## Changes

### A01 — Enable PERF, N, FAST ruff rule sets
Added `PERF`, `N`, and `FAST` to `lint.select` in `ruff.toml` and fixed all
resulting findings.

- `packages/core/plugin_manager.py` — `discover()` append-loop replaced with
  a list comprehension (PERF401).
- `packages/provider_sdk/exceptions.py` — `ResourceNotFound` renamed to
  `ResourceNotFoundError` (N818 — exception names must end in `Error`);
  `tests/test_exceptions.py` updated accordingly.
- `packages/core/main.py` — `get_runs()` query parameters converted from
  `param: int = Query(...)` to `Annotated[int, Query(...)]` pattern (FAST002);
  `Annotated` imported from `typing`.
- `packages/providers/proxmox/provider.py` — PERF401 added to per-file-ignores:
  the nested async loops there are network-bound; flattening would harm
  readability without measurable gain.

### B01 — Suppress StarletteDeprecationWarning in pytest
Added `filterwarnings` entry to `[tool.pytest.ini_options]` in `pyproject.toml`:

```toml
filterwarnings = [
    "ignore:Using `httpx` with `starlette.testclient`",
]
```

Silences the `httpx`/`starlette.testclient` deprecation noise. Test output is
now 355 passed with zero warnings.

### C01 — ADR-006 Observability
Created `docs/adr/ADR-006-observability.md` documenting the architectural
decisions made in sprint-006 for the Prometheus `/metrics` endpoint and the
loguru-based structured logging (`STARCORE_LOG_JSON`).

Key decisions recorded:
- Dedicated `CollectorRegistry` to avoid duplicate timeseries across test
  processes.
- `X-API-Key` auth on `/metrics` consistent with all other non-public
  endpoints.
- `STARCORE_LOG_JSON` env var for toggling JSON output; configured at startup
  in both `core/main.py` and `apps/cli/main.py`.
- OpenTelemetry deferred until a tracing backend is chosen.

## Test counts
| Before | After |
|--------|-------|
| 355 passed, 1 warning | 355 passed, 0 warnings |
| 100% coverage | 100% coverage |
