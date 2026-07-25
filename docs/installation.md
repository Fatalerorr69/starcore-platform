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
60, `0` disables) and AI-assisted blueprint generation, which supports
two providers via `STARCORE_AI_PROVIDER`:

- `anthropic` (default) — `STARCORE_ANTHROPIC_API_KEY`, `STARCORE_ANTHROPIC_MODEL`
- `openai-compatible` — any `/v1/chat/completions` server (Ollama, LM
  Studio, vLLM, LocalAI, OpenAI itself): `STARCORE_AI_BASE_URL`, optional
  `STARCORE_AI_API_KEY`

## Deployment environments

STARCORE can run in three distinct contexts, and `starcore audit` / `starcore
doctor` / `starcore diagnose` / `GET /diagnostics` all report which one they
detect (`runtime_environment`: `proxmox-host`, `container`, or `local`) so
you don't have to infer it from symptoms:

- **Proxmox host** — the STARCORE process itself runs directly on a Proxmox
  VE node (uncommon, but possible for a minimal single-box homelab). Detected
  via the presence of `/etc/pve/.version`.
- **Container** — the documented Docker/Docker Compose deployment (see
  below). Covers both a container on your local machine and one on a cloud
  VPS.
- **Local** — a bare process on a developer workstation, e.g. running via
  `uv run uvicorn core.main:app --reload` outside of any container. This is
  also the fallback for any environment that matches neither of the above.

In every case, the Proxmox/Docker *targets* STARCORE orchestrates
(`STARCORE_PROXMOX_*`) are configured independently of where STARCORE itself
runs — you can run STARCORE locally on your laptop and have it manage VMs on
a remote Proxmox cluster, or run it in a container on that same cluster.

### Distinguishing "local PC" from "cloud"

`starcore audit`/`doctor` (documented as instant, local-only commands) add an
`os_platform` field — OS family, release, and whether it's WSL (Windows
Subsystem for Linux, common for a Windows development workstation) — entirely
from local, offline checks.

`GET /diagnostics` / `starcore diagnose` go one step further with
`environment_details.cloud_provider`: a bounded-timeout (250ms per provider)
probe of the AWS/GCP/Azure link-local metadata endpoints, which only respond
when actually running on that provider's infrastructure. This is what
distinguishes "container on a cloud VPS" from "container on your local
machine" — a distinction `runtime_environment` alone cannot make. It's
deliberately *not* run from `audit`/`doctor`, which are documented as
instant and local-only; `diagnose`/`/diagnostics` already make comparable
network calls to Docker/Proxmox and are the appropriate place for it. A
homelab machine or Proxmox node simply gets `cloud_provider: null` — the
probes fail fast rather than hang, since these addresses are normally
unreachable outside their respective clouds.

### Client access

`GET /diagnostics` also reports `client.platform` — a best-effort
classification (`browser-desktop`, `browser-mobile`, `cli-or-script`, or
`unknown`) of whoever is *currently calling* the API, derived from the
request's `User-Agent` header. This is what tells you a given request came
from, say, a mobile browser (including Android) rather than a desktop one or
a script — a per-request concern, not a server property.

Otherwise, client access is client-agnostic by design: the REST API and CLI
work identically regardless of caller. `GET /ui` (the static web dashboard)
works from any modern browser, including one on a phone or tablet, on the
same network — it stores the `X-API-Key` in `localStorage` and requires no
native app.
