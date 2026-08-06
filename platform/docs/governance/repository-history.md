# Repository History

## Purpose

This document is a factual, chronological record of a structural event in
the repository's history — the relocation of the STARCORE Platform product
from the repository root into the `platform/` directory prefix — and its
relationship to a discrepancy discovered in `regression_baseline.json`
during the 2026-08-06 STARCORE Architecture Governance iteration.

It exists to prevent this event from being re-discovered by a future
session. It records verified facts only, distinct from unresolved
questions listed under "Remaining Uncertainties" below.

## Timeline

### v0.4.0

| Date | Commit | Description | Evidence |
|---|---|---|---|
| 2026-08-01 18:37:31 UTC | `c5044ff` | chore(release): bump version to 0.4.0, add CHANGELOG [0.4.0] section | `git log -1 c5044ff`; product resided at repository root (`git ls-tree c5044ff`); `regression_baseline.json` captured same day (`captured_at: 2026-08-01`, `commit: c5044ff`) |

### Repository Restructure

| Date | Commit | Description | Evidence |
|---|---|---|---|
| 2026-08-04 16:33:36 UTC | `e372369` | test: přidány E2E integration testy pokrývající celý request→execution→persistence stack | `git show e372369` — adds `tests/test_e2e_integration.py`, still at repository root |
| 2026-08-04 17:05:08 UTC | `97d76ad` | refactor: split core/main.py into FastAPI routers + fix type: ignore | `git show 97d76ad` — still at repository root |

### Phase 11

| Date | Commit | Description | Evidence |
|---|---|---|---|
| 2026-08-05 07:48:22 +0200 | `0af3560` | STARCORE Phase 11 Android Security Engine unified repository | `git show --stat -M 0af3560` — 126 file renames from repository-root paths to `platform/`-prefixed paths, each with zero content change; ~180 additional unrelated new files added in the same commit; `git merge-base --is-ancestor c5044ff 0af3560` confirms ancestry |

### v0.6.0

| Date | Commit | Description | Evidence |
|---|---|---|---|
| 2026-08-05 17:35:50 +0200 | `7976cad` (PR #121) | feat: Kubernetes provider, per-run SSE/WS isolation, and exec error surfacing | `git show --stat 7976cad` — adds Kubernetes provider and 7 new test files under `platform/tests/` (`test_kubernetes_provider.py`, `test_jwt_auth.py`, `test_sse.py`, `test_tracing.py`, `test_blueprint_parametrization.py`, `postgres/test_smoke.py`, plus changes to `test_events.py`, `test_plugin_manager.py`) |
| 2026-08-05 18:09:50 +0200 | `68473cd` (PR #123) | chore: release v0.6.0 | `git tag` lists `v0.6.0`; `platform/pyproject.toml` declares `version = "0.6.0"` |

## Repository Evolution

| State | Product location | Version (pyproject.toml) | ADR count | Verified via |
|---|---|---|---|---|
| At `c5044ff` (2026-08-01) | Repository root | 0.4.0 | 16 | `git ls-tree c5044ff` |
| At `0af3560` (2026-08-05) | `platform/` prefix (renamed) | 0.4.0 (unchanged by this commit) | unchanged by this commit | `git show --stat -M 0af3560` |
| At `68473cd` (2026-08-05) | `platform/` prefix | 0.6.0 | unchanged by this commit | `git tag`, `pyproject.toml` |
| Current HEAD (2026-08-06 governance iteration) | `platform/` prefix | 0.6.0 | 25 | this session's own commits |

The current authoritative boundary between `platform/` and the repository
root is established by ADR-018 (Repository Root vs. `platform/` Boundary)
and ADR-020 (Legacy Root Layer Freeze). Those ADRs define the *current*
rule; this document records *how* the repository arrived at that
structure.

## Regression Baseline Notes

### Verified Facts

- `regression_baseline.json`, as captured on 2026-08-01 (same date as
  `c5044ff`), contains two different test-count figures within the same
  file: `tests.total: 601` and `sentinel.test_count: 801`.
- This inconsistency predates the 2026-08-06 governance iteration.
- Commit `7976cad` (2026-08-05) added test files containing at least 86
  directly counted test functions (44 in `test_jwt_auth.py`, 33 in
  `test_blueprint_parametrization.py`, 9 in `test_tracing.py`, counted via
  direct `grep` of `def test_` occurrences; other new files in the same
  commit were not individually tallied).
- During the 2026-08-06 governance iteration, `sentinel.test_count` was
  updated from `801` to `805` (a delta of `+4`), based on a fresh
  `pytest --collect-only` measurement matching the current repository
  state.

### Remaining Uncertainties

- The magnitude of test code added by `7976cad` appears larger than the
  `+4` delta recorded between the 2026-08-01 baseline and the current
  measurement. Whether the original `801` figure was accurate at capture
  time could not be determined.
- The original probe run that produced `sentinel.test_count: 801` is not
  available for re-inspection.
- No commit message, PR description, or prior documentation was found
  explaining the decision to combine an unrelated large file addition
  with a full-tree rename in commit `0af3560`.

## References

- Commits: `c5044ff`, `e372369`, `97d76ad`, `0af3560`, `7976cad` (PR #121), `68473cd` (PR #123)
- `platform/.starcore/state/regression_baseline.json`
- `platform/docs/adr/ADR-018-repository-root-boundary.md`
- `platform/docs/adr/ADR-020-legacy-root-freeze.md`
