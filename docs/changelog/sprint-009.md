# Sprint 009 — MkDocs Nav, README Update, Sprint-008 Changelog & Planner Property Tests

**Date:** 2026-07-25
**Branch:** `claude/starcore-discovery-audit-ai5otv` → merged as PR #77
**Mode:** MODE 5 — CONTROLLED AUTONOMY

## Changes

### A01 — `mkdocs.yml` nav updated
Added missing entries so all docs files are reachable from the MkDocs site index:

- `changelog/sprint-006.md`, `changelog/sprint-007.md`, `changelog/sprint-008.md`
- `adr/ADR-006-observability.md`

Previously, sprints 006–008 and ADR-006 were present on disk but absent from the
`nav:` block, making them unreachable via the generated site.

### B01 — README "What Works Today" table
Updated the feature table to reflect the current state of the repository:

| Field | Before | After |
|-------|--------|-------|
| Test count | 114 | 361 |
| CLI row | `plan` / `run` / `health` | added `doctor` / `audit` commands |
| Observability | absent | `GET /metrics`, `STARCORE_LOG_JSON` |

### C01 — `docs/changelog/sprint-008.md`
Created the missing changelog for sprint-008 (PR #76), documenting:
- `STARCORE_LOG_JSON` added to `.env.example`
- Sprint-007 changelog backfill
- 6 Hypothesis property tests for `core/metrics.py`

### D01 — `create_plan()` topological ordering property tests
Added 5 Hypothesis tests to `tests/test_property_based_blueprints.py`:

| Test | Invariant |
|------|-----------|
| `test_create_plan_length_equals_resource_count` | Plan length == number of resources in blueprint |
| `test_create_plan_contains_all_resource_names` | Resource name set in plan == resource name set in blueprint |
| `test_create_plan_respects_dependency_order` | For every `depends_on` edge, dependency appears before dependent in plan |
| `test_create_plan_agrees_with_create_graph` | Sequential plan and parallel graph contain the same resource set |
| `test_create_plan_contains_no_duplicates` | No resource appears twice in the output plan |

## Test counts
| Before | After |
|--------|-------|
| 361 passed | 366 passed |
| 0 warnings | 0 warnings |
| 100% coverage | 100% coverage |
