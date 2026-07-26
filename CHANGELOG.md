# Changelog

All notable changes to STARCORE Platform are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Property-based (Hypothesis) tests for `BlueprintExecutor` (the sequential execution
  path): 5 new tests mirroring the existing `Scheduler` property tests — task count,
  terminal-status, all-succeed, unregistered-provider, and dependency-failure-propagation
  invariants. Hypothesis found that the unregistered-provider invariant needed a
  dependency-free blueprint to hold cleanly (a dependent task correctly reaches
  SKIPPED_DEPENDENCY_FAILED rather than SKIPPED).
- Test matrix corrected: "Event bus", "Plugins", "Persistence", and "Request
  correlation" already had property-based coverage in `test_property_based_core.py`
  that was never reflected in `docs/test-matrix.md`.

### Added
- Property-based (Hypothesis) tests for `core.security`: 6 new tests covering
  `redact_database_url` (never-raises, postgres password masked, SQLite passthrough) and
  `scrub_configured_secrets` (never returns configured secret, idempotent, no-op when no
  secrets). Hypothesis found and fixed a subtle test-invariant bug: `password not in result`
  was too broad (password chars can appear in the hostname); corrected to
  `f":{password}@" not in result`.
- ADR-014 (Task Timeout Integration — Deliberate Deferral): documents that
  `execute_with_timeout` in `orchestrator/timeout.py` is intentionally not wired into
  `Scheduler` or `BlueprintExecutor`, with trigger conditions for revisiting.
- Test matrix updated: "Secret redaction" row gains property-based checkmark.

### Added
- Property-based (Hypothesis) tests for `provider_sdk.retry` and `orchestrator.timeout`:
  17 new tests covering `calculate_delay` bounds/monotonicity/determinism,
  `RetryableError` attribute preservation, `attempt_with_retry` single-attempt and
  non-retryable-propagation invariants, `TimeoutConfig.is_enabled` for all `float | None`
  inputs, `TaskTimeoutError` attribute and str invariants, and the disabled-path
  pass-through of `execute_with_timeout`.
- Test matrix (`docs/test-matrix.md`) updated with rows for retry, timeout, and request
  correlation; test catalog (`reports/starcore-tests-catalog.md`) brought current with all
  52 tests added since sprint-019.



### Fixed
- **Broken `provider_sdk` import** (`ProviderException` → `ProviderError`): the wrong
  class name caused every test to fail at collection time with `ImportError`; corrected
  to `ProviderError`, the actual class in `provider_sdk/exceptions.py`.
- **`classify_client_platform` marker priority**: script markers (curl, python-httpx,
  …) are now checked before browser markers so a UA containing both (e.g. `curlchrome`)
  correctly classifies as `cli-or-script` rather than `browser-desktop`. Found by a
  Hypothesis property test.
- Lint and type violations introduced by external PRs in `retry.py`, `timeout.py`,
  `correlation.py`, and `provider_sdk/__init__.py` (ruff UP035/UP042/UP045/UP041×2/B904/
  E501/F841/I001; pyright `float | None` narrowing in `execute_with_timeout`).

### Added
- Tests for four untested modules added by PR #100: `provider_sdk.retry`,
  `orchestrator.timeout`, `core.correlation`, `core.request_id_middleware` (35 new
  tests; 531 total, 100% coverage restored).



### Fixed
- **Dependency failure semantics now enforced, not just documented** (ADR-010): a task whose dependency finished `FAILED`, `SKIPPED`, or `SKIPPED_DEPENDENCY_FAILED` is itself marked `SKIPPED_DEPENDENCY_FAILED` and never reaches `provider.execute()`, transitively across scheduler waves — in both the sequential (`BlueprintExecutor`) and parallel (`Scheduler`) paths. Previously `depends_on` only gated on the prerequisite having *finished*, not succeeded (flagged as an open question in the 0.1.0 audit, now resolved as a deliberate semantics fix).
- `docker compose config` (and `docker compose up -d --build api`, the documented non-scaffold workflow) no longer fails when `STARCORE_POSTGRES_PASSWORD` is unset — Compose interpolates every service's environment block at parse time regardless of active profile; switched to a default-to-empty interpolation, with the official postgres image still refusing to start on an empty password if the scaffold profile is actually enabled.
- `release.yml` quality gate brought to parity with `ci.yml`: was only `ruff check` + `pyright` + `pytest --cov-fail-under=80`, now also runs `uv lock --check`, `pip-audit`, Bandit, gitleaks, `alembic check`, and `mkdocs build --strict`, at the same 100% coverage floor as every other gate.

### Added
- Request correlation: every HTTP response carries `X-Request-ID` (caller-supplied if present and well-formed, generated otherwise), bound to every log line emitted while handling that request.
- `starcore snapshot rollback` shows a dry-run diff of what will change before prompting for confirmation (unless `--yes`), matching the existing `snapshot delete` confirmation pattern.
- Centralized secret redaction (`packages/core/security.py`): `redact_database_url()` masks credentials in `STARCORE_DATABASE_URL` before `/health`/`/diagnostics` can echo them back; `scrub_configured_secrets()` strips any configured secret found verbatim in provider exception text.
- ADR-010 (Dependency Failure Semantics), ADR-011 (Plugin Trust Boundary — plugins are **not sandboxed**), ADR-012 (API Authentication Model), ADR-013 (Provider Concurrency Policy — no rate limit for now, by deliberate decision with stated trigger conditions for revisiting).
- CodeQL static analysis workflow, running alongside Bandit/gitleaks/pip-audit.
- Docker: multi-stage build; final image drops dev dependencies and the runtime PyPI dependency.
- New reference documentation, all wired into the MkDocs nav: CLI Reference, API Reference, Security, Plugins, Test Matrix, Current Architecture State, Test Strategy, Operations Runbook.
- `uv run mkdocs build --strict` added as a CI gate, catching orphaned/unreachable doc pages.

### Changed
- README's "What's Planned, Not Built Yet" section (which had drifted — several listed items were already implemented) replaced with "Production Limitations" (the actual security-relevant caveats, cross-referenced to ADR-011/012/013) and a shorter, accurate "Roadmap / Vision" section.

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
