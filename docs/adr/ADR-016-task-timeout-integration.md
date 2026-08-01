# ADR-016 — Task Timeout Integration

**Status:** Implemented
**Date:** 2026-07-26
**Implemented:** 2026-08-01
**Supersedes:** —
**Superseded by:** —

## Context

PR #100 (sprint-019) introduced `orchestrator/timeout.py`, which exposes:

- `TimeoutConfig` — dataclass holding `timeout_seconds: float | None` and a
  `TimeoutStrategy` enum (`CANCEL`, `WAIT_AND_MARK`, `IGNORE`).
- `TaskTimeoutError` — exception raised when a task exceeds its configured deadline.
- `execute_with_timeout(coro, config)` — async wrapper that applies the configured
  strategy via `asyncio.wait_for`.

ADR-016 (original) deliberately deferred wiring this module into the executors,
pending a per-task configuration mechanism in the blueprint schema.

## Decision (2026-08-01 — implemented)

Add `timeout_seconds: float | None = None` to `ResourceSpec` (blueprint model) and
`Task` (orchestrator model), then wire `execute_with_timeout` into both execution paths:

- `BlueprintExecutor.execute()` — sequential path
- `Scheduler._run_task()` — parallel path

When `timeout_seconds` is `None` (the default), `execute_with_timeout` short-circuits
immediately (`TimeoutConfig.is_enabled()` returns `False`) — no behavioral change for
existing blueprints. When set, the default strategy is `CANCEL`: the task is cancelled
and marked `FAILED` if `provider.execute()` does not return within the deadline.
`TaskTimeoutError` is caught before the broad `except Exception` handler so it produces
a clean WARNING log instead of a full traceback.

Do **not** add a global `STARCORE_TASK_TIMEOUT_SECONDS` environment variable — this
ADR explicitly rejected it as too coarse for mixed workloads (slow Proxmox clone vs.
fast container start). Per-task `timeout_seconds` in the blueprint YAML is the
correct granularity.

## Blueprint schema

```yaml
resources:
  - name: web-vm
    provider: proxmox
    kind: vm
    timeout_seconds: 300   # optional; null / omitted = no timeout
    config:
      template: debian-12
```

## Alternatives Considered (original deferral, 2026-07-26)

1. **Wire a global configurable timeout now** (`STARCORE_TASK_TIMEOUT_SECONDS`) —
   rejected. A single knob is too coarse.

2. **Delete the module until it is needed** — rejected. The code and tests already
   existed and were correct.

3. **Add an optional `timeout_seconds` field to `ResourceSpec` now** — deferred
   until it could be done with a proper ADR and migration story. That point is now.

## Consequences

- Blueprint authors can set `timeout_seconds` per resource; omitting it preserves
  previous behavior exactly.
- A timed-out task is marked `FAILED`, which causes any dependent resources to be
  marked `SKIPPED_DEPENDENCY_FAILED` via the existing `depends_on` success-gate logic.
- `TimeoutStrategy.WAIT_AND_MARK` and `TimeoutStrategy.IGNORE` remain available via
  `TimeoutConfig` directly but are not yet exposed in the blueprint schema — `CANCEL`
  is the only strategy applied at the executor level today. This can be extended with
  a per-resource `timeout_strategy` field if the need arises.

> **Defect fixed (2026-07-27):** The original implementation re-awaited the coroutine
> object after `asyncio.wait_for` had already cancelled it, raising
> `RuntimeError: cannot reuse already awaited coroutine`. The fix wraps the coroutine
> in `asyncio.create_task` and protects it with `asyncio.shield` so the inner task
> keeps running after the first deadline fires.
