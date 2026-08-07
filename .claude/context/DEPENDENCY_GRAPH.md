# DEPENDENCY GRAPH

Standard: SPOS-012 §6 | Aktualizováno: 2026-08-07

Graf závislostí mezi komponentami STARCORE. Vychází z přímého auditu importů a konfigurace.

---

## MODULE GRAPH (platform/packages/)

```
COMP-009 CLI (Typer)
    └── COMP-001 Platform API (FastAPI)
            ├── COMP-002 Blueprint Engine (blueprints/)
            │       └── COMP-003 Orchestrator (orchestrator/)
            │               └── COMP-004 Provider SDK
            │                       ├── COMP-005 Docker Provider
            │                       ├── COMP-006 Proxmox Provider
            │                       └── COMP-007 Kubernetes Provider
            ├── COMP-008 AI Provider (ai/)
            │       ├── Anthropic API [EXTERNAL]
            │       └── OpenAI-compat Server [EXTERNAL / OFFLINE]
            └── COMP-010 Plugin System
                    ├── COMP-011 example_provider plugin
                    └── COMP-012 run_logger plugin
```

**Bez cyklických závislostí v platform/ — potvrzeno typecheckem (pyright 0 errors)**

---

## SERVICE GRAPH (CI/CD + runtime)

```
git push
    └── GitHub Actions
            ├── COMP-050 ci.yml [AKTIVNÍ]
            │       ├── pytest (796 testů)
            │       ├── ruff
            │       ├── pyright
            │       ├── bandit
            │       ├── pip-audit
            │       └── alembic check
            ├── COMP-051 starcore-security.yml [AKTIVNÍ]
            │       └── gitleaks
            ├── COMP-052 starcore-integrity.yml [ROZBITÉ]
            │       └── core/ [NEEXISTUJE]
            └── COMP-053 release.yml [AKTIVNÍ]
```

---

## AI GRAPH

```
Uživatel / AI agent
    └── POST /ai/generate-blueprint
            └── COMP-008 AI Provider
                    ├── AnthropicProvider → Anthropic API (claude-*)
                    └── OpenAICompatProvider → Ollama/vLLM/... [OFFLINE]
                            ↓
                    Blueprint YAML
                            ↓
                    BlueprintLoader (validation)
                            ↓
                    POST /blueprints/run
                            ↓
                    Scheduler.execute(TaskGraph)
                            ├── Docker tasks → COMP-005 [OFFLINE]
                            ├── Proxmox tasks → COMP-006 [OFFLINE]
                            └── Kubernetes tasks → COMP-007 [OFFLINE]
```

---

## PROVIDER GRAPH

```
ProviderRegistry
    ├── DockerProvider
    │       └── Docker Engine API (socket) [OFFLINE]
    ├── ProxmoxProvider
    │       └── Proxmox VE REST API [OFFLINE — no credentials]
    └── KubernetesProvider
            └── K8s API Server [OFFLINE — no cluster]
```

---

## DOCUMENTATION GRAPH

```
SES-000 Engineering Constitution
    └── SES-001 Technical Standard
            └── SAKB-000 Knowledge Model
                    └── knowledge/ (6 profiles)
            └── SPOS-000 Runtime Bootstrap
                    └── SPOS-001..011 (implementováno)
                            └── .claude/registry/*.md (15+ registry souborů)
                                    └── DIGITAL_TWIN.md (live snapshot)

platform/docs/
    ├── architecture.md
    ├── api.md (odkaz na API_REGISTRY.md)
    ├── cli.md
    ├── security.md
    ├── adr/ (17 ADRs)
    └── mkdocs.yml (build: PASS --strict)
```

---

## KNOWLEDGE GRAPH

```
knowledge/
    ├── technologies/ai/
    │       ├── anthropic-claude.md
    │       └── ollama.md
    ├── technologies/development/
    │       ├── python.md
    │       └── fastapi.md
    ├── technologies/infrastructure/
    │       ├── proxmox-ve.md
    │       └── docker.md
    ├── packages/
    │       └── PKG-001-ai-provider-abstraction.md
    └── registry/SOURCE_REGISTRY.md (9 L5 zdrojů)

RAG indexing: CHYBÍ (žádný vector DB)
```

---

## MEMORY GRAPH

```
AI Session (cold start)
    └── CONTEXT_RESTORATION_PROTOCOL.md (6 kroků)
            ├── .claude/context/DIGITAL_TWIN.md
            ├── .claude/registry/SPOS_REGISTRY.md
            ├── platform/.starcore/sessions/current.md
            └── platform/.starcore/memory/current_state.md
                    ├── platform/.starcore/sessions/ledger.yaml (active)
                    └── platform/.starcore/sessions/archive/*.md
```

---

## WORKFLOW GRAPH

```
BLUEPRINT WORKFLOW:
NL Input → AI Generate → Blueprint YAML → Plan → TaskGraph → Parallel Execution → Results

CI WORKFLOW:
Push → GitHub Actions → [pytest + ruff + pyright + bandit + pip-audit + alembic] → Status

GOVERNANCE WORKFLOW:
SPOS Prompt → Discovery → Audit → Registry Updates → Digital Twin → Commit → Push
```

---

## EVENT GRAPH

```
EventBus (in-process, packages/core/events.py)

Emitters → Events → Subscribers
───────────────────────────────
Scheduler → task.started → [SSE/WS streaming handlers]
Scheduler → task.completed → [SSE/WS streaming handlers]
Scheduler → run.completed → [run_logger plugin, SSE/WS]
Plugin run_logger → (consumes run.completed → writes log file)
_STREAM_CTX → stream isolation → (concurrent run filter by _stream_id)
```

---

## CIRCULAR DEPENDENCY SCAN

```yaml
circular_dependencies_found: 0
methodology: "pyright type checking (0 errors) + manual review"
note: "platform/packages/ is designed as acyclic DAG (COMP-001 → COMP-002 → COMP-003 → COMP-004 → providers)"
```
