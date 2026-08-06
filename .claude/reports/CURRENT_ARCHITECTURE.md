# CURRENT ARCHITECTURE

Datum: 2026-08-06

---

## CELKOVÁ ARCHITEKTURA

```
STARCORE PLATFORM ECOSYSTEM
═══════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────┐
│                  UŽIVATELSKÝ PŘÍSTUP                │
│  CLI (Typer)        HTTP API (FastAPI)    Web UI     │
│  starcore ...       :8000/...             /ui        │
└──────────────┬──────────────┬────────────┬──────────┘
               │              │            │
               ▼              ▼            ▼
┌─────────────────────────────────────────────────────┐
│                    CORE LAYER                        │
│  Config (pydantic-settings / STARCORE_* env vars)   │
│  Database (SQLite + SQLAlchemy + Alembic)           │
│  Event Bus (in-process)                             │
│  Plugin Manager (plugins/<name>/register(ctx))      │
│  Observability (Prometheus /metrics, Loguru, OTLP)  │
└──────────────────────────┬──────────────────────────┘
                           │
               ┌───────────┼───────────┐
               ▼           ▼           ▼
┌──────────────────┐ ┌──────────┐ ┌──────────────────┐
│  BLUEPRINT ENGINE│ │ORCHESTRAT│ │   AI PROVIDER    │
│  Load YAML       │ │OR        │ │  Abstraction     │
│  Plan (topo sort)│ │Task      │ │  ├ Anthropic      │
│  Execute         │ │TaskGraph │ │  └ OpenAI-compat  │
│  Sequential/     │ │Scheduler │ │  (Ollama, vLLM)  │
│  Parallel        │ │Waves     │ └──────────────────┘
└──────────────────┘ └──────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│                 PROVIDER SDK                         │
│  BaseProvider ABC: connect, disconnect, health,      │
│  list_resources, execute                             │
│  ProviderRegistry (singletons per process)          │
└───────────────────┬─────────────────────────────────┘
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
┌─────────────────┐   ┌─────────────────────┐
│ DOCKER PROVIDER │   │  PROXMOX PROVIDER   │
│ docker-py       │   │  proxmoxer          │
│ containers      │   │  VMs, LXC           │
│ images          │   │  snapshots          │
└─────────────────┘   │  templates          │
                      │  discovery          │
                      └─────────────────────┘
```

---

## DEPLOYMENT MODEL

### Aktuální stav (Local/Dev)

```
Developer Machine
├── uv run starcore ...          ← CLI přístup
└── uv run uvicorn ...           ← HTTP API
    └── SQLite (local file)
```

### Cílový stav (Proxmox Production)

```
Proxmox Host
└── AI Core VM
    └── Docker Stack
        ├── starcore-api         ← FastAPI (port 8000)
        ├── ollama               ← LLM inference (port 11434)
        ├── open-webui           ← WebUI (port 3000)
        ├── qdrant               ← Vector DB (port 6333)
        ├── redis                ← Cache / session store
        └── postgres             ← Production DB (místo SQLite)
```

---

## ARCHITECTURE DECISION RECORDS (ADR)

Platform obsahuje 17 ADR dokumentů:

| ADR | Téma | Rozhodnutí |
|---|---|---|
| 001 | Blueprint dependency execution | Topologické řazení |
| 002 | Provider lifecycle | Singleton per process |
| 003 | Rate limiting | slowapi middleware |
| 004 | Dependency vuln. scanning | pip-audit v CI |
| 005 | Unified schema management | Alembic only |
| 006 | Observability | Prometheus + Loguru + OTLP |
| 007 | AI provider abstraction | Pluggable ABC |
| 008 | CI security gates | Bandit + gitleaks |
| 009 | Environment detection | runtime_environment field |
| 010 | Dependency failure semantics | Fail fast |
| 011 | Plugin trust boundary | NOT sandboxed (dokumentováno) |
| 012 | API authentication model | Single shared API key |
| 013 | Provider concurrency policy | Bez limitu (homelab škála) |
| 014 | Task timeout | Konfigurovatelný |
| 015 | Request correlation | X-Request-ID header |
| 016 | Task timeout integration | Integrace s Scheduler |
| 017 | Plugin operator controls | Operator controls |

---

## BEZPEČNOSTNÍ ARCHITEKTURA

```
Aktuální bezpečnostní vrstvy:
✅ API autentizace (X-API-Key)
✅ SAST (Bandit) — každý PR
✅ Secret scanning (gitleaks) — každý PR + nightly
✅ Dependency audit (pip-audit)
✅ HTTPS-only v produkci (doporučení)
✅ JWT + bcrypt (přítomno v závislostech)
⚠️ Žádné RBAC (jeden sdílený klíč — ADR-012)
⚠️ Pluginy nejsou sandboxovány (ADR-011)
⚠️ SQLite (nevhodné pro multi-node produkci)
```

---

## TESTOVACÍ ARCHITEKTURA

```
601 testů procházejících (pytest)
├── unit testy         ← packages/*/tests/
├── integration testy  ← tests/integration/
├── property testy     ← hypothesis
├── coverage floor     ← 100%
├── type checking      ← pyright
└── linting            ← ruff
```

---

## MULTI-LAYER ARCHITEKTURA (celý ekosystém)

Mimo `platform/` existují další architektonické vrstvy v root repo:

| Vrstva | Adresář | Stav |
|---|---|---|
| Agent Framework | `agents/` | Existuje, integrace nejasná |
| Runtime State | `runtime/` | JSON state soubory (39 adresářů) |
| Knowledge Base | `knowledge/` | RAG vrstva |
| Security Layer | `security/` | Audit + backup engine |
| Intelligence | `intelligence/` | Vrstva inteligence |
| Control Center | `control_center/` | Kontrolní centrum |
| AI Core | `ai_core/` | AI infrastruktura |
| Automation | `automation/` | Automation framework |

**Klíčový problém:** Integrace mezi těmito vrstvami a `platform/` není dokumentována.
