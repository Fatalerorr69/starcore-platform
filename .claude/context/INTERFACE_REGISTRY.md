# INTERFACE REGISTRY

Standard: SPOS-012 §4-5 | Aktualizováno: 2026-08-07

Registr všech rozhraní (vazeb) mezi komponentami STARCORE. Vychází z Discovery auditu.

---

## FORMÁT

```yaml
id: IF-XXX
source: COMP-XXX
target: COMP-XXX
type: REST | CLI | PYTHON_IMPORT | DOCKER | FILESYSTEM | SQLITE | HTTP | WEBSOCKET | MCP | GIT | SSH
protocol: ""
input: ""
output: ""
auth: ""
status: AKTIVNÍ | OFFLINE | PLÁNOVANÝ | ORPHANED
```

---

## AKTIVNÍ ROZHRANÍ

### IF-001 — CLI → Platform API

```yaml
id: IF-001
source: COMP-009 (CLI)
target: COMP-001 (Platform API)
type: HTTP
protocol: "REST JSON over HTTP"
input: "CLI args → HTTP requests"
output: "JSON responses → formatted stdout"
auth: "X-API-Key (z env STARCORE_API_KEY)"
status: AKTIVNÍ
note: "Tenká CLI vrstva volající vlastní REST API lokálně"
```

### IF-002 — Platform API → Blueprint Engine

```yaml
id: IF-002
source: COMP-001 (Platform API)
target: COMP-002 (Blueprint Engine)
type: PYTHON_IMPORT
protocol: "In-process function call"
input: "POST /blueprints/plan|run → YAML text"
output: "Blueprint model + TaskGraph"
auth: N/A (in-process)
status: AKTIVNÍ
```

### IF-003 — Blueprint Engine → Orchestrator

```yaml
id: IF-003
source: COMP-002 (Blueprint Engine)
target: COMP-003 (Orchestrator)
type: PYTHON_IMPORT
protocol: "planner.py → TaskGraph → Scheduler.execute()"
input: "Blueprint model"
output: "list[Task] s finálními statusy"
auth: N/A
status: AKTIVNÍ
```

### IF-004 — Orchestrator → ProviderRegistry

```yaml
id: IF-004
source: COMP-003 (Orchestrator)
target: COMP-004 (Provider SDK / Registry)
type: PYTHON_IMPORT
protocol: "registry.get(provider_name).execute(action, resource, payload)"
input: "Task.provider, Task.action, Task.resource, Task.payload"
output: "dict výsledek nebo ProviderError"
auth: N/A (in-process)
status: AKTIVNÍ (kód) / provider instances offline
```

### IF-005 — ProviderRegistry → Docker Provider

```yaml
id: IF-005
source: COMP-004 (Provider SDK)
target: COMP-005 (Docker Provider)
type: DOCKER
protocol: "docker-py SDK → Docker Engine API (Unix socket)"
input: "Container specs"
output: "Container state"
auth: "Unix socket /var/run/docker.sock"
status: OFFLINE (daemon neběží)
```

### IF-006 — ProviderRegistry → Proxmox Provider

```yaml
id: IF-006
source: COMP-004 (Provider SDK)
target: COMP-006 (Proxmox Provider)
type: HTTP
protocol: "proxmoxer → Proxmox VE REST API"
input: "VM/LXC specs"
output: "VM/LXC state"
auth: "STARCORE_PROXMOX_HOST/USER/PASSWORD env (chybí)"
status: OFFLINE (credentials chybí)
```

### IF-007 — Platform API → AI Provider

```yaml
id: IF-007
source: COMP-001 (Platform API)
target: COMP-008 (AI Provider)
type: PYTHON_IMPORT
protocol: "ai.generator.generate_blueprint_yaml(description)"
input: "Natural language description"
output: "Blueprint YAML string"
auth: N/A (in-process, credentials v env)
status: AKTIVNÍ
```

### IF-008 — AI Provider → Anthropic API

```yaml
id: IF-008
source: COMP-008 (AI Provider — AnthropicProvider)
target: Anthropic Cloud API
type: HTTP
protocol: "HTTPS REST (anthropic SDK)"
input: "description: str"
output: "Blueprint YAML text"
auth: "STARCORE_ANTHROPIC_API_KEY env"
status: AKTIVNÍ (klíč z env, live volání neověřena)
```

### IF-009 — AI Provider → OpenAI-compat Server

```yaml
id: IF-009
source: COMP-008 (AI Provider — OpenAICompatProvider)
target: OpenAI-compatible server (Ollama/vLLM/etc.)
type: HTTP
protocol: "HTTPS/HTTP REST (httpx, /v1/chat/completions)"
input: "description: str"
output: "Blueprint YAML text"
auth: "STARCORE_OPENAI_API_KEY env (volitelné)"
status: OFFLINE (žádný server neběží)
```

### IF-010 — Orchestrator → EventBus

```yaml
id: IF-010
source: COMP-003 (Orchestrator)
target: COMP-001 (Platform API — EventBus)
type: PYTHON_IMPORT
protocol: "event_bus.emit('task.started'|'task.completed'|'run.completed')"
input: "Task state changes"
output: "Event fanout k subscribers"
auth: N/A (in-process)
status: AKTIVNÍ
```

### IF-011 — Platform API → SQLite

```yaml
id: IF-011
source: COMP-001 (Platform API)
target: SQLite DB
type: SQLITE
protocol: "SQLAlchemy ORM + Alembic migrations"
input: "ORM model writes (runs, users, blueprints)"
output: "Persisted records"
auth: N/A (filesystem)
status: AKTIVNÍ (platform/data/starcore.db)
```

### IF-012 — Plugin System → Provider/EventBus

```yaml
id: IF-012
source: COMP-010 (Plugin System)
target: COMP-004 (ProviderRegistry) + EventBus
type: PYTHON_IMPORT
protocol: "plugin.register(context) → context.register_provider() / context.subscribe()"
input: "Plugin module"
output: "Registered provider or event subscriber"
auth: N/A (in-process)
status: AKTIVNÍ
```

### IF-013 — GitHub Actions → CI Pipeline

```yaml
id: IF-013
source: GitHub push/PR event
target: COMP-050 (CI Pipeline)
type: GIT
protocol: "GitHub Actions webhook → ci.yml"
input: "git push, pull_request"
output: "CI pass/fail + status check"
auth: "GITHUB_TOKEN (automatic)"
status: AKTIVNÍ
```

### IF-014 — QC Engine → CI Tools

```yaml
id: IF-014
source: COMP-013 (QC Engine)
target: pytest, ruff, pyright, bandit, pip-audit, alembic
type: CLI
protocol: "subprocess / direct Python invocation"
input: "--quick or --full mode"
output: "Decision Engine format report"
auth: N/A (local)
status: AKTIVNÍ
```

### IF-015 — Session Ledger → Filesystem

```yaml
id: IF-015
source: COMP-017 (Ledger.py)
target: FILESYSTEM (platform/.starcore/sessions/)
type: FILESYSTEM
protocol: "YAML read/write"
input: "ledger.py start/end/list commands"
output: "sessions/ledger.yaml, sessions/archive/*.md"
auth: N/A
status: AKTIVNÍ
```

### IF-016 — GitHub MCP → GitHub API

```yaml
id: IF-016
source: Claude Code session (tato session)
target: GitHub REST API v3 (Fatalerorr69/starcore-platform)
type: MCP
protocol: "MCP toolcalls → GitHub API"
input: "mcp__github__* tool calls"
output: "PR data, commit data, file contents"
auth: "GitHub App OAuth (session-scoped)"
status: AKTIVNÍ (tato session)
```

---

## ORPHANED / BROKEN ROZHRANÍ

| ID | Source | Target | Typ | Problém |
|---|---|---|---|---|
| IF-B01 | COMP-054 (platform/.github/ci.yml) | GitHub Actions | GIT | Orphaned — GitHub nečte platform/.github/ |
| IF-B02 | COMP-055 (docker-publish.yml) | ghcr.io registry | DOCKER | Orphaned — platf/.github/ nečteno |
| IF-B03 | COMP-052 (starcore-integrity.yml) | root `core/` directory | FILESYSTEM | Broken — `core/` neexistuje jako CI entry point |

---

## PLÁNOVANÁ ROZHRANÍ

| ID | Source | Target | Typ | Status |
|---|---|---|---|---|
| IF-P01 | Platform API | PostgreSQL | TCP | PLÁNOVANÝ (scaffold profile) |
| IF-P02 | Orchestrator/EventBus | Redis | TCP | PLÁNOVANÝ (scaffold profile) |
| IF-P03 | Orchestrator | NATS | TCP | PLÁNOVANÝ (scaffold profile) |
| IF-P04 | AI Provider (RAG) | Qdrant | HTTP | PLÁNOVANÝ (nezačato) |
| IF-P05 | AI Provider | Ollama | HTTP | PLÁNOVANÝ (ai-core VM) |

---

## STATISTIKY

```yaml
total_interfaces: 23
active: 16 (IF-001..016)
orphaned_broken: 3 (IF-B01..B03)
planned: 5 (IF-P01..P05)
offline_active_code: 2 (IF-005 Docker, IF-006 Proxmox)
```
