# DATA FLOW

Standard: SPOS-012 §8 | Aktualizováno: 2026-08-07

Mapa dat proudících skrze STARCORE ekosystém. Vychází z Discovery auditu.

---

## HLAVNÍ DATA FLOW (SPOS-012 §8 model)

```
REPOSITORY (git)
        ↓ změna kódu
DISCOVERY (Impact Analyzer)
        ↓ změněné soubory → dotčené testy
KNOWLEDGE (knowledge/ + .claude/sakb/)
        ↓ tech profily, ADR, dokumentace
MEMORY (.starcore/sessions/, memory/)
        ↓ session context, project state
PLANNER (BlueprintLoader + blueprints/planner.py)
        ↓ YAML → TaskGraph (dependency-sorted)
AI ROUTER (packages/ai/)
        ↓ NL description → Blueprint YAML
PROVIDERS (Docker / Proxmox / Kubernetes)
        ↓ TaskGraph → Provider.execute()
EXECUTION (Orchestrator / Scheduler)
        ↓ parallel wave execution
AUDIT (QC Engine + bandit + pip-audit)
        ↓ findings → Decision Engine report
DOCUMENTATION (mkdocs + .claude/registry/)
        ↓ aktualizace, build --strict
DIGITAL TWIN (.claude/context/DIGITAL_TWIN.md)
        ↓ live snapshot systému
```

---

## DETAILNÍ DATA FLOWS

### DF-001 — Blueprint Execution Flow

```
POST /ai/generate-blueprint
  input: {description: str}
        ↓
AnthropicProvider.generate_blueprint_yaml()
  → HTTPS → Anthropic API → response.content[0].text
        ↓
BlueprintLoader.load_from_string(yaml_text)
  → Pydantic Blueprint model (validated)
        ↓
planner.create_graph(blueprint)
  → TaskGraph (topologically sorted)
        ↓
Scheduler.execute(graph)
  → asyncio.gather() per wave
        ↓
BaseProvider.execute(action, resource, payload)
  → {result: dict, status: TaskStatus}
        ↓
event_bus.emit("run.completed", {tasks})
  → SSE stream / WebSocket / run_logger plugin
        ↓
RunRecord persisted → SQLite (platform/data/starcore.db)
```

### DF-002 — CI Audit Flow

```
git push
        ↓
GitHub Actions (ci.yml)
        ↓
[parallel gates]
  pytest -q         → pass/fail + coverage
  ruff check .      → linting errors
  pyright           → type errors
  bandit -r ...     → security findings
  pip-audit         → CVE count
  alembic check     → migration status
        ↓
GitHub Status Check (pass/fail)
        ↓
[if pass] merge allowed
[if fail] merge blocked
```

### DF-003 — SPOS Governance Flow

```
SPOS Prompt (uživatel)
        ↓
Discovery (read existing files)
        ↓
Analysis (ověření živými nástroji kde možné)
        ↓
Registry Creation (.claude/registry/*.md)
        ↓
Digital Twin Update (DIGITAL_TWIN.md)
        ↓
SES-INDEX + SPOS_REGISTRY update
        ↓
SPOS-XXX-IMPLEMENTATION-REPORT.md
        ↓
git commit + push (na explicitní souhlas u SPOS-012+)
```

### DF-004 — Memory Flow

```
New AI session (cold start)
        ↓
CONTEXT_RESTORATION_PROTOCOL.md (6 kroků)
  Step 1: DIGITAL_TWIN.md
  Step 2: SESSION_CONTEXT.md
  Step 3: SPOS_REGISTRY.md
  Step 4: .starcore/sessions/current.md
  Step 5: .starcore/memory/current_state.md
  Step 6: git log --oneline -10
        ↓
Working Memory (session kontext)
        ↓
Actions (edits, reads, tool calls)
        ↓
ledger.py (add-decision, add-risk, add-file)
        ↓
sessions/ledger.yaml (persisted)
        ↓
ledger.py end → sessions/archive/YYYY-MM-DD-*.md
```

---

## DATA STORES

| Store | Type | Location | Size (approx.) | Status |
|---|---|---|---|---|
| SQLite DB | Relační | `platform/data/starcore.db` | ~12KB | AKTIVNÍ |
| session ledger | YAML | `platform/.starcore/sessions/ledger.yaml` | ~3KB | AKTIVNÍ |
| session archive | Markdown | `platform/.starcore/sessions/archive/` | ~15KB | AKTIVNÍ |
| prompt registry | YAML | `platform/.starcore/prompts/registry.yaml` | ~10KB | AKTIVNÍ |
| regression baseline | JSON | `platform/.starcore/memory/regression_baseline.json` | ~1KB | AKTIVNÍ (drift: 801→805) |
| knowledge profiles | Markdown | `knowledge/` | ~50KB | AKTIVNÍ (6/22) |
| governance registries | Markdown | `.claude/registry/` | ~200KB | AKTIVNÍ |
| PostgreSQL | Relační | docker-compose scaffold | N/A | PLÁNOVANÝ |
| Redis | Key-Value | docker-compose scaffold | N/A | PLÁNOVANÝ |
| NATS | Message Bus | docker-compose scaffold | N/A | PLÁNOVANÝ |
| Qdrant | Vector DB | neexistuje | N/A | PLÁNOVANÝ |

---

## DATA FLOW GAPS

```yaml
gaps:
  - "Knowledge → RAG: žádný embedding pipeline, Qdrant chybí"
  - "Events → Persistence: EventBus nevyperzistuje events (logging pouze v run_logger)"
  - "Memory → Auto-sync: Digital Twin aktualizován ručně, ne automaticky"
  - "Audit → Trending: QC výsledky nejsou historicky srovnávány (jen baseline snapshot)"
  - "regression_baseline.json: drift 801→805 testů (neaktualizováno)"
```
