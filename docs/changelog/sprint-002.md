# Sprint 002 — API Key Timing Safety, Real Liveness Check & Packaging Consistency

**Date:** 2026-07-16
**Scope:** Audit findings TD-11 (Low/Security), TD-16 (Medium/Operational Readiness),
TD-03 (Medium/Packaging), per `STARCORE-Platform-Audit-Report.md` (commit `d25b76a`)
and the Sprint 002 prioritization agreed after Sprint 001.

This sprint contains no architectural changes. No API contract changes beyond
the `/health` response body gaining a `database` field and a `503` status on
failure (documented as a behavior change below — not a breaking one for any
consumer that only checks `status_code == 200` and `status == "healthy"` on
success).

---

## Fixed

### TD-11 — Constant-time API key comparison (Security, Low)

`verify_api_key()` in `core/main.py` compared the `X-API-Key` header to
`settings.api_key` using Python's `!=` operator, a non-constant-time
comparison. This is a low-severity timing side-channel: an attacker with
fine-grained network-timing access could in principle infer how many
leading characters of a guess match the real key.

The comparison now uses `hmac.compare_digest()`, which always compares the
full length of both inputs regardless of where they first differ. A `None`
header (no key supplied) is short-circuited before reaching
`compare_digest()`, since that function requires both arguments to be
`str`/`bytes`.

**Files:** `packages/core/main.py`

### TD-16 — `/health` now reflects real database reachability (Operational Readiness, Medium)

`/health` previously returned an unconditional `{"status": "healthy"}` with
no dependency checks, so container/orchestration health checks relying on
it could not detect a database failure — only that the HTTP server process
itself was responding.

`/health` now calls the same `check_database_connectivity()` check used by
`/diagnostics` (extracted from the previously-private `_check_database()`,
no behavior change to that check itself) and returns:

- `200 {"status": "healthy", "database": "<detail>"}` when the database is
  reachable.
- `503 {"status": "unhealthy", "database": "<detail>"}` when it is not.

**Deliberate design decision — scope of what `/health` checks:**
`/health` intentionally checks only local, fast dependencies (the
database). It does **not** call out to external infrastructure providers
(Docker daemon, Proxmox API) the way `/diagnostics` does. `/health` is
public and unauthenticated by design, so orchestrators can probe it
without a credential; having an unauthenticated endpoint trigger slow,
externally-observable network calls to infrastructure providers on every
probe would itself be a denial-of-service and provider-abuse surface. Use
the existing, authenticated `/diagnostics` endpoint (or `starcore
diagnose`) for a full provider-inclusive deployment check — that endpoint
and its authentication model are unchanged by this sprint.

**Files:** `packages/core/diagnostics.py`, `packages/core/main.py`

### TD-03 — Explicit `__init__.py` for all declared wheel build targets (Packaging, Medium)

`packages/orchestrator`, `packages/provider_sdk`, `packages/providers`,
`packages/providers/docker`, `packages/providers/proxmox`, `apps`, and
`apps/cli` are all listed as packages in
`pyproject.toml`'s `[tool.hatch.build.targets.wheel]` (the first five
directly, `apps` because it contains `apps/cli`), and are all imported
elsewhere as regular packages (e.g. `from orchestrator.task import Task`,
`from providers.docker.provider import DockerProvider`, the `starcore =
"apps.cli.main:app"` entry point) — but relied on Python's implicit
namespace-package mechanism instead of an explicit `__init__.py`, unlike
`packages/ai`, `packages/blueprints`, `packages/core`, and every
`plugins/*` subdirectory, which already had one.

Each of the seven missing files now exists, with a short module-level
docstring matching the style already used in `packages/core/__init__.py`
and `packages/blueprints/__init__.py`. No re-exports were added (unlike
`packages/blueprints/__init__.py`'s `from .executor import
BlueprintExecutor` pattern) to avoid introducing any new eager-import
ordering — this is a pure packaging-consistency fix, not a public-API
change.

`packages/__init__.py` itself was deliberately **not** added:
`packages/` is not a wheel build target in its own right (only its
subdirectories are), and it is never imported as a package — `pytest`'s
`pythonpath = [".", "packages"]` and the equivalent runtime `PYTHONPATH`
add `packages/` directly to `sys.path`, making its subdirectories
top-level import roots. Adding `packages/__init__.py` would not be
incorrect, but it isn't required to close this finding and isn't
consistent with how the directory is actually used, so it was left as-is.

**Files:** `apps/__init__.py`, `apps/cli/__init__.py`,
`packages/orchestrator/__init__.py`, `packages/provider_sdk/__init__.py`,
`packages/providers/__init__.py`, `packages/providers/docker/__init__.py`,
`packages/providers/proxmox/__init__.py`

---

## Tests

5 tests added:

- `tests/test_auth.py` — a key of a different length is rejected; a key
  sharing a long common prefix with the real key is rejected (the specific
  guess shape a timing attack would exploit); an empty key is rejected.
- `tests/test_health.py` — `/health` includes a `database` detail field on
  success; `/health` returns `503` with `status: "unhealthy"` when the
  configured database path is unreachable (forced via a blocked directory,
  not a mock, so the real `check_database_connectivity()` path is
  exercised end-to-end).

```
131 passed (126 pre-existing + 5 new), 0 failed
ruff format --check .   -> 60 files already formatted
ruff check .            -> All checks passed
pyright                 -> 0 errors, 0 warnings, 0 informations
uv build                -> wheel built successfully; verified via
                            `zipfile -l` that all 7 previously-implicit
                            packages now ship an __init__.py
uv run starcore --help / starcore version -> entry point still resolves
                            correctly through apps.cli.main:app
```

## Breaking changes

`/health`'s response body gains a `database` field and can now return
`503` instead of always `200`. Any consumer checking only
`response.status_code == 200` and `body["status"] == "healthy"` on the
success path (as the existing test suite and the CI Docker smoke-test
both do) is unaffected. A consumer that asserted the response body was
*exactly* `{"status": "healthy"}` with no other keys would need updating —
no such consumer was found in this repository.

`verify_api_key()`'s external behavior (401 on mismatch, 503 on
unconfigured server key, 200 on match) is unchanged; only the internal
comparison mechanism changed.

No `BaseProvider`, `ProviderRegistry`, `Scheduler`, `ExecutionPlanner`, or
CLI command signatures were touched.

## Out of scope for this sprint

TD-12 (rate limiting) and TD-13 (dependency-vulnerability/CVE scanning)
were deliberately deferred to Sprint 003 — both require a tool/middleware
selection and CI configuration change substantial enough to warrant their
own ADR rather than being folded into this sprint. TD-04/TD-05 (Makefile),
TD-06 (MkDocs), TD-07 (Ruff duplication), TD-08 (Pyright version/scope),
TD-09/TD-10 (unused pytest-cov/mypy), TD-14 (non-root container), TD-15
(unused Compose services), TD-17 (dual schema management), TD-18
(governance docs), TD-19 (dead `Resource` model), TD-20 (unbounded
`/runs`) remain untouched — see the audit's Prioritized Findings for the
full remaining backlog.
