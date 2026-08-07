# MULTI-AGENT MODEL

Standard: SPOS-014 §5 | Aktualizováno: 2026-08-07

Model multi-agentní koordinace v STARCORE AAOS. Vychází z živého auditu.

---

## STAV: CHYBÍ

```yaml
multi_agent_status: NEIMPLEMENTOVÁNO
real_multi_agent_code: 0 řádků
stubs_pretending_multiagent: 21+ souborů (agents/, autonomous/, distributed/)
active_agents: 4 (ale fungují IZOLOVANĚ, bez vzájemné komunikace)
```

STARCORE má 4 reálné agenty, ale žádná z nich nekomunikuje s druhou.
Každý agent je izolovaný: HTTP endpoint, CLI skript, nebo asyncio coroutine.

---

## AKTUÁLNÍ "MULTI-AGENT" INTERAKCE

Jediná koordinace agentů existuje jako lineární pipeline, ne skutečná multi-agent síť:

```
POST /ai/generate-blueprint
  ↓ AGENT-001 (Blueprint Generator)
  ↓ generuje YAML
  ↓ [ručně nebo přes API]
POST /blueprints/run
  ↓ AGENT-002 (Task Scheduler)
  ↓ spouští TaskGraph

---

python qc_engine.py run
  ↓ AGENT-003 (QC Engine) orchestruje:
  ├── AGENT-004 (Impact Analyzer) jako subprocess/import
  ├── regression_sentinel.py
  └── release_readiness.py
```

QC Engine (AGENT-003) je jediný případ kde jeden agent řídí druhý (AGENT-004).
Implementováno jako přímý Python import, ne message passing.

---

## EVENT BUS — JEDINÝ SDÍLENÝ KANÁL

```yaml
shared_channel:
  name: EventBus
  location: packages/core/events.py
  type: "In-process asyncio pub/sub singleton"
  events:
    - "task.started (payload: run_id, task_id, provider)"
    - "task.completed (payload: run_id, task_id, status, duration)"
    - "run.completed (payload: run_id, total, succeeded, failed)"
  subscribers:
    - "metrics.py → BLUEPRINT_TASKS_TOTAL counter"
    - "run_logger plugin (pokud načten)"
  isolation: "_STREAM_CTX ContextVar — izolace concurrent runs"
  limitations:
    - "Pouze in-process (žádný cross-process messaging)"
    - "Žádná perzistence (zprávy ztraceny při restartu)"
    - "Žádné queuing nebo backpressure"
    - "NATS scaffold v docker-compose.yml ale neintegrován"
```

---

## STUB MULTI-AGENT INFRASTRUKTURA (nepoužitelná)

### distributed/ — Agent Network (stub)

```yaml
distributed_stubs:
  distributed/agents/network.py: "~/STARCORE agent_network.json print"
  distributed/bus/bus.py: "~/STARCORE agent_bus.json print"
  distributed/memory/memory_sync.py: "~/STARCORE memory_sync.json print"
  distributed/events/events.py: "~/STARCORE events.json print"
  distributed/workflows/federation.py: "~/STARCORE federation.json print"
  distributed/vector/vector_sync.py: "~/STARCORE vector_sync.json print"
  distributed/auth/auth.py: "~/STARCORE auth.json print"
  distributed/execution/execution.py: "~/STARCORE execution.json print"
  distributed/recovery/recovery.py: "~/STARCORE recovery.json print"
status: "Všechny jsou Termux stubs — zapisují do ~/STARCORE/ (homelab path)"
```

### autonomous/ — Agent Mesh (stub)

```yaml
autonomous_stubs:
  autonomous/agents/orchestrator.py: "~/STARCORE agent_registry.json print"
  autonomous/mesh/node_mesh.py: "~/STARCORE node_mesh.json print"
  autonomous/scheduler/scheduler.py: "~/STARCORE scheduler.json print"
  autonomous/connectors/ollama_connector.py: "localhost:11434 ref, print"
  autonomous/connectors/rag_bridge.py: "~/STARCORE rag_bridge.json print"
  autonomous/connectors/ai_core_bridge.py: "~/STARCORE ai_core_bridge.json print"
  autonomous/connectors/proxmox_controller.py: "~/STARCORE proxmox.json print"
  autonomous/health/health_loop.py: "~/STARCORE health_loop.json print"
  autonomous/runtime/runtime.py: "~/STARCORE runtime_state.json print"
status: "Všechny jsou Termux stubs — zapisují do ~/STARCORE/ (homelab path)"
```

---

## AI COMMUNICATION PROTOCOL (existující dokument)

Viz `.claude/context/AI_COMMUNICATION_PROTOCOL.md` (SPOS-011 §10):

```yaml
ai_comm_protocol_status:
  document_exists: true
  real_implementation: CHYBÍ
  planned_features:
    - "Standardizovaný message format mezi agenty"
    - "NATS jako message broker (docker-compose scaffold)"
    - "Redis jako shared state (docker-compose scaffold)"
  current_reality: "Žádný cross-agent messaging (pouze EventBus in-process)"
```

---

## PLÁNOVANÝ MULTI-AGENT MODEL

```yaml
planned_multi_agent:
  MAM-P01:
    name: "Agent Mesh (NATS-based)"
    description: "Agenti komunikují přes NATS pub/sub"
    prerequisite: "NATS scaffold aktivní (docker-compose.yml -- profile scaffold)"
    current_gap: "NATS v docker-compose ale EventBus neintegrován"
    effort: HIGH

  MAM-P02:
    name: "Agent Registry (runtime)"
    description: "Centrální runtime registry dostupných agentů a jejich schopností"
    current: "AGENT_REGISTRY.md (governance dokument, ne runtime registry)"
    gap: "Žádný runtime agent discovery"
    effort: MEDIUM

  MAM-P03:
    name: "Planner → Scheduler pipeline"
    description: "AGENT-001 generuje blueprint → AGENT-002 ho automaticky spustí"
    current: "Dvě oddělená API volání (ruční napojení)"
    effort: LOW (jednoduchý pipeline wrapper)

  MAM-P04:
    name: "QC → CI feedback loop"
    description: "AGENT-003 výsledky triggerují GitHub Actions workflow"
    current: "QC a CI jsou izolované (žádná zpětná vazba)"
    effort: MEDIUM
```

---

## MULTI-AGENT KOORDINACE: REFERENČNÍ ARCHITEKTURA

Navrhovaná (ne implementovaná) cílová architektura:

```
┌─────────────────────────────────────────────────┐
│              AGENT ORCHESTRATOR                  │
│    (plánovaný — koordinuje všechny agenty)       │
│                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │AGENT-001 │ │AGENT-002 │ │AGENT-003 │  ...     │
│  │Blueprint │ │Scheduler │ │QC Engine │         │
│  │Generator │ │          │ │          │         │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘         │
│       │            │            │               │
│  ─────┴────────────┴────────────┴────────────── │
│              NATS MESSAGE BUS                   │
│          (scaffold — neintegrováno)             │
└─────────────────────────────────────────────────┘
         │                │
   ┌─────▼──────┐  ┌──────▼──────┐
   │Redis Cache │  │ProviderReg. │
   │(scaffold)  │  │(Docker/PVE) │
   └────────────┘  └─────────────┘
```

Současný stav: pouze EventBus (in-process, 3 events) jako jediný sdílený komunikační kanál.

---

## STATISTIKY

```yaml
multi_agent_stats:
  real_coordination: 1 (QC Engine → Impact Analyzer, přímý import)
  stub_coordination: 21+ (nepoužitelné)
  shared_channels: 1 (EventBus in-process)
  planned_brokers: 2 (NATS, Redis — scaffold)
  multi_agent_maturity: "Level 0 / 5"
  gap_to_level_1: "NATS integrace + Agent Registry runtime"
```
