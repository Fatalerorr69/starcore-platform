# Sprint 009 — MkDocs Nav, README Update, Sprint-008 Changelog & Planner Property Tests

**Date:** 2026-07-25
**Branch:** `claude/new-session-k19m37` → merged as PR #77
**Mode:** MODE 5 — CONTROLLED AUTONOMY

## Changes

### A01 — MkDocs nav repair and extension
`mkdocs.yml` nav was missing sprint-006, sprint-007, sprint-008 changelogs and
ADR-006 Observability. All six previously-orphaned pages are now reachable from
the site index. `mkdocs serve` / `mkdocs build` no longer silently omits them.

### B01 — README "What Works Today" table
Updated test count 114 → 361; added **Observability** row covering
`GET /metrics` (Prometheus) and `STARCORE_LOG_JSON` structured logging; updated
CLI row to include the `doctor` and `audit` commands added in sprint-006.

### C01 — `docs/changelog/sprint-008.md`
Changelog for sprint-008 (PR #76): `.env.example` `STARCORE_LOG_JSON` entry,
sprint-007 changelog created, and 6 Hypothesis property tests for
`core/metrics.py`.

### D01 — `create_plan()` topological ordering property tests
Added 5 Hypothesis property tests to `tests/test_property_based_blueprints.py`:

| Test | Invariant |
|------|-----------|
| `test_plan_length_equals_resource_count` | Plan length == number of resources |
| `test_plan_resource_name_set_equals_input_set` | Every resource appears exactly once |
| `test_plan_order_respects_depends_on` | Dependency always precedes dependant |
| `test_plan_provider_agreement_with_create_graph` | Sequential and parallel plans agree on provider assignments |
| `test_plan_contains_no_duplicate_names` | No resource appears twice |

## Test counts
| Before | After |
|--------|-------|
| 361 passed | 366 passed |
| 0 warnings | 0 warnings |
| 100% coverage | 100% coverage |
