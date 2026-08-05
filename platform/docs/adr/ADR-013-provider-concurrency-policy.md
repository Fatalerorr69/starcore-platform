# ADR-013 — Provider Concurrency Policy (No Rate Limit, For Now)

- **Status:** Accepted — decision is "do not add a concurrency limit yet",
  not "a limit exists"
- **Date:** 2026-07-26

## Context

ADR-002 established `_connect_lock`, an `asyncio.Lock` guarding
`connect()` so a shared provider instance's connection setup runs at most
once per process even when multiple tasks in the same `Scheduler` wave
target it concurrently. That lock's scope is deliberately narrow: it
covers `connect()` only, not `execute()`. This means once a provider is
connected, `Scheduler.execute()` can dispatch many `execute()` calls
against the same shared `DockerProvider`/`ProxmoxProvider` instance
concurrently, via `asyncio.gather()`, with no coordination between them.

This ADR asks the question the runbook raised directly: does that need a
limit?

## What was actually checked (not assumed)

- **`ProxmoxProvider`**: `proxmoxer`'s HTTPS backend
  (`proxmoxer/backends/https.py`) defines `ProxmoxHttpSession`, which
  subclasses `requests.Session`. For our specific configuration (API
  token auth via `STARCORE_PROXMOX_TOKEN_NAME`/`_TOKEN_VALUE`, not
  username/password session-cookie auth), `ProxmoxHttpSession.request()`
  reads `self.auth`/`self.cookies` but does not need to mutate them
  per-request for the token-auth path — the token is a fixed header sent
  with every request, not session state renegotiated per call. Each
  `self._client.*.get()/.post()` call in `packages/providers/proxmox/provider.py`
  is wrapped in `asyncio.to_thread()`, so concurrent `execute()` calls
  issue concurrent blocking requests from a thread pool against this
  session.
- **`DockerProvider`**: `docker-py`'s `APIClient`
  (`docker/api/client.py`) also subclasses `requests.Session` directly.
  Same shape: concurrent `execute()` calls issue concurrent blocking
  requests via `asyncio.to_thread()`.
- **`requests.Session`** is documented and widely relied upon (by both
  libraries here) as safe for issuing concurrent requests from multiple
  threads — its connection pool (via `urllib3`) is the part that needs
  thread-safety, and that's exactly what it's designed for. What is *not*
  safe, in general, is concurrently *mutating* session-level state
  (headers, auth, cookies) while requests are in flight — and neither
  provider's `execute()` path does that for our configuration (verified
  above for Proxmox; `docker-py`'s `APIClient` similarly sets its auth/TLS
  config once at client construction, not per-call).

## What was not independently verified

- Real load-testing of either provider under a large concurrent wave (10s
  or 100s of simultaneous tasks against the same provider) was not
  performed — no environment with a real Proxmox cluster or a Docker
  daemon under meaningful load was available to this cycle.
- Proxmox's and Docker's own API rate limits / request-handling capacity
  under concurrent load from a single client were not measured. A
  resource-constrained homelab Proxmox node (the platform's actual target
  deployment) could plausibly be slower to respond under many concurrent
  API calls than a well-provisioned cluster, independent of any
  client-side thread-safety question.

## Decision

**Do not add a per-provider concurrency limit now.** No concrete evidence
of a problem exists: no bug report, no flaky test, no operator complaint,
and the code-level analysis above found no shared-mutable-state hazard in
either provider's request path for STARCORE's actual auth configuration.
Adding a bounded `asyncio.Semaphore` (or similar) without a demonstrated
need would be exactly the kind of speculative infrastructure this
project's own operating principles argue against.

**Concrete trigger conditions to revisit this decision:**

1. A blueprint or use case emerges where a single wave routinely dispatches
   more than roughly 10–20 concurrent tasks against the *same* provider
   instance (today's typical homelab blueprint — a handful of VMs/
   containers — is nowhere near this).
2. An operator reports Proxmox or Docker daemon slowness/errors correlated
   with `--parallel` blueprint runs.
3. A future provider (a third `BaseProvider` implementation) has a
   documented, hard API rate limit (many cloud provider APIs do) that
   would be violated by unbounded concurrent calls.

If any of these occurs, the fix is a bounded `asyncio.Semaphore` acquired
around the `provider.execute(task)` call in `Scheduler._run_task`, sized
via a new per-provider setting (e.g. `STARCORE_PROXMOX_MAX_CONCURRENT`),
analogous to how `_connect_lock` is already scoped per-provider-instance.
This ADR's job is to make that a deliberate future decision with a stated
trigger, not to guess at a number now.

## Alternatives rejected

- **Add a semaphore now, sized arbitrarily** (e.g., "5 concurrent calls"):
  rejected — an arbitrary limit imposed without evidence risks throttling
  real use cases that would have worked fine, in exchange for protection
  against a problem that hasn't been observed.
- **Widen `_connect_lock`'s scope to cover `execute()` too**: rejected —
  this would serialize all execution against a provider, defeating the
  entire purpose of the concurrent `Scheduler` (ADR-001) for any blueprint
  using more than one resource per provider. The lock is correctly scoped
  to the narrow problem it solves (connection setup happening more than
  once), and should stay that way.
