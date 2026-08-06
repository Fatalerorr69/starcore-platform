# MODULE REGISTRY

Aktualizováno: 2026-08-06 | Standard: SES-001

Formát dle SES-001 §3: MODULE_ID, MODULE_NAME, PURPOSE, OWNER, STATUS, DEPENDENCIES, INPUTS, OUTPUTS, INTERFACES, TEST_STRATEGY, DOCUMENTATION.

---

## AKTIVNÍ MODULY (LAYER 1 — Core Platform)

### MOD-001 — Platform API
```yaml
purpose: FastAPI HTTP API — hlavní vstupní bod platformy
owner: platform team
status: ACTIVE
location: platform/packages/core
dependencies: [fastapi, uvicorn, pydantic-settings, sqlalchemy, alembic]
inputs: HTTP requests (REST), config (STARCORE_* env vars)
outputs: JSON responses, DB writes, Prometheus metrics
interfaces: [REST API, /metrics, /diagnostics, /health]
test_strategy: unit + integration (pytest), 100% coverage floor
documentation: platform/docs/api.md
```

### MOD-002 — Blueprint Engine
```yaml
purpose: Load YAML blueprints, plan (topological sort), execute
owner: platform team
status: ACTIVE
location: platform/packages/blueprints
dependencies: [pydantic, MOD-004 Provider SDK]
inputs: YAML blueprint files
outputs: ExecutionPlan (sequential) / TaskGraph (parallel)
interfaces: [ExecutionPlanner.create_plan(), create_graph()]
test_strategy: unit + property tests (hypothesis)
documentation: platform/docs/architecture.md
```

### MOD-003 — Orchestrator
```yaml
purpose: Execute prepared plans; concurrent wave scheduling
owner: platform team
status: ACTIVE
location: platform/packages/orchestrator
dependencies: [asyncio, MOD-002 Blueprint Engine]
inputs: TaskGraph
outputs: Task execution results, stall detection
interfaces: [Scheduler.run()]
test_strategy: unit + integration
documentation: platform/docs/architecture.md
```

### MOD-004 — Provider SDK
```yaml
purpose: Stable contract for infrastructure providers
owner: platform team
status: ACTIVE
location: platform/packages/provider_sdk
dependencies: [asyncio]
inputs: Provider-specific config
outputs: Registered provider instances
interfaces: [BaseProvider ABC (connect, disconnect, health, list_resources, execute), ProviderRegistry]
test_strategy: unit tests, contract tests
documentation: platform/docs/architecture.md, ADR-002
```

### MOD-005 — Docker Provider
```yaml
purpose: Docker container lifecycle management
owner: platform team
status: ACTIVE
location: platform/packages/providers
dependencies: [docker-py, MOD-004]
inputs: Container specs
outputs: Container state
interfaces: implements BaseProvider
test_strategy: integration tests (docker-py mocks)
documentation: platform/docs/architecture.md
```

### MOD-006 — Proxmox Provider
```yaml
purpose: Proxmox VE VM/LXC lifecycle, snapshots, discovery
owner: platform team
status: ACTIVE
location: platform/packages/providers
dependencies: [proxmoxer, MOD-004]
inputs: VM/LXC specs, template aliases
outputs: Resource state, snapshots
interfaces: implements BaseProvider
test_strategy: integration tests (proxmoxer mocks)
documentation: platform/docs/architecture.md
```

### MOD-007 — AI Provider
```yaml
purpose: Pluggable AI abstraction — blueprint generation from natural language
owner: platform team
status: ACTIVE
location: platform/packages/ai
dependencies: [anthropic, httpx]
inputs: Natural language description
outputs: Validated blueprint YAML
interfaces: AIProvider ABC (Anthropic / OpenAI-compatible)
test_strategy: unit tests, mocked API calls
documentation: ADR-007
```

### MOD-008 — CLI (Typer)
```yaml
purpose: Command-line interface — thin delivery layer over domain logic
owner: platform team
status: ACTIVE
location: platform/apps/cli
dependencies: [typer, rich, MOD-001..007]
inputs: CLI args
outputs: stdout, exit codes
interfaces: starcore blueprint/health/doctor/audit/snapshot/resource/proxmox/ai
test_strategy: CLI integration tests
documentation: platform/docs/cli.md
```

### MOD-009 — Plugin System
```yaml
purpose: Extend providers/events via plugins/<name>/register(context)
owner: platform team
status: ACTIVE
location: platform/packages/core/plugins
dependencies: [MOD-001, MOD-004]
inputs: plugin modules
outputs: registered providers, event subscriptions
interfaces: register(context)
test_strategy: unit tests
documentation: platform/docs/plugins.md, ADR-011 (NOT sandboxed)
```

---

## AKTIVNÍ MODULY (LAYER 5 — Ecosystem, mimo strict SES-001 §3 scope)

> Formální výjimka dle SES-001 §2 rozhodnutí (Varianta B). Tyto moduly nemají zatím testy ani dokumentaci — GAP zaznamenán v DOCUMENTATION_REGISTRY.

### MOD-010 — Agent Framework
```yaml
purpose: Agent kernel, mission planning
owner: nepřiřazeno
status: ACTIVE (nedokumentováno)
location: agents/
dependencies: neznámé — vyžaduje audit
inputs: neznámé
outputs: neznámé
interfaces: neznámé
test_strategy: CHYBÍ
documentation: CHYBÍ
```

### MOD-011 — Knowledge Base
```yaml
purpose: RAG / knowledge storage
status: ACTIVE (nedokumentováno)
location: knowledge/
test_strategy: CHYBÍ
documentation: CHYBÍ
```

### MOD-012 — Security Layer
```yaml
purpose: Security audit, backup engine
status: ACTIVE (nedokumentováno)
location: security/
test_strategy: CHYBÍ
documentation: CHYBÍ
```

### MOD-013 — Intelligence
```yaml
purpose: Intelligence layer (nejasný účel — vyžaduje audit)
status: ACTIVE (nedokumentováno)
location: intelligence/
test_strategy: CHYBÍ
documentation: CHYBÍ
```

### MOD-014 — Control Center
```yaml
purpose: Kontrolní centrum (nejasný účel — vyžaduje audit)
status: ACTIVE (nedokumentováno)
location: control_center/
test_strategy: CHYBÍ
documentation: CHYBÍ
```

### MOD-015 — AI Core
```yaml
purpose: AI core infrastruktura (nejasný účel — vyžaduje audit)
status: ACTIVE (nedokumentováno)
location: ai_core/
test_strategy: CHYBÍ
documentation: CHYBÍ
```

---

## PLÁNOVANÉ MODULY

| ID | Název | Adresář | Status |
|---|---|---|---|
| MOD-100 | Docker AI Stack | `docker/ai-stack/` | PLÁNOVÁNO |
| MOD-101 | Ollama Integration | `platform/packages/providers` | PLÁNOVÁNO |
| MOD-102 | Qdrant Integration | `platform/packages/providers` | PLÁNOVÁNO |
| MOD-103 | Ansible Playbooks | `ansible/` | PLÁNOVÁNO |
| MOD-104 | Proxmox VM Blueprints | `platform/packages/blueprints` | PLÁNOVÁNO |

---

## AUDIT TODO (vyplývá ze SES-001 gap analýzy)

MOD-010 až MOD-015 vyžadují plný audit (PURPOSE/DEPENDENCIES/INTERFACES) předtím, než mohou být deklarovány plně COMPLIANT se SES-001 §3-4. Naplánováno jako samostatný DISCOVERY úkol.
