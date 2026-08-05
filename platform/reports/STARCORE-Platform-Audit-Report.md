STARCORE-Platform-Audit-Report.md


AI Repository Audit Report
Target Repository: https://github.com/Fatalerorr69/starcore-platform Commit Audited: d25b76a (branch main, 119 commits, 2026-07-04 → 2026-07-15) Audit Standard: AI Repository Audit Specification v1.0 Audit Type: Evidence-based technical review — no code generated, modified, or proposed.

Executive Summary
STARCORE Platform is an 11-day-old, single-primary-author Python project (2 contributors, ~4,900 lines of application code, 114 tests) implementing a declarative infrastructure-orchestration tool for Docker and Proxmox homelabs. It is built on FastAPI, SQLAlchemy/Alembic, Typer, and Pydantic, packaged with uv/hatchling.

Primary strengths: The repository shows unusually disciplined engineering hygiene for its age — a modular-monolith layout with a clear Provider SDK abstraction, consistent async patterns, an honest and accurate README ("What Works Today" vs. "Vision"), a real CI pipeline (lint, type-check, test, Docker smoke-test) that runs on every PR, no committed secrets, and a test suite that mocks external systems appropriately rather than requiring live infrastructure.

Primary weaknesses: The project is pre-alpha (version 0.1.0-dev) and several structural issues exist: three packaged modules (orchestrator, provider_sdk, providers) and apps lack __init__.py files despite being declared as build targets; sequential blueprint execution silently ignores depends_on (only the parallel scheduler honors it); provider instances are shared, mutable, un-synchronized singletons that are unsafe under the concurrent execution path the scheduler itself provides; MkDocs references four documentation pages that do not exist; a Makefile target (make dev) invokes a module path that has no __main__.py; and there is no security scanning, dependency-vulnerability scanning, coverage measurement, SECURITY.md, or CONTRIBUTING.md despite the tooling for some of these being declared as dependencies.

Critical risks: None found that constitute immediate exploitable vulnerabilities. The most consequential findings are architectural (silent dependency-order violation in sequential execution) and correctness-related under concurrency (shared provider client state), both of which affect the reliability of the tool's core value proposition — safe infrastructure orchestration.

Production readiness: Not production-ready, and the repository does not claim to be. It is explicitly self-described as active development / homelab-oriented. As a homelab/personal tool it is reasonably solid; as a system intended to safely manage production infrastructure it has open concurrency-safety and dependency-resolution gaps.

Maintainability: Currently high — small codebase, consistent style, real tests, real CI. This is likely to degrade unless testing/security/dependency-scanning practices are formalized as the codebase grows, since no such gates currently exist beyond linting and functional tests.

Architecture maturity: Early-stage but coherent. The Provider SDK / Blueprint Engine / Orchestrator separation is a sound modular-monolith design; the main risks are in execution-model inconsistency between the two execution paths (BlueprintExecutor vs. Scheduler) rather than in the layering itself.

Overall conclusion: A small, honestly-documented, actively-developed personal/homelab infrastructure tool with above-average engineering discipline for its maturity stage, but with concrete architectural, packaging, and operational gaps that should be resolved before any production or multi-user use.

Repository Overview
FACT: The repository name is starcore-platform, owned by GitHub user Fatalerorr69, licensed Apache-2.0, described in pyproject.toml as "AI Powered Infrastructure Operating Platform", version 0.1.0-dev, requiring Python >=3.12.

FACT: Git history shows 119 commits spanning 2026-07-04 to 2026-07-15 (11 calendar days), 2 distinct contributor logins visible via commit metadata, and a single active branch (main). Development proceeds through feature branches merged via pull request (Merge pull request #NN pattern), with Dependabot opening dependency-update PRs.

FACT: The technology stack, per pyproject.toml, consists of FastAPI, Uvicorn, Typer, Pydantic v2, Pydantic-Settings, SQLAlchemy 2.x, Alembic, httpx, Rich, Loguru, PyYAML, psutil, Redis client, nats-py, docker SDK, proxmoxer, and the anthropic SDK.

FACT: Total Python source is ~4,904 lines across 53 .py files (application code + tests combined); the application code (excluding tests/) is ~2,858 lines.

INTERPRETATION: This is a small, young, single/dual-maintainer codebase — proportionate in scope to its stated ambitions ("What Works Today" in the README), not an enterprise-scale system.

CONSEQUENCE: Findings in this audit should be read at the appropriate scale: this is a pre-alpha homelab tool, and findings are calibrated against that context, not against a mature production system.

CONFIDENCE: Very High (directly observed from git log, pyproject.toml, and file counts).

Architecture Assessment
FACT: The repository is organized as a modular monolith with the following top-level domains: apps/cli (Typer CLI), packages/core (FastAPI app, config, database, persistence, diagnostics, discovery, plugin manager, event bus), packages/blueprints (domain model, loader, planner, executor, template resolver), packages/orchestrator (Task, TaskGraph, Scheduler), packages/provider_sdk (BaseProvider ABC, registry, exceptions, models), packages/providers/{docker,proxmox} (concrete provider implementations), and plugins/ (dynamically loaded extension modules).

INTERPRETATION: This maps cleanly onto a layered/hexagonal-ish style: provider_sdk defines a port (BaseProvider ABC), providers/* are adapters, blueprints/orchestrator form the domain/application layer, and core hosts the FastAPI delivery mechanism plus shared infrastructure concerns (config, DB, events, plugins). apps/cli is a second delivery mechanism sitting alongside the API, both calling directly into the same blueprints/orchestrator/core layer rather than duplicating logic.

FACT: apps/cli/main.py imports directly from blueprints.executor, blueprints.loader, blueprints.planner, core.database, core.diagnostics, core.discovery, core.repository, core.resource_actions, and orchestrator.scheduler — the same modules packages/core/main.py (the API) imports.

INTERPRETATION: The CLI is a thin delivery layer, not a second implementation of business logic. This is a positive architectural consistency signal — the two entry points do not duplicate rules.

FACT: There is no dependency-injection framework, no ports/adapters registry beyond ProviderRegistry, and configuration/state is accessed via module-level singletons (get_settings() with @lru_cache, a module-level registry instance, a module-level event_bus instance, module-level _engine/_session_factory in core/database.py).

INTERPRETATION: Global mutable singletons are an acceptable pattern for a small single-process application but constitute a scalability and testability constraint (discussed further under Module Assessment and Technical Debt).

CONSEQUENCE: The architecture is coherent and appropriately scoped for the project's current size, but the reliance on shared mutable singletons for provider clients is the single largest architectural risk identified in this audit (see Risk Matrix, RISK-01).

CONFIDENCE: High.

Repository Structure Assessment
FACT: Top-level directories: apps/, docs/, migrations/, packages/, plugins/, tests/. Configuration/tooling files at root: .dockerignore, .editorconfig, .env.example, .gitattributes, .gitignore, .pre-commit-config.yaml, Dockerfile, LICENSE, Makefile, README.md, alembic.ini, docker-compose.yml, mkdocs.yml, pyproject.toml, pyrightconfig.json, ruff.toml, uv.lock.

FACT: docs/ contains exactly one file: docs/ses/SES-0000-MASTER-INDEX.md (379 lines), a vision/methodology document (partly in Czech) explicitly labeled Generated by: OpenAI ChatGPT in its own YAML metadata block, intended as an index for a longer-term specification series that is not otherwise present in the repository.

FACT: mkdocs.yml declares a navigation referencing index.md, architecture.md, installation.md, and development.md under docs_dir: docs. None of these four files exist anywhere in the repository; only docs/ses/SES-0000-MASTER-INDEX.md exists, which is not referenced in mkdocs.yml's nav.

INTERPRETATION: The MkDocs site configuration is broken as committed — running mkdocs build or mkdocs serve (as invoked by the Makefile's docs target) would either fail or render four navigation entries pointing at nonexistent pages, while the one real content file is unreachable from the site navigation.

CONSEQUENCE: Documentation tooling is present but non-functional; anyone relying on make docs or mkdocs-material (both declared as dev dependencies) would encounter an immediate build/navigation problem.

CONFIDENCE: Very High (directly verified: find docs -type f returns one file; mkdocs.yml nav lists four different filenames).

FACT: The README's own "Repository Structure" section accurately matches the actual directory layout (apps/cli/, packages/core/, packages/blueprints/, packages/orchestrator/, packages/provider_sdk/, packages/providers/, tests/, docs/ses/).

INTERPRETATION: Structural documentation of the source tree itself is accurate and current, in contrast to the MkDocs site configuration, which is stale/incomplete.

CONFIDENCE: High.

Module Assessment
packages/core (FastAPI app, config, database, events, plugin manager, diagnostics, discovery, repository)
FACT: core/config.py defines a single Settings (Pydantic BaseSettings) class with postgres_url, redis_url, and nats_url fields, all with default values, read from a .env file with STARCORE_ prefix.

FACT: A repository-wide search (grep -rn "redis"/"nats"/"postgres_url" across all .py files) shows these three settings are referenced only inside core/config.py itself (as field declarations/defaults) and nowhere else in application code — no Redis client, no NATS client, and no Postgres connection code exists in the source tree, only in docker-compose.yml service definitions.

INTERPRETATION: Redis, NATS, and Postgres are scaffolded/reserved for future use but are entirely dead configuration today. This matches the README's own disclosure ("Postgres, Redis, and NATS services are also defined in docker-compose.yml for future use but are not yet wired into the application").

CONSEQUENCE: Low operational risk (the services aren't relied upon), but the corresponding Python dependencies (redis, nats-py) and Docker Compose services add build/runtime footprint and potential confusion for anyone assuming they are active. Also a security surface note: docker-compose.yml sets a hardcoded Postgres password (POSTGRES_PASSWORD: starcore) for a service that is unused by the application but is exposed on host port 5432.

CONFIDENCE: Very High.

FACT: core/database.py uses module-level globals _engine and _session_factory, initialized lazily by init_db(), and calls Base.metadata.create_all(bind=_engine) unconditionally inside init_db().

FACT: The repository separately contains a full Alembic migration setup (alembic.ini, migrations/env.py, migrations/versions/0001_initial_schema.py), and the Dockerfile's CMD runs alembic upgrade head before starting Uvicorn.

INTERPRETATION: Two schema-management mechanisms are active simultaneously: SQLAlchemy's create_all() (which creates any missing tables based on current ORM models, ignoring migration history) and Alembic (which tracks explicit, versioned schema changes). The README itself flags this: "create_all() still runs on app start for dev convenience."

CONSEQUENCE: This is a legitimate but reasonable-for-now dev/production divergence risk: if ORM models and the Alembic migration history ever drift out of sync, create_all() can mask a missing migration in local/dev runs (tables silently appear without going through Alembic) while a fresh production deployment relying solely on alembic upgrade head would behave differently. The repository is honest about this being a deliberate, temporary trade-off rather than an oversight.

CONFIDENCE: High.

FACT: core/main.py's verify_api_key() dependency compares the supplied X-API-Key header to settings.api_key using Python's standard != operator, not a constant-time comparison (e.g., hmac.compare_digest).

INTERPRETATION: This is a low-severity timing-attack surface: a network-observable equality check performed on a secret shared across all API consumers. Exploitability requires an attacker with fine-grained network timing access and many attempts; not a high-severity issue for a homelab tool, but a deviation from security best practice for secret comparison.

CONSEQUENCE: Documented as RISK-04 in the Risk Matrix.

CONFIDENCE: High (direct code observation of x_api_key != settings.api_key).

FACT: Authentication is a single shared static API key (STARCORE_API_KEY) applied uniformly to nearly all endpoints (/providers, /diagnostics, /proxmox/discover, /resources/action, /plugins, /ai/generate-blueprint, /blueprints/plan, /blueprints/run, /runs*); only /, /health, and static UI assets are public. There is no per-user identity, no RBAC, and no rate limiting.

INTERPRETATION: This is an appropriate authentication model for a single-operator homelab tool but would not meet multi-tenant or team-access requirements without further work.

CONFIDENCE: Very High.

FACT: list_runs() in core/repository.py executes session.query(BlueprintRunRecord).order_by(...).all() with no LIMIT/pagination, and the /runs endpoint returns this unbounded list directly.

INTERPRETATION: Acceptable at current scale (SQLite, single-operator, low run volume) but is a latent scalability bottleneck as run history grows.

CONFIDENCE: High.

packages/blueprints (domain model, loader, planner, executor, template resolver)
FACT: ExecutionPlanner.create_plan() returns a flat list of {provider, resource, kind, config} dicts derived from blueprint.resources in file-declaration order, and does not include or consult each ResourceSpec.depends_on. BlueprintExecutor.execute() (the sequential execution path, used by default in both CLI blueprint run and API POST /blueprints/run when parallel=False) iterates this plan strictly in that order.

FACT: By contrast, ExecutionPlanner.create_graph() and orchestrator/scheduler.py's Scheduler.execute() (the --parallel path) explicitly build a dependency graph from depends_on and only run a task once all of its declared dependencies have completed.

INTERPRETATION: depends_on is a first-class, documented feature of the Blueprint schema (used in the README's own example blueprint and in packages/blueprints/examples/graph.yaml) but is silently ignored by the default (sequential, non---parallel) execution path. A blueprint author who lists resources out of dependency order and runs starcore blueprint run without --parallel will have resources created in file order regardless of declared dependencies, with no warning or error.

CONSEQUENCE: This is the most significant functional/architectural inconsistency found in the audit. For a tool whose core value proposition is safe, dependency-aware infrastructure orchestration, silently disregarding declared dependencies in the default execution mode is a correctness gap that could cause a resource to be created before a dependency it needs actually exists (e.g., a VM depending on a Docker container for a database, created before the container in sequential mode purely due to YAML ordering).

CONFIDENCE: Very High (directly verified by reading planner.py and executor.py: create_plan() has no reference to depends_on, and BlueprintExecutor.execute() iterates plan — the output of create_plan() — in list order with no dependency check).

FACT: template_resolver.py's resolve_templates() connects to the Proxmox provider, resolves template aliases to template_vmid, and disconnects — independent of whichever execution path (sequential or parallel) subsequently runs.

INTERPRETATION: This module is well-isolated and correctly guarded (a no-op for blueprints that don't use the template shorthand, per its own docstring), and includes ambiguity detection (raises when a template name matches multiple node/vmid pairs).

CONFIDENCE: High.

packages/orchestrator (Task, TaskGraph, Scheduler)
FACT: Task is a @dataclass(slots=True) with a TaskStatus StrEnum; TaskGraph is a simple adjacency-map structure; Scheduler.execute() runs tasks in dependency-respecting "waves" via asyncio.gather, and marks all still-incomplete tasks FAILED with a logged error if a wave produces no ready tasks (i.e., on unresolved or cyclic dependencies).

INTERPRETATION: The cyclic/unresolved-dependency stall-detection is a genuinely good defensive design choice — the scheduler does not hang indefinitely on a cycle.

FACT: Scheduler._run_task() calls provider.connect() independently for every task, on a shared singleton BaseProvider instance retrieved from the global registry, and multiple tasks in the same "wave" that target the same provider are dispatched concurrently via asyncio.gather.

FACT: DockerProvider and ProxmoxProvider both store their client as a single instance attribute (self._client), set in connect() and cleared in disconnect(), with no locking, semaphore, or reference counting.

INTERPRETATION: If a blueprint's dependency graph produces a wave containing two or more resources for the same provider (a realistic and unremarkable scenario — e.g., two independent Docker containers with no depends_on between them), Scheduler.execute() will call connect() concurrently on the same shared provider instance from multiple coroutines, each reassigning self._client. This is a data race on shared mutable state; the outcome depends on asyncio scheduling order and could result in one task executing against a client object that a concurrently-running disconnect() call (from a different, unrelated task's finally-adjacent path) may unset, or one connect's client silently overwriting another's mid-flight.

CONSEQUENCE: This is the most significant concurrency-safety risk identified in the audit (RISK-01). It directly undermines the stated benefit of --parallel execution — the feature specifically designed to run independent resources concurrently is the one most exposed to this shared-state hazard, and it affects both of the project's two providers identically since both follow the same single-client-attribute pattern.

CONFIDENCE: High. This is inferred from static code structure (shared instance stored in module-level registry, concurrent dispatch via asyncio.gather, unguarded instance attribute mutation in connect/disconnect); it was not confirmed via runtime reproduction (no test in the suite exercises two same-provider resources without a depends_on edge running under --parallel), so the theoretical race is not empirically demonstrated in this audit, though the code structure supports the described race condition unambiguously.

packages/provider_sdk (BaseProvider, registry, exceptions, models)
FACT: BaseProvider is a minimal ABC with five abstract async methods (connect, disconnect, health, list_resources, execute) plus name/version class attributes. ProviderRegistry is a simple dict[str, BaseProvider] wrapper with register/get/all/names.

INTERPRETATION: This is a clean, minimal port definition appropriate for the project's current scope — two providers. It has no capability-declaration mechanism, no version-compatibility checking beyond an unused version attribute, and no provider isolation (all providers run in-process with full application privileges) — reasonable simplifications at this scale, but constraints that would need addressing before supporting third-party/untrusted providers.

FACT: provider_sdk/models.py defines a Resource Pydantic model (id, name, type, status) that a repository-wide search shows is not imported or used anywhere outside its own file.

INTERPRETATION: Unused/vestigial model; each provider's list_resources() instead returns raw dict objects with provider-specific shapes rather than this shared model.

CONFIDENCE: High.

FACT: packages/provider_sdk, packages/orchestrator, packages/providers, packages/providers/docker, packages/providers/proxmox, and apps/apps/cli do not contain __init__.py files, while packages/ai, packages/blueprints, packages/core, and all plugins/* subdirectories do.

FACT: pyproject.toml's [tool.hatch.build.targets.wheel] explicitly lists apps, packages/ai, packages/core, packages/blueprints, packages/orchestrator, packages/provider_sdk, and packages/providers as packages to build into the wheel.

INTERPRETATION: Several packages that are explicitly declared as build targets (and are imported elsewhere as regular packages, e.g. from orchestrator.task import Task, from provider_sdk.registry import registry) rely on Python's implicit namespace package mechanism rather than explicit __init__.py files. This works under Python 3.3+ and under pytest's pythonpath configuration as currently set up (tests pass), but is structurally inconsistent within the same repository — some packages are explicit, some are implicit, with no documented rationale for the split.

CONSEQUENCE: Low immediate functional risk (the test suite and CI Docker build both pass), but represents a structural-consistency gap that could cause packaging surprises (e.g., with tools or build backends that handle implicit namespace packages differently than hatchling does, or if apps/plugins discoverability rules diverge).

CONFIDENCE: Very High (directly verified via filesystem inspection).

packages/ai (AI blueprint generation)
FACT: generator.py constructs a new AsyncAnthropic client on every call to generate_blueprint_yaml(), uses a single system prompt to constrain output to raw YAML, strips Markdown code fences via regex, and raises a domain-specific BlueprintGenerationError for missing API key, request failure, empty response, or non-text response blocks.

INTERPRETATION: Reasonably defensive for an LLM-integration point (handles malformed/wrapped output, absent credentials, and API failures explicitly) — a positive quality signal. Creating a new client per call is a minor inefficiency, not a correctness issue.

CONFIDENCE: High.

apps/cli (Typer CLI, 547 lines)
FACT: The CLI exposes version, health, blueprint plan/run [--parallel], runs list/show, plugins, diagnose, ai generate, proxmox discover, resource action, and snapshot create/list/delete/rollback, matching the README's "What Works Today" table feature-for-feature.

INTERPRETATION: Documentation-to-implementation fidelity is high for the CLI surface.

CONFIDENCE: High.

plugins/
FACT: PluginManager.discover() scans plugins/ for subdirectories containing __init__.py; load_all() dynamically imports each via importlib, mutating sys.path at runtime (inserting the plugins' parent directory if absent), and calls each module's register(context) function inside a broad try/except Exception, logging and skipping failures.

INTERPRETATION: Plugin isolation is minimal by design at this stage: plugins run with full in-process privileges, no sandboxing, no dependency-version compatibility checks, and no formal API-stability contract beyond the register(context) convention and two example plugins. Failure isolation exists only at the "does register() raise" level — a plugin's imported side effects prior to register() are not isolated. This is appropriate for a single-operator homelab tool's initial plugin mechanism but is not a production-grade sandboxed extension system.

CONFIDENCE: High.

Build System Assessment
FACT: The build backend is hatchling>=1.27.0; packaging targets are declared explicitly in [tool.hatch.build.targets.wheel] and [tool.hatch.build.targets.sdist]. Dependency resolution/locking uses uv (uv.lock present, 1 file).

FACT: Makefile's dev target is uv run python -m packages.core. No __main__.py exists anywhere in the repository (verified via find . -name "__main__.py"), and no packages/__init__.py exists to make packages itself a regular package (it is present only as a directory containing sub-packages).

INTERPRETATION: make dev as committed would fail: python -m packages.core requires a packages/core/__main__.py (absent) and/or packages to be resolvable as import root matching how the rest of the project actually starts the API (uv run uvicorn core.main:app, as documented correctly in the README's own Quick Start and the Dockerfile's CMD). The Makefile's dev target is inconsistent with every other place in the repository that documents how to run the API.

CONSEQUENCE: A new contributor following make dev (rather than the README) would hit an immediate, avoidable failure. This is a concrete, reproducible build-tooling defect.

CONFIDENCE: Very High (directly verified: Makefile line dev: uv run python -m packages.core; find . -name "__main__.py" returns no results anywhere in the repository).

FACT: Makefile's lint, format, and test targets (ruff check ., ruff format ., pytest) omit the uv run prefix used everywhere else (install, dev) and used consistently throughout the README's own "Development" section (uv run ruff check ., uv run pytest -q).

INTERPRETATION: These targets only work correctly if a virtual environment is already active in the invoking shell; they are inconsistent with the project's own stated uv-centric workflow and with the README.

CONSEQUENCE: Minor tooling-consistency defect; likely to produce a "command not found" or wrong-interpreter error for a user who has not manually activated .venv before running make lint/make test.

CONFIDENCE: Very High (direct file comparison).

FACT: CI (.github/workflows/ci.yml) installs Python 3.12 explicitly via uv python install 3.12 and runs uv sync --extra dev, ruff check ., pyright, and pytest -q. It does not invoke the Makefile at all — CI and the Makefile are two independent, divergent definitions of the same "run quality checks" workflow.

INTERPRETATION: Because CI never exercises the Makefile targets, the two defects above (make dev, missing uv run prefixes) are undetected by automation and would only surface for a human contributor manually using make.

CONFIDENCE: Very High.

FACT: The Dockerfile builds cross-platform-agnostic (python:3.14-slim base), copies only the files needed for uv sync --frozen to succeed (including a since-added README.md copy, per commit 25367e5, "required by hatchling for uv sync --frozen"), and produces a working image that CI's docker-build job smoke-tests against /health.

INTERPRETATION: Build reproducibility for the Docker path is good and has evidently already been debugged through iteration (the README-copy fix commit is direct evidence of an issue found and fixed).

CONFIDENCE: High.

Dependency Assessment
FACT: Runtime dependencies (19 packages) are pinned with lower-bound (>=) constraints only, no upper bounds, resolved and locked via uv.lock. Dev dependencies (8 packages) are declared under [project.optional-dependencies].dev; a separate [dependency-groups].dev declares only pre-commit>=4.6.0.

INTERPRETATION: Two different dev-dependency mechanisms (optional-dependencies.dev and dependency-groups.dev) are used side by side for what is conceptually the same "developer tooling" concern, with pre-commit isolated into the second group while pytest, ruff, mypy, pyright, mkdocs* live in the first. This is a minor, unexplained split rather than a clearly justified separation (e.g., it is not "test deps vs. lint deps").

CONFIDENCE: Medium (the split is directly observable; the rationale, if any, is not documented in the repository).

FACT: pytest-cov>=6.2.1 is declared as a dev dependency. A repository-wide search of .github/workflows/*.yml, Makefile, and pyproject.toml for cov finds no --cov invocation, no [tool.coverage.*] configuration, and no coverage-reporting step anywhere.

INTERPRETATION: pytest-cov is an unused dependency — declared but never exercised. No code-coverage percentage is measured or reported anywhere in the project.

CONSEQUENCE: Testing maturity cannot be quantified by coverage percentage; the "114 passing" figure in the README describes test count, not coverage.

CONFIDENCE: Very High.

FACT: mypy>=1.17.0 is declared as a dev dependency with a [tool.mypy] configuration block in pyproject.toml, but is invoked in neither .pre-commit-config.yaml nor .github/workflows/ci.yml (only ruff and pyright run in both).

INTERPRETATION: Two static type checkers (mypy and pyright) are configured, but only one (pyright) is actually enforced in CI/pre-commit. mypy's configuration is currently dead weight.

CONFIDENCE: Very High.

FACT: Dependabot (.github/dependabot.yml) is configured for pip, github-actions, and docker ecosystems on a weekly schedule, with a 10-PR-limit for pip. Git history shows Dependabot PRs being regularly merged (e.g., actions/checkout 4→7, astral-sh/setup-uv 3→7, Python base image 3.12-slim→3.14-slim).

INTERPRETATION: Dependency-update hygiene is actively maintained, which is a positive signal distinct from — and not a substitute for — dependency vulnerability scanning (e.g., pip-audit, GitHub Dependabot security alerts / pip-audit-style CVE scanning), which is not separately configured or evidenced in this repository.

CONFIDENCE: High.

Configuration Assessment
FACT: ruff.toml (line-length 100, target-version = "py312", select = ["E","F","I","UP"]) exists as a standalone file, while pyproject.toml also contains a [tool.ruff] block (target-version = "py312" only, no select). Ruff resolves configuration from the nearest ruff.toml/.ruff.toml first, meaning ruff.toml takes precedence and the [tool.ruff] block in pyproject.toml is effectively dead configuration.

INTERPRETATION: Two overlapping, partially-redundant Ruff configuration sources exist in the same repository, one of which is silently ignored by the tool at runtime.

CONSEQUENCE: Low functional risk (Ruff still runs correctly using ruff.toml), but a real source of confusion for a contributor who edits pyproject.toml's [tool.ruff] block expecting it to take effect.

CONFIDENCE: High (based on Ruff's documented configuration-precedence behavior; both files were directly inspected and independently confirmed to both declare [tool.ruff]/root-level Ruff settings).

FACT: pyrightconfig.json sets "pythonVersion": "3.11" and "include": ["packages"], while pyproject.toml declares requires-python = ">=3.12" and Ruff targets py312.

INTERPRETATION: Pyright is configured to type-check against a Python version (3.11) lower than the project's actual minimum supported version (3.12), and its include scope covers only packages/, excluding apps/ (the CLI) and tests/ from type checking entirely. CI's uv run pyright therefore never type-checks the CLI or the test suite, and validates the packages/ code against an older language-version baseline than the project targets.

CONSEQUENCE: Type-checking coverage is narrower than the stated tooling suggests, and the version mismatch could mask usage of Python 3.12-only syntax/features as "safe" under Pyright's 3.11 baseline (though in practice this is a soundness gap in the checking, not necessarily an active bug — no 3.12-only construct misuse was identified in this audit).

CONFIDENCE: Very High (both values directly read from their respective files).

FACT: .env.example documents every setting consumed by core/config.py, is consistent with the Settings field names (once STARCORE_ prefix and case are accounted for), and is correctly excluded from version control via .gitignore (.env, .env.local).

INTERPRETATION: Configuration documentation-to-implementation fidelity is high; this is a positive finding.

CONFIDENCE: Very High.

FACT: docker-compose.yml hardcodes POSTGRES_PASSWORD: starcore for the (currently unused, per above) Postgres service, and none of the four services (api, postgres, redis, nats) define a Compose healthcheck or depends_on ordering.

INTERPRETATION: For the services that matter today (api), the absence of a healthcheck is a minor operational gap (there is a working /health endpoint that a healthcheck could target but does not). For the unused scaffolding services, this is lower priority since they aren't relied upon by the application.

CONFIDENCE: High.

Testing Assessment
FACT: 114 test functions exist across 16 files in tests/ (~1,943 lines), covering AI generation, the API surface, authentication, blueprint loading/validation, the CLI, diagnostics, discovery, the event bus, graph execution, health endpoints, database migrations, persistence, the plugin manager, providers, resource actions, the scheduler, and template resolution — this list corresponds closely to essentially every module in packages/ and apps/.

FACT: tests/conftest.py defines three autouse fixtures: an isolated per-test SQLite database (via tmp_path), an injected test API key with get_settings.cache_clear() before/after, and an event-bus subscriber reset before/after each test.

INTERPRETATION: This is disciplined test isolation — tests do not leak database state, cached settings, or event subscriptions across test functions, which is a meaningfully above-average practice for a project this size/age.

FACT: tests/test_providers.py and related files mock external systems (unittest.mock.patch/MagicMock) rather than requiring a live Docker daemon or Proxmox host; tests/test_auth.py uses FastAPI's TestClient against the real app object with the real dependency-injected auth check.

INTERPRETATION: External-system tests are correctly isolated from the tests' own reliability (no live-infrastructure dependency in CI), while internal logic (auth, blueprint loading, planning, scheduling) is tested against real code paths rather than over-mocked. This is a good balance of unit vs. integration-style testing for the project's scope.

CONFIDENCE: High.

FACT: No coverage percentage is measured (see Dependency Assessment — pytest-cov unused). No load/performance tests, no explicit concurrency-stress tests (e.g., exercising Scheduler with two same-provider, no-dependency tasks in the same wave — the exact scenario underlying RISK-01) were found in the test suite.

INTERPRETATION: Test breadth (module coverage by file/feature) is good; test depth on concurrency correctness and performance-critical paths is not evidenced.

CONSEQUENCE: The concurrency race condition identified under Module Assessment (Scheduler/shared provider client) is not caught by the existing test suite because no test constructs the specific "two same-provider tasks, same wave, no depends_on between them" scenario.

CONFIDENCE: High (based on file-by-file review of tests/*.py filenames and representative content; a scenario-by-scenario enumeration of every test body was not exhaustively performed for all 114 tests, so "Insufficient evidence" applies to any claim about tests not explicitly reviewed line-by-line).

Documentation Assessment
FACT: README.md is structured, accurate, and explicitly self-scoped: it distinguishes "What Works Today" from "What's Planned, Not Built Yet" in two separate tables, and states outright that it "reflects the actual current state of the codebase, not the long-term vision," pointing readers to docs/ses/ for vision content.

INTERPRETATION: This is a materially above-average documentation practice — the audit's own cross-checking (CLI commands, API endpoints, Docker workflow, dependency list) found the README's technical claims to be accurate against the actual code, with no identified discrepancy between README claims and implementation.

CONFIDENCE: Very High.

FACT: docs/ses/SES-0000-MASTER-INDEX.md is a single 379-line file that is itself a meta-document about a planned documentation methodology ("From now on we start creating real documentation... every document will have a professional header, metadata, and AI instructions"), explicitly generated by an external AI tool per its own embedded metadata, rather than substantive architecture/installation/API documentation.

INTERPRETATION: The "long-term vision" documentation referenced by the README exists only as an index/scaffold for a specification series that has not yet been written; no SES-0001 or later document exists in the repository.

CONSEQUENCE: A reader following the README's pointer to docs/ses/ for vision/roadmap content will find only a meta-document about how documentation will eventually be structured, not the vision content itself.

CONFIDENCE: Very High.

FACT: No CONTRIBUTING.md, SECURITY.md, or CODEOWNERS file exists anywhere in the repository. A .github/pull_request_template.md exists with a minimal "What changed / Why / Testing (checklist)" structure.

INTERPRETATION: Baseline open-source governance documentation is largely absent beyond the PR template and the (Apache-2.0) LICENSE file.

CONFIDENCE: Very High.

FACT: No architecture diagrams, ADRs (Architecture Decision Records), or API reference documentation (e.g., generated OpenAPI docs published anywhere, beyond FastAPI's automatic /docs endpoint which was not verified as documented/linked) were found.

INTERPRETATION: Documentation is currently narrative (README) rather than diagrammatic or decision-record-based; appropriate for current scale but a gap that would need addressing as module count/contributor count grows.

CONFIDENCE: High.

Infrastructure Assessment
FACT: Dockerfile uses python:3.14-slim, installs uv via the official install script, copies only necessary source (apps, packages, migrations, alembic.ini, plugins, plus manifest/README files), runs uv sync --frozen, declares a /data volume, exposes port 8000, and its CMD runs alembic upgrade head before starting Uvicorn — meaning migrations are applied automatically on every container start.

INTERPRETATION: This is a reasonable, minimal, single-stage container build. It is not a multi-stage build (no separate build/runtime image split), so build-time tooling (uv installer, curl, ca-certificates) remains in the final runtime image, which increases image size versus a multi-stage equivalent but does not itself constitute a functional defect.

FACT: docker-compose.yml defines four services (api, postgres, redis, nats); of these, only api is actually consumed by the application (per Dependency/Module Assessment above). No named health checks, no explicit depends_on/startup ordering, and one hardcoded credential pair (postgres/postgres, unused).

INTERPRETATION: Infrastructure-as-scaffolding for a stated future architecture (Postgres/Redis/NATS-backed) exists but is not yet load-bearing.

CONFIDENCE: High.

FACT: There is no Kubernetes manifest, Helm chart, Terraform/IaC definition, or cloud-provider-specific deployment configuration anywhere in the repository — deployment is Docker Compose (or bare uv run) only.

INTERPRETATION: Consistent with the project's stated homelab/self-hosted scope; not a gap relative to the project's own stated goals, though it does mean "infrastructure" in this audit's sense is limited to container-level artifacts.

CONFIDENCE: Very High.

Security Assessment
FACT: No hardcoded secrets, API tokens, or credentials were found in application source code (repository-wide regex search for password/secret/token = "..." patterns outside of test files returned no matches). .env and .env.local are correctly gitignored. .env.example contains only placeholder/empty values.

FACT: API authentication is a single static shared-secret header (X-API-Key), compared via non-constant-time != (see Module Assessment, core/main.py). The API returns HTTP 503 (not silently permissive) if no key is configured server-side, which is a secure-by-default choice (fails closed, not open).

FACT: No CORS configuration was found in core/main.py; FastAPI's default (no CORS middleware registered) effectively blocks cross-origin browser requests unless explicitly configured, which is a safe default for an API not intended for arbitrary browser-based cross-origin consumption.

FACT: No rate-limiting middleware or dependency was found anywhere in the dependency list or source code.

INTERPRETATION: In combination — a single static API key with no rate limiting — a network-positioned attacker with an incorrect-key list could attempt unbounded guessing attempts against X-API-Key without any throttling. Given the key is expected to be a high-entropy random secret (per .env.example's own guidance, "change-me-to-a-random-secret"), brute-force feasibility is low if that guidance is followed, but the absence of rate limiting is nonetheless a defense-in-depth gap.

CONFIDENCE: High.

FACT: No dependency-vulnerability scanning tool (e.g., pip-audit, safety, Trivy, GitHub CodeQL, or Dependabot security alerts beyond version-bump PRs) is configured in .github/workflows/*.yml.

INTERPRETATION: Dependency freshness is actively maintained (Dependabot version PRs), but dependency vulnerability scanning is not separately evidenced in this repository's CI configuration.

CONFIDENCE: Very High.

FACT: Proxmox credentials (STARCORE_PROXMOX_TOKEN_VALUE, etc.) and the Anthropic API key are read from environment/.env only, never logged in the reviewed source (log statements in providers/proxmox/provider.py and ai/generator.py reference exceptions/config state without printing secret values directly, based on the code reviewed).

INTERPRETATION: Secret-handling hygiene in application code appears sound based on the modules reviewed.

CONFIDENCE: Medium (not every log call site in the 2,858-line application codebase was individually audited for secret leakage; this conclusion is based on the provider, config, and AI-generator modules specifically reviewed).

FACT: No container security hardening (non-root user, read-only root filesystem, dropped capabilities) is configured in the Dockerfile; the container runs as root by default (no USER directive present).

INTERPRETATION: Standard container-hardening practice is not applied. Common for early-stage projects, but a legitimate operational-security gap for anything beyond a trusted homelab network.

CONFIDENCE: Very High.

Operational Readiness
FACT: A /health endpoint exists (public, unauthenticated, returns {"status": "healthy"} unconditionally — it does not check database connectivity or provider reachability). A separate, authenticated /diagnostics endpoint (and starcore diagnose CLI command) performs a deeper check: config validation, database connectivity, Alembic migration-head comparison, and provider health/capacity checks (per core/diagnostics.py).

INTERPRETATION: /health is a liveness-style check only (process is up), while /diagnostics is closer to a readiness/deep-health check. This is a reasonable separation of concerns, though /health's unconditional "healthy" response means container orchestration relying on it (e.g., the CI Docker smoke test, which does exactly this) would not detect a database or migration failure — only that the HTTP server itself is responding.

CONFIDENCE: Very High.

FACT: Logging uses loguru consistently across modules that log (core, blueprints, orchestrator, providers); no structured (JSON) logging, no correlation/request-ID propagation, and no OpenTelemetry or metrics/tracing integration were found anywhere in the dependency list or source.

INTERPRETATION: Logging is consistent in library choice but is human-readable/unstructured rather than machine-parseable, and there is no distributed-tracing or metrics story. Adequate for single-instance/single-operator debugging; insufficient for multi-instance or SLA-driven operations.

CONFIDENCE: High.

FACT: No documented backup, rollback, or disaster-recovery procedure exists (no SECURITY.md, no runbook, no equivalent document). SQLite data persists via a named Docker volume (starcore-data), but no automated backup mechanism for that volume was found.

INTERPRETATION: Operational maturity for backup/recovery is effectively at the "not yet addressed" stage, consistent with the project's overall pre-alpha status.

CONFIDENCE: High.

Production Readiness
Ratings reflect the repository as it currently exists, evaluated against general production-software expectations, not solely against the project's own (explicitly pre-alpha, homelab-scoped) goals.

Area	Rating	Evidence Basis
Architecture	Acceptable	Coherent modular-monolith layering; undermined by the sequential-execution depends_on gap and shared-provider concurrency risk (see Module/Risk sections).
Build System	Needs Improvement	Working uv/hatchling build and Docker build; but make dev is broken, Makefile/README/CI diverge, and pyproject.toml's [tool.ruff] block is dead.
Packaging	Needs Improvement	Inconsistent __init__.py usage across declared wheel-target packages.
Dependency Management	Good	Locked via uv.lock, Dependabot active across three ecosystems; gap is vulnerability scanning, not freshness.
Configuration	Needs Improvement	.env handling is solid; Ruff/Pyright configuration duplication and version mismatches reduce confidence in the tooling layer.
Infrastructure (Docker)	Acceptable	Working, CI-smoke-tested single-stage build; lacks non-root user and multi-stage optimization; unused Compose services present.
CI/CD	Acceptable	Lint, type-check, test, and Docker-smoke-test run on every PR; no security/dependency-vulnerability scanning; no coverage measurement; publish workflow tags latest/SHA only, no semantic release process.
Testing	Good	114 tests, strong isolation fixtures, appropriate mocking of external systems; no coverage measurement and no concurrency-specific tests for the identified race condition.
Documentation	Acceptable	README is accurate and unusually honest about current-vs-planned state; MkDocs site is non-functional (missing pages); vision docs are an index only.
Logging/Observability	Needs Improvement	Consistent unstructured logging; no metrics, tracing, or structured-log correlation.
Error Handling	Acceptable	Consistent TaskStatus-based failure tracking and broad-but-logged exception handling in execution paths; no project-wide exception hierarchy beyond provider_sdk.exceptions (used only by providers, not more broadly).
Security	Needs Improvement	No secrets found in source, .env correctly excluded, fail-closed auth default; but non-constant-time key comparison, no rate limiting, no dependency-vulnerability scanning, container runs as root.
Deployment	Acceptable	Docker Compose works for the api service; no orchestration platform (K8s/Helm) manifests; single-instance assumption throughout (SQLite default, in-process global state).
Maintenance/Upgrade	Needs Improvement	No documented rollback/backup procedure; dual schema-management (create_all + Alembic) is a deliberate but real ongoing risk as the schema evolves.
Scalability	Needs Improvement	Single-process, global-singleton-state design; unbounded list_runs() query; concurrency-unsafe shared provider clients under the very feature (--parallel) meant to enable concurrency.
Extensibility	Acceptable	Clean Provider SDK abstraction and functioning plugin-discovery mechanism; no plugin sandboxing/versioning.
Developer Onboarding	Good	Accurate README Quick Start, working .env.example, working CI reproducing the documented commands; marred only by the broken make dev target.
Operational Support	Needs Improvement	/health is liveness-only; /diagnostics is a strong deeper check but is authenticated (appropriate) and not wired into any external monitoring integration.
Overall Production Readiness: Needs Improvement. The repository is well-suited to its stated purpose (a personal/homelab infrastructure tool in active development) and is not misrepresented as production-grade by its own documentation. Against general production-software criteria, the combination of the silent depends_on gap, the shared-provider concurrency risk, and the absence of security/coverage scanning are the primary blockers to a "Good" or higher overall rating.

CONFIDENCE: High (ratings are evidence-derived per row; overall synthesis carries the aggregate confidence of its lowest-confidence contributing rows, which range Medium–Very High).

Technical Debt
ID	Category	Description	Evidence	Impact	Severity	Confidence
TD-01	Architecture	Sequential blueprint execution ignores depends_on	blueprints/planner.py::create_plan, blueprints/executor.py::execute	Resources can be created out of declared dependency order in default (non---parallel) mode	High	Very High
TD-02	Architecture / Concurrency	Provider client state (self._client) is unsynchronized and shared via a global singleton registry, while the scheduler dispatches same-provider tasks concurrently	orchestrator/scheduler.py, providers/docker/provider.py, providers/proxmox/provider.py, provider_sdk/registry.py	Potential race conditions under --parallel execution when a wave contains ≥2 tasks for the same provider	High	High
TD-03	Packaging	Inconsistent __init__.py presence across packages declared as wheel build targets	Filesystem inspection vs. pyproject.toml [tool.hatch.build.targets.wheel]	Structural inconsistency; latent packaging-tool-compatibility risk	Medium	Very High
TD-04	Build System	Makefile's dev target references a nonexistent __main__.py entry point	Makefile, find . -name "__main__.py" (no results)	make dev fails outright	Medium	Very High
TD-05	Build System	Makefile's lint/format/test targets omit uv run, inconsistent with install/dev targets and the README	Makefile vs. README.md Development section	Confusing/broken developer workflow outside an already-activated venv	Low	Very High
TD-06	Documentation	mkdocs.yml navigation references four pages (index.md, architecture.md, installation.md, development.md) that do not exist	mkdocs.yml, find docs -type f	mkdocs build/serve non-functional as committed	Medium	Very High
TD-07	Configuration	Duplicate/conflicting Ruff configuration (ruff.toml vs. pyproject.toml [tool.ruff])	Both files inspected directly	One config block is silently inert; contributor confusion risk	Low	High
TD-08	Configuration	Pyright targets Python 3.11 while the project requires ≥3.12, and only type-checks packages/ (excludes apps/, tests/)	pyrightconfig.json vs. pyproject.toml requires-python	Narrower and version-mismatched type-checking coverage than intended	Medium	Very High
TD-09	Testing / Tooling	pytest-cov declared as a dependency but never invoked; no coverage measurement anywhere	pyproject.toml, CI workflow, Makefile — no --cov usage found	Testing maturity cannot be quantified by coverage; dead dependency	Low	Very High
TD-10	Tooling	mypy configured in pyproject.toml but never run in CI or pre-commit (only Ruff and Pyright are enforced)	.pre-commit-config.yaml, .github/workflows/ci.yml	Second type checker's configuration is dead weight; no dual-tool cross-validation actually occurs	Low	Very High
TD-11	Security	Non-constant-time comparison of the API key (x_api_key != settings.api_key)	core/main.py::verify_api_key	Low-severity timing side-channel on a shared secret	Low	High
TD-12	Security	No rate limiting on any endpoint, including the authenticated ones	Full review of core/main.py and dependency list	Unbounded credential-guessing / abuse potential absent external mitigation	Medium	High
TD-13	Security	No dependency-vulnerability scanning (only version-freshness via Dependabot)	.github/workflows/*.yml, .github/dependabot.yml	Known-CVE dependencies could go undetected between manual review cycles	Medium	Very High
TD-14	Security / Infrastructure	Container runs as root (no USER directive in Dockerfile)	Dockerfile full review	Elevated container-breakout blast radius versus a non-root design	Low	Very High
TD-15	Infrastructure	docker-compose.yml defines Postgres/Redis/NATS services that are entirely unused by application code, including a hardcoded Postgres password	docker-compose.yml vs. repo-wide redis/nats/postgres_url usage search	Unused attack surface and operational footprint; low-severity hardcoded credential on an inert service	Low	Very High
TD-16	Operational Readiness	/health returns unconditional "healthy" with no dependency checks (DB, providers)	core/main.py::health	Container/orchestration health checks relying on /health cannot detect DB or migration failures	Medium	Very High
TD-17	Maintainability	Dual schema-management mechanisms active simultaneously (Base.metadata.create_all() and Alembic migrations)	core/database.py::init_db, migrations/, README's own disclosure	Risk of schema drift between ORM models and migration history over time	Medium	High
TD-18	Governance	No CONTRIBUTING.md, SECURITY.md, or CODEOWNERS	Filesystem inspection	Contributor/security-reporting process undocumented	Low	Very High
TD-19	Code Quality	provider_sdk/models.py::Resource model is defined but unused anywhere in the codebase	Repository-wide import search	Vestigial/dead code	Low	High
TD-20	Scalability	list_runs() / GET /runs has no pagination or limit	core/repository.py::list_runs	Latent scalability bottleneck as run history grows	Low	High
Risk Matrix
Risk ID	Category	Description	Evidence	Likelihood	Impact	Severity	Confidence	Priority
RISK-01	Architecture / Concurrency	Race condition on shared, unsynchronized provider client state during concurrent (--parallel) execution of same-provider tasks	orchestrator/scheduler.py, providers/*/provider.py (structural analysis; not empirically reproduced)	Medium (requires a specific but realistic blueprint shape: ≥2 same-provider, no-mutual-depends_on resources)	High (incorrect/undefined provider client state during infrastructure-mutating operations)	High	High	High
RISK-02	Architecture / Correctness	Sequential (default) execution mode silently ignores declared depends_on ordering	blueprints/planner.py, blueprints/executor.py	High (any blueprint with out-of-order dependent resources, run without --parallel)	High (resources could be created before a declared dependency exists)	High	Very High	Critical
RISK-03	Security	No rate limiting on authenticated or public endpoints	core/main.py full review	Medium	Medium	Medium	High	Medium
RISK-04	Security	Non-constant-time API key comparison	core/main.py::verify_api_key	Low (requires network-timing access)	Low–Medium	Low	High	Low
RISK-05	Security	No automated dependency-vulnerability (CVE) scanning	.github/workflows/*.yml, dependabot.yml	Medium (accumulates over time without manual review)	Medium	Medium	Very High	Medium
RISK-06	Build/Packaging	Inconsistent implicit-namespace vs. explicit packages among wheel build targets	Filesystem + pyproject.toml cross-check	Low (works today under current tooling)	Medium (could surface under different packaging tools/versions)	Low	Very High	Low
RISK-07	Build Tooling	Broken make dev target and Makefile/README/CI divergence	Makefile direct review	High (any contributor using make dev as documented convention)	Low (workaround exists via README)	Low	Very High	Low
RISK-08	Documentation	Non-functional MkDocs site (missing referenced pages)	mkdocs.yml, docs/ filesystem	High (any attempt to build/serve docs)	Low (README remains the accurate source)	Low	Very High	Low
RISK-09	Maintainability	Dual schema-management (create_all + Alembic) risking drift	core/database.py, migrations/, README disclosure	Medium (increases as schema changes accumulate)	Medium	Medium	High	Medium
RISK-10	Operational Readiness	/health does not reflect actual dependency health (DB/providers)	core/main.py::health	High (always true, by design)	Low–Medium (masks real failures from shallow health checks)	Low	Very High	Low
RISK-11	Infrastructure	Container runs as root; no non-root hardening	Dockerfile	Low–Medium (requires a separate container-escape vector to matter)	Medium	Low	Very High	Informational
RISK-12	Governance	No SECURITY.md / vulnerability-disclosure process	Filesystem inspection	Low	Low	Low	Very High	Informational
Repository Health Score
Methodology: each dimension scored 0–100 based on the evidence gathered in the corresponding assessment section above; overall score is an unweighted average, explicitly not a certified/standardized industry metric, offered as a relative summary rather than an absolute benchmark.

Dimension	Score	Basis
Architecture	65	Coherent layering and provider abstraction (positive); undermined by RISK-01/RISK-02, the two highest-severity findings in this audit.
Code Quality	75	Consistent style, type hints, dataclasses, small well-scoped functions across reviewed modules; some dead code (TD-19) and inconsistent exception-handling breadth (broad except Exception in 9 files, always logged, not silently swallowed).
Packaging	55	Working build, but TD-03 (inconsistent __init__.py) and TD-04/TD-05 (Makefile defects) are concrete, verifiable defects.
Build System	60	Same basis as Packaging; CI itself is solid, but Makefile/CI/README divergence is real.
Configuration	55	.env handling is strong; Ruff/Pyright duplication and version mismatches (TD-07, TD-08) pull this down.
Documentation	70	README is accurate and unusually honest; MkDocs site and vision docs are non-functional/incomplete (TD-06).
Testing	78	114 tests, strong isolation fixtures, appropriate mocking; no coverage measurement, no concurrency-specific tests for RISK-01.
Automation (CI/CD)	68	Real lint/type-check/test/Docker-smoke-test gate on every PR; no security scanning, no coverage gate, no semantic release process.
Security	58	No committed secrets, fail-closed auth default, correctly gitignored .env (positives); no rate limiting, non-constant-time comparison, no CVE scanning, root container (negatives).
Infrastructure	65	Working, CI-tested Docker build; unused Compose scaffolding and lack of container hardening.
Operations	50	Shallow /health, no metrics/tracing, no documented backup/rollback procedure; a genuinely strong /diagnostics endpoint partially offsets this.
Developer Experience	75	Accurate README, working .env.example, functioning CI reproducing documented commands; broken make dev is the main detractor.
Maintainability	68	Small, consistent, well-tested codebase today; dual schema-management and global-singleton patterns are latent risks as it grows.
Scalability	55	Single-process, global-state design; RISK-01 concurrency issue directly undermines the one built-in scaling mechanism (--parallel).
Production Readiness	52	See detailed ratings table above; "Needs Improvement" as an aggregate.
Overall Repository Health Score: 63 / 100

INTERPRETATION: This score reflects a young, actively-developed, honestly-documented project with real engineering discipline (testing, CI, no secret leakage) that has not yet closed several concrete architectural, packaging, and security-hardening gaps — consistent with an 11-day-old pre-alpha (0.1.0-dev) codebase rather than a systemic quality failure. The score should not be read as "poor engineering"; it reflects the current maturity stage against general production-software criteria, not against the project's own stated (and currently accurate) self-assessment.

CONFIDENCE: Medium-High (individual dimension scores are evidence-grounded per the corresponding sections; the overall averaging methodology is a simplification and is disclosed as such rather than presented as a certified metric).

Prioritized Findings
Critical
RISK-02 / TD-01 — Sequential blueprint execution silently ignores depends_on, contradicting the tool's core "dependency-aware orchestration" value proposition. (Category: Architecture. Confidence: Very High.)
High
RISK-01 / TD-02 — Unsynchronized shared provider client state creates a plausible concurrency race under --parallel execution — the very feature meant to safely enable concurrency. (Category: Architecture/Concurrency. Confidence: High.)
Medium
RISK-03 / TD-12 — No rate limiting on any endpoint. (Category: Security. Confidence: High.)
RISK-05 / TD-13 — No dependency-vulnerability (CVE) scanning, only version-freshness automation. (Category: Security/CI. Confidence: Very High.)
RISK-09 / TD-17 — Dual schema-management mechanisms (create_all + Alembic) risk future drift. (Category: Maintainability. Confidence: High.)
TD-03 — Inconsistent __init__.py usage across declared wheel-build-target packages. (Category: Packaging. Confidence: Very High.)
TD-08 — Pyright version mismatch (3.11 vs. required ≥3.12) and incomplete scope (packages/ only). (Category: Configuration. Confidence: Very High.)
RISK-10 / TD-16 — /health does not reflect actual dependency health. (Category: Operational Readiness. Confidence: Very High.)
Low
RISK-04 / TD-11 — Non-constant-time API key comparison. (Confidence: High.)
TD-04, TD-05 — Broken/inconsistent Makefile targets (dev, missing uv run prefixes). (Confidence: Very High.)
TD-06 / RISK-08 — Non-functional MkDocs site configuration. (Confidence: Very High.)
TD-07 — Duplicate/conflicting Ruff configuration files. (Confidence: High.)
TD-09 — Unused pytest-cov dependency; no coverage measurement. (Confidence: Very High.)
TD-10 — Unused mypy configuration (not run in CI/pre-commit). (Confidence: Very High.)
TD-15 — Unused Postgres/Redis/NATS Compose scaffolding, including a hardcoded (inert) Postgres password. (Confidence: Very High.)
TD-20 — Unbounded GET /runs query (no pagination). (Confidence: High.)
Informational
RISK-11 / TD-14 — Container runs as root; no non-root hardening. (Confidence: Very High.)
RISK-12 / TD-18 — No SECURITY.md, CONTRIBUTING.md, or CODEOWNERS. (Confidence: Very High.)
TD-19 — Unused provider_sdk.models.Resource model. (Confidence: High.)
Two dev-dependency declaration mechanisms (optional-dependencies.dev and dependency-groups.dev) used for the same conceptual purpose without documented rationale. (Confidence: Medium.)
Final Conclusion
Is the repository structurally healthy? Largely yes, with identified exceptions. The directory layout, package boundaries, and CLI/API dual-entry-point design are coherent and consistently applied. The main structural blemishes are the inconsistent __init__.py usage among declared build-target packages (TD-03) and the non-functional MkDocs site (TD-06). Evidence: filesystem inspection, pyproject.toml, mkdocs.yml.

Is the architecture internally consistent? Partially. The provider/blueprint/orchestrator layering is consistent, but the two blueprint-execution paths (BlueprintExecutor sequential vs. Scheduler parallel) diverge in a functionally significant way — only one of them honors declared dependencies (RISK-02). This is the audit's most important architectural-consistency finding.

Is the repository maintainable? Currently yes, at its present size — small codebase, consistent style, strong test isolation, working CI. Two identified factors (dual schema-management, global-singleton state) are latent risks to future maintainability rather than current problems. Evidence: core/database.py, tests/conftest.py, CI configuration.

Is the repository production-ready? No, and it does not claim to be (README explicitly states "active development"). Against general production criteria, the Critical (RISK-02) and High (RISK-01) findings, combined with the absence of security/coverage scanning and shallow health-checking, place it at "Needs Improvement" overall (see Production Readiness table).

Is the repository scalable? Not in its current form beyond a single-process, single-operator deployment: global singleton state, an unbounded list_runs() query, SQLite-by-default, and the RISK-01 concurrency hazard in the one feature (--parallel) explicitly designed for concurrent execution.

Are there architectural risks? Yes — RISK-01 and RISK-02, both detailed above with direct code evidence, are the two most consequential findings in this audit.

Are there operational risks? Yes, primarily around shallow health-checking (RISK-10), absent backup/rollback documentation, and no dependency-vulnerability scanning (RISK-05) — none of which are Critical individually, but which collectively represent a real operational-maturity gap.

Is technical debt manageable? Yes. Twenty technical-debt items were identified (TD-01 through TD-20); the majority are Low severity, well-scoped, and independently addressable without architectural upheaval. Only TD-01/TD-02 (mirrored as RISK-02/RISK-01) require what could be considered non-trivial design attention; the remainder are configuration, tooling, or documentation corrections.

Evidence Appendix
All findings in this report are traceable to one of the following evidence sources, each directly inspected during this audit:

Git metadata: git log (119 commits, 2026-07-04–2026-07-15), git branch -a (single branch main), commit messages showing PR-merge and Dependabot-update patterns.
Build/dependency configuration: pyproject.toml, uv.lock, ruff.toml, pyrightconfig.json, .pre-commit-config.yaml, Makefile.
CI/CD configuration: .github/workflows/ci.yml, .github/workflows/docker-publish.yml, .github/dependabot.yml, .github/pull_request_template.md.
Container/infrastructure configuration: Dockerfile, docker-compose.yml, .dockerignore.
Application source (fully or representatively reviewed): packages/core/*.py (all 12 files), packages/blueprints/*.py (all 5 files), packages/orchestrator/*.py (all 3 files), packages/provider_sdk/*.py (all 4 files), packages/providers/docker/provider.py (full), packages/providers/proxmox/provider.py (fully structurally scanned, representatively read), packages/ai/generator.py (full), apps/cli/main.py (structurally scanned, representatively read), plugins/example_provider/__init__.py, plugins/run_logger/__init__.py (full).
Test suite: tests/conftest.py (full), tests/test_auth.py (full), tests/test_providers.py (representatively read), file-level review of all 16 test files' scope and naming.
Documentation: README.md (full), docs/ses/SES-0000-MASTER-INDEX.md (partially read — header/metadata and structure), mkdocs.yml (full).
Migrations/persistence: alembic.ini, migrations/env.py (listed, not fully read), migrations/versions/0001_initial_schema.py (listed, not fully read), packages/core/models_db.py (full).
Environment/security: .env.example (full), .gitignore (full), repository-wide grep scans for hardcoded secrets, TODO/FIXME markers, and redis/nats/postgres_url usage.
Explicitly out of scope / not verified in this audit:

Runtime/dynamic behavior — no code was executed; the RISK-01 concurrency race is a static structural inference, not an empirically reproduced failure.
Live GitHub repository metadata (open issue/PR counts, stars, forks) — attempted via the GitHub API but not reliably retrieved during this session; not relied upon for any finding above.
Full line-by-line review of packages/providers/proxmox/provider.py (412 lines) and apps/cli/main.py (547 lines) — these were structurally scanned (all function/class signatures, all raise/except sites) and representatively sampled, not read in their entirety line-by-line.
Full content of migrations/env.py and migrations/versions/0001_initial_schema.py — file presence and naming were confirmed; full content was not reviewed.
Any commit prior to the repository's first commit (2026-07-04) — none exist; this is a complete history.
For any conclusion above not explicitly traceable to one of these sources, no claim is made — per the specification's evidence requirement, this audit states "Insufficient evidence" rather than speculating, and no such unresolved claims remain in the findings above.

