# Sprint 004 — Unified Database Schema Management

**Date:** 2026-07-16
**Scope:** Audit finding TD-17 / RISK-09 (Maintainability, Medium), per
`STARCORE-Platform-Audit-Report.md` (commit `d25b76a`) — the last
remaining Medium-severity finding after Sprints 001–003.
**Related ADR:** ADR-005 (Unified Database Schema Management) — presented
for approval before implementation; see conversation record. As with
ADR-001–004, no standalone ADR file exists yet in the repository (pre-
existing documentation gap, not addressed in this sprint).

No changes to `BaseProvider`, `ProviderRegistry`, `Scheduler`,
`ExecutionPlanner`, CLI command signatures, rate limiting, or any API
endpoint's request/response shape.

---

## Fixed

### TD-17 / RISK-09 — Unified schema management (Maintainability, Medium)

`core/database.py`'s `init_db()` previously called
`Base.metadata.create_all(bind=_engine)` **unconditionally** on every
first database access (it is called lazily, from `get_session()`), while
a fully separate Alembic migration setup existed in parallel
(`alembic.ini`, `migrations/versions/`). Two schema-management mechanisms
were active at once, risking silent drift between ORM models and
migration history as the project grows.

**Investigation finding beyond the original audit's scope:** `init_db()`
being lazy (triggered by first DB access, not application startup) means
the CLI and a bare `uv run uvicorn core.main:app` — both explicitly
documented deployment paths (README Quick Start; the audit's own
Infrastructure Assessment notes "deployment is Docker Compose (or bare
`uv run`) only") — **never ran `alembic upgrade head` automatically at
all**. Only the Docker path did, via the `Dockerfile`'s `CMD`. This was
harmless today (only one migration, `0001`, exists, and it is fully
consistent with the current ORM models — verified directly). It would not
have stayed harmless: `create_all()` only creates missing tables, it does
not alter existing ones, so a future migration adding a column to an
already-`create_all()`-initialized non-Docker database would have been
silently skipped, surfacing later as a confusing `OperationalError` at
query time instead of a clear error at startup.

`init_db()` now brings every database under Alembic's tracking on first
contact, then relies on Alembic exclusively:

- **Untracked database** (no `alembic_version` table — either genuinely
  new, or created by the old always-`create_all()` behavior before this
  fix, including any existing `data/starcore.db`): `create_all()` runs
  exactly once more (a no-op for tables that already exist), then the
  database is stamped (`alembic stamp head`) as being at the current
  head. This preserves today's "it just works" experience for a
  brand-new database — verified by a passing test — while bringing it
  under real migration tracking from that point on.
- **Already-tracked database**: `create_all()` is never called again. If
  its recorded revision doesn't match head, `init_db()` now raises
  `RuntimeError` with an actionable message (`Run 'alembic upgrade
  head'...`) instead of silently proceeding against a potentially
  incomplete schema.

A useful side effect on the Docker path specifically: since the
`Dockerfile`'s `CMD` already runs `alembic upgrade head` before Uvicorn
starts, the database is already tracked and at head by the time
`init_db()` runs — `create_all()` now never executes on the Docker path
at all (previously it ran as a harmless no-op every time; now it doesn't
run there at all).

**Refactor, no behavior change:** `diagnostics.py::_check_migrations()`
duplicated the same "read Alembic head, read the database's current
revision" logic now needed by `init_db()`. Both now share
`get_migration_head()` and `get_database_revision(engine)` (new functions
in `core/database.py`); `_check_migrations()`'s own observable behavior
(the `CheckResult` it returns for `/diagnostics`) is unchanged.

**Files:** `packages/core/database.py`, `packages/core/diagnostics.py`,
`README.md`

---

## Tests

4 tests added, in a new `tests/test_schema_management.py`, one per
scenario identified above:

- `test_fresh_database_is_created_and_stamped_to_head` — a brand-new
  database ends up with working tables *and* a matching `alembic_version`
  (today's Quick Start experience preserved).
- `test_legacy_create_all_only_database_is_safely_adopted` — a database
  built the old way (tables via raw `create_all()`, no Alembic tracking,
  containing real data) is adopted on the next `init_db()` call without
  error and **without data loss** (a row inserted before the fix is still
  present and correct after).
- `test_database_already_at_head_is_left_untouched` — a database brought
  to head via `alembic upgrade head` directly (the exact Docker deployment
  path) is accepted as-is.
- `test_stale_database_revision_fails_fast_instead_of_drifting` — a
  database with a deliberately stale `alembic_version` row causes
  `init_db()` to raise `RuntimeError` mentioning `alembic upgrade head`,
  rather than silently continuing.

```
140 passed (136 pre-existing + 4 new), 0 failed
ruff format --check .   -> 62 files already formatted
ruff check .            -> All checks passed
pyright                 -> 0 errors, 0 warnings, 0 informations
pip-audit               -> No known vulnerabilities found
uv build                -> wheel built successfully
```

## Breaking changes

**Behavioral, not structural, and only relevant to non-Docker deployments
with more than one migration.** Today (only `migrations/versions/0001_*`
exists) there is no observable difference for any current deployment.
From the next time a second migration is added onward: a CLI or bare
`uv run uvicorn` deployment running against an existing database that
hasn't had `alembic upgrade head` applied for that new migration will now
refuse to start with a clear `RuntimeError`, instead of starting anyway
against a schema `create_all()` silently failed to update. README's
Development section now documents this. No change to the Docker deployment
path's behavior or to any test that exercises only today's single
migration.

No `BaseProvider`, `Scheduler`, `ExecutionPlanner`, CLI, or API
request/response contract changes.

## Out of scope for this sprint

All remaining findings are Low severity or governance/documentation gaps:
TD-04/TD-05 (Makefile), TD-06 (MkDocs), TD-07 (Ruff duplication), TD-08
(Pyright version/scope), TD-09/TD-10 (unused pytest-cov/mypy), TD-14
(non-root container), TD-15 (unused Redis/Postgres/NATS Compose services),
TD-18 (governance docs, including the still-missing ADR-001–005 files
themselves), TD-19 (dead `Resource` model), TD-20 (unbounded `/runs`).
With this sprint, every Critical/High/Medium finding from the original
audit is closed.
