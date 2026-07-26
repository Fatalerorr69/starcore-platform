# ADR-016 — Task Timeout Integration: Deliberate Deferral

**Status:** Accepted
**Date:** 2026-07-26
**Supersedes:** —
**Superseded by:** —

## Context

PR #100 (sprint-019) introduced `orchestrator/timeout.py`, which exposes:

- `TimeoutConfig` — dataclass holding `timeout_seconds: float | None` and a
  `TimeoutStrategy` enum (`CANCEL`, `WAIT_AND_MARK`, `IGNORE`).
- `TaskTimeoutError` — exception raised when a task exceeds its configured deadline.
- `execute_with_timeout(coro, config)` — async wrapper that applies the configured
  strategy via `asyncio.wait_for`.

Neither `Scheduler._run_task()` (the parallel execution path) nor `BlueprintExecutor`
(the sequential path) currently calls `execute_with_timeout`. The module is tested
(12 unit tests, 8 property-based tests) but is dead at runtime.

## Decision

Do **not** wire `execute_with_timeout` into `Scheduler._run_task()` or
`BlueprintExecutor` at this time.

Connecting it requires per-task timeout configuration that does not yet exist:
blueprints carry no `timeout_seconds` field, `Task` has no `timeout` attribute,
and there is no universal default that would be correct across both a
"clone a Proxmox template" task (which may legitimately take minutes) and a
"start a container" task (which should take seconds). Choosing an arbitrary global
default would silently break workloads that currently succeed; requiring per-task
configuration in the blueprint schema would be a breaking change.

The module is retained because the implementation is sound, its contracts are
verified by tests, and it will be needed once per-task timeouts are introduced.

## Alternatives Considered

1. **Wire a global configurable timeout now** (`STARCORE_TASK_TIMEOUT_SECONDS`) —
   rejected. A single knob is too coarse: it must be large enough for slow Proxmox
   operations (which conceals genuinely hung tasks) or small enough to cancel fast
   operations (which breaks long-running legitimate work).

2. **Delete the module until it is needed** — rejected. The code and tests already
   exist and are correct. Deleting and re-introducing them later is pure churn with
   no safety benefit.

3. **Add an optional `timeout_seconds` field to `ResourceSpec` now** — deferred.
   This is the correct long-term shape but involves a blueprint schema change that
   warrants its own ADR and a migration story for existing blueprint files.

## Trigger Conditions

Revisit when any of the following occur:

1. A provider operation is observed hanging in production and a per-task deadline
   would have bounded the damage.
2. The blueprint schema gains a formal versioning mechanism that makes
   additive breaking changes safe to deploy.
3. A third `BaseProvider` implementation is added that has meaningfully different
   timing characteristics, making a global fallback impossible to justify.

## Consequences

- `execute_with_timeout`, `TimeoutConfig`, and `TaskTimeoutError` remain tested
  but inactive at runtime until a future ADR closes this gap.
- Blueprint authors cannot specify per-task timeouts until then.
- No existing workloads are affected.
