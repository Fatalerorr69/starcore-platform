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
make dev               # uv run uvicorn core.main:app --reload --port 8000

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

# Run tests with coverage (100% required)
uv run pytest -q --cov --cov-report=term-missing --cov-fail-under=100

# Dependency vulnerability scan (required by CI)
uv run pip-audit

# SAST
uv run bandit -r packages/ apps/ scripts/ -ll -q

# All pre-commit hooks
uv run pre-commit run --all-files

# Database migrations (only needed when new migrations are added)
uv run alembic upgrade head
uv run alembic revision -m "describe the change"
uv run alembic check        # verify migration head matches models

# CLI — blueprint commands
uv run starcore blueprint plan <path.yaml>
uv run starcore blueprint run <path.yaml>
uv run starcore blueprint run <path.yaml> --parallel

# CLI — diagnostics
uv run starcore health
uv run starcore doctor [--fast]
uv run starcore diagnose
uv run starcore audit

# CLI — infrastructure tools
uv run starcore proxmox discover
uv run starcore ai generate "<description>"
uv run starcore snapshot create|list|delete|rollback
uv run starcore resource action <provider> <action> <resource>

# CLI — run history
uv run starcore runs list
uv run starcore runs get <run-id>

# Makefile shortcuts
make lint          # ruff check
make format        # ruff format
make type-check    # pyright
make test          # pytest -q
make test-cov      # pytest with coverage
make security      # pip-audit + bandit
make docs          # mkdocs serve
make docs-build    # mkdocs build --strict
make clean         # remove __pycache__, .pytest_cache, etc.
```

`doctor`, `audit`, and `diagnose` each accept `--json` (machine-readable output) and
`--quiet` (suppress output, rely on exit code) for scripting/CI use.

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
   packages/provider_sdk    ← port (BaseProvider ABC, ProviderRegistry, retry)
         |
         v
   packages/providers/*     ← adapters (docker, proxmox)
```

### Package roles

**`packages/provider_sdk`** — The stable contract every infrastructure provider must implement: five async methods (`connect`, `disconnect`, `health`, `list_resources`, `execute`). Providers are registered as singletons in a global `ProviderRegistry`. `BaseProvider` supplies a lazily-created `_connect_lock` (an `asyncio.Lock`) so concurrent `connect()` calls from a scheduler wave execute the real connection work exactly once. `retry.py` provides `RetryConfig` / `attempt_with_retry` — exponential backoff with optional jitter over configurable `retryable_exceptions`; raises `RetryableError` when all attempts are exhausted.

**`packages/blueprints`** — Loads YAML blueprints into Pydantic models, resolves Proxmox template aliases (friendly name → `template_vmid`), and produces execution plans. `ExecutionPlanner.create_plan()` returns a flat topologically-sorted list for the sequential executor, carrying each step's `depends_on` through so the executor can enforce success (not just order); `create_plan()` / `create_graph()` both honor `depends_on` as a binding constraint — unknown or circular dependencies raise `ValueError`, never produce a silently wrong order.

**`packages/orchestrator`** — Executes already-prepared `TaskGraph` plans. `Scheduler` runs dependency-satisfied tasks concurrently in "waves" via `asyncio.gather` and detects stalls (unresolvable graphs) instead of hanging. `depends_on` is a success gate, not just ordering (ADR-010): a task whose dependency finished `FAILED`/`SKIPPED`/`SKIPPED_DEPENDENCY_FAILED` is itself marked `TaskStatus.SKIPPED_DEPENDENCY_FAILED` without ever reaching `provider.execute()`, and this propagates transitively across waves. `BlueprintExecutor` (the sequential path, `packages/blueprints/executor.py`) enforces the identical rule. `timeout.py` provides `TimeoutConfig` / `TimeoutStrategy` / `execute_with_timeout` — wired into both `Scheduler._run_task()` and `BlueprintExecutor`. `ResourceSpec` carries an optional `timeout_seconds: float | None` field; when set, a task whose `provider.execute()` exceeds the deadline is cancelled and marked `FAILED` (ADR-016).

**`packages/core`** — FastAPI app and all supporting infrastructure:
- `config.py`: `pydantic-settings`-based `Settings` singleton (all env vars prefixed `STARCORE_`), LRU-cached via `get_settings()`.
- `database.py`: SQLite persistence via SQLAlchemy + Alembic; `init_db()` enforces fresh-vs-existing schema on startup.
- `models_db.py`: ORM models; must stay in sync with `migrations/versions/`.
- `events.py`: in-process `EventBus` singleton; emits `task.started`, `task.completed`, `run.completed`.
- `metrics.py`: Prometheus metrics via a **dedicated `CollectorRegistry`** (not the global default, to avoid duplicate-registration errors in the test suite). Subscribes to `EventBus` `task.completed` to record `BLUEPRINT_TASKS_TOTAL`. `HTTP_REQUESTS_TOTAL` and `HTTP_REQUEST_DURATION_SECONDS` are recorded by middleware. Exposed at the authenticated `GET /metrics` endpoint.
- `logger.py`: centralizes the process-wide loguru sink. Import it early (both `core/main.py` and `apps/cli/main.py` do this as a side effect). Every log record carries a `request_id` extra (default `"-"` for non-request contexts). Set `STARCORE_LOG_JSON=true` for JSON-structured log output suited to log aggregators (Loki, ELK, CloudWatch).
- `correlation.py`: `ContextVar`-based request ID propagation (ADR-015). `resolve_request_id()` accepts a caller-supplied `X-Request-ID` header (validated against `[A-Za-z0-9_-]{1,128}`) or generates a UUID. `contextualize_request()` binds the ID to the asyncio context so it propagates automatically to all awaited coroutines.
- `request_id_middleware.py`: `RequestIdMiddleware` class wrapping the correlation module. The inline `_request_id_middleware` in `main.py` also handles this for the FastAPI app directly, echoing `X-Request-ID` in every response.
- `security.py`: `redact_database_url()` masks credentials in `STARCORE_DATABASE_URL` before `/health`/`/diagnostics` echo them; `scrub_configured_secrets()` strips any configured secret found verbatim in provider exception text.
- `environment.py`: four independent environment checks — `detect_runtime_environment()` (`proxmox-host`/`container`/`local`), `detect_os_platform()` (OS family, WSL detection), `detect_cloud_provider()` (bounded-timeout AWS/GCP/Azure metadata probe, async only), `classify_client_platform()` (User-Agent-based client classification).
- `plugin_manager.py`: `PluginManager` discovers and loads plugins from `plugins/`. **Plugins are not sandboxed** — `importlib.import_module()` runs top-level plugin code with full process privileges before `register()` is called; see `docs/plugins.md` and ADR-011.
- `rate limiting`: API-wide per-IP rate limiting via `slowapi` (`/health` is exempt). `STARCORE_RATE_LIMIT_PER_MINUTE=0` disables it.

**`packages/ai`** — Translates natural language into a blueprint YAML via a pluggable `AIProvider` abstract base (`packages/ai/base.py`). `STARCORE_AI_PROVIDER` selects the implementation:
- `anthropic` (default): requires `STARCORE_ANTHROPIC_API_KEY`, model via `STARCORE_ANTHROPIC_MODEL` (default: `claude-sonnet-5`).
- `openai-compatible`: any `/v1/chat/completions` server (Ollama, LM Studio, vLLM, LocalAI, OpenAI), configured via `STARCORE_AI_BASE_URL` / `STARCORE_AI_API_KEY` / `STARCORE_AI_MODEL` (required; no fallback to the Anthropic model name).

`packages/ai/generator.py` builds the configured provider and exposes the public `generate_blueprint_yaml()` API.

**`packages/providers/docker`** and **`packages/providers/proxmox`** — Concrete `BaseProvider` implementations using `docker-py` and `proxmoxer` respectively. Both use blocking SDK calls wrapped in `asyncio.to_thread`.

### Execution paths

- **Sequential**: `BlueprintExecutor.execute(blueprint)` — iterates the topologically-sorted plan steps one at a time.
- **Parallel**: `Scheduler.execute(graph)` — dispatches all dependency-satisfied tasks of a wave concurrently via `asyncio.gather`, then advances to the next wave.

Both paths use the same `ExecutionPlanner` logic and must produce identical dependency orderings and failure semantics.

### API endpoints

All endpoints except `/`, `/health`, and `/ui/*` require `X-API-Key` header.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Root — returns project name and status |
| GET | `/health` | Unauthenticated liveness/readiness (DB only, rate-limit exempt) |
| GET | `/ui` | Static dashboard (serves `packages/core/static/index.html`) |
| GET | `/providers` | List registered providers |
| GET | `/providers/{name}/health` | Provider health check |
| GET | `/diagnostics` | Full diagnostics including cloud provider detection |
| GET | `/metrics` | Prometheus scrape endpoint |
| GET | `/proxmox/discover` | Discover Proxmox environment resources |
| POST | `/resources/action` | Execute a single ad-hoc provider action |
| GET | `/plugins` | List discovered and loaded plugins |
| POST | `/ai/generate-blueprint` | Generate blueprint YAML from natural language |
| POST | `/blueprints/plan` | Validate blueprint and return execution plan |
| POST | `/blueprints/run` | Execute blueprint (`?parallel=true` for concurrent) |
| GET | `/runs` | List persisted run records (`?limit=&offset=`) |
| GET | `/runs/{run_id}` | Get a specific run record |

### API security

A single static shared API key (`X-API-Key` header, constant-time comparison via `hmac.compare_digest`) protects all endpoints except `/`, `/health`, and static UI assets (ADR-012). The API returns 503 if no key is configured — it fails closed. The `/health` endpoint is intentionally unauthenticated and checks only the database; full provider health lives behind auth at `/diagnostics`. Both endpoints' detail messages are credential-redacted via `core/security.py`.

### Schema management

`init_db()` in `packages/core/database.py` enforces one of two outcomes:
- **Fresh database** (no `alembic_version` table): `create_all()` runs once and the database is stamped at the current head.
- **Existing database**: startup fails immediately if the recorded revision doesn't match the migration head. Run `uv run alembic upgrade head` to resolve.

Never run `create_all()` outside `init_db()`. ORM models live in `packages/core/models_db.py` and must be kept in sync with `migrations/versions/`.

### Plugin system

Plugins are directories in `plugins/<name>/` with an `__init__.py` that exports a `register(context)` function. `context.registry` is the global `ProviderRegistry` (to add custom providers); `context.events` is the global `EventBus` (to subscribe to `task.started`, `task.completed`, `run.completed` events). See `plugins/example_provider/` and `plugins/run_logger/` for reference implementations. **Plugins are not sandboxed** — `importlib.import_module()` runs a plugin's top-level code with the full privileges of the STARCORE process before `register()` is even looked up; see `docs/plugins.md` and ADR-011 before treating `plugins/` as anything less trusted than the codebase itself.

### Configuration

All settings are read from environment variables with the `STARCORE_` prefix (or a `.env` file, which is gitignored). The `Settings` object is a singleton behind `get_settings()` (LRU-cached). Tests must call `get_settings.cache_clear()` around any `monkeypatch.setenv`/`delenv` calls — `conftest.py` already handles this globally.

Key variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `STARCORE_API_KEY` | _(none)_ | Required; 503 if unset |
| `STARCORE_DATABASE_URL` | `sqlite:///./data/starcore.db` | SQLAlchemy DSN |
| `STARCORE_LOG_JSON` | `false` | JSON-structured log output |
| `STARCORE_RATE_LIMIT_PER_MINUTE` | `60` | `0` disables rate limiting |
| `STARCORE_AI_PROVIDER` | `anthropic` | `anthropic` or `openai-compatible` |
| `STARCORE_ANTHROPIC_API_KEY` | _(none)_ | Required for `anthropic` provider |
| `STARCORE_ANTHROPIC_MODEL` | `claude-sonnet-5` | Anthropic model ID |
| `STARCORE_AI_BASE_URL` | _(none)_ | Required for `openai-compatible` |
| `STARCORE_AI_MODEL` | _(none)_ | Required for `openai-compatible` |
| `STARCORE_AI_API_KEY` | _(none)_ | Optional for `openai-compatible` |
| `STARCORE_PROXMOX_HOST` | _(none)_ | Proxmox API hostname |
| `STARCORE_PROXMOX_USER` | _(none)_ | Proxmox API user |
| `STARCORE_PROXMOX_TOKEN_NAME` | _(none)_ | Proxmox API token name |
| `STARCORE_PROXMOX_TOKEN_VALUE` | _(none)_ | Proxmox API token value |
| `STARCORE_PROXMOX_VERIFY_SSL` | `true` | SSL verification for Proxmox |
| `STARCORE_POSTGRES_PASSWORD` | _(none)_ | PostgreSQL password for the `postgres` service in `docker-compose.yml`; not read by `Settings` — docker-compose only |

## Test Isolation

`tests/conftest.py` applies **five** autouse fixtures to every test:
1. `_no_dotenv_file` — prevents any real `.env` file from leaking into tests (critical when a populated `.env` sits in the repo root).
2. `_isolated_database` — creates a fresh SQLite DB in `tmp_path` for each test.
3. `_api_key` — sets `STARCORE_API_KEY=test-api-key` via `monkeypatch`.
4. `_clean_event_bus` — clears `event_bus._subscribers` before and after each test so EventBus state from one test (including metrics subscriptions) cannot bleed into another.
5. `_reset_rate_limiter` — clears the process-wide `slowapi` limiter's in-memory counters between tests.

When writing tests that hit the FastAPI app, use `httpx.AsyncClient` with `app=app` and include `X-API-Key: test-api-key` in headers.

### Property-based tests

The test suite includes 12 Hypothesis-based property test files (`tests/test_property_based_*.py`) covering blueprints, dependency semantics, providers, security, retry, timeout, metrics, core, AI, CLI, and environment detection. These verify structural invariants over all valid inputs, not just specific examples. Use `@given` / `@settings` from `hypothesis` when adding new property tests.

## Linting and Type Checking

- **Ruff** (`ruff.toml`): line length 100, Python 3.12, rules `E`, `F`, `I` (isort), `UP`, `B` (bugbear), `PERF`, `N` (naming), `FAST` (FastAPI-specific). Single source of truth for lint/format config. Per-file ignores: `apps/cli/main.py` suppresses `B008` (Typer idiom), `packages/providers/proxmox/provider.py` suppresses `PERF401`.
- **Pyright** (`pyrightconfig.json`): `basic` mode, checks `packages/`, `apps/`, `tests/`. The `packages/` directory is on `pythonpath` (see `pyproject.toml`), so imports like `from core.config import ...` are valid without package-relative paths.

## CI Gates (all must pass)

```
uv lock --check
uv run ruff check .
uv run pyright
uv run pip-audit
uv run bandit -r packages/ apps/ scripts/ -ll -q
# gitleaks secret scanning (via gitleaks/gitleaks-action, not a local uv command)
uv run pytest -q --cov --cov-report=term-missing --cov-fail-under=100
uv run alembic upgrade head && uv run alembic check   # against a throwaway DB, see docs/development.md
uv run mkdocs build --strict
```

CI also builds the Docker image and smoke-tests `GET /health`. A nightly workflow (`security-nightly.yml`) reruns pip-audit, Bandit, and gitleaks independent of any PR. CodeQL analysis runs via `codeql.yml`.

### GitHub workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | PR / push | Full gate: lint, types, security, tests, Docker build |
| `codeql.yml` | PR / schedule | GitHub CodeQL static analysis |
| `release.yml` | Tag push | Build and publish release artifacts |
| `docker-publish.yml` | Push to main | Publish Docker image |
| `security-nightly.yml` | Nightly | pip-audit, Bandit, gitleaks |
| `dependabot-auto-merge.yml` | Dependabot PRs | Auto-merge patch-level dependency updates |

## Key Design Decisions (ADR index)

| ADR | Title | Status |
|-----|-------|--------|
| ADR-001 | Blueprint Dependency Execution Model | Accepted |
| ADR-002 | Provider Connection Lifecycle Management | Accepted |
| ADR-003 | API Rate Limiting | Accepted |
| ADR-004 | Dependency Vulnerability Scanning | Accepted |
| ADR-005 | Unified Database Schema Management | Accepted |
| ADR-006 | Observability: Prometheus Metrics & Structured Logging | Accepted |
| ADR-007 | Pluggable AI Provider Abstraction | Accepted |
| ADR-008 | CI Security Gates: Bandit, gitleaks, Nightly Audit | Accepted |
| ADR-009 | Environment Detection: Runtime, OS, Cloud Provider, Client | Accepted |
| ADR-010 | Dependency Failure Semantics (`depends_on` as success gate) | Accepted |
| ADR-011 | Plugin Trust Boundary (not sandboxed) | Accepted |
| ADR-012 | API Authentication Model | Accepted |
| ADR-013 | Provider Concurrency Policy (no semaphore now; trigger conditions defined) | Accepted |
| ADR-014 | Task Timeout Support | Accepted |
| ADR-015 | Request Correlation via Context Variables | Accepted |
| ADR-016 | Task Timeout Integration | Implemented |

### Task timeouts (ADR-016)

`ResourceSpec` carries `timeout_seconds: float | None = None`. When set, both `BlueprintExecutor` and `Scheduler._run_task()` wrap `provider.execute()` in `execute_with_timeout()` using `TimeoutStrategy.CANCEL`; a task that exceeds its deadline is marked `FAILED`, which propagates to dependents via the `depends_on` success-gate. Omitting `timeout_seconds` (or setting it to `null`) preserves the previous no-timeout behavior exactly. Do not add a global `STARCORE_TASK_TIMEOUT_SECONDS` shortcut — ADR-016 explicitly rejected it as too coarse for mixed workloads (slow Proxmox clone vs. fast container start).

### Provider concurrency (ADR-013)

`execute()` calls against a shared provider instance are deliberately unbounded — no `asyncio.Semaphore` exists. ADR-013 confirmed no shared-mutable-state hazard for current Docker and Proxmox SDK clients under STARCORE's actual configuration, but load testing was not performed. Three trigger conditions are defined in the ADR for adding a bounded semaphore later.

## Persistent project memory (`.starcore/`)

The `.starcore/` directory is a cross-session state layer for the STARCORE Autonomous Engineering Agent. New sessions should read it before deriving context from scratch.

```
.starcore/
  README.md                  — overview and cold-start protocol
  memory/
    project_snapshot.md      — key facts for cold start (metrics, architecture)
    risks.md                 — canonical risk register (source of truth)
    user_preferences.md      — communication rules, approval gates
    architecture.md          — architecture reference
    decisions.md             — working decisions (pre-ADR)
    known_issues.md          — active known issues
    completed_work.md        — record of completed work
    pending_work.md          — remaining work with priorities
  sessions/
    current.md               — human-readable session ledger (reference)
    ledger.yaml              — machine-readable session ledger (source of truth)
    archive/                 — past session history
  prompts/
    registry.yaml            — prompt catalog (PROM-001..PROM-008)
  scripts/
    models.py                — data models (PromptEntry, SessionEntry, CheckResult)
    registry.py              — Prompt Registry CLI
    ledger.py                — Session Ledger CLI
    decision_engine.py       — Interactive Decision Engine CLI
    impact_analyzer.py       — Change Impact Analyzer (file → module → categories)
    regression_sentinel.py   — Regression Sentinel (detects drift vs baseline)
    release_readiness.py     — Release Readiness Engine (12 gates)
    qc_engine.py             — QC Orchestrator (unified report)
    startup_protocol.py      — Startup Protocol (12-step session init, Czech report)
    tests/                   — standalone tests for scripts/ (171 tests)
  state/
    regression_baseline.json — test/coverage/vulnerability + sentinel baseline
    release.md               — release readiness gate status
```

**Cold-start protocol for new sessions:** read `memory/project_snapshot.md`, then run `uv run python .starcore/scripts/ledger.py current`, then `memory/pending_work.md` before any other action. Never store secrets or credentials in `.starcore/`.

## Interactive Decision Engine

After every audit, implementation, or failure, respond in the standard Decision Engine format. Full protocol: `.starcore/memory/decision_engine.md`.

**Mandatory sections:** STAV / CO BYLO ZJIŠTĚNO / CO BYLO OVĚŘENO / RIZIKA / DOPORUČENÍ / DOPAD / RIZIKO / ROLLBACK / DALŠÍ KROK

**Default language:** Czech for all user-facing text; technical identifiers unchanged.

**Safety gates** — require explicit confirmation before executing:
`merge` · `push` · `delete` · `reset` · `--force` · `infrastructure` · `production` · `secret` / `credential` / `password` / `token`

**CLI tools:**
```bash
uv run python .starcore/scripts/decision_engine.py render --file report.yaml
uv run python .starcore/scripts/decision_engine.py parse-choice "Varianta 1"
uv run python .starcore/scripts/decision_engine.py check-safety "git push --force"
uv run python .starcore/scripts/decision_engine.py format
uv run python .starcore/scripts/decision_engine.py log --decision "..."
uv run python .starcore/scripts/tests/test_decision_engine.py   # 49 tests
```

## Startup Protocol

Run at the beginning of every new session to produce a Czech session status report with a 6-option decision menu. Implements the 12-step startup flow: identify repo → branch → HEAD → worktree → project state → last session → risks → pending work → decisions → Regression Sentinel → GitHub state → Czech report.

```bash
uv run python .starcore/scripts/startup_protocol.py           # full (runs sentinel + github checks)
uv run python .starcore/scripts/startup_protocol.py --quick   # skip slow QC checks
uv run python .starcore/scripts/startup_protocol.py --json    # machine-readable output
uv run python .starcore/scripts/tests/test_startup_protocol.py   # 54 tests
```

Exit code: 1 if Regression Sentinel detects a regression (FAIL), 0 otherwise.

## QC Engines

Three quality-control engines run against the repository without modifying it.

**Change Impact Analyzer** — maps `git diff` → module → impact categories using actual repo evidence (no speculation):
```bash
uv run python .starcore/scripts/impact_analyzer.py analyze
uv run python .starcore/scripts/impact_analyzer.py analyze --since HEAD~1
uv run python .starcore/scripts/impact_analyzer.py module packages/core/main.py
```

**Regression Sentinel** — detects drift across 7 dimensions (test count, API routes, CLI commands, config fields, ADR count, workflow count, lock sync):
```bash
uv run python .starcore/scripts/regression_sentinel.py check
uv run python .starcore/scripts/regression_sentinel.py diff
uv run python .starcore/scripts/regression_sentinel.py update  # only after confirmed CI pass
```

**Release Readiness Engine** — evaluates 12 gates (BUILD/TEST/SECURITY/DEPENDENCIES/PACKAGE/ARTIFACT/DOCUMENTATION/GITHUB/GOVERNANCE/DEPLOYMENT/BACKUP/RECOVERY). UNKNOWN ≠ PASS.
```bash
uv run python .starcore/scripts/release_readiness.py evaluate --quick
uv run python .starcore/scripts/release_readiness.py evaluate           # full (slow)
uv run python .starcore/scripts/release_readiness.py gate SECURITY
```

**QC Orchestrator** — unified report from all three engines:
```bash
uv run python .starcore/scripts/qc_engine.py run --quick
uv run python .starcore/scripts/qc_engine.py run --impact --since HEAD~1
uv run python .starcore/scripts/tests/test_qc_engines.py   # 68 tests
```

Full protocol: `.starcore/memory/qc_engines.md`
```

## Communication Preferences

When presenting options, next steps, or decisions, always include a **recommended answer pre-filled directly in the chat**. Format it as:

> **Doporučená odpověď:** `<konkrétní příkaz nebo volba>`

This applies to:
- Decision Engine option menus (pre-select the recommended varianta)
- Next-step proposals (state the recommended step first, with the command ready to copy)
- Confirmation prompts before safety-gated actions (state what will be executed)

The user can confirm with "ano" / "yes" or override by specifying a different option. Never wait silently for a choice without first offering a recommendation.
