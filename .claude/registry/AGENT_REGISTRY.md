# AGENT REGISTRY

Standard: SPOS-011 §3 | Aktualizováno: 2026-08-07

Registr AI agentů STARCORE ekosystému. Záznamy vycházejí z živého auditu — označeny jako AKTIVNÍ (existující kód), PLÁNOVANÝ (navrženo, kód chybí), nebo STUB (existuje jen placeholder).

---

## FORMÁT ZÁZNAMU

```yaml
# Pole dle SPOS-011 §3
id: AGENT-XXX
name: ""
role: ""
description: ""
inputs: []
outputs: []
tools: []
memory: []
knowledge: []
capabilities: []
provider: ""
priority: LOW|MEDIUM|HIGH|CRITICAL
owner: ""
status: AKTIVNÍ|PLÁNOVANÝ|STUB|NEOVĚŘITELNÝ
dependencies: []
interfaces: []
health: UNKNOWN|OK|DEGRADED|OFFLINE
version: ""
```

---

## AKTIVNÍ AGENTI (živě ověřeno v platform/)

### AGENT-001 — Blueprint Generator

```yaml
id: AGENT-001
name: "Blueprint Generator"
role: AI Infrastructure Code Generator
description: "Přijme přirozený jazyk popis infrastruktury a vygeneruje YAML blueprint pro Provider Scheduler. Implementován jako FastAPI endpoint /ai/generate-blueprint."
inputs:
  - "description: str (přirozený jazyk popis)"
outputs:
  - "yaml: str (STARCORE blueprint YAML)"
  - "blueprint: Blueprint | None (parsed + validated)"
  - "validation_error: str | None"
tools:
  - "Anthropic Messages API (claude-*)"
  - "OpenAI-compatible /v1/chat/completions (Ollama, vLLM, LM Studio)"
memory: []
knowledge:
  - "BLUEPRINT_SYSTEM_PROMPT (platform/packages/ai/prompts.py)"
capabilities:
  - "AI-powered YAML generation"
  - "Code fence stripping"
  - "Pydantic blueprint validation"
  - "Error propagation (BlueprintGenerationError)"
provider: "Anthropic | OpenAI-compatible (env-based selection)"
priority: HIGH
owner: platform
status: AKTIVNÍ
dependencies: [PROVIDER-001, PROVIDER-002]
interfaces:
  - "POST /ai/generate-blueprint (FastAPI)"
health: OK
version: "0.6.0"
```

### AGENT-002 — Scheduler / Workflow Executor

```yaml
id: AGENT-002
name: "Task Scheduler"
role: Async Infrastructure Task Orchestrator
description: "Spouští TaskGraph respektující závislosti. Úkoly bez závislostí běží paralelně (asyncio.gather). Implementuje success-gate model pro depends_on."
inputs:
  - "graph: TaskGraph (DAG úkolů)"
outputs:
  - "list[Task] (s finálními TaskStatus)"
tools:
  - "ProviderRegistry (Docker, Proxmox, Kubernetes)"
  - "event_bus (task.started, task.completed, run.completed)"
  - "OpenTelemetry tracer"
memory: []
knowledge: []
capabilities:
  - "Parallel task execution (asyncio.gather)"
  - "Dependency resolution (topological)"
  - "Success gate enforcement (SKIPPED_DEPENDENCY_FAILED)"
  - "Timeout handling (CANCEL/FORCE_COMPLETE)"
  - "Provider connect/disconnect lifecycle"
provider: N/A (provider-agnostic orchestrator)
priority: CRITICAL
owner: platform
status: AKTIVNÍ
dependencies: [PROVIDER-003, PROVIDER-004, PROVIDER-005]
interfaces:
  - "Scheduler.execute(graph: TaskGraph) -> list[Task]"
health: OK
version: "0.6.0"
```

### AGENT-003 — QC Engine (Project Intelligence Agent)

```yaml
id: AGENT-003
name: "QC Engine"
role: Quality Control + Decision Intelligence
description: "Orchestruje plný CI toolchain a produkuje STAV/ZJIŠTĚNO/RIZIKA/DOPORUČENÍ výstup ve formátu Decision Engine. Adoptován v SPOS-004 jako Project Intelligence Engine."
inputs:
  - "--quick (rychlý mód)"
  - "--full (plný mód, all gates)"
outputs:
  - "Decision Engine format report"
  - "PROJECT_HEALTH_SCORE (manuálně vypočítán: 88.2%)"
tools:
  - "pytest"
  - "ruff"
  - "pyright"
  - "bandit"
  - "pip-audit"
  - "alembic"
memory:
  - "regression_baseline.json (platform/.starcore/)"
knowledge: []
capabilities:
  - "Full CI gate orchestration"
  - "Regression detection"
  - "Release readiness evaluation (12 gates)"
provider: local
priority: HIGH
owner: platform
status: AKTIVNÍ
dependencies: []
interfaces:
  - "python qc_engine.py run [--quick|--full]"
health: OK
version: "0.6.0"
```

### AGENT-004 — Impact Analyzer

```yaml
id: AGENT-004
name: "Impact Analyzer"
role: Code Change Impact Intelligence
description: "Mapuje změněné soubory na dotčené moduly a testy. Implementuje OBSERVE->COLLECT->ANALYZE->UNDERSTAND cyklus."
inputs:
  - "--since <git ref>"
  - "--file <path>"
outputs:
  - "Impact report (modul → test mapping)"
tools:
  - "git"
memory: []
knowledge:
  - "MODULE_REGISTRY.md"
capabilities:
  - "35 souborů → test mapping (živě ověřeno)"
provider: local
priority: MEDIUM
owner: platform
status: AKTIVNÍ
dependencies: []
interfaces:
  - "python impact_analyzer.py analyze --since HEAD~N"
health: OK
version: "0.6.0"
```

---

## PLÁNOVANÍ AGENTI (kód neexistuje — návrh)

### AGENT-010 — RAG Knowledge Agent

```yaml
id: AGENT-010
name: "RAG Knowledge Agent"
role: Retrieval-Augmented Generation pro STARCORE knowledge base
description: "Plánovaný agent pro dotazování knowledge base přes vector embeddings. Qdrant jako vector DB (zmíněn v SPOS-011, není v docker-compose.yml)."
status: PLÁNOVANÝ
dependencies: ["Qdrant (PLANNED)", "Embedding model (PLANNED)"]
```

### AGENT-011 — Model Router

```yaml
id: AGENT-011
name: "Intelligent Model Router"
role: Runtime AI provider selection na základě task requirements
description: "Plánovaný router který vybírá provider (Anthropic/Ollama/vLLM/Groq/etc.) podle context size, schopností (vision/coding/reasoning), ceny, dostupnosti offline."
status: PLÁNOVANÝ
note: "Aktuálně: provider vybrán staticky přes env var STARCORE_AI_PROVIDER. Runtime routing neexistuje."
```

### AGENT-012 — Automation Pipeline Agent

```yaml
id: AGENT-012
name: "Automation Pipeline Agent"
role: Orchestrace SPOS-011 §11 CI automation pipeline
description: "Plánovaný agent: Repository Change → Impact Analysis → Docs → Tests → Audit → Release Check → Commit → Knowledge Update → Digital Twin."
status: PLÁNOVANÝ
```

---

## STUB AGENTI (placeholder, ne reálná implementace)

| ID | Soubor | Typ | Poznámka |
|---|---|---|---|
| AGENT-S01 | `agents/planner/task_planner.py` | JSON print | create_task() → {"task": name, "status": "queued"} |
| AGENT-S02 | `agents/kernel/agent_kernel.py` | JSON print | state = {"component": "Agent Kernel", "agents": "ready"} |
| AGENT-S03 | `agents/missions/mission_executor.py` | JSON print | {"component": "Mission Executor", "state": "ready"} |
| AGENT-S04 | `ai_core/kernel/ai_kernel.py` | JSON print | {"component": "AI Runtime Kernel", "version": "8A.01"} |
| AGENT-S05 | `ai_runtime/` | Termux stub | ~/STARCORE path, 3 soubory |

---

## STATISTIKY

```yaml
total_agents: 12 (4 aktivní + 3 plánovaní + 5 stub)
active_code: 4 (AGENT-001..004)
planned: 3 (AGENT-010..012)
stubs: 5 (AGENT-S01..S05, nezapočítávají root ~/STARCORE dirs)
health_score: "4/4 aktivní = OK"
```
