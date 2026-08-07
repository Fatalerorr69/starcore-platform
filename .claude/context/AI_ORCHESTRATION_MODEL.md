# AI ORCHESTRATION MODEL

Standard: SPOS-011 §2 | Aktualizováno: 2026-08-07

Tento dokument mapuje EXISTUJÍCÍ AI orchestrační vrstvy STARCORE platformy.
Vychází výhradně z živého auditu repozitáře — žádné fiktivní konfigurace.

---

## DISCOVERY SHRNUTÍ

### CO JE REÁLNÉ (ověřeno v `platform/packages/`)

```
platform/packages/
├── ai/
│   ├── base.py          — AIProvider ABC (generate_blueprint_yaml)
│   ├── generator.py     — Top-level generator (env-based provider selection)
│   ├── prompts.py       — BLUEPRINT_SYSTEM_PROMPT
│   └── providers/
│       ├── anthropic.py      — AnthropicProvider (AsyncAnthropic SDK)
│       └── openai_compat.py  — OpenAICompatProvider (httpx, Ollama/vLLM/LM Studio)
│
├── orchestrator/
│   ├── scheduler.py     — Scheduler (asyncio.gather, dependency-sorted TaskGraph execution)
│   ├── task.py          — Task dataclass + TaskStatus enum
│   ├── task_graph.py    — TaskGraph (DAG s topologickým řazením)
│   └── timeout.py       — TimeoutConfig + TimeoutStrategy (CANCEL/FORCE_COMPLETE)
│
└── provider_sdk/
    ├── base.py          — BaseProvider ABC (connect/execute/disconnect)
    ├── registry.py      — ProviderRegistry (Docker, Proxmox, Kubernetes)
    ├── retry.py         — RetryConfig
    └── exceptions.py    — Provider exceptions
```

### CO JSOU TERMUX STUBS (NOT real orchestration)

```yaml
confirmed_stubs:
  - agents/           # JSON print, no real logic (3 soubory bez ~/STARCORE, ale prázdné)
  - ai_core/          # JSON print stub (ai_kernel.py)
  - ai_runtime/       # ~/STARCORE path (3 soubory, Termux)
  - autonomous/       # ~/STARCORE path (9 souborů, Termux)
  - distributed/      # ~/STARCORE path (9 souborů, Termux)
  - mission_engine/   # ~/STARCORE path (3 soubory, Termux)
  - knowledge_engine/ # ~/STARCORE path (1 soubor, Termux)
  - runtime/android/  # 100+ adresářů, Termux/Android targeted
```

---

## ARCHITEKTURÁLNÍ MODEL (existující + plánované vrstvy)

```
┌─────────────────────────────────────────────┐
│              AI GATEWAY                      │
│    FastAPI /ai/* endpoints                   │
│    platform/packages/core/routers/ai.py ✅   │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│            TASK PLANNER                      │
│    BlueprintLoader + planner.py              │
│    platform/packages/blueprints/ ✅          │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│           DECISION ENGINE                    │
│    scripts/decision_engine.py ✅             │
│    scripts/qc_engine.py ✅                   │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│          WORKFLOW ENGINE                     │
│    Scheduler (async TaskGraph) ✅            │
│    platform/packages/orchestrator/           │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│            TOOL ROUTER                       │
│    ProviderRegistry ✅                       │
│    platform/packages/provider_sdk/           │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│          PROVIDER ROUTER                     │
│    AIProvider ABC → Anthropic / OpenAI-compat│
│    platform/packages/ai/ ✅                  │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│           MEMORY LAYER                       │
│    platform/.starcore/memory/ ✅             │
│    platform/.starcore/sessions/ ✅           │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         KNOWLEDGE LAYER                      │
│    knowledge/ (6 tech profiles) ✅           │
│    .claude/sakb/ ✅                          │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         EXECUTION ENGINE                     │
│    BaseProvider.execute() ✅                 │
│    Docker + Proxmox + Kubernetes providers   │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│   MONITORING + AUDIT                         │
│    event_bus (core/events.py) ✅             │
│    OpenTelemetry tracer ✅                   │
│    SPOS-005 Audit Engine ✅                  │
└─────────────────────────────────────────────┘
```

---

## STATUS VRSTEV

| Vrstva | Implementace | Status | Soubor |
|---|---|---|---|
| AI Gateway | FastAPI /ai/generate-blueprint | ✅ AKTIVNÍ | `packages/core/routers/ai.py` |
| Task Planner | BlueprintLoader + planner | ✅ AKTIVNÍ | `packages/blueprints/planner.py` |
| Decision Engine | qc_engine + decision_engine | ✅ AKTIVNÍ | `platform/.starcore/scripts/` |
| Workflow Engine | Scheduler + TaskGraph | ✅ AKTIVNÍ | `packages/orchestrator/scheduler.py` |
| Tool Router | ProviderRegistry | ✅ AKTIVNÍ | `packages/provider_sdk/registry.py` |
| Provider Router | AIProvider + 2 providers | ✅ AKTIVNÍ | `packages/ai/providers/` |
| Memory Layer | platform/.starcore/memory/ | ✅ AKTIVNÍ | `platform/.starcore/memory/` |
| Knowledge Layer | knowledge/ + .claude/sakb/ | ✅ AKTIVNÍ | `knowledge/` |
| Execution Engine | BaseProvider.execute() | ✅ AKTIVNÍ (kód) / ⚠️ PROVIDERS offline | `packages/providers/` |
| Monitoring | event_bus + OTel | ✅ AKTIVNÍ (kód) | `packages/core/events.py` |

---

## MEZERY OPROTI SPOS-011 SPECIFIKACI

```yaml
gaps:
  - RAG/Vector DB: Qdrant zmíněn v SPOS-011, ale není v docker-compose.yml (jen scaffold: postgres/redis/nats)
  - Ollama/OpenWebUI: nejsou v docker-compose.yml — plánované, ne nasazené
  - ComfyUI/Whisper/Piper/Browser: nejsou v repozitáři (neexistují ani jako stub)
  - Multi-agent communication protocol: chybí formální definice (SPOS-011 §10)
  - Embedding indexer: žádný vector DB kód v platform/packages/
  - Model routing intelligence: AIProvider vybírán env var, ne runtime routing logikou
```
