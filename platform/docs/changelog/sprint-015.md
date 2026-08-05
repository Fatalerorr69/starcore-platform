# Sprint 015 — Fix `starcore health` Stub, `scripts/doctor.py` Parity, ADR-009, Property Tests

**Date:** 2026-07-25
**Branch:** `claude/new-session-r91v56`
**Mode:** MODE 5 — CONTROLLED AUTONOMY

## Changes

### P0 — Fix `starcore health` stub
`starcore health` unconditionally printed `"System OK"` with zero actual
checking — the test asserting this behavior confirmed it was doing no work
at all, unlike `GET /health` (API), which genuinely checks database
connectivity. An operator running it as a smoke test would get a false "OK"
even with an unreachable database.

Fixed to call `check_database_connectivity()` (the same check `GET /health`
uses) and report real status: `"System OK (<detail>)"` on success, exit 0;
`"System UNHEALTHY: <detail>"` on failure, exit 1.

### P1 — `scripts/doctor.py` gate parity + scripts documentation
The standalone `scripts/doctor.py` (sprint-006) had drifted from
`starcore doctor` (CLI, sprint-010): it was missing the Bandit SAST gate.
Added it, matching the CLI version's gate list exactly.

`docs/development.md` gained a new "Standalone scripts" section documenting
both `scripts/doctor.py` and `scripts/health.py` — neither was referenced in
any documentation before, despite `scripts/health.py` serving a genuinely
distinct purpose (HTTP health probe of a *running remote* instance) from
`starcore health` (local process's own database check, no HTTP).

### P2 — `docs/architecture.md`: add environment detection
The architecture doc had zero mention of `packages/core/environment.py`
despite it growing to four functions wired into two CLI commands and one API
endpoint across sprint-013/014. Added an "Environment Detection" entry to
the Key Components section.

### P3 — ADR-009: Environment Detection
`docs/adr/ADR-009-environment-detection.md` documents the four-check design
from sprint-013/014: the cost/wiring table (which check goes where and why),
the fast/local vs. deep/networked split rationale, `detect_cloud_provider()`'s
never-raises design, and alternatives considered (a single "get everything"
function, IMDSv2-only AWS detection).

### P4 — Property-based tests for `environment.py`
New `tests/test_property_based_environment.py` — 6 Hypothesis tests:

| Test | Invariant |
|------|-----------|
| `classify_client_platform` never raises, always returns a known bucket | for any string or `None` |
| `classify_client_platform` is case-insensitive | upper/lower/mixed give the same result |
| Any User-Agent containing a mobile marker → `browser-mobile` | for arbitrary prefix/suffix noise |
| Any User-Agent containing a script marker (no mobile marker) → `cli-or-script` | for arbitrary prefix/suffix noise |
| `detect_os_platform`'s `is_wsl` matches `/proc/version` content exactly | for arbitrary content + injected "microsoft" |
| `detect_os_platform` always returns exactly `{system, release, is_wsl}` | for any system/release combination |

## Test counts
| Before | After |
|--------|-------|
| 442 passed | 449 passed |
| 100% coverage | 100% coverage |
| 0 pyright errors | 0 pyright errors |
| bandit clean | bandit clean |
