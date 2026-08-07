# AGENT REGISTRY

Standard: SPOS-014 §3 | Aktualizováno: 2026-08-07

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

### agents/ (JSON print — bez ~/STARCORE path)

| ID | Soubor | Typ | Poznámka |
|---|---|---|---|
| AGENT-S01 | `agents/planner/task_planner.py` | JSON print | create_task() → {"task": name, "status": "queued"} |
| AGENT-S02 | `agents/kernel/agent_kernel.py` | JSON print (11 řádků) | {"component": "Agent Kernel", "agents": "ready"} |
| AGENT-S03 | `agents/missions/mission_executor.py` | JSON print (8 řádků) | {"component": "Mission Executor", "state": "ready"} |
| AGENT-S04 | `ai_core/kernel/ai_kernel.py` | JSON print | {"component": "AI Runtime Kernel", "version": "8A.01"} |

### ai_runtime/ (Termux stubs — ~/STARCORE path)

| ID | Soubor | Řádky | Výstup |
|---|---|---|---|
| AGENT-S05 | `ai_runtime/agents/agent_registry.py` | 25 | ~/STARCORE/runtime/ai/agent_registry.json |
| AGENT-S06 | `ai_runtime/inference/inference_engine.py` | 29 | ~/STARCORE/runtime/ai/inference_state.json |
| AGENT-S07 | `ai_runtime/models/model_registry.py` | 25 | ~/STARCORE/runtime/ai/model_registry.json |

### autonomous/ (Termux stubs — ~/STARCORE path, 9 souborů)

| ID | Soubor | Řádky | Výstup |
|---|---|---|---|
| AGENT-S08 | `autonomous/agents/orchestrator.py` | 18 | ~/STARCORE/runtime/autonomous/agent_registry.json |
| AGENT-S09 | `autonomous/runtime/runtime.py` | 16 | ~/STARCORE/runtime/autonomous/runtime_state.json |
| AGENT-S10 | `autonomous/scheduler/scheduler.py` | 16 | ~/STARCORE/runtime/autonomous/scheduler.json |
| AGENT-S11 | `autonomous/mesh/node_mesh.py` | 16 | ~/STARCORE/runtime/autonomous/node_mesh.json |
| AGENT-S12 | `autonomous/health/health_loop.py` | 17 | ~/STARCORE/runtime/autonomous/health_loop.json |
| AGENT-S13 | `autonomous/connectors/ai_core_bridge.py` | 16 | ~/STARCORE/runtime/autonomous/ai_core_bridge.json |
| AGENT-S14 | `autonomous/connectors/ollama_connector.py` | 16 | localhost:11434 ref + print |
| AGENT-S15 | `autonomous/connectors/rag_bridge.py` | 16 | ~/STARCORE/runtime/autonomous/rag_bridge.json |
| AGENT-S16 | `autonomous/connectors/proxmox_controller.py` | 16 | ~/STARCORE/runtime/autonomous/proxmox.json |

### distributed/ (Termux stubs — ~/STARCORE path, 9 souborů)

| ID | Soubor | Řádky | Výstup |
|---|---|---|---|
| AGENT-S17 | `distributed/agents/network.py` | 14 | ~/STARCORE/runtime/agent_network.json |
| AGENT-S18 | `distributed/bus/bus.py` | 14 | ~/STARCORE/runtime/agent_bus.json |
| AGENT-S19 | `distributed/memory/memory_sync.py` | 14 | ~/STARCORE/runtime/memory_sync.json |
| AGENT-S20 | `distributed/events/events.py` | 14 | ~/STARCORE/runtime/events.json |
| AGENT-S21 | `distributed/workflows/federation.py` | 14 | ~/STARCORE/runtime/federation.json |
| AGENT-S22 | `distributed/vector/vector_sync.py` | 14 | ~/STARCORE/runtime/vector_sync.json |
| AGENT-S23 | `distributed/auth/auth.py` | 15 | ~/STARCORE/runtime/auth.json |
| AGENT-S24 | `distributed/execution/execution.py` | 14 | ~/STARCORE/runtime/execution.json |
| AGENT-S25 | `distributed/recovery/recovery.py` | 14 | ~/STARCORE/runtime/recovery.json |

### knowledge/ (JSON print stubs)

| ID | Soubor | Řádky | Výstup |
|---|---|---|---|
| AGENT-S26 | `knowledge/rag/rag_engine.py` | 7 | {"component": "RAG Engine", "status": "ready"} |
| AGENT-S27 | `knowledge/core/knowledge_core.py` | 9 | {"component": "Knowledge Core", "version": "8C.01"} |

---

## STATISTIKY

```yaml
total_agents: 30 (4 aktivní + 3 plánovaní + 27 stub)
active_code: 4 (AGENT-001..004)
planned: 3 (AGENT-010..012)
stubs: 27 (AGENT-S01..S27)
  agents/: 4 stubs (JSON print, bez ~/STARCORE path)
  ai_runtime/: 3 stubs (Termux)
  autonomous/: 9 stubs (Termux)
  distributed/: 9 stubs (Termux)
  knowledge/: 2 stubs (JSON print)
health_score: "4/4 aktivní = OK"
aaos_maturity: "Level 2 / 5"
aaos_health: "38% (SPOS-014 baseline)"
```
