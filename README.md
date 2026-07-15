# STARCORE Platform

**AI-Powered Infrastructure Operating Platform**

![Version](https://img.shields.io/badge/version-0.1.0--dev-blue)
![License](https://img.shields.io/badge/license-Apache--2.0-green)
![Status](https://img.shields.io/badge/status-active--development-orange)

---

## Overview

STARCORE Platform is an infrastructure orchestration platform for homelabs and self-hosted environments, currently focused on **Proxmox VE** and **Docker**.

It lets you describe infrastructure declaratively in YAML "blueprints" and have STARCORE plan and execute the required provider actions, sequentially or, when resources declare dependencies, in parallel.

This README reflects the **actual current state of the codebase**, not the long-term vision. The long-term vision is documented separately in `docs/ses/`.

---

## What Works Today

| Component | Status | Description |
|---|---|---|
| Provider SDK | Done | BaseProvider interface, registry, exceptions |
| API Authentication | Done | X-API-Key header required on all endpoints except / and /health; returns 503 if server has no key configured |
| Docker Provider | Done | Real implementation via docker-py: connect, health, list, create/start/stop/remove containers |
| Proxmox Provider | Done | Real implementation via proxmoxer: connect, health, list, start/stop/shutdown VMs and LXC containers, clone VM or LXC from template |
| Blueprint Engine | Done | Load YAML, plan, execute. Sequential (BlueprintExecutor) or parallel graph execution (Scheduler + TaskGraph) via depends_on |
| CLI | Done | starcore blueprint plan/run [--parallel], starcore version, starcore health |
| Core API | Done | FastAPI: providers, blueprint plan/run, run history |
| Persistence | Done | SQLite (via SQLAlchemy) stores blueprint run history and task results |
| Config | Done | .env-based settings via pydantic-settings |
| Tests | 91 passing | ruff, pyright, pytest, pre-commit, CI on every PR |

## What's Planned, Not Built Yet

| Component | Status | Notes |
|---|---|---|
| Alembic Migrations | Done | migrations/ tracks schema via `alembic upgrade head`; create_all() still runs on app start for dev convenience |
| Plugin System | Done | Plugins in plugins/<name>/ expose register(context) to add custom providers (context.registry) and subscribe to blueprint execution events (context.events); discoverable via 'starcore plugins' and GET /plugins |
| Diagnostics | Done | `starcore diagnose` CLI and `GET /diagnostics` API report config, database, migrations, and Docker/Proxmox provider health including node CPU/RAM/disk, storage, and orphaned resource detection |
| Web Dashboard | Done (read-only) | Static HTML/JS at GET /ui, calls the existing API (providers, runs, diagnostics) via fetch() with an X-API-Key stored in localStorage. No build step |
| Proxmox Environment Discovery | Done | 'starcore proxmox discover' and GET /proxmox/discover catalog node capacity, storage, available VM/LXC templates, and network bridges, used to tailor deployments before they run |
| AI Blueprint Generation | Done (requires API key) | 'starcore ai generate "<description>"' and POST /ai/generate-blueprint use Anthropic's API to translate natural language into a validated blueprint YAML. Requires STARCORE_ANTHROPIC_API_KEY |
| Installer Studio | Vision | Not started |
| Dashboard (Web UI) | Vision | Not started |
| AI Brain | Vision | Not started |
| Marketplace | Vision | Not started |

---

## Quick Start

```bash
uv sync --extra dev
cp .env.example .env
uv run starcore blueprint plan packages/blueprints/examples/basic.yaml
uv run starcore blueprint run packages/blueprints/examples/basic.yaml
```

Run the API:

```bash
uv run uvicorn core.main:app --reload
```

## Example Blueprint

```yaml
name: demo
resources:
  - name: db
    provider: docker
    kind: container
    config:
      image: postgres:17
  - name: web-vm
    provider: proxmox
    kind: vm
    config:
      node: fatalab
      template_vmid: 9000
    depends_on:
      - db
```

Run it in parallel-aware mode: `starcore blueprint run <path> --parallel`

---

## Repository Structure

```
apps/cli/              CLI entry point (Typer)
packages/core/          FastAPI app, config, database, persistence models
packages/blueprints/    Blueprint models, loader, planner, executor
packages/orchestrator/  Task, TaskGraph, Scheduler
packages/provider_sdk/  BaseProvider, registry, exceptions
packages/providers/     Docker and Proxmox implementations
tests/                  pytest test suite
docs/ses/               Long-term engineering specification and vision docs
```

---

## Docker Deployment

```bash
cp .env.example .env
docker compose up -d --build api
```

The `api` service builds this repo, runs Alembic migrations, and starts the FastAPI server on port 8000. SQLite data persists in the `starcore-data` volume. Postgres, Redis, and NATS services are also defined in `docker-compose.yml` for future use but are not yet wired into the application.

---

## Development

```bash
uv sync --extra dev
uv run ruff check .
uv run pyright
uv run pytest -q
uv run pre-commit run --all-files
```

CI runs the same checks on every pull request.

---

## Documentation

Long-term vision and engineering specifications live in `docs/ses/`. They describe where the project is headed, not its current state. See the tables above for that.

## License

Apache License 2.0

## Project Owner

GitHub: Fatalerorr69
