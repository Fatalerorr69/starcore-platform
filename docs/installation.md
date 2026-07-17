# Installation

## Requirements

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/) (dependency management and virtualenv)
- Optional: Docker (for containerized deployment), a Docker daemon and/or
  a Proxmox VE cluster to actually orchestrate

## Local installation

```bash
git clone https://github.com/Fatalerorr69/starcore-platform.git
cd starcore-platform
uv sync --extra dev
cp .env.example .env
```

Edit `.env` and set at minimum `STARCORE_API_KEY` (the API refuses to
serve protected endpoints until it is set). For Proxmox features, fill in
the `STARCORE_PROXMOX_*` variables (API token, see Datacenter →
Permissions → API Tokens in the Proxmox UI).

Try the CLI:

```bash
uv run starcore blueprint plan packages/blueprints/examples/basic.yaml
uv run starcore blueprint run packages/blueprints/examples/basic.yaml
uv run starcore diagnose
```

Run the API:

```bash
uv run uvicorn core.main:app --reload
```

A brand-new database is created and brought under Alembic tracking
automatically on first run. If you later upgrade an existing installation
and a new migration has been added, run `uv run alembic upgrade head`
before starting — the application refuses to start against an out-of-date
schema rather than run against it silently.

## Docker deployment

```bash
cp .env.example .env   # set STARCORE_API_KEY at minimum
docker compose up --build
```

The `api` service applies migrations (`alembic upgrade head`) on startup,
persists its SQLite database in the `starcore-data` volume, exposes port
8000, and runs as a non-root user.

The `postgres`, `redis`, and `nats` services in `docker-compose.yml` are
scaffolding for planned features and are **not** started by default; opt
in with `docker compose --profile scaffold up` (requires
`STARCORE_POSTGRES_PASSWORD` in `.env`).

## Configuration reference

All settings are environment variables with the `STARCORE_` prefix, read
from `.env`. See `.env.example` for the complete annotated list,
including `STARCORE_RATE_LIMIT_PER_MINUTE` (API rate limiting, default
60, `0` disables) and `STARCORE_ANTHROPIC_API_KEY` (AI-assisted blueprint
generation).
