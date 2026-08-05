# ADR-003 — API Rate Limiting

- **Status:** Accepted (implemented in Sprint 003, PR #39, commit `71e72d2`)
- **Date:** 2026-07-16

## Context

No endpoint had rate limiting (audit finding RISK-03 / TD-12, Medium).
Authentication is a single static shared `X-API-Key`; without request
throttling, unbounded credential guessing was possible. The application
is single-process by design; Redis is scaffolded in `docker-compose.yml`
but not wired into the application anywhere (TD-15).

## Options

1. In-process, in-memory limiter (`slowapi` over the `limits` library),
   per-IP, configurable via settings.
2. Redis-backed limiter.
3. Delegate to a reverse proxy (documentation-only).

## Decision

Option 1. `STARCORE_RATE_LIMIT_PER_MINUTE` (default 60; `0` disables)
applied to every route via middleware `default_limits`; `/health` is
exempt (`@limiter.exempt`) so orchestration probes are never throttled.
Exceeding the limit returns `429` with `Retry-After`.

## Consequences

Limits are per-process and reset on restart — acceptable for the current
single-instance architecture. A future move to Redis is a `storage_uri`
change on the existing `Limiter`, not a redesign. Tests reset the
limiter's counters between tests (shared module-level app singleton).

## Alternatives rejected

Option 2 would bundle "activate Redis" (an unrelated architectural
decision) into a security fix; option 3 violates security-by-default for
a tool commonly exposed without a proxy.
