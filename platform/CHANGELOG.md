# Changelog

All notable changes to STARCORE Platform are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **Root-level release workflows**: promoted `release.yml` (publishes GitHub Releases on
  `v*` tag push or `workflow_dispatch`) and `manual-tag.yml` (creates and pushes a tag from
  the Actions UI) from `platform/.github/workflows/` to `.github/workflows/` so GitHub
  Actions can discover and run them. `release.yml` gains `defaults: run: working-directory:
  platform` to match `ci.yml`. Also fixed the changelog gate in `ci.yml` to skip the
  `[Unreleased]` check on release PRs/commits (title or message starts with
  `chore: release`).
- **Release workflow fixes**: corrected `release.yml` tag filter from regex (`v[0-9]+…+`) to
  valid glob (`v[0-9]*…*`) so tag-push events actually trigger the workflow. Updated
  `manual-tag.yml` to guard against duplicate tags and explicitly dispatch `release.yml` via
  `workflow_dispatch` after pushing the tag (GITHUB_TOKEN push events do not re-trigger other
  workflows per GitHub Actions security model).

## [0.6.0] — 2026-08-05

### Added

- **Plugin operator controls (REC-009)**: Two new settings give operators control over which plugins
  are loaded, without requiring code changes or plugin removal.
  - `STARCORE_PLUGINS_ENABLED=false` disables all plugin loading at the `load_all()` level — no
    plugin imports execute, regardless of what is in `plugins/`.
  - `STARCORE_PLUGINS_ALLOWLIST=name1,name2` restricts loading to explicitly named plugins;
    any discovered plugin not on the list is skipped with a warning. An empty value (the default)
    keeps the existing behavior where every discovered plugin may load.
  - These controls restrict *which* plugins are loaded, not *what* a loaded plugin can do — the
    full-privilege trust model documented in `docs/plugins.md` and ADR-011 still applies.
  - 4 new tests, 100% coverage.

- **Kubernetes infrastructure provider (REC-008)**: New `KubernetesProvider` implementing the full
  `BaseProvider` contract against any Kubernetes cluster.
  - Authenticates via explicit kubeconfig (`STARCORE_KUBERNETES_KUBECONFIG`), in-cluster service
    account (when running inside a Pod), or the default `~/.kube/config` — tried in that order.
  - Optional `STARCORE_KUBERNETES_CONTEXT` selects the kubeconfig context; `STARCORE_KUBERNETES_NAMESPACE`
    sets the default namespace (default: `default`).
  - Five actions: `deploy` (create or update a Deployment), `delete` (delete a Deployment),
    `scale` (set replica count), `restart` (rolling restart via annotation patch), and
    `apply-namespace` (idempotent namespace creation).
  - `connect()` is concurrency-safe via `BaseProvider._connect_lock`; the Kubernetes `ApiClient`
    is created at most once per instance regardless of concurrent callers.
  - All blocking SDK calls are offloaded to `asyncio.to_thread`; the provider never blocks the
    event loop.
  - Registered in `ProviderRegistry` alongside Docker and Proxmox via `register_default_providers()`.
  - 37 new tests in `tests/test_kubernetes_provider.py` covering connect/disconnect/health,
    list_resources, all five actions, error paths, and registry integration.

- **WebSocket blueprint execution stream (REC-002)**: New `WS /blueprints/run/ws` endpoint streams
  real-time execution events over a persistent WebSocket connection — a full-duplex alternative to
  the SSE endpoint.
  - After connecting, client sends the blueprint as a single JSON text frame; server streams
    `task.started`, `task.completed`, `run.completed`, and `run.persisted` JSON frames.
  - Auth via query parameters (HTTP headers are not forwarded on WebSocket handshakes):
    `?token=<jwt>` or `?api_key=<key>`; requires `operator` role or higher.
  - Custom application close codes: `4401` (auth failure), `4403` (forbidden / insufficient role),
    `4422` (invalid blueprint JSON or template resolution error).
  - Client disconnect cancels the in-flight `asyncio.Task` via `Task.cancel()`, mirroring the SSE
    endpoint's disconnect semantics.
  - `?parallel=true` engages `Scheduler` (wave-based graph execution); default is sequential
    `BlueprintExecutor`.
  - 20 new tests in `tests/test_ws_blueprint.py` covering all auth paths, happy-path event
    ordering, error events, multi-resource blueprints, parallel mode, and disconnect/cancel.

- **RBAC / JWT authentication (REC-001)**: Full role-based access control layered on top of the
  existing single-key model. Three roles (`reader`, `operator`, `admin`) gate every API endpoint;
  `reader ≤ operator ≤ admin` hierarchy is enforced by `require_role()` FastAPI dependencies.
  - `POST /auth/token` — password login returns a short-lived access JWT + long-lived refresh JWT.
  - `POST /auth/refresh` — exchange a valid refresh token for a new access token.
  - `POST /auth/users` (admin only) — create users.
  - `GET /auth/users` (admin only) — list users.
  - `User` ORM model added; Alembic migration `0002_add_users.py` creates the `users` table.
  - `STARCORE_JWT_SECRET_KEY`, `STARCORE_JWT_ALGORITHM`, `STARCORE_ACCESS_TOKEN_EXPIRE_MINUTES`,
    `STARCORE_REFRESH_TOKEN_EXPIRE_DAYS`, and `STARCORE_INITIAL_ADMIN_PASSWORD` settings added.
  - `STARCORE_INITIAL_ADMIN_PASSWORD` bootstraps a first `admin` user on startup.
  - Backward-compatible: `X-API-Key` header still accepted on all endpoints and maps to `admin`.
    Existing deployments with no `STARCORE_JWT_SECRET_KEY` continue to work unchanged.
  - Dependencies added: `pyjwt>=2.8.0`, `bcrypt>=4.0.0`.

## [0.5.0] — 2026-08-04

### Added

- **Blueprint parametrization (REC-006)**: `Blueprint` model carries a `vars:` map;
  `BlueprintLoader` renders the YAML through a Jinja2 `SandboxedEnvironment` with
  `StrictUndefined` before loading — undefined variables raise `BlueprintRenderError`.
  `starcore blueprint plan/run` accept repeatable `--var KEY=VALUE` flags; values are
  auto-coerced to `int`, `float`, or `bool` where unambiguous.

- **SSE streaming endpoint (REC-004)**: `POST /blueprints/run/stream` streams Server-Sent
  Events in real time: `task.started`, `task.completed`, `run.completed`, and a final
  `run.persisted` event carrying the database `run_id`. Client disconnect cancels the
  in-flight execution task via `asyncio.Task.cancel()`. `EventBus` gains an `unsubscribe()`
  method for per-request handler cleanup.

- **OpenTelemetry distributed tracing (REC-005)**: `packages/core/tracing.py` provides
  `configure_tracing(endpoint)` (no-op when unset, zero overhead) and `get_tracer()`.
  `STARCORE_OTLP_ENDPOINT` activates a `BatchSpanProcessor` + OTLP/HTTP exporter targeting
  any OTel-compatible collector (Jaeger, Grafana Tempo, Honeycomb, etc.). Span instrumentation
  added to `BlueprintExecutor` (`blueprint.execute`, `task.dispatch`) and `Scheduler`
  (`blueprint.execute`, `task.run`).

- **PostgreSQL CI smoke tests (REC-003)**: `postgres-smoke` job in `ci.yml` spins up
  `postgres:16`, runs Alembic migrations against it, and executes a dedicated
  `tests/postgres/` suite verifying schema compatibility, run persistence, and multi-run
  queries under the PostgreSQL dialect.

### Changed

- **BlueprintExecutor refactor (REC-007)**: `execute()` reduced from ~110 lines to ~20 by
  extracting `_build_task()`, `_dispatch_task()`, `_finalize_run()`, and `_emit_task_completed()`
  helpers. No behaviour change; all 685 tests pass.

- Test suite: 685 tests (↑ from 601), 100% coverage maintained.

## [0.4.0] — 2026-08-01

Per-task timeout strategy: blueprint authors can now control what happens when a resource hits its deadline.

### Added

- **Per-task `timeout_strategy` field (ADR-016)**: `ResourceSpec` and `Task` now carry an
  optional `timeout_strategy: TimeoutStrategy | None` field alongside `timeout_seconds`.
  Both `BlueprintExecutor` and `Scheduler._run_task()` feed the strategy into `TimeoutConfig`;
  default remains `TimeoutStrategy.CANCEL` (backwards-compatible).
  Supported values: `cancel` (cancels on timeout), `wait_and_mark` (lets task finish, marks
  `FAILED`), `ignore` (lets task finish, result is `SUCCESS`).

### Changed

- Test suite: 601 tests (↑ from 591), 100% coverage maintained.

## [0.3.0] — 2026-08-01

Per-task timeout support: blueprint authors can now set a deadline on individual resources.

### Added

- **Per-task `timeout_seconds` (ADR-016)**: `ResourceSpec` and `Task` carry an optional
  `timeout_seconds: float | None = None` field. When set, both `BlueprintExecutor` and
  `Scheduler._run_task()` wrap `provider.execute()` in `execute_with_timeout()` with
  `TimeoutStrategy.CANCEL`. A task that exceeds its deadline is cancelled and marked
  `FAILED`, which propagates to dependents via the existing `depends_on` success gate.
  Omitting the field (or setting `null`) preserves the previous no-timeout behaviour exactly.

### Changed

- **ADR-016 status**: `Accepted (deliberate deferral)` → `Implemented`. The deferral is
  closed: per-task timeout configuration now exists, and the globally-rejected
  `STARCORE_TASK_TIMEOUT_SECONDS` shortcut is still not introduced.
- Test suite: 591 tests (↑ from 582), 100% coverage maintained.

## [0.2.0] — 2026-08-01

Security hardening cycle, observability improvements, and cross-session memory layer.
Covers sprints 016–024 and the STARCORE autonomous engineering session (2026-07-26 – 2026-08-01).

### Security

- **GitHub Actions SHA pinning (R-001)**: 22 mutable `@vN` action references replaced
  with immutable commit SHAs in all 7 workflow files; version preserved as inline comment.
- **SBOM + image signing (R-010)**: `docker-publish.yml` now generates a SPDX-JSON SBOM
  via `anchore/sbom-action@v0.24.0` and signs every pushed image via `cosign sign` (keyless
  OIDC, no key management); SBOM attached as a verifiable `cosign attest` predicate on the
  image digest.
- **Dependabot auto-merge scope (R-008)**: auto-merge now restricted to `pip` ecosystem
  only; GitHub Actions updates require manual review before merge.
- **Remove inactive jekyll-gh-pages.yml (R-007)**: project uses MkDocs; the Jekyll
  workflow was unreachable dead attack surface.
- **assert guards → explicit RuntimeError (R-012)**: 11 `assert self._client is not None`
  statements in `proxmox/provider.py` (9×) and `docker/provider.py` (2×) replaced with
  `if/raise RuntimeError`; `assert` is silently disabled under Python `-O`.
- **Centralized secret redaction**: `redact_database_url()` masks credentials in
  `STARCORE_DATABASE_URL` before `/health`/`/diagnostics` can echo them; `scrub_configured_secrets()`
  strips configured secrets from provider exception text.
- CodeQL static analysis workflow added, running alongside Bandit/gitleaks/pip-audit.

### Fixed

- **Timeout coroutine reuse RuntimeError (R-005)**: `execute_with_timeout()` re-awaited
  a spent coroutine after `asyncio.wait_for` cancellation. Fixed by wrapping the coroutine
  in `asyncio.create_task()` before calling `asyncio.shield()` for WAIT_AND_MARK and IGNORE
  strategies. Tests rewritten from monkeypatching to real async timing.
- **Dependency failure semantics enforced (ADR-010)**: a task whose `depends_on` prerequisite
  finished `FAILED`, `SKIPPED`, or `SKIPPED_DEPENDENCY_FAILED` is now marked
  `SKIPPED_DEPENDENCY_FAILED` and never reaches `provider.execute()`, transitively across
  scheduler waves — in both `BlueprintExecutor` and `Scheduler` paths.
- **`mkdocs build --strict` CI failure**: four doc files orphaned from `mkdocs.yml` nav,
  two broken internal links, ADR numbering collision resolved.
- **`classify_client_platform` marker priority**: script markers now checked before browser
  markers; found by a Hypothesis property test.
- **`provider_sdk` import error** (`ProviderException` → `ProviderError`): wrong class
  name caused test suite to fail at collection.
- `docker compose config` no longer fails when `STARCORE_POSTGRES_PASSWORD` is unset
  (switched to default-to-empty interpolation; postgres service still refuses to start
  with an empty password when the scaffold profile is active).
- Ruff format gate (`ruff format --check .`) added to `ci.yml` (R-006); 8 non-compliant
  source files reformatted.
- Dead code removed from Proxmox provider (R-009): permanently unreachable
  `if resource_kind == "lxc"` block deleted.
- `release.yml` quality gate brought to parity with `ci.yml`: now runs `uv lock --check`,
  `pip-audit`, Bandit, gitleaks, `alembic check`, `mkdocs build --strict`, and
  `--cov-fail-under=100`.

### Added

- **Request correlation (ADR-015)**: every HTTP response carries `X-Request-ID`
  (caller-supplied if valid, generated otherwise), bound to every log line emitted while
  handling that request.
- **`starcore snapshot rollback` dry-run diff**: shows what will change before prompting
  for confirmation (unless `--yes`), matching `snapshot delete` confirmation pattern.
- **`.starcore/` cross-session memory layer**: persistent project state versioned in the
  repo — risk register, session ledger, prompt registry, interactive decision engine with
  safety gates, Change Impact Analyzer, Regression Sentinel (7 dimensions), Release
  Readiness Engine (12 gates), and Startup Protocol (12-step session init with Czech
  report + 6-option decision menu). 171 standalone tests.
- ADR-010 (Dependency Failure Semantics), ADR-011 (Plugin Trust Boundary), ADR-012
  (API Authentication Model), ADR-013 (Provider Concurrency Policy), ADR-014 (Task
  Timeout Support), ADR-015 (Request Correlation), ADR-016 (Timeout Deferral).
- New reference documentation wired into MkDocs nav: CLI Reference, API Reference,
  Security, Plugins, Test Matrix, Architecture State, Test Strategy, Operations Runbook.
- Docker: multi-stage build; final image drops dev dependencies.
- 87 new property-based (Hypothesis) tests across 6 new files: retry, timeout, security,
  dependency semantics, executor, core.

### Changed

- README "What's Planned, Not Built Yet" section (which had drifted) replaced with
  "Production Limitations" and a shorter, accurate "Roadmap / Vision" section.
- `STARCORE_POSTGRES_PASSWORD` documented in CLAUDE.md config table (R-016); noted as
  docker-compose only — not read by `Settings`.
- Wheel build completeness (R-018): `plugins` added to `packages`; `migrations/` and
  `alembic.ini` added to `force-include`; wheel entries: 58 → 65.
- Test count: 493 (0.1.0) → 580 (0.2.0); 100% coverage maintained throughout.

Test count: 449 → 493 (100% coverage maintained throughout).

## [0.1.0] — 2026-07-26

First numbered release. Covers sprints 001–015.

### Added

**Infrastructure Providers**
- Docker provider via docker-py: connect, health, list resources, create / start / stop / remove containers
- Proxmox VE provider via proxmoxer: connect, health, list resources, start / stop / shutdown VMs and LXC containers, clone VM or LXC from template, snapshot create / list / delete / rollback
- `BaseProvider` ABC, `ProviderRegistry` singleton, and typed `ProviderError` exception hierarchy (`packages/provider_sdk`)
- Proxmox environment discovery — `starcore proxmox discover` / `GET /proxmox/discover` catalogs node capacity, storage, available templates, and network bridges

**Blueprint Engine**
- YAML blueprint loading and Pydantic v2 validation (`packages/blueprints`)
- `ExecutionPlanner.create_plan()` with `depends_on` topological sort; unknown or circular dependencies raise `ValueError` rather than producing a silently wrong order
- Sequential execution via `BlueprintExecutor`; parallel graph execution via `Scheduler` + `TaskGraph` (`--parallel`)
- Proxmox template alias resolution: blueprints can reference `template: "ubuntu-24.04"` instead of a raw `template_vmid`
- Resource lifecycle actions: `starcore resource action <provider> <action> <resource>` / `POST /resources/action`

**Core API (FastAPI)**
- `GET /health` — unauthenticated database connectivity check
- `GET /diagnostics` — authenticated: full provider health, environment detection, calling-client classification
- `GET /providers`, `GET /providers/{name}/health`
- `POST /blueprints/plan`, `POST /blueprints/run` (sequential and parallel modes)
- `GET /runs`, `GET /runs/{run_id}` — blueprint run history
- `GET /metrics` — Prometheus text format (authenticated)
- `POST /resources/action`, `POST /snapshots/{action}`
- `GET /proxmox/discover`
- `POST /ai/generate-blueprint`
- `GET /ui` — read-only web dashboard (static HTML/JS, no build step)
- `GET /plugins`
- Per-IP rate limiting via slowapi (`STARCORE_RATE_LIMIT_PER_MINUTE`; `/health` always exempt)
- Single static API key authentication (`X-API-Key` header, constant-time `hmac.compare_digest`; fails closed with 503 when unconfigured)

**CLI (Typer)**
- `starcore blueprint plan <path>` / `starcore blueprint run <path> [--parallel]`
- `starcore health` — real database connectivity check; exits 0 on success, 1 on failure
- `starcore doctor [--fast] [--json] [--quiet]` — full local quality gate runner
- `starcore audit [--json] [--quiet]` — runtime configuration health checks
- `starcore diagnose [--json] [--quiet]` — deep provider and environment diagnostics
- `starcore proxmox discover`
- `starcore snapshot create | list | delete | rollback`
- `starcore resource action <provider> <action> <resource>`
- `starcore ai generate "<description>"`

**AI Blueprint Generation**
- Pluggable `AIProvider` abstraction (`packages/ai/base.py`); `STARCORE_AI_PROVIDER` selects implementation
- Anthropic provider (default): `STARCORE_ANTHROPIC_API_KEY` + optional `STARCORE_ANTHROPIC_MODEL`
- OpenAI-compatible provider: `STARCORE_AI_PROVIDER=openai-compatible` + `STARCORE_AI_BASE_URL` — supports Ollama, LM Studio, vLLM, LocalAI, and OpenAI itself

**Persistence**
- SQLite via SQLAlchemy; `BlueprintRunRecord` and `TaskRunRecord` ORM models
- Alembic migrations; startup enforces migration head; `create_all()` on fresh database only
- `STARCORE_DATABASE_URL` configurable (default: `sqlite:///./data/starcore.db`)

**Observability**
- Prometheus metrics: HTTP request counter + duration histogram, blueprint task counter by provider and status (`packages/core/metrics.py`)
- Structured JSON logging via loguru (`STARCORE_LOG_JSON=true`)
- `GET /health` and `GET /diagnostics` with distinct unauthenticated / authenticated access levels

**Environment Detection**
- `detect_runtime_environment()`: classifies host as `proxmox-host`, `container`, or `local`
- `detect_os_platform()`: OS family, release, and WSL detection
- `detect_cloud_provider()`: async bounded-timeout AWS / GCP / Azure metadata probe (`run_diagnostics()` only)
- `classify_client_platform()`: User-Agent-based calling-client classification; surfaced in `GET /diagnostics`

**Plugin System**
- Plugins in `plugins/<name>/` with a `register(context)` entry point
- `context.registry` to add custom providers; `context.events` to subscribe to `task.started`, `task.completed`, `run.completed`
- Reference implementations: `plugins/example_provider/`, `plugins/run_logger/`

**Security**
- Bandit SAST gate on every PR and nightly (`security-nightly.yml`)
- gitleaks secret scanning on every PR and nightly
- pip-audit dependency vulnerability scan on every PR
- Dependabot for pip, GitHub Actions, and Docker — weekly, auto-merge patch/minor updates

**Testing and Quality**
- 449 passing tests, 100% statement coverage (enforced in CI)
- Hypothesis property-based tests across all major packages
- Ruff (format + lint), Pyright type checking, pre-commit hooks on every commit
- Alembic schema drift detection in CI

### Infrastructure
- Docker: `python:3.12-slim` base, non-root `starcore` user, `/health` HEALTHCHECK, `restart: unless-stopped`, SQLite volume at `/data`
- Docker Compose: `api` service + optional Postgres / Redis / NATS scaffold (opt-in `--profile scaffold`)
- GitHub Actions: `ci.yml` (quality + docker-build), `docker-publish.yml` (GHCR on push to `main` and version tags), `security-nightly.yml`
