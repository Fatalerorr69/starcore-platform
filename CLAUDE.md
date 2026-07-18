# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

STARCORE Platform is an infrastructure orchestration platform for homelabs/self-hosted
environments (currently Proxmox VE and Docker). Infrastructure is declared in YAML
"blueprints"; STARCORE plans and executes the required provider actions, either
sequentially or, when resources declare `depends_on`, concurrently.

The project is pre-alpha and moves quickly. `README.md`'s "What Works Today" /
"What's Planned" tables are the source of truth for feature status — check them before
assuming a feature exists. `docs/ses/` holds the long-term vision (not the current state).

## Commands

```bash
uv sync --extra dev              # install (project uses uv, not pip/poetry)
uv run ruff format --check .     # formatting check
uv run ruff check .              # lint
uv run pyright                   # type check (packages/, apps/, tests/, Python 3.12)
uv run pip-audit                 # dependency vulnerability scan
uv run pytest -q                 # full test suite
uv run pytest -q tests/test_blueprints.py::test_name   # single test
uv run pre-commit run --all-files
```

`make lint` / `make format` / `make test` wrap the ruff/pytest commands. CI (`.github/workflows/ci.yml`)
runs ruff check, pyright, pip-audit, and pytest with coverage on every PR, plus a Docker
build + `/health` smoke test. Run the full quality gate above before considering a change
done — this is what the CI `quality` job and the PR review gate both check.

Ruff config lives in `ruff.toml` (line-length 100, py312, `E`/`F`/`I`/`UP`) — do not add a
`[tool.ruff]` section to `pyproject.toml`.

Running the app:

```bash
uv run starcore blueprint plan <file.yaml>
uv run starcore blueprint run <file.yaml> [--parallel]
uv run uvicorn core.main:app --reload      # note: module path is core.main, not packages.core.main
docker compose up -d --build api           # Dockerfile + compose; SQLite persists in a named volume
```

`packages/` is on `pythonpath` (see `pyproject.toml`'s `[tool.pytest.ini_options]` and
`pyrightconfig.json`), so internal imports are rooted at each package directly
(`from core.config import ...`, `from blueprints.executor import ...`, `from
provider_sdk.registry import ...`), not `packages.core...`.

**Database schema:** managed by Alembic (`migrations/versions/`). A brand-new database is
created and stamped to head automatically on `init_db()` (see "Schema management" below).
After pulling a change that adds a migration, run `uv run alembic upgrade head` — the app
refuses to start against a schema that doesn't match the expected head.

## Architecture

### Package layout and dependency direction

```
apps/cli/              Typer CLI (starcore command) — thin wrapper over packages/*
packages/core/          FastAPI app, settings, database/schema, persistence, plugin manager,
                         diagnostics, environment discovery, resource-action dispatch
packages/blueprints/    Blueprint (Pydantic) models, YAML loader, planner, two executors,
                         Proxmox template-name resolver
packages/orchestrator/  Task, TaskGraph, Scheduler — provider-agnostic execution primitives
packages/provider_sdk/  BaseProvider ABC, ProviderRegistry, exceptions — the plugin contract
packages/providers/     Docker and Proxmox provider implementations
packages/ai/            Anthropic-backed natural-language -> blueprint YAML generator
plugins/<name>/         External providers/event-subscribers, discovered by convention
tests/                  pytest suite, one file roughly per module above
migrations/             Alembic revisions
docs/adr/               Accepted architecture decisions (numbered, read before changing
                         provider lifecycle, execution ordering, schema management, etc.)
docs/changelog/         Per-sprint changelog entries
docs/ses/               Long-term vision/spec, NOT current state
```

Both `apps/cli/main.py` and `packages/core/main.py` (the FastAPI app) call into the same
`packages/blueprints`, `packages/orchestrator`, and `packages/core/*` functions — the CLI is
not a separate implementation, it's a second entry point over identical logic. When you
change orchestration/persistence behavior, both entry points need to stay in sync (there is
no shared "service layer" beyond the functions themselves).

### Blueprint execution: two parallel paths, one dependency contract

`ExecutionPlanner` (`packages/blueprints/planner.py`) builds two different representations
of the same `Blueprint`, both honoring every resource's `depends_on`:

- `create_plan()` → flat, topologically-sorted list of steps, consumed by
  `BlueprintExecutor` (`packages/blueprints/executor.py`), which runs steps strictly
  sequentially. This is the default (`starcore blueprint run <file>`).
- `create_graph()` → an `orchestrator.task_graph.TaskGraph`, consumed by
  `orchestrator.scheduler.Scheduler` (`--parallel` flag), which dispatches every
  dependency-satisfied task in a wave concurrently via `asyncio.gather` and advances wave
  by wave until all tasks complete or the graph stalls (unresolved/cyclic deps → remaining
  tasks marked FAILED).

Both paths emit the same `task.started` / `task.completed` / `run.completed` events via
`core.events.event_bus`, and both persist through the same `core.repository.save_run`. See
ADR-001 for why this dual-path/single-dependency-contract design exists — a past bug had the
sequential path silently ignore `depends_on`.

### Providers: singleton registry + concurrency-safe connect

`provider_sdk.registry.registry` is a single process-wide `ProviderRegistry`; each
concrete provider (`DockerProvider`, `ProxmoxProvider`) is registered once as a long-lived
singleton via `register_default_providers()`. Because the Scheduler fires a whole wave of
same-provider tasks concurrently, `BaseProvider.connect()` **must** be safe to call
concurrently — subclasses guard their client-creation with the inherited
`self._connect_lock` (an `asyncio.Lock` created lazily per-instance) so only the first
concurrent caller actually connects. See ADR-002 before touching provider connect/disconnect
logic. Adding a new built-in provider means implementing `BaseProvider`'s five abstract
methods (`connect`, `disconnect`, `health`, `list_resources`, `execute`) and registering it
in `provider_sdk/registry.py::register_default_providers`.

### Plugins

`plugins/<name>/__init__.py` with a `register(context)` function is auto-discovered by
`core.plugin_manager.PluginManager` (`starcore plugins`, `GET /plugins`). `context.registry`
lets a plugin register additional `BaseProvider`s at runtime; `context.events` lets it
subscribe to the same `task.started`/`task.completed`/`run.completed` events blueprint
execution emits. See `plugins/example_provider` and `plugins/run_logger` for the two
patterns.

### Config, database, schema management

- All configuration is `pydantic-settings` (`core.config.Settings`), env-prefixed
  `STARCORE_*`, loaded from `.env` (see `.env.example` for the full list — keep it updated
  when adding a setting). `get_settings()` is `lru_cache`d; tests must call
  `get_settings.cache_clear()` after monkeypatching env vars (see `tests/conftest.py`).
- `core.database.init_db()` is the single schema entry point (ADR-005): on a database with
  no `alembic_version` table, it runs `Base.metadata.create_all()` once and stamps it to
  Alembic head (fresh-DB convenience); on a database already under Alembic tracking, it
  raises immediately if the recorded revision isn't head — startup fails fast rather than
  running against a stale schema. Never add a second, parallel schema-management path;
  new tables/columns go through `uv run alembic revision` and must match
  `packages/core/models_db.py`.
- SQLite is the only wired-up datastore. Postgres/Redis/NATS appear in
  `docker-compose.yml` (opt-in via `--profile scaffold`) and in `Settings`, but are not used
  by any code path yet — don't assume they're reachable.

### API surface (`packages/core/main.py`)

Single FastAPI app. Every route except `/`, `/health`, and the static `/ui` assets requires
`X-API-Key` (via `verify_api_key`, constant-time compare against `settings.api_key`; 503 if
no key is configured server-side). A single process-wide `slowapi` `Limiter` rate-limits all
routes except `/health` (`STARCORE_RATE_LIMIT_PER_MINUTE`, 0 disables it — see ADR-003).
`/health` deliberately checks only the local database, never providers, since it's public and
unauthenticated (see the docstring in `main.py` for the reasoning before changing it).
`/ui` is a static, no-build-step HTML/JS dashboard reading the same API via `fetch()` with an
API key from `localStorage`.

### Diagnostics vs. discovery

Two distinct read-only reports, easy to confuse: `core.diagnostics.run_diagnostics()`
(`starcore diagnose`, `GET /diagnostics`) answers "is everything healthy?" (config, DB,
migrations, provider connectivity, and — for Proxmox — orphaned resources: things that exist
on the host but aren't in STARCORE's run history). `core.discovery.discover_proxmox_environment()`
(`starcore proxmox discover`, `GET /proxmox/discover`) answers "what can I deploy into?"
(node capacity, storage, templates, network bridges).

### AI blueprint generation

`packages/ai/generator.py` calls the Anthropic API (`STARCORE_ANTHROPIC_API_KEY`,
default model `claude-sonnet-5` via `STARCORE_ANTHROPIC_MODEL`) with a fixed system prompt
describing the blueprint YAML schema, then strips markdown code fences from the response.
Output is still run through the normal `BlueprintLoader`/Pydantic validation before use —
treat generated YAML as untrusted input, same as any user-supplied blueprint.

## Conventions

- **Tests are part of the change.** New behavior needs a test; bug fixes need a regression
  test that fails without the fix. `tests/` mirrors `packages/`+`apps/` roughly 1:1 by module.
- **Type hints everywhere**; pyright runs in `basic` mode over `packages/`, `apps/`, `tests/`.
- Schema changes always go through `uv run alembic revision`; keep `models_db.py` and
  migrations in sync (startup fails fast on drift, by design — see ADR-005).
- No secrets in code, tests, or logs; configuration goes through `Settings`
  (`STARCORE_*` env vars), with `.env.example` updated in the same PR as any new setting.
- A significant change should add a `docs/changelog/sprint-NNN.md` entry; a decision with
  real trade-offs (provider lifecycle, execution ordering, rate limiting, schema management,
  etc.) gets an ADR in `docs/adr/` — read the existing ones before revisiting those areas.
- Keep README's "What Works Today" table honest if a PR changes the feature surface.
- Direct pushes to `main` are blocked; work on a focused feature branch, one concern per PR.
