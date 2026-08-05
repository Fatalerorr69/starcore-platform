# Sprint 024 — Test Catalog Update, ADR-010 Property-Based Tests

**Date:** 2026-07-26
**Branch:** `claude/new-session-s52x55`
**Mode:** MODE 5 — CONTROLLED AUTONOMY

## Changes

### A — Test catalog updated

`reports/starcore-tests-catalog.md` was last generated after sprint-019 (490 functions /
438 AST functions, stale by 4 sprints). Regenerated to reflect the current state:
43 test files, 558 AST test functions (pytest collects 567 — the difference is
Hypothesis and fixture-parametrised cases expanding a single function into multiple
test runs).

### B — Property-based tests for ADR-010 (Dependency Failure Semantics)

ADR-010 defines the success-gate invariant: a task whose dependency finished FAILED,
SKIPPED, or SKIPPED_DEPENDENCY_FAILED is itself marked SKIPPED_DEPENDENCY_FAILED
without ever reaching `provider.execute()`, transitively. This invariant had unit and
integration coverage but no property-based tests — now covered by
`tests/test_property_based_dependency_semantics.py` (8 new tests):

| Test | Invariant | Path |
|------|-----------|------|
| `test_scheduler_dependent_of_skipped_reaches_skipped_dependency_failed` | SKIPPED dep → dependent is SKIPPED_DEPENDENCY_FAILED | Scheduler |
| `test_scheduler_dependent_of_failed_reaches_skipped_dependency_failed` | FAILED dep → dependent is SKIPPED_DEPENDENCY_FAILED | Scheduler |
| `test_scheduler_chain_propagates_skipped_dependency_failed` | Propagates transitively through chains of any length (2–6) | Scheduler |
| `test_scheduler_independent_task_succeeds_despite_sibling_failure` | Unrelated task still reaches SUCCESS despite sibling failure | Scheduler |
| `test_scheduler_execute_never_called_for_skipped_dependency_failed` | `provider.execute()` is never called for SKIPPED_DEPENDENCY_FAILED | Scheduler |
| `test_executor_dependent_of_skipped_reaches_skipped_dependency_failed` | SKIPPED dep → dependent is SKIPPED_DEPENDENCY_FAILED | BlueprintExecutor |
| `test_executor_chain_propagates_skipped_dependency_failed` | Propagates transitively through chains of any length (2–6) | BlueprintExecutor |
| `test_executor_execute_never_called_for_skipped_dependency_failed` | `provider.execute()` is never called for SKIPPED_DEPENDENCY_FAILED | BlueprintExecutor |

Three test providers are defined locally:
- `_SucceedingProvider` — connect() returns True, execute() is a no-op
- `_FailingProvider` — connect() returns False (→ FAILED)
- `_TrackingProvider` — records every execute() call for assertion

### C — Documentation

- `docs/test-matrix.md`: "Dependency failure semantics (ADR-010)" row gains
  property-based checkmark and `test_property_based_dependency_semantics.py` reference.
- `docs/changelog/sprint-024.md`: this file.
- `mkdocs.yml`: Sprint 024 nav entry.
- `CHANGELOG.md`: [Unreleased] entry.
- `reports/starcore-tests-catalog.md`: regenerated (Bundle A).

## Test counts

| Before | After |
|--------|-------|
| 559 passed | 567 passed |
| 100% coverage | 100% coverage |
