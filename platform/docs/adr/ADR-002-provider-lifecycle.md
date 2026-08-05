# ADR-002 — Provider Connection Lifecycle Management

- **Status:** Accepted (implemented in Sprint 001, PR #37, commit `b3b7dce`)
- **Date:** 2026-07-16

## Context

Providers are process-wide singletons shared via `ProviderRegistry`.
`Scheduler.execute()` dispatches every dependency-satisfied task in a
wave concurrently via `asyncio.gather`, and each task calls
`provider.connect()`. Both providers stored their client in an unguarded
`self._client` attribute (audit finding RISK-01 / TD-02, High): two
same-provider tasks in one wave raced to reassign it.

## Problem

Make singleton providers safe under concurrent `connect()`/`disconnect()`
without changing the `BaseProvider` abstract contract or the Scheduler.

## Options

1. Instance-scoped `asyncio.Lock` on `BaseProvider` (lazily created so
   subclasses need not call `super().__init__()`); providers guard their
   connection state with it — first caller connects, others observe the
   established client.
2. Per-task provider instances (no sharing).
3. Locking inside the Scheduler.

## Decision

Option 1 (`BaseProvider._connect_lock`). The five abstract methods are
unchanged; existing subclasses that ignore the lock keep working.

## Consequences

Connection work happens exactly once per provider instance per
connected-period, regardless of wave width. `disconnect()` is guarded
identically for symmetry.

## Alternatives rejected

Option 2 would multiply authenticated sessions (notably against Proxmox)
and contradict the registry design; option 3 would leak provider
implementation concerns into the orchestrator layer.
