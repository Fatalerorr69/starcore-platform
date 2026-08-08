# SPOS-020 IMPLEMENTATION REPORT

Standard: SPOS-020 | Datum: 2026-08-08 | Status: DOKONCENO | Commit: 87a0ede

---

## SCOPE

Milestone 4: Code Quality from CONSOLIDATION_ROADMAP.md — deduplicate _persist_run(), remove unused psutil dependency.

## DISCOVERY FINDINGS

### TD-008: _persist_run() duplication

- `packages/core/routers/blueprints.py:177` — identical definition
- `packages/core/routers/ws.py:202` — identical definition
- Both: `get_session()` + `save_run()` + `session.close()` wrapper
- Same imports from `core.database` and `core.repository`
- No direct test coverage (tested indirectly via endpoint tests)
- Used in 3 call sites: blueprints run, blueprints SSE stream, ws execution

### TD-009: psutil dependency

- Listed in `pyproject.toml:23` as `psutil>=7.0.0`
- Zero imports anywhere in codebase (packages/, apps/, tests/, scripts/)
- No transitive dependents in uv.lock
- Not referenced in CI, Docker, or Makefile
- Safe to remove

## IMPLEMENTED CHANGES

### M4.1: _persist_run() deduplicated

**Approach:** Moved canonical implementation to `packages/core/repository.py` as `persist_run()` (public function, alongside existing `save_run()`).

**Changes:**
- `packages/core/repository.py` — added `persist_run()` with `Blueprint` import
- `packages/core/routers/blueprints.py` — removed local `_persist_run()`, updated 3 call sites to `persist_run()`, removed unused `get_session`/`save_run` imports
- `packages/core/routers/ws.py` — removed local `_persist_run()`, updated 1 call site to `persist_run()`, removed unused `get_session`/`save_run` imports

**Behavior preservation:** Identical logic, same error handling, same session lifecycle, same return type.

### M4.2: psutil removed

- Removed `"psutil>=7.0.0"` from `pyproject.toml` dependencies
- Regenerated `uv.lock` — psutil cleanly removed
- `uv sync --extra dev` confirmed clean install without psutil

## QC RESULTS

| Check | Result |
|---|---|
| pytest | 796 passed, 9 skipped (baseline match) |
| ruff check | All checks passed |
| pyright | 0 errors, 0 warnings |
| bandit | All checks passed |
| pip-audit | Clean (starcore-platform skip expected) |
| mkdocs --strict | Build OK |

## TECHNICAL DEBT RESOLUTION

| ID | Description | Status |
|---|---|---|
| TD-008 | _persist_run() duplication | RESOLVED |
| TD-009 | psutil unused dependency | RESOLVED |
| TD-010 | platform/reports/ stale | OPEN (out of scope) |

## METRICS

| Metric | Before | After |
|---|---|---|
| Code duplicates | 1 | 0 |
| Direct dependencies | 21 | 20 |
| Tech debt items | 3 | 1 |
| Repo hygiene | 88% | 90% |
| Consolidation progress | M1+M2+M3 | M1+M2+M3+M4 (100%) |
