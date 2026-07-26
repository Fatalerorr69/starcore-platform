# Sprint 023 — Property-Based Tests for Sequential Executor, Test-Matrix Corrections

**Date:** 2026-07-26
**Branch:** `claude/new-session-s52x55`
**Mode:** MODE 5 — CONTROLLED AUTONOMY

## Changes

### A — Property-based tests for `BlueprintExecutor` (sequential path)

`test_property_based.py` already had 5 property-based tests for `Scheduler` (the
concurrent path); `BlueprintExecutor` had none, despite both paths sharing the
identical `depends_on` success-gate contract (ADR-010). Added 5 tests to
`tests/test_property_based_blueprints.py`, mirroring the existing `Scheduler`
property tests:

| Test | Invariant |
|------|-----------|
| `test_executor_returns_one_task_per_resource` | Task list length always equals blueprint resource count |
| `test_executor_all_tasks_reach_terminal_status` | Every task always ends in SUCCESS, FAILED, SKIPPED, or SKIPPED_DEPENDENCY_FAILED — never PENDING/RUNNING |
| `test_executor_all_tasks_succeed_with_working_provider` | With a functional provider, all tasks always reach SUCCESS |
| `test_executor_unregistered_provider_marks_tasks_skipped` | With a provider absent from the registry, independent (no `depends_on`) tasks reach SKIPPED |
| `test_executor_dependency_failure_propagates` | A task with an unresolvable dependency reaches SKIPPED; anything depending on it reaches SKIPPED_DEPENDENCY_FAILED |

The `valid_dag_blueprint` composite strategy gained an optional `provider` parameter
so a test can pin every resource to the same provider (needed to exercise the
succeeding/unregistered-provider paths deterministically), matching the existing
`valid_dag_task_graph(provider=...)` pattern in `test_property_based.py`.

The unregistered-provider test initially reused `valid_dag_blueprint`, which can
produce dependency edges; Hypothesis found that a dependent task correctly reaches
`SKIPPED_DEPENDENCY_FAILED` rather than `SKIPPED`, falsifying the blanket
`status == SKIPPED` assertion. Fixed by testing this invariant only against a flat
(dependency-free) blueprint, isolating the specific behavior under test.

### B — Test-matrix corrections

Four rows already had property-based test coverage in `tests/test_property_based_core.py`
(18 tests across EventBus, PluginManager, Repository, and `_resolve_request_id`) that
was never reflected in `docs/test-matrix.md`. Corrected: Event bus, Plugins,
Persistence, Request correlation.

### C — Documentation update

- `docs/test-matrix.md`: "Sequential executor" row gains property-based checkmark
  and `test_property_based_blueprints.py` reference.
- `docs/changelog/sprint-023.md`: this file.
- `mkdocs.yml`: Sprint 023 nav entry.
- `CHANGELOG.md`: [Unreleased] entry.

## Test counts

| Before | After |
|--------|-------|
| 554 passed | 559 passed |
| 100% coverage | 100% coverage |
