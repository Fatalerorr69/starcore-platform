# Sprint 018 — Request Correlation IDs, Rollback Dry-Run Diff, ADR-013, Docker Compose Fix

**Date:** 2026-07-26
**Branch:** `claude/p2-observability-hardening` (merged PR #93) + `main` (PR #94)
**Mode:** MODE 5 — CONTROLLED AUTONOMY

## Changes

### Request correlation IDs
Every HTTP response now carries `X-Request-ID` — accepted from the caller
if present and well-formed, generated otherwise — bound to every log line
emitted while handling that request via `logger.contextualize()` and echoed
back in the response header. Documented in `docs/api.md#request-correlation`
and `docs/architecture.md`.

### Snapshot rollback dry-run diff
`starcore snapshot rollback` now shows a dry-run diff of what will change
before prompting for confirmation (unless `--yes` is passed), matching the
existing confirmation pattern for `snapshot delete`.

### ADR-013 — Provider Concurrency Policy (No Rate Limit, For Now)
Documents a deliberate "do not add a concurrency limit yet" decision after
code-level analysis of both `ProxmoxProvider` (proxmoxer's `requests.Session`
subclass, token-auth path, no per-request session-state mutation) and
`DockerProvider` (docker-py's `APIClient`, same shape) found no
shared-mutable-state hazard in either provider's `execute()` path for
STARCORE's actual configuration. Real load-testing under a large concurrent
wave was explicitly not performed (no environment available this cycle) and
is called out as a known gap. Three concrete trigger conditions are defined
for revisiting the decision (a wave routinely exceeding ~10-20 concurrent
tasks against one provider instance, operator-reported slowness/errors
correlated with `--parallel` runs, or a future provider with a documented
hard API rate limit).

### README cleanup
Fixed a misleading "Planned, Not Built Yet" section — several listed items
were already implemented. Replaced with "Production Limitations" (the
actual security-relevant caveats: no per-user identity/RBAC, plugins not
sandboxed, provider calls within a `--parallel` wave not rate-limited — see
ADR-011/012/013) and a much shorter "Roadmap / Vision" section for what
genuinely doesn't exist yet.

### Docker Compose scaffold variable fix (PR #94)
Compose interpolates every service's environment block unconditionally at
parse time, even for a profile that isn't active. The postgres service's
`POSTGRES_PASSWORD: ${STARCORE_POSTGRES_PASSWORD:?...}` made bare
`docker compose config` — and even the documented non-scaffold workflow,
`docker compose up -d --build api` — fail on a missing
`STARCORE_POSTGRES_PASSWORD` despite never touching the postgres service.
Switched to `${STARCORE_POSTGRES_PASSWORD:-}` (default to empty); the
official postgres image already refuses to start with an empty
`POSTGRES_PASSWORD`, so enabling the scaffold profile without setting the
variable still fails loudly, just at container startup instead of at
compose-file parse time.

## Test counts
| Before | After |
|--------|-------|
| 470 passed | 493 passed |
| 100% coverage | 100% coverage |
