# Sprint 003 — API Rate Limiting & Dependency Vulnerability Scanning

**Date:** 2026-07-16
**Scope:** Audit findings TD-12/RISK-03 (Security, Medium) and TD-13/RISK-05
(Security/CI, Medium), per `STARCORE-Platform-Audit-Report.md` (commit
`d25b76a`).
**Related ADRs:** ADR-003 (Rate Limiting), ADR-004 (Dependency Vulnerability
Scanning) — see design rationale below; no separate ADR files exist yet in
the repository (this is itself a pre-existing documentation gap: Sprint
001's changelog references ADR-001/ADR-002, but no ADR files exist anywhere
in the repo. Not addressed in this sprint — out of scope, noted for the
backlog).

This sprint contains no changes to `BaseProvider`, `ProviderRegistry`,
`Scheduler`, `ExecutionPlanner`, or any CLI command signature.

---

## Fixed

### TD-12 / RISK-03 — API rate limiting (Security, Medium)

No endpoint had any rate limiting — not `/`, not `/health`, and not any of
the authenticated endpoints protected by `verify_api_key()`. Combined with
a single static shared `X-API-Key` secret (constant-time-compared since
Sprint 002, but still guessable given unlimited attempts), this left the
authenticated surface open to unbounded credential-guessing.

A single, process-wide, in-memory rate limiter (`slowapi`, wrapping the
`limits` library) is now applied to every route via `SlowAPIMiddleware`'s
`default_limits`, **except** `/health`, which is explicitly exempted
(`@limiter.exempt`) so container/orchestration health probes are never
throttled by their own polling interval.

- New setting: `STARCORE_RATE_LIMIT_PER_MINUTE` (default `60`). Set to `0`
  to disable rate limiting entirely (e.g. local development, or a
  deployment an operator has already decided to expose only on a trusted
  network).
- Exceeding the limit returns `429` with a `Retry-After` header and a body
  of `{"error": "Rate limit exceeded: <limit>"}`.
- The limit is **in-memory and per-process**, read once at startup — not
  per-instance-synchronized. This is a deliberate scope decision (see
  ADR-003 rationale below), consistent with the project's current
  single-process, single-operator architecture. `redis` is already declared
  as a dependency and scaffolded in `docker-compose.yml` (TD-15) but is not
  wired into the application anywhere, including here — wiring it in only
  for rate limiting would have bundled an unrelated architectural decision
  (activating Redis) into a security bugfix. A future move to a
  Redis-backed store (if the project ever becomes genuinely multi-instance)
  is a drop-in `storage_uri` change to the existing `Limiter` construction,
  not a redesign.

**Files:** `packages/core/config.py`, `packages/core/main.py`,
`.env.example`, `pyproject.toml`, `tests/conftest.py`,
`tests/test_rate_limiting.py`

**Test-isolation note:** `core.main.app` (and therefore its `limiter`) is a
module-level singleton shared by every test file that imports it. A new
autouse fixture (`_reset_rate_limiter` in `tests/conftest.py`) resets the
limiter's in-memory counters before and after every test, for the same
reason the existing `_isolated_database`, `_api_key`, and
`_clean_event_bus` autouse fixtures exist: without it, request counts from
one test file would silently carry over into another via shared process
state, making pass/fail depend on cumulative test-suite request volume and
ordering rather than each test's own behavior. This was verified to
actually matter: the test suite's total pre-existing request count (29
`client.get`/`client.post` calls across `test_api.py`, `test_auth.py`,
`test_health.py`) was already close enough to the 60/minute default that
adding a modest number of further tests could have started producing
nondeterministic `429`s without this fixture.

### TD-13 / RISK-05 — Dependency vulnerability (CVE) scanning (Security/CI, Medium)

No dependency-vulnerability scanning tool was configured anywhere in CI;
only Dependabot version-freshness PRs existed. `pip-audit` (the official
PyPA tool) now runs as a blocking step in the `CI/quality` GitHub Actions
job, directly against the project's `uv.lock`, alongside the existing
`ruff check` / `pyright` / `pytest` steps.

**Investigated but not relied upon:** this repository already has a
"Socket Security" GitHub App integration running on every PR (visible only
in live CI check runs, not in any repository file, so the original
file-based audit could not have found it). Its `Project Report` check was
observed to always report `✅` regardless of findings and link out to an
external dashboard rather than gating the PR — i.e., even if it does
surface known-CVE information (unconfirmed; Socket's primary focus is
generally supply-chain/malicious-package risk, a related but distinct
concern from CVE-in-known-version scanning), it does not appear to satisfy
TD-13's core requirement of blocking a merge on a known vulnerability.
Separately confirmed via `gh api repos/.../vulnerability-alerts` (returns
`204 No Content`): native GitHub Dependabot **security alerts** are also
already enabled on this repository — but these are asynchronous
notifications on the repository's Security tab, not a PR check, and do not
block a merge either. This sprint proceeds with `pip-audit` regardless of
what Socket/native Dependabot alerts already cover, since none of the
three (Socket, native alerts, `pip-audit`) is redundant with the others in
the one dimension that matters for TD-13: **blocking a PR before merge**,
which only the new `pip-audit` CI step does.

**Current status (informational, not a gate on this sprint):** `pip-audit`
against the `uv.lock` produced by this sprint reports **no known
vulnerabilities**, run independently three times (twice in this sandbox,
before and after adding `slowapi`; once more by the repository owner via
`uvx pip-audit`, confirming the result outside this sandbox).

**Files:** `.github/workflows/ci.yml`, `pyproject.toml`

---

## Tests

5 tests added, all in `tests/test_rate_limiting.py`:

- the deployed default (`STARCORE_RATE_LIMIT_PER_MINUTE` unset → `60`)
  results in an *enabled* limiter (regression guard against a future
  default-value change silently disabling protection);
- exceeding a limit returns `429` with a `Retry-After` header and the
  expected error body, exercised against an isolated probe app built with
  the same wiring pattern as `core/main.py` (not by mutating the shared
  production `limiter`'s internals, which would depend on `slowapi`
  implementation details and pollute other tests' counters);
- `/health` remains reachable for 80 consecutive requests against the real
  app/limiter, proving the `@limiter.exempt` wiring actually works end to
  end, not just the underlying `slowapi` mechanism in isolation;
- `_build_rate_limit_config()` unit tests covering both the enabled
  (`60` → `["60/minute"]`, `enabled=True`) and disabled (`0` → `[]`,
  `enabled=False`) branches, without needing to reconstruct a full FastAPI
  app per configuration.

```
136 passed (131 pre-existing from Sprints 001+002 + 5 new), 0 failed
ruff format --check .   -> 61 files already formatted
ruff check .            -> All checks passed
pyright                 -> 0 errors, 0 warnings, 0 informations
pip-audit               -> No known vulnerabilities found
uv build                -> wheel built successfully
uv sync --frozen        -> succeeds against the regenerated uv.lock,
                            reproducing exactly what the Dockerfile's
                            `RUN uv sync --frozen` step does
```

## Breaking changes

None to any existing endpoint's success-path behavior. New failure mode:
any client (including legitimate ones) issuing more than
`STARCORE_RATE_LIMIT_PER_MINUTE` (default 60) requests per minute to any
single endpoint other than `/health` will now receive `429` instead of
being served. No such volume is exercised by the existing test suite or
the CI Docker smoke-test (which only calls `/health`, itself exempt).

`pyproject.toml` gained one new runtime dependency (`slowapi`) and one new
dev dependency (`pip-audit`); `uv.lock` was regenerated accordingly and
verified against `uv sync --frozen` (the exact command the Dockerfile
runs).

## Out of scope for this sprint

TD-04/TD-05 (Makefile), TD-06 (MkDocs), TD-07 (Ruff duplication), TD-08
(Pyright version/scope), TD-09/TD-10 (unused pytest-cov/mypy), TD-14
(non-root container), TD-15 (unused Redis/Postgres/NATS Compose services —
note Redis remains unused even after this sprint; see rationale above),
TD-17 (dual schema management), TD-18 (governance docs), TD-19 (dead
`Resource` model), TD-20 (unbounded `/runs`) remain untouched. Also noted
but not fixed: the missing ADR-001/ADR-002 files referenced by Sprint
001's own changelog (pre-existing documentation gap, predates this
sprint).
