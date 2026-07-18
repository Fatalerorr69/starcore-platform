# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

STARCORE Platform is an infrastructure orchestration platform for homelabs/self-hosted
environments (currently Docker and Proxmox VE). Infrastructure is described declaratively
in YAML "blueprints"; STARCORE plans and executes the required provider actions, either
sequentially or — when resources declare `depends_on` — as a concurrent dependency graph.

The project is pre-alpha. `README.md`'s "What Works Today" / "What's Planned, Not Built
Yet" tables are the source of truth for feature status — check them before assuming a
capability exists. Long-term vision docs live in `docs/ses/` and describe where the
project is headed, **not** its current state.

## Commands

```bash
uv sync --extra dev              # install deps (Python 3.12+, uv-managed)
cp .env.example .env             # required before running the API or CLI against real providers

uv run ruff format --check .     # formatting check (CI)
uv run ruff format .             # auto-format
uv run ruff check .              # lint
uv run pyright                   # type check (packages/, apps/, tests/)
uv run pip-audit                 # dependency vulnerability scan (CI)
uv run pytest -q                 # full test suite
uv run pytest tests/test_blueprints.py -q            # one file
uv run pytest tests/test_blueprints.py::test_name -q # one test
uv run pre-commit run --all-files

make lint / make format / make test / make dev / make docs   # thin wrappers, see Makefile
```

`ruff.toml` is the single source of truth for lint/format config — don't add a
`[tool.ruff]` section to `pyproject.toml`. Pyright runs in `basic` mode against
`packages/`, `apps/`, `tests/`.

Run the API locally: `uv run uvicorn core.main:app --reload` (note: module path is
`core.main`, not `packages.core.main` — see "Import paths" below).

Run the CLI: `uv run starcore <command>` (entry point defined in `pyproject.toml` as
`apps.cli.main:app`), e.g. `uv run starcore blueprint plan packages/blueprints/examples/basic.yaml`.

Docker: `docker compose up -d --build api`. Postgres/Redis/NATS are defined behind the
`scaffold` compose profile for future use and are **not** wired into the application —
don't assume code paths that use them exist.

### Database migrations

Schema is managed exclusively by Alembic; `packages/core/models_db.py` and
`migrations/versions/` must stay in sync.

```bash
uv run alembic revision -m "describe the change"
# edit the generated migration, then:
uv run alembic upgrade head
uv run pytest tests/test_migrations.py tests/test_schema_management.py -q
```

A brand-new database is auto-created and stamped at head on first run (see
`_ensure_schema_at_head()` in `packages/core/database.py`). A database whose recorded
Alembic revision doesn't match the migration head causes the app to **fail fast at
startup** rather than run against a stale schema — this is intentional (ADR-005), don't
work around it by re-adding an unconditional `create_all()`.

## Architecture

Modular monolith: one deployable process, two thin delivery layers (Typer CLI, FastAPI
HTTP API) that both call into the same domain logic — never duplicate business rules
between `apps/cli/main.py` and `packages/core/main.py`.

```
apps/cli (Typer)          packages/core/main.py (FastAPI)
        \                        /
         v                      v
   packages/blueprints    packages/core (config, DB, events,
   (loader, planner,       diagnostics, discovery, plugins,
    executor, templates)   repository, resource actions)
                |
                v
      packages/orchestrator
      (Task, TaskGraph, Scheduler)
                |
                v
      packages/provider_sdk        <- the port (BaseProvider ABC,
      (base, registry, exceptions)    ProviderRegistry)
                |
                v
      packages/providers/*         <- the adapters
      (docker, proxmox)
```

### Import paths

`pyproject.toml`'s `[tool.pytest.ini_options] pythonpath` is `[".", "packages"]`, and the
Dockerfile/uvicorn invocation relies on the same layout. Code imports packages under
`packages/` by their bare name — `from core.config import get_settings`,
`from provider_sdk.registry import registry`, `from blueprints.models import Blueprint` —
never `from packages.core...`. Keep new modules consistent with this.

### Provider SDK — the extension point

`packages/provider_sdk/base.py` defines `BaseProvider`, an ABC with five async methods:
`connect`, `disconnect`, `health`, `list_resources`, `execute`. Concrete providers
(`packages/providers/docker`, `packages/providers/proxmox`) are registered **once per
process as singletons** in the global `ProviderRegistry` (`provider_sdk/registry.py`).

Because a single provider instance is shared across concurrently-dispatched tasks (the
`Scheduler` runs a whole dependency-satisfied "wave" via `asyncio.gather`), `connect()`
must be safe to call concurrently. `BaseProvider` provides a lazily-created,
instance-scoped `_connect_lock` (`asyncio.Lock`) for exactly this: acquire it before
inspecting/mutating connection state so only the first concurrent caller does the real
connect work. Both `DockerProvider` and `ProxmoxProvider` follow this pattern — follow it
too for any new provider.

### Blueprint engine — two execution paths that must agree

`packages/blueprints/planner.py`'s `ExecutionPlanner` builds **two representations** of
the same blueprint from its `ResourceSpec.depends_on` edges:

- `create_plan()` — a flat, topologically-sorted (Kahn's algorithm) list consumed by the
  sequential `BlueprintExecutor` (`blueprints/executor.py`). Declaration order is
  preserved when there are no dependencies.
- `create_graph()` — a `TaskGraph` (`packages/orchestrator/task_graph.py`) consumed by
  the concurrent `Scheduler` (`packages/orchestrator/scheduler.py`, used via `--parallel`
  / `parallel=True`), which dispatches each wave of dependency-satisfied tasks together
  via `asyncio.gather` and detects stalls (cyclic/unresolvable graphs) instead of hanging.

Both paths must never disagree about dependency order — this is a standing invariant
(see ADR-001 / `docs/adr/ADR-001-blueprint-dependency-execution.md`), so a change to one
path's dependency handling generally needs a matching change (and test) for the other.
Unknown or circular `depends_on` references raise `ValueError` in both paths rather than
producing a silently-wrong plan.

Blueprints can reference Proxmox templates by name (`config: {template: "ubuntu-24.04"}`)
instead of a raw `template_vmid`; `blueprints/template_resolver.py` resolves this against
`ProxmoxProvider.list_templates()` before planning/execution, raising
`TemplateResolutionError` on missing/ambiguous names.

### Core

- **Config** (`core/config.py`): Pydantic Settings, `STARCORE_*` env prefix, loaded from
  `.env`. Add new settings here, not scattered `os.environ` reads; update `.env.example`
  in the same change.
- **Events** (`core/events.py`): a minimal in-process async pub/sub `EventBus`. Both
  `BlueprintExecutor` and `Scheduler` emit `task.started`, `task.completed`, and
  `run.completed`; plugins subscribe via `context.events.subscribe(...)`.
- **Plugin manager** (`core/plugin_manager.py`): discovers subdirectories of `plugins/`
  containing `__init__.py`, imports them as `plugins.<name>`, and calls their
  `register(context)` function, where `context` exposes `.registry` (to add custom
  providers) and `.events` (to subscribe to the event bus). See `plugins/example_provider`
  and `plugins/run_logger` for the two supported patterns.
- **Repository / persistence** (`core/repository.py`, `core/models_db.py`): SQLite via
  SQLAlchemy, storing blueprint run + per-task history (`BlueprintRunRecord`,
  `TaskRunRecord`).
- **Diagnostics / discovery** (`core/diagnostics.py`, `core/discovery.py`): deep,
  authenticated health/audit checks (DB, migration status, Docker/Proxmox provider
  connectivity, node capacity, orphaned-resource detection) — distinct from the public,
  unauthenticated `/health`, which deliberately checks only local fast dependencies (the
  database) and never calls out to external providers.

### Security model

A single static shared secret (`STARCORE_API_KEY`) via the `X-API-Key` header protects
every endpoint except `/`, `/health`, and static `/ui` assets. Comparison uses
`hmac.compare_digest` (constant-time) — never replace this with `==`. The API fails
closed: if no key is configured, protected endpoints return 503 rather than opening up.
This is a single-operator homelab security model, not multi-tenant authorization —
don't over-engineer around it (e.g. adding per-user auth) without being asked.

Per-IP rate limiting (`slowapi`) applies process-wide via `STARCORE_RATE_LIMIT_PER_MINUTE`
(0 disables it); `/health` is explicitly exempt so orchestrator liveness probes aren't
throttled by their own polling interval.

### AI blueprint generation

`packages/ai/generator.py` calls the Anthropic API (`STARCORE_ANTHROPIC_API_KEY`,
`STARCORE_ANTHROPIC_MODEL`) with a fixed system prompt describing the blueprint YAML
schema, and strips markdown code fences from the response. Exposed via
`starcore ai generate` and `POST /ai/generate-blueprint`. Raises
`BlueprintGenerationError` (not a raw exception) when the key is missing or the API call
fails — both CLI and API layers handle that type specifically.

## Testing conventions

`tests/conftest.py` defines autouse fixtures that isolate every test — read it before
writing tests that touch settings, the database, the event bus, or rate limiting:

- `_no_dotenv_file` disables `Settings`' `.env` loading entirely (not just clearing env
  vars), so tests never accidentally pick up a real deployment's `.env` — this matters
  because a populated `.env` with real Proxmox credentials would make live network calls
  during "missing credentials" tests otherwise.
- `_isolated_database` gives every test a fresh temp-file SQLite DB via `init_db()`.
- `_api_key` injects a fixed test `STARCORE_API_KEY`.
- `_clean_event_bus` / `_reset_rate_limiter` clear the module-level singleton `EventBus`
  and the `slowapi` `Limiter`'s in-memory counters between tests (both are shared
  process-wide state via `core.main`, so cross-test leakage is otherwise possible).

## Contribution workflow

- Branch from `main` (direct pushes to `main` are blocked); one concern per PR.
- A significant change set adds a `docs/changelog/sprint-NNN.md` entry; architectural
  decisions get an ADR in `docs/adr/` (see existing ADRs for the format: Status, Context,
  Options, Decision, Consequences, Alternatives rejected).
- If a PR changes the feature surface, update the README's "What Works Today" table —
  keep it honest.
- New behavior needs new tests; bug fixes need a regression test that fails without the fix.
