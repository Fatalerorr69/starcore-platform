# ADR-005 — Unified Database Schema Management

- **Status:** Accepted (implemented in Sprint 004, PR #40, commit `b30e09c`)
- **Date:** 2026-07-16

## Context

`init_db()` called `Base.metadata.create_all()` unconditionally on first
database access, while a separate Alembic setup existed in parallel
(audit finding RISK-09 / TD-17, Medium). Investigation showed non-Docker
deployments (CLI, bare `uv run uvicorn` — both documented paths) never
ran `alembic upgrade head` automatically at all; only the Dockerfile's
CMD did. Harmless while only migration `0001` exists (verified consistent
with ORM models), but `create_all()` never alters existing tables — a
future migration would have been silently skipped on non-Docker
databases.

## Options

1. Remove `create_all()` entirely; require explicit `alembic upgrade head`.
2. Bootstrap-and-stamp: on an untracked database (no `alembic_version`),
   run `create_all()` once and immediately `alembic stamp head`; on a
   tracked database, never call `create_all()` and fail fast
   (`RuntimeError`) if its revision doesn't match head.
3. Gate `create_all()` behind `settings.debug`.

## Decision

Option 2, implemented in `_ensure_schema_at_head()`. Shared helpers
`get_migration_head()` / `get_database_revision()` were extracted and are
reused by `diagnostics.py` (removing duplicated logic there).

## Consequences

Fresh databases keep the "it just works" Quick Start experience while
coming out Alembic-tracked; legacy `create_all()`-only databases
(including any existing `data/starcore.db`) are adopted without data loss
on next startup; out-of-date tracked databases refuse to start with an
actionable message. From the first post-`0001` migration onward,
`alembic upgrade head` is a required upgrade step for non-Docker
deployments (documented in README). Verified by four scenario tests
(fresh / legacy / at-head / stale).

## Alternatives rejected

Option 1 breaks the documented Quick Start on a fresh clone; option 3
breaks it even harder (default `debug=False` → immediate failure).
