# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

STARCORE Platform is an AI-powered infrastructure orchestration platform for homelabs. It lets you describe infrastructure declaratively in YAML "blueprints" and executes the required provider actions against **Proxmox VE** and **Docker**, sequentially or in parallel based on declared `depends_on` edges.

The package manager is **uv**. Python 3.12 is required.

## Commands

```bash
# Install dependencies (including dev tools)
uv sync --extra dev

# Run the API server (with auto-reload)
make dev               # uv run uvicorn core.main:app --reload

# Lint / format
uv run ruff check .
uv run ruff format .

# Type check
uv run pyright

# Run all tests
uv run pytest -q

# Run a single test file
uv run pytest tests/test_blueprints.py -q

# Run a single test by name
uv run pytest tests/test_blueprints.py::test_function_name -q

# Run tests with coverage
uv run pytest -q --cov --cov-report=term-missing

# Dependency vulnerability scan (required by CI)
uv run pip-audit

# All pre-commit hooks
uv run pre-commit run --all-files

# Database migrations (only needed when new migrations are added)
uv run alembic upgrade head
uv run alembic revision -m "describe the change"

# CLI
uv run starcore blueprint plan <path.yaml>
uv run starcore blueprint run <path.yaml>
uv run starcore blueprint run <path.yaml> --parallel
uv run starcore health
uv run starcore diagnose
uv run starcore proxmox discover
uv run starcore ai generate "<description>"
uv run starcore snapshot create|list|delete|rollback
uv run starcore resource action <provider> <action> <resource>
```

## Architecture

STARCORE is a **modular monolith**: one deployable process with two delivery layers (CLI and HTTP API) that both call into the same domain packages. Business logic is never duplicated between them.

```
apps/cli (Typer)           packages/core/main.py (FastAPI)
        \                          /
         v                        v
   packages/blueprints      packages/core
   packages/orchestrator
         |
         v
   packages/provider_sdk    ← port (BaseProvider ABC, ProviderRegistry)
         |
         v
   packages/providers/*     ← adapters (docker, proxmox)
```

### Package roles

**`packages/provider_sdk`** — The stable contract every infrastructure provider must implement: five async methods (`connect`, `disconnect`, `health`, `list_resources`, `execute`). Providers are registered as singletons in a global `ProviderRegistry`. `BaseProvider` supplies a lazily-created `_connect_lock` (an `asyncio.Lock`) so concurrent `connect()` calls from a scheduler wave execute the real connection work exactly once.

**`packages/blueprints`** — Loads YAML blueprints into Pydantic models, resolves Proxmox template aliases (friendly name → `template_vmid`), and produces execution plans. `ExecutionPlanner.create_plan()` returns a flat topologically-sorted list for the sequential executor; `create_plan()` / `create_graph()` both honor `depends_on` as a binding constraint — unknown or circular dependencies raise `ValueError`, never produce a silently wrong order.

**`packages/orchestrator`** — Executes already-prepared `TaskGraph` plans. `Scheduler` runs dependency-satisfied tasks concurrently in "waves" via `asyncio.gather` and detects stalls (unresolvable graphs) instead of hanging.

**`packages/core`** — FastAPI app, `pydantic-settings`-based config (all env vars prefixed `STARCORE_`), SQLite persistence via SQLAlchemy + Alembic, an in-process `EventBus`, `PluginManager`, deep diagnostics, and API-wide per-IP rate limiting via `slowapi` (`/health` is exempt).

**`packages/ai`** — Calls the Anthropic API to translate natural language into a blueprint YAML. Requires `STARCORE_ANTHROPIC_API_KEY`.

**`packages/providers/docker`** and **`packages/providers/proxmox`** — Concrete `BaseProvider` implementations using `docker-py` and `proxmoxer` respectively.

### Execution paths

- **Sequential**: `BlueprintExecutor.execute(blueprint)` — iterates the topologically-sorted plan steps one at a time.
- **Parallel**: `Scheduler.execute(graph)` — dispatches all dependency-satisfied tasks of a wave concurrently, then advances to the next wave.

Both paths must produce identical dependency orderings. The sequential and parallel paths are separate code paths sharing the same `ExecutionPlanner` logic.

### API security

A single static shared API key (`X-API-Key` header, constant-time comparison via `hmac.compare_digest`) protects all endpoints except `/`, `/health`, and static UI assets. The API returns 503 if no key is configured — it fails closed. The `/health` endpoint is intentionally unauthenticated and checks only the database; full provider health lives behind auth at `/diagnostics`.

### Schema management

`init_db()` in `packages/core/database.py` enforces one of two outcomes:
- **Fresh database** (no `alembic_version` table): `create_all()` runs once and the database is stamped at the current head.
- **Existing database**: startup fails immediately if the recorded revision doesn't match the migration head. Run `uv run alembic upgrade head` to resolve.

Never run `create_all()` outside `init_db()`. ORM models live in `packages/core/models_db.py` and must be kept in sync with `migrations/versions/`.

### Plugin system

Plugins are directories in `plugins/<name>/` with an `__init__.py` that exports a `register(context)` function. `context.registry` is the global `ProviderRegistry` (to add custom providers); `context.events` is the global `EventBus` (to subscribe to `task.started`, `task.completed`, `run.completed` events). See `plugins/example_provider/` and `plugins/run_logger/` for reference implementations.

### Configuration

All settings are read from environment variables with the `STARCORE_` prefix (or a `.env` file, which is gitignored). The `Settings` object is a singleton behind `get_settings()` (LRU-cached). Tests must call `get_settings.cache_clear()` around any `monkeypatch.setenv`/`delenv` calls — `conftest.py` already handles this globally.

Key variables: `STARCORE_API_KEY`, `STARCORE_DATABASE_URL` (default: `sqlite:///./data/starcore.db`), `STARCORE_PROXMOX_*`, `STARCORE_ANTHROPIC_API_KEY`, `STARCORE_RATE_LIMIT_PER_MINUTE` (0 disables rate limiting).

## Test Isolation

`tests/conftest.py` applies four autouse fixtures to every test:
1. `_no_dotenv_file` — prevents any real `.env` file from leaking into tests (critical when a populated `.env` sits in the repo root).
2. `_isolated_database` — creates a fresh SQLite DB in `tmp_path` for each test.
3. `_api_key` — sets `STARCORE_API_KEY=test-api-key` via `monkeypatch`.
4. `_reset_rate_limiter` — clears the process-wide `slowapi` limiter's in-memory counters between tests.

When writing tests that hit the FastAPI app, use `httpx.AsyncClient` with `app=app` and include `X-API-Key: test-api-key` in headers.

## Linting and Type Checking

- **Ruff** (`ruff.toml`): line length 100, Python 3.12, rules `E`, `F`, `I` (isort), `UP`. Single source of truth for lint/format config.
- **Pyright** (`pyrightconfig.json`): `basic` mode, checks `packages/`, `apps/`, `tests/`. The `packages/` directory is on `pythonpath` (see `pyproject.toml`), so imports like `from core.config import ...` are valid without package-relative paths.

## CI Gates (all must pass)

```
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pip-audit
uv run pytest -q
```

CI also builds the Docker image and smoke-tests `GET /health`.
