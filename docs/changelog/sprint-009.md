# Sprint 009 — MkDocs Nav, README Update, Sprint-008 Changelog & Planner Property Tests

**Date:** 2026-07-25
**Branch:** `claude/starcore-discovery-audit-ojgwdo` → merged as PR #77
**Mode:** MODE 5 — CONTROLLED AUTONOMY

## Changes

### A01 — `mkdocs.yml` nav completed

Sprint-006, sprint-007, sprint-008 changelog entries and ADR-006 Observability
were added to the MkDocs nav. All documentation files are now reachable from
the site index.

### B01 — README "What Works Today" test count

Updated test count from 114 → 361 to reflect actual suite size. Added
Observability row (`GET /metrics`, `STARCORE_LOG_JSON`) and updated CLI row to
include `doctor`/`audit` commands.

### C01 — `docs/changelog/sprint-008.md`

Created the missing changelog for sprint-008 (PR #76), covering `.env.example`
`STARCORE_LOG_JSON` addition, sprint-007 changelog, and metrics property tests.

### C02 — `create_plan()` topological ordering property tests

Five new Hypothesis tests added to `tests/test_property_based_blueprints.py`:

| Test | Invariant |
|------|-----------|
| `test_plan_length_equals_resource_count` | Plan length == number of resources |
| `test_plan_contains_all_resource_names` | All resource names appear in plan |
| `test_plan_respects_dependency_ordering` | Every dependency precedes its dependent |
| `test_plan_with_no_dependencies_any_order` | Any order valid when no deps declared |
| `test_plan_is_deterministic` | Same blueprint always produces same plan |

### D01 — Pre-commit `pyright` hook fixed

Replaced the `pyright-python` remote hook (which runs in an isolated
environment and cannot resolve project packages, producing ~296 false-positive
errors) with a local hook using `uv run pyright`. This aligns pre-commit with
the CI gate and the documented `uv run pyright` developer workflow.

### D02 — README test count updated to 366

Corrected README "What Works Today" table from 361 → 366 to match the
verified test suite output.

## Test counts

| Before | After |
|--------|-------|
| 361 passed | 366 passed |
| 0 warnings | 0 warnings |
| 100% coverage | 100% coverage |
