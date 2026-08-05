# ADR-010 — Dependency Failure Semantics

- **Status:** Accepted (implemented in this sprint)
- **Date:** 2026-07-26

## Context

ADR-001 made `depends_on` a binding *ordering* constraint in both execution
paths: a resource's dependencies are always attempted before the resource
itself. It did not address what happens when a dependency's attempt does
not succeed. Prior to this ADR, both `BlueprintExecutor` (sequential) and
`Scheduler` (concurrent) would still call `provider.execute()` for a
resource whose declared dependency finished `FAILED` or `SKIPPED` —
`depends_on` gated *when* a resource ran, never *whether* it should run at
all. This was consistent between the two execution paths (not a divergence
bug), but was unverified by any test until a regression test was added to
document it, and was not a deliberate product decision on record anywhere.

## Problem

For a tool whose entire purpose is safe infrastructure orchestration,
silently continuing to provision resources after a declared prerequisite
failed is a real risk: a VM could be created against a network or storage
resource that never actually came up, an application container could start
against a database that never finished initializing, and so on. The
platform's own value proposition — "don't build on top of something broken"
— was not actually enforced.

## Options

1. **Skip (chosen):** a task whose `depends_on` names a task that did not
   reach `SUCCESS` is marked with a new terminal status,
   `SKIPPED_DEPENDENCY_FAILED`, and `provider.execute()` is never called
   for it. Propagates transitively: a task skipped this way blocks its own
   dependents in the same manner as a genuine failure.
2. **Configurable (`on_dependency_failure: "skip" | "continue"`):** add a
   per-blueprint or per-resource setting so operators can choose the
   old "best effort" behavior where desired.
3. **Continue (status quo):** leave `depends_on` as ordering-only, document
   the current behavior as intentional.

## Decision

Option 1. `depends_on` is now a **success gate**, not just an ordering
constraint, with no configuration knob. There is no default under which
"provision on top of a failed prerequisite" is a safe choice for this
platform's stated purpose, so this ADR does not introduce a way to opt back
into the old behavior. `TaskStatus.SKIPPED_DEPENDENCY_FAILED` is added
(distinct from `SKIPPED`, which continues to mean "provider not
registered") so operators can distinguish the two causes in CLI/API output,
persisted run history, and event-bus payloads.

Both execution paths enforce the same rule from the same information:
- `Scheduler.execute()` checks, per wave, whether every task a `ready` task
  depends on reached `TaskStatus.SUCCESS`; if not, the task is marked
  `SKIPPED_DEPENDENCY_FAILED` and events are emitted for it, but
  `provider.execute()` is never called. Because `SKIPPED_DEPENDENCY_FAILED`
  tasks are added to `completed` like any other finished task, the check
  naturally propagates across multiple waves (chains, diamonds).
- `ExecutionPlanner.create_plan()` now threads `depends_on` through its
  flat plan (previously discarded once ordering was computed), so
  `BlueprintExecutor` can track each resource's outcome by name and apply
  the identical gate before each step.

## Consequences

- A blueprint where an early resource fails will now show its dependents
  (and their transitive dependents) as `SKIPPED_DEPENDENCY_FAILED` instead
  of `SUCCESS` or silently-attempted. This is a **behavior change**: a
  blueprint run that previously "succeeded" for downstream resources
  despite an upstream failure will now correctly report those downstream
  resources as not provisioned.
- Independent resources (no path back to a failed resource) are unaffected
  and still run exactly as before.
- CLI status-color rendering (`apps/cli/main.py`) and persisted run history
  both handle the new status value like any other `TaskStatus` member — no
  schema migration needed, since `status` is a plain string column.
- Stall detection (cyclic or permanently-unresolvable dependencies) is
  unchanged: those tasks still resolve to `FAILED`, a distinct failure mode
  from a *named, resolvable* dependency that ran and did not succeed.

## Alternatives rejected

Option 2 (configurable) was rejected per this sprint's explicit direction:
adding a configuration knob to avoid making a necessary correctness
decision would have left the *default* behavior exactly as unsafe as
before for anyone who didn't discover and set the flag. Option 3 (status
quo) was rejected because it was never a deliberate decision to begin with
— it was an unverified gap, not a considered trade-off, and the
regression tests added alongside ADR-001 already anticipated this as
follow-up work (see the previous sprint's audit report, RISK-05).
