# Sprint 013 — Flaky Test Fix, Makefile Bug, Doc Catch-Up, ADR-008 & Runtime Environment Detection

**Date:** 2026-07-25
**Branch:** `claude/new-session-w47t28`
**Mode:** MODE 5 — CONTROLLED AUTONOMY

## Changes

### P0 — Fix flaky Hypothesis property tests
Three property tests in `tests/test_property_based_core.py` called
`get_session()` inside a `@given`-decorated function body without
suppressing Hypothesis's `function_scoped_fixture` health check — the same
pattern fixed for one test in sprint-006 (F-03) but missed for the other
three:

- `test_repository_save_and_get_run_round_trips_blueprint_fields`
- `test_repository_save_run_persists_all_task_records`
- `test_repository_list_runs_limit_returns_at_most_k_records`

Reproduced the failure on a full-suite run (`1 failed, 406 passed`), applied
`@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])` to
all three, verified stable across 3 consecutive full-suite runs afterward.

### P1 — Fix `Makefile` install/lint mismatch
`make install` ran `uv sync` (no `--extra dev`), but `ruff`, `pyright`, and
`pytest` all live in the `dev` optional-dependencies extra — so the
documented workflow `make install && make lint` would fail on a clean
checkout. Fixed `install` to `uv sync --extra dev`; added a `security`
target (`pip-audit` + Bandit) for local parity with CI.

### P2 — `docs/architecture.md`: add `packages/ai`
The architecture doc never mentioned the AI package, before or after the
provider abstraction (ADR-007). Added it to the layering diagram and a new
"AI Blueprint Generation" component description.

### P3 — `docs/development.md`: quality gates catch-up
The "Quality gates" command block only listed 5 basic gates. Added
`uv lock --check`, Bandit, a gitleaks note, and `--cov-fail-under=100` to
match the actual CI pipeline; documented the `make security` target.

### P4 — `docs/installation.md`: AI provider config + deployment environments
- Configuration reference expanded to cover both AI providers
  (`STARCORE_AI_PROVIDER`, `STARCORE_AI_BASE_URL`, `STARCORE_AI_API_KEY`),
  previously only `STARCORE_ANTHROPIC_API_KEY` was mentioned.
- New "Deployment environments" section explaining the three runtime
  contexts STARCORE detects (`proxmox-host` / `container` / `local`) and
  clarifying that client access (browser, mobile/Android, CLI) is a
  separate, client-agnostic concern from server-side environment detection.

### P5 — `docs/changelog/sprint-012.md`
Missing changelog for PR #81 (AI provider abstraction, CLAUDE.md/README
catch-up, ADR-007) — retroactively documented.

### P6 — ADR-008: CI Security Gates
`docs/adr/ADR-008-ci-security-gates.md` documents the Bandit SAST + gitleaks
+ nightly security audit stack added in PR #78 (CI-001/CI-002/AUTO-001) —
context, decision, trade-offs (Bandit `-ll` threshold rationale), and
alternatives considered (Trivy, stricter Bandit level, pre-commit-only
scanning).

### ENV-001 — Runtime environment detection
New `packages/core/environment.py`: `detect_runtime_environment()` returns
one of `"proxmox-host"`, `"container"`, or `"local"` via filesystem
heuristics (`/etc/pve/.version`, `/.dockerenv`, `/proc/1/cgroup`). Wired into:

- `run_diagnostics()` (`packages/core/diagnostics.py`) — new
  `runtime_environment` field in `GET /diagnostics` and `starcore diagnose`.
- `starcore audit` (`apps/cli/main.py`) — new "Runtime environment" table
  row / `runtime_environment` JSON field.

7 new unit tests in `tests/test_environment.py` cover all four detection
branches (Proxmox host, container via `/.dockerenv`, container via cgroup
`docker`/`kubepods` markers, and the local fallback including an unreadable
cgroup file). Documented in `docs/installation.md`'s new "Deployment
environments" section.

`mkdocs.yml` nav updated with sprint-012, sprint-013, and ADR-008.

## Test counts
| Before | After |
|--------|-------|
| 407 passed (1 intermittently flaky) | 414 passed (stable across repeated runs) |
| 100% coverage | 100% coverage |
| 0 pyright errors | 0 pyright errors |
| bandit clean | bandit clean |
