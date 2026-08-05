# Architecture

STARCORE Platform is a **modular monolith**: a single deployable process
with strictly separated internal packages. Two thin delivery layers (a
Typer CLI and a FastAPI HTTP API) call into the same domain logic — no
business rules are duplicated between them.

## Layering

```
apps/cli (Typer)          packages/core/main.py (FastAPI)
        \                        /
         v                      v
   packages/blueprints    packages/core (config, DB, events,
   (loader, planner,       diagnostics, discovery, plugins,
    executor, templates)   repository, resource actions)
                |                |
                v                v
      packages/orchestrator    packages/ai (AIProvider ABC,
      (Task, TaskGraph,         Anthropic / OpenAI-compatible)
       Scheduler)
                |
                v
      packages/provider_sdk        <- the port (BaseProvider ABC,
      (base, registry, exceptions)    ProviderRegistry)
                |
                v
      packages/providers/*         <- the adapters
      (docker, proxmox)
```

## Key components

**Provider SDK** (`packages/provider_sdk`) — the stable contract every
infrastructure provider implements: five async methods (`connect`,
`disconnect`, `health`, `list_resources`, `execute`). Providers are
registered once per process as singletons in `ProviderRegistry`.
`BaseProvider` supplies a lazily-created, instance-scoped `asyncio.Lock`
(`_connect_lock`) so concurrent `connect()` calls from tasks in the same
scheduler wave perform the real connection work exactly once.

**Blueprint Engine** (`packages/blueprints`) — loads YAML blueprints into
Pydantic models, resolves Proxmox template aliases, and plans execution.
`ExecutionPlanner.create_plan()` returns a flat, **topologically sorted**
list (every `depends_on` edge is honored) for the sequential executor;
`create_graph()` returns a `TaskGraph` for the concurrent scheduler. Both
paths treat declared dependencies as a binding constraint; unknown or
circular dependencies raise `ValueError` instead of producing an
incorrect plan.

**Orchestrator** (`packages/orchestrator`) — executes already-prepared
plans only. The `Scheduler` runs dependency-satisfied tasks in concurrent
"waves" via `asyncio.gather` and detects stalls (cyclic/unresolvable
graphs) instead of hanging.

**Core** (`packages/core`) — FastAPI app, Pydantic Settings configuration
(`STARCORE_*` env vars), SQLite persistence with Alembic-tracked schema
(fresh databases are bootstrapped and stamped automatically; databases
behind the migration head fail fast at startup), an in-process event bus,
a plugin manager (`plugins/` directory, `register(context)` convention —
see [Plugins](plugins.md) for the discovery/import/trust model, which is
**not sandboxed**),
deep diagnostics (`/diagnostics`, `starcore diagnose`), API-wide per-IP
rate limiting (`slowapi`, `/health` exempt), Prometheus metrics
(`/metrics`, `core/metrics.py` — HTTP request count/latency via
middleware, blueprint task outcomes via an event-bus subscription), and
structured logging (`core/logger.py`; set `STARCORE_LOG_JSON=true` for
one JSON object per log line, suited for log aggregators). Every HTTP
request is assigned a correlation ID (`X-Request-ID` — accepted from the
caller if present and well-formed, generated otherwise), bound to every
log line emitted while handling that request via `logger.contextualize()`
and echoed back in the response header; see [API Reference](api.md#request-correlation).

**Environment Detection** (`packages/core/environment.py`, ADR-009) — four
independent checks answering "where and how is this actually running?",
surfaced via `starcore audit`/`doctor`/`diagnose` and `GET /diagnostics`:
`detect_runtime_environment()` (`proxmox-host`/`container`/`local`, fast,
local-only filesystem heuristics), `detect_os_platform()` (OS family,
release, WSL detection, fast, local-only), `detect_cloud_provider()`
(bounded-timeout AWS/GCP/Azure metadata probe — the one check that makes
network calls, so it's wired only into the already-network-calling
`run_diagnostics()`, never into the instant `audit`/`doctor` commands), and
`classify_client_platform()` (User-Agent-based classification of whichever
client is calling `GET /diagnostics` right now — a per-request concern,
not a server property).

**AI Blueprint Generation** (`packages/ai`) — translates a natural-language
description into a blueprint YAML via a pluggable `AIProvider` abstract base
(`packages/ai/base.py`, ADR-007). `STARCORE_AI_PROVIDER` selects the
implementation at runtime: `anthropic` (default, wraps the Anthropic Messages
API) or `openai-compatible` (any `/v1/chat/completions` server — Ollama, LM
Studio, vLLM, LocalAI, OpenAI itself). `packages/ai/generator.py`'s
`_build_provider()` factory is the only place that knows about concrete
provider classes; callers (CLI, `POST /ai/generate-blueprint`) depend only on
the stable `generate_blueprint_yaml()` function.

**Security model** — a single static shared API key (`X-API-Key` header,
compared in constant time) protects all endpoints except `/`, `/health`,
and static UI assets. The API fails closed (503) if no key is configured.
Appropriate for a single-operator homelab deployment; not a multi-tenant
authorization system.

## Design decisions of note

- Sequential and parallel execution paths must never disagree about
  dependency order (Sprint 001).
- Schema management is unified under Alembic; `create_all()` runs at most
  once, on first contact with an untracked database, immediately followed
  by `alembic stamp head` (Sprint 004).
- `/health` checks local dependencies only (database); the authenticated
  `/diagnostics` endpoint performs the full provider-inclusive check —
  an unauthenticated endpoint must not trigger outbound provider calls
  (Sprint 002).
