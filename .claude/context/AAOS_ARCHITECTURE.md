# AI AGENT OPERATING SYSTEM (AAOS) — ARCHITEKTURA

Standard: SPOS-014 §2 | Aktualizováno: 2026-08-07

Kompletní architekturální model AAOS vrstvy STARCORE. Vychází z živého auditu repozitáře.
Každý komponent je označen stavem: AKTIVNÍ (existující kód), PLÁNOVANÝ (návrh bez kódu), STUB (placeholder).

---

## EXECUTIVE OVERVIEW

STARCORE AAOS je sada AI komponent zajišťující inteligentní infrastrukturní automatizaci.
Aktuální stav: **Level 2 / 5** — AI Blueprint Generation + Task Orchestration fungují,
ale multi-agent koordinace, RAG, runtime routing a samooptimalizace chybí.

```
AAOS Health Score: 38%   (Úroveň: KRITICKÝ)
AAOS Maturity:    Level 2 / 5
Active Agents:    4 (z plánovaných 12+)
Stub Agents:      21+ (Termux/JSON print stubs)
```

---

## AAOS ARCHITEKTURÁLNÍ VRSTVY

```
╔══════════════════════════════════════════════════════════════════╗
║                    AI GATEWAY                                    ║
║   FastAPI /ai/* + /blueprints/*  [packages/core/routers/]  ✅   ║
╠══════════════════════════════════════════════════════════════════╣
║                   PROMPT ENGINE                                  ║
║   BLUEPRINT_SYSTEM_PROMPT [packages/ai/prompts.py]          ✅   ║
║   Prompt Registry [.starcore/prompts/registry.yaml]         ✅   ║
╠══════════════════════════════════════════════════════════════════╣
║                  PROVIDER ROUTER                                 ║
║   AIProvider ABC → Anthropic / OpenAI-compat               ✅   ║
║   (statická env-based volba, ne runtime routing)                 ║
╠══════════════════════════════════════════════════════════════════╣
║                 TASK PLANNER                                     ║
║   BlueprintLoader + ExecutionPlanner [packages/blueprints/] ✅   ║
║   Kahn's topological sort + DAG validation                       ║
╠══════════════════════════════════════════════════════════════════╣
║               WORKFLOW ENGINE                                    ║
║   Scheduler + TaskGraph [packages/orchestrator/]            ✅   ║
║   asyncio wave execution + depends_on success gate               ║
╠══════════════════════════════════════════════════════════════════╣
║                  TOOL ROUTER                                     ║
║   ProviderRegistry [packages/provider_sdk/registry.py]      ✅   ║
║   Docker / Proxmox / Kubernetes (kód OK, providers OFFLINE)      ║
╠══════════════════════════════════════════════════════════════════╣
║                 PLUGIN SYSTEM                                    ║
║   PluginManager [packages/core/plugin_manager.py]           ✅   ║
║   example_provider + run_logger (2 aktivní pluginy)              ║
╠══════════════════════════════════════════════════════════════════╣
║                 CONTEXT ENGINE                                   ║
║   CONTEXT_RESTORATION_PROTOCOL (6-step)                     ✅   ║
║   ContextVar request correlation [packages/core/correlation] ✅  ║
║   (runtime agent context management: CHYBÍ)                  ❌  ║
╠══════════════════════════════════════════════════════════════════╣
║                 MEMORY ENGINE                                    ║
║   SHORT: Claude konverzační kontext                         ✅   ║
║   WORKING: .starcore/sessions/ (ledger.yaml)                ✅   ║
║   LONG: .starcore/memory/ + state/project_state.json        ✅   ║
║   VECTOR: Qdrant RAG (CHYBÍ)                                ❌   ║
╠══════════════════════════════════════════════════════════════════╣
║                KNOWLEDGE ENGINE                                  ║
║   knowledge/technologies/ (6/22 profilů)                    ✅   ║
║   knowledge/packages/PKG-001.md                             ✅   ║
║   RAG pipeline (CHYBÍ — Qdrant + embedding)                 ❌   ║
╠══════════════════════════════════════════════════════════════════╣
║              EVENT BUS / AGENT COMMUNICATION                     ║
║   EventBus singleton [packages/core/events.py]              ✅   ║
║   3 events: task.started / task.completed / run.completed        ║
║   Multi-agent messaging protocol (CHYBÍ)                    ❌   ║
╠══════════════════════════════════════════════════════════════════╣
║              OBSERVABILITY                                       ║
║   OpenTelemetry tracer [packages/core/tracing.py]           ✅   ║
║   Prometheus metrics [packages/core/metrics.py]             ✅   ║
║   loguru structured logs                                    ✅   ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## REGISTROVANÉ AAOS KOMPONENTY

| ID | Název | Stav | Soubor |
|---|---|---|---|
| AAOS-C01 | AI Gateway | ✅ AKTIVNÍ | `packages/core/routers/ai.py` |
| AAOS-C02 | Prompt Engine | ✅ AKTIVNÍ (základní) | `packages/ai/prompts.py` |
| AAOS-C03 | Provider Router | ✅ AKTIVNÍ (statický) | `packages/ai/generator.py` |
| AAOS-C04 | Task Planner | ✅ AKTIVNÍ | `packages/blueprints/planner.py` |
| AAOS-C05 | Workflow Engine | ✅ AKTIVNÍ (kód) | `packages/orchestrator/scheduler.py` |
| AAOS-C06 | Tool Router | ✅ AKTIVNÍ (kód) | `packages/provider_sdk/registry.py` |
| AAOS-C07 | Plugin System | ✅ AKTIVNÍ | `packages/core/plugin_manager.py` |
| AAOS-C08 | Context Engine | ⚠️ ČÁSTEČNÝ | `packages/core/correlation.py` |
| AAOS-C09 | Memory Engine | ⚠️ ČÁSTEČNÝ (bez vektoru) | `.starcore/memory/` |
| AAOS-C10 | Knowledge Engine | ⚠️ ČÁSTEČNÝ (bez RAG) | `knowledge/` |
| AAOS-C11 | Event Bus | ✅ AKTIVNÍ (in-process) | `packages/core/events.py` |
| AAOS-C12 | Observability | ✅ AKTIVNÍ | `packages/core/metrics.py` |
| AAOS-C13 | Multi-Agent Protocol | ❌ CHYBÍ | — |
| AAOS-C14 | RAG Pipeline | ❌ CHYBÍ | — |
| AAOS-C15 | Runtime Model Router | ❌ CHYBÍ | — |
| AAOS-C16 | Self-Optimization Engine | ❌ CHYBÍ | — |

---

## DATA FLOW — AI BLUEPRINT GENERATION (primární AAOS flow)

```
Uživatel → POST /ai/generate-blueprint
  ↓
  [AAOS-C01] AI Gateway (FastAPI auth + rate limit)
  ↓
  [AAOS-C03] Provider Router (STARCORE_AI_PROVIDER env)
  ↓
  ┌────────────────┬───────────────────────┐
  │ Anthropic      │  OpenAI-compat        │
  │ (AsyncAnthropic│  (httpx POST)         │
  │  SDK)          │  /v1/chat/completions │
  └────────────────┴───────────────────────┘
  ↓ [AAOS-C02] Prompt Engine (BLUEPRINT_SYSTEM_PROMPT)
  ↓
  YAML text → _strip_code_fences() → BlueprintGenerationError?
  ↓
  [AAOS-C04] Task Planner (BlueprintLoader → Pydantic validate)
  ↓
  GenerateBlueprintResponse { yaml, blueprint, validation_error }
  ↓
  Uživatel → POST /blueprints/run[?parallel=true]
  ↓
  [AAOS-C05] Workflow Engine (Scheduler nebo BlueprintExecutor)
  ↓
  [AAOS-C06] Tool Router (ProviderRegistry → Docker/Proxmox/K8s)
  ↓
  [AAOS-C11] Event Bus → task.started / task.completed / run.completed
  ↓
  [AAOS-C12] Observability (OTel trace + Prometheus metrics + loguru)
```

---

## REAL vs. STUB INVENTORY

### Reálné AI komponenty (platform/packages/)

```yaml
real_aaos_code:
  packages/ai/:
    - base.py: "AIProvider ABC + BlueprintGenerationError"
    - generator.py: "Factory: env → AnthropicProvider | OpenAICompatProvider"
    - prompts.py: "BLUEPRINT_SYSTEM_PROMPT (docker + proxmox resource types)"
    - providers/anthropic.py: "AsyncAnthropic SDK, claude-sonnet-5 default"
    - providers/openai_compat.py: "httpx, /v1/chat/completions"
  packages/orchestrator/:
    - scheduler.py: "asyncio wave execution, stall detection"
    - task.py: "Task dataclass + TaskStatus StrEnum"
    - task_graph.py: "TaskGraph DAG"
    - timeout.py: "TimeoutConfig + TimeoutStrategy"
  packages/provider_sdk/:
    - base.py: "BaseProvider ABC (5 abstract methods)"
    - registry.py: "ProviderRegistry singleton"
    - retry.py: "RetryConfig + attempt_with_retry"
  packages/core/:
    - events.py: "EventBus + _STREAM_CTX ContextVar"
    - plugin_manager.py: "PluginManager (discover + load_all)"
    - correlation.py: "ContextVar request ID"
    - metrics.py: "Prometheus CollectorRegistry"
    - tracing.py: "OpenTelemetry tracer"
```

### Stub adresáře (JSON print / Termux stubs)

```yaml
stubs:
  agents/:
    - kernel/agent_kernel.py: "11 řádků, JSON print"
    - missions/mission_executor.py: "8 řádků, JSON print"
    - planner/task_planner.py: "JSON print, create_task() → dict"
  autonomous/: "9 souborů, ~/STARCORE path, Termux"
  distributed/: "9 souborů, ~/STARCORE path, Termux"
  ai_runtime/: "3 soubory, ~/STARCORE path, Termux"
  knowledge/rag/rag_engine.py: "7 řádků, JSON print"
  knowledge/core/knowledge_core.py: "9 řádků, JSON print"
```

---

## AAOS MATURITY MODEL

| Level | Popis | Stav STARCORE |
|---|---|---|
| Level 1 | Manuální AI (API call, human in loop) | ✅ DOSAŽENO |
| Level 2 | Automated AI Pipeline (blueprint gen + execution) | ✅ DOSAŽENO |
| Level 3 | Multi-step Reasoning + RAG | ❌ NEDOSAŽENO |
| Level 4 | Multi-agent Collaboration | ❌ NEDOSAŽENO |
| Level 5 | Self-optimizing OS (autonomní zlepšování) | ❌ NEDOSAŽENO |

**Aktuální úroveň: Level 2 / 5**

---

## INTEGRACE S EXISTUJÍCÍ INFRASTRUKTUROU

```yaml
aaos_integration_points:
  ci_cd:
    - "CI gate (ci.yml): testuje packages/ai/, packages/orchestrator/ při každém PR"
    - "Security scan: pip-audit + bandit zahrnují AI balíčky"
  database:
    - "RunRecord ORM (models_db.py): perzistuje výsledky blueprint runs"
    - "Alembic migrations: DB schema má run_history"
  api_security:
    - "X-API-Key: všechny /ai/* + /blueprints/* endpointy chráněny"
    - "hmac.compare_digest: constant-time comparison"
  settings:
    - "Settings (pydantic-settings): STARCORE_AI_PROVIDER, STARCORE_ANTHROPIC_API_KEY"
    - "STARCORE_ANTHROPIC_MODEL default: claude-sonnet-5"
```
