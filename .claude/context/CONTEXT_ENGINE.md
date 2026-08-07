# CONTEXT ENGINE

Standard: SPOS-014 §8 | Aktualizováno: 2026-08-07

Dokumentace Context Engine STARCORE AAOS — jak se kontext předává, udržuje a obnovuje.

---

## PŘEHLED VRSTEV KONTEXTU

STARCORE Context Engine existuje ve dvou doménách:

1. **Platform Runtime Context** — request correlation, ContextVar, EventBus isolation
2. **Governance/AI Session Context** — DIGITAL_TWIN, CONTEXT_RESTORATION_PROTOCOL, cold-start

---

## PLATFORM RUNTIME CONTEXT (živě ověřeno)

### Request Correlation (packages/core/correlation.py)

```python
# ContextVar — propaguje se přes všechny awaited coroutines
_request_id: ContextVar[str] = ContextVar("request_id", default="-")

def resolve_request_id(x_request_id: str | None = None) -> str:
    # Přijme X-Request-ID header (validace: [A-Za-z0-9_-]{1,128})
    # nebo vygeneruje UUID
    ...

def contextualize_request() -> None:
    # Váže ID do asyncio kontextu (loguru extra: request_id)
    ...
```

```yaml
request_correlation:
  mechanism: "ContextVar (ADR-015)"
  propagation: "Automatická přes asyncio await chain"
  header: "X-Request-ID (validace regex [A-Za-z0-9_-]{1,128})"
  default: '"-" pro non-request kontexty (CLI, skripty)'
  middleware: "RequestIdMiddleware + inline _request_id_middleware v main.py"
  response_echo: "X-Request-ID vrácen v každé odpovědi"
```

### Stream Context Isolation (packages/core/events.py)

```python
# _STREAM_CTX: izoluje concurrent blueprint runs
_STREAM_CTX: ContextVar[str] = ContextVar("stream_ctx", default="")
```

```yaml
stream_context:
  purpose: "Izolace event subscriberů pro concurrent blueprint runs"
  mechanism: "ContextVar[str] — unikátní run_id per asyncio context"
  scope: "EventBus.emit() + SSE/WebSocket handlers"
  prevents: "Event cross-talk mezi souběžnými runy"
```

### Settings Context (packages/core/config.py)

```python
# Singleton za LRU cache — jeden Settings objekt per process
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
```

```yaml
settings_context:
  type: "Pydantic-settings singleton"
  prefix: "STARCORE_"
  cache: "LRU cache — jeden objekt per process"
  test_isolation: "get_settings.cache_clear() v conftest.py (autouse fixture)"
  ai_relevant:
    - "STARCORE_AI_PROVIDER"
    - "STARCORE_ANTHROPIC_API_KEY"
    - "STARCORE_ANTHROPIC_MODEL"
    - "STARCORE_AI_BASE_URL"
    - "STARCORE_AI_MODEL"
```

---

## GOVERNANCE/AI SESSION CONTEXT

### CONTEXT_RESTORATION_PROTOCOL (6-step cold-start)

```yaml
location: ".claude/context/CONTEXT_RESTORATION_PROTOCOL.md"
steps:
  1: "Read .claude/context/DIGITAL_TWIN.md (ekosystémový stav)"
  2: "Read platform/.starcore/memory/current_state.md (platform stav)"
  3: "Read .claude/registry/SPOS_REGISTRY.md (SPOS stav)"
  4: "Run python .starcore/scripts/startup_protocol.py --quick"
  5: "Read aktuální SPOS-0XX-HANDOVER-REPORT.md"
  6: "Read CLAUDE.md (platform kontext)"
purpose: "Umožňuje cold-start nové Claude session bez ztráty kontextu"
```

### DIGITAL_TWIN (ekosystémový kontext)

```yaml
location: ".claude/context/DIGITAL_TWIN.md"
role: "Live snapshot celého STARCORE ekosystému"
update_trigger: "Každý SPOS milestone (SPOS-001..014)"
content:
  - "Verze platformy (v0.6.0)"
  - "Health scores (5 dimenzí)"
  - "SPOS progress (001..013 dokončeno)"
  - "Automation inventory stav"
  - "Risk register"
auto_sync: CHYBÍ (ruční aktualizace — GAP-006 z SPOS-013)
```

### Session Ledger Context

```yaml
location: "platform/.starcore/sessions/ledger.yaml"
cli: "python ledger.py start/end/current/add-decision/add-risk/add-file"
content:
  - "Aktivní session metadata"
  - "Rozhodnutí přijatá v session"
  - "Rizika identifikovaná v session"
  - "Soubory vytvořené v session"
persistence: "YAML soubor, git-tracked"
archive: "sessions/archive/YYYY-MM-DD-<session-id>.md"
```

---

## CONTEXT PROPAGATION (blueprint execution)

```
HTTP Request (X-Request-ID nebo UUID)
  ↓
  RequestIdMiddleware → ContextVar[request_id]
  ↓
  POST /blueprints/run
  ↓
  BlueprintLoader → ExecutionPlanner → TaskGraph
  ↓
  Scheduler.execute(graph)
  ├── ContextVar[_STREAM_CTX] = run_id  ← isolates this run
  ├── asyncio.gather(wave tasks)
  │   └── provider.execute(resource_spec)
  │       └── event_bus.emit("task.started", ctx=_STREAM_CTX)
  └── event_bus.emit("run.completed")
  ↓
  loguru (request_id extra → structured log)
  ↓
  OTel trace (span → Jaeger/OTLP)
```

---

## CONTEXT ENGINE GAPS

```yaml
context_gaps:
  GAP-CE01:
    description: "Žádná agent-to-agent context propagation"
    impact: "AGENT-001 výsledky nejsou automaticky k dispozici AGENT-002"
    current: "Dvě oddělená HTTP volání, kontext ztracen"
    priority: HIGH

  GAP-CE02:
    description: "AI kontext není perzistován napříč sessions"
    impact: "Každá Claude session začíná cold-start (6-step protokol)"
    current: "CONTEXT_RESTORATION_PROTOCOL (manuální)"
    mitigation: "Vector embedding DIGITAL_TWIN (Qdrant PLANNED)"
    priority: MEDIUM

  GAP-CE03:
    description: "Settings context není sdílen přes procesy"
    impact: "CLI a API server mají oddělené Settings instance"
    current: "LRU cache per-process (STARCORE design)"
    priority: LOW

  GAP-CE04:
    description: "BLUEPRINT_SYSTEM_PROMPT není parametrizovatelný za runtime"
    impact: "Nelze přizpůsobit AI kontext bez změny kódu"
    current: "Konstanta v packages/ai/prompts.py"
    priority: MEDIUM
```

---

## PLÁNOVANÝ CONTEXT ENGINE

```yaml
planned_features:
  CE-P01:
    name: "Agent Context Bus"
    description: "Sdílený kontext prostor pro všechny agenty (request_id → session_id → agent_id)"
    prerequisite: "NATS nebo Redis"
    effort: HIGH

  CE-P02:
    name: "RAG Context Injection"
    description: "Automatická augmentace BLUEPRINT_SYSTEM_PROMPT relevantními knowledge chunks"
    prerequisite: "Qdrant + embedding model"
    effort: HIGH

  CE-P03:
    name: "Dynamic System Prompt"
    description: "BLUEPRINT_SYSTEM_PROMPT parametrizovatelný (provider constraints, user prefs)"
    effort: LOW (jednoduchá parametrizace)
```
