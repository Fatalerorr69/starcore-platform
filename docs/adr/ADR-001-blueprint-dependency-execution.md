# ADR-001 — Blueprint Dependency Execution Model

- **Status:** Accepted (implemented in Sprint 001, PR #37, commit `b3b7dce`)
- **Date:** 2026-07-16

## Context

Blueprints declare per-resource `depends_on` edges. Two execution paths
existed: the sequential `BlueprintExecutor` (default) and the concurrent
`Scheduler` (`--parallel`). Only the concurrent path honored `depends_on`;
`ExecutionPlanner.create_plan()` returned resources in raw file-declaration
order (audit finding RISK-02 / TD-01, Critical).

## Problem

The default execution mode of a dependency-aware orchestration tool
silently ignored declared dependencies — the two paths could produce
different results for the same blueprint.

## Options

1. Topologically sort inside `create_plan()` (Kahn's algorithm, FIFO
   ready-queue seeded in declaration order).
2. Make the sequential executor consume the `TaskGraph` and run it with
   concurrency of 1.
3. Deprecate sequential execution entirely.

## Decision

Option 1. `create_plan()` sorts topologically before returning; unknown
and circular dependencies raise `ValueError`. Blueprints without
`depends_on` keep their exact declaration order (backward compatible).
`BlueprintExecutor` itself is unchanged.

## Consequences

Both paths now treat `depends_on` as a binding constraint. Plan shape and
return type are unchanged; only ordering changes, and only for blueprints
that declare dependencies.

## Alternatives rejected

Option 2 would have coupled the sequential path to orchestrator
internals; option 3 would have removed a documented, working feature.
