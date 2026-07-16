# Sprint 001 — Blueprint Dependency Execution & Provider Lifecycle Safety

**Date:** 2026-07-16
**Scope:** Audit findings RISK-02 / TD-01 (Critical) and RISK-01 / TD-02 (High),
per `STARCORE-Platform-Audit-Report.md` (commit `d25b76a`).
**Related ADRs:** ADR-001 (Blueprint dependency execution model),
ADR-002 (Provider lifecycle management).

This sprint contains no architectural changes beyond what ADR-001 and
ADR-002 explicitly authorize. No other subsystem was touched.

---

## Fixed

### Dependency-aware blueprint execution (RISK-02 / TD-01 — Critical)

`ExecutionPlanner.create_plan()` previously returned resources in raw
blueprint-declaration order and never consulted `depends_on`. The default,
sequential execution path (`starcore blueprint run` without `--parallel`,
and `POST /blueprints/run` with `parallel=False`) therefore silently ignored
declared dependencies, while the `--parallel` path (`Scheduler`) already
respected them — the two paths could produce different, inconsistent
results for the same blueprint.

`create_plan()` now performs a topological sort of `blueprint.resources`
(Kahn's algorithm, FIFO ready-queue seeded in declaration order) before
returning the plan, so `BlueprintExecutor` receives a dependency-safe order
without requiring any change to `BlueprintExecutor` itself.

- Unknown `depends_on` targets raise `ValueError`, matching the existing
  behavior of `create_graph()`.
- Circular dependencies raise `ValueError` naming the unresolved resources,
  instead of silently producing an incomplete or incorrect plan.
- Blueprints with no `depends_on` at all are unaffected: declaration order
  is preserved exactly.

**Files:** `packages/blueprints/planner.py`

### Provider connection lifecycle safety (RISK-01 / TD-02 — High)

`DockerProvider` and `ProxmoxProvider` stored their client
(`self._client`) as an unsynchronized instance attribute on a
singleton shared through `ProviderRegistry`. `Scheduler.execute()`
dispatches every dependency-satisfied task in a wave concurrently via
`asyncio.gather`, so two independent tasks targeting the same provider in
the same wave could call `connect()` concurrently, each reassigning
`self._client` non-deterministically.

`BaseProvider` now exposes a lazily-created, instance-scoped
`asyncio.Lock` (`_connect_lock`). Both `DockerProvider.connect()` and
`ProxmoxProvider.connect()` acquire this lock before inspecting or mutating
`self._client`: the first concurrent caller performs the real connection
work, every other concurrent caller observes the already-established
client and returns immediately without redoing the work. `disconnect()` on
both providers is guarded the same way for consistency and to remain safe
if ever invoked concurrently in the future.

This does not change `BaseProvider`'s abstract contract (still five
abstract methods, same signatures) and does not change `ProviderRegistry`,
`Scheduler`, or `BlueprintExecutor`.

**Files:** `packages/provider_sdk/base.py`, `packages/providers/docker/provider.py`,
`packages/providers/proxmox/provider.py`

---

## Tests

12 tests added, covering exactly the gaps the audit identified as missing:

- `tests/test_blueprints.py` — sequential execution respects `depends_on`
  regardless of declaration order; `create_plan()` rejects unknown and
  circular dependencies; declaration order is preserved when there are no
  dependencies.
- `tests/test_providers.py` — concurrent `connect()` calls on a shared
  `DockerProvider` / `ProxmoxProvider` instance perform the real connection
  work exactly once; connection failure is visible to all concurrent
  callers; `_connect_lock` is memoized per instance and not shared across
  instances; concurrent `disconnect()` is idempotent.
- `tests/test_scheduler.py` — end-to-end proof at the orchestrator level
  that two independent, same-provider tasks in one scheduler wave trigger
  the provider's real connection logic exactly once.

```
126 passed (114 pre-existing + 12 new), 0 failed
ruff check .     -> All checks passed
pyright          -> 0 errors, 0 warnings, 0 informations
```

## Breaking changes

None. `create_plan()`'s return type and shape are unchanged (same list of
`{provider, resource, kind, config}` dicts); only the order changes, and
only for blueprints that declare `depends_on`. `BaseProvider`'s abstract
contract is unchanged. Existing subclasses (including test fakes and any
third-party providers that do not use `_connect_lock`) continue to work
exactly as before.

## Out of scope for this sprint

Everything else identified in the audit (MkDocs configuration, `__init__.py`
consistency, dependency-vulnerability scanning, Pyright version/scope
mismatch, Makefile inconsistencies, coverage reporting, etc.) is
intentionally untouched — see the remediation roadmap for planned
follow-up sprints.
