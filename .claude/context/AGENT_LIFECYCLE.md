# AGENT LIFECYCLE

Standard: SPOS-014 §4 | Aktualizováno: 2026-08-07

Dokumentace životního cyklu AI agentů v STARCORE AAOS. Vychází z živého auditu.

---

## PŘEHLED

STARCORE implementuje 4 reálné agenty s různými lifecycle modely:

| Agent | Lifecycle Model | Trigger | Persistence |
|---|---|---|---|
| AGENT-001 (Blueprint Generator) | Request-scoped | HTTP POST /ai/generate-blueprint | Bez stavu (stateless) |
| AGENT-002 (Task Scheduler) | Run-scoped | POST /blueprints/run | RunRecord v DB |
| AGENT-003 (QC Engine) | Session-scoped | Manuální python qc_engine.py | Reporty v /reports/ |
| AGENT-004 (Impact Analyzer) | On-demand | Manuální python impact_analyzer.py | Stdout |

---

## AGENT-001: Blueprint Generator — Lifecycle

```
INIT
  ↓
  FastAPI request → X-API-Key ověření → rate limit check
  ↓
LOAD
  ↓
  _build_provider(settings) → env STARCORE_AI_PROVIDER
  ├── "anthropic" → AnthropicProvider(api_key, model)
  └── "openai-compatible" → OpenAICompatProvider(base_url, model, api_key)
  ↓
EXECUTE
  ↓
  provider.generate_blueprint_yaml(description)
  ├── AsyncAnthropic.messages.create(model, max_tokens=2000, system=BLUEPRINT_SYSTEM_PROMPT)
  └── httpx.POST /v1/chat/completions
  ↓
  _strip_code_fences(raw_text) → yaml_str
  ↓
VALIDATE
  ↓
  BlueprintLoader.load(yaml_str) → Blueprint | validation_error
  ↓
TERMINATE
  ↓
  GenerateBlueprintResponse(yaml, blueprint, validation_error)
  (žádný stav, žádná perzistence)
```

**Chybové stavy:**
- `BlueprintGenerationError` — API selhání nebo prázdná odpověď
- `validation_error` — YAML parsovatelný, ale nevalidní blueprint schéma
- `503` — STARCORE_AI_PROVIDER není nastaven nebo klíč chybí

---

## AGENT-002: Task Scheduler — Lifecycle

```
INIT
  ↓
  POST /blueprints/run → blueprint YAML parsing
  ↓
  ExecutionPlanner.create_graph(blueprint) → TaskGraph (DAG)
  ├── Kahn's algorithm: topological sort
  ├── Circular dependency detection → ValueError
  └── Unknown dependency → ValueError
  ↓
CONNECT
  ↓
  Scheduler.execute(graph) → provider.connect() per required provider
  (BaseProvider._connect_lock: lazy asyncio.Lock — connect exactly once concurrent)
  ↓
EXECUTE (wave model)
  ↓
  Wave N: všechny task s in_degree=0 → asyncio.gather(...)
  ├── task.status = RUNNING
  ├── provider.execute(resource, action, payload)
  ├── timeout_seconds? → execute_with_timeout(TimeoutStrategy.CANCEL)
  ├── SUCCESS: status = SUCCESS, spustit závislé
  ├── FAILED: status = FAILED → závislé = SKIPPED_DEPENDENCY_FAILED (tranzitivně)
  └── STALL detection: žádný pokrok → RuntimeError
  ↓
  event_bus.emit("task.started" | "task.completed" | "run.completed")
  ↓
PERSIST
  ↓
  RunRecord → SQLite (models_db.py)
  ↓
DISCONNECT
  ↓
  provider.disconnect() per connected provider
  ↓
TERMINATE
  ↓
  list[Task] se finálními TaskStatus
```

**TaskStatus StrEnum:**
```python
PENDING = "pending"
RUNNING = "running"
SUCCESS = "success"
FAILED = "failed"
SKIPPED = "skipped"
SKIPPED_DEPENDENCY_FAILED = "skipped_dependency_failed"
```

---

## AGENT-003: QC Engine — Lifecycle

```
INIT
  ↓
  python qc_engine.py run [--quick | --full | --impact]
  ↓
LOAD BASELINE
  ↓
  regression_baseline.json (7 dimenzí: test_count, coverage, api_routes,
  cli_commands, config_fields, adr_count, workflow_count, lock_sync)
  ↓
EXECUTE
  ↓
  1. startup_protocol.py --quick (volitelné)
  2. impact_analyzer.py analyze (pokud --impact)
  3. regression_sentinel.py check → PASS | WARNING | FAIL
  4. release_readiness.py evaluate → 12 gates
  ↓
REPORT
  ↓
  Decision Engine formát:
  STAV / CO BYLO ZJIŠTĚNO / CO BYLO OVĚŘENO / RIZIKA / DOPORUČENÍ
  ↓
TERMINATE
  ↓
  Exit code 0 (OK) nebo 1 (regrese detekována)
```

---

## AGENT-004: Impact Analyzer — Lifecycle

```
INIT
  ↓
  python impact_analyzer.py analyze [--since HEAD~N | --file path]
  ↓
COLLECT
  ↓
  git diff --name-only → seznam změněných souborů
  ↓
ANALYZE
  ↓
  soubor → modul → impact kategorie
  (35 souborů → test mapping, živě ověřeno)
  ↓
REPORT
  ↓
  stdout: impactovaná testy + kategorie
  ↓
TERMINATE
  ↓
  Exit code 0
```

---

## AGENT SESSION MANAGEMENT (Claude Code sessions)

Zvláštní případ: Claude Code AI agent (tento agent) má vlastní lifecycle:

```yaml
claude_agent_lifecycle:
  trigger: "Nová Claude Code session (SPOS-014 prompt)"
  init_protocol:
    - "Read DIGITAL_TWIN.md (ekosystémový stav)"
    - "Read SPOS_REGISTRY.md (SPOS-001..013)"
    - "Read current_state.md (platform stav)"
    - "Read SPOS-013-HANDOVER-REPORT.md (kontext)"
  session_memory:
    - "sessions/ledger.yaml → ledger.py start"
    - "sessions/current.md → update"
  session_close:
    - "ledger.py end"
    - "Archivace do sessions/archive/"
    - "SPOS-0XX-HANDOVER-REPORT.md"
    - "Aktualizace DIGITAL_TWIN.md"
  commit_policy: "Explicitní schválení vyžadováno (SES-000 P007)"
```

---

## STUB AGENT LIFECYCLE (dokumentace absence)

Tyto adresáře vypadají jako agenti, ale nemají žádný lifecycle:

```yaml
stub_agents_no_lifecycle:
  agents/kernel/agent_kernel.py:
    action: "Zapíše JSON do ~/STARCORE/runtime/ + print"
    real_lifecycle: ŽÁDNÝ

  autonomous/agents/orchestrator.py:
    action: "Zapíše agent_registry.json do ~/STARCORE/runtime/ + print"
    real_lifecycle: ŽÁDNÝ

  distributed/agents/network.py:
    action: "Zapíše agent_network.json do ~/STARCORE/runtime/ + print"
    real_lifecycle: ŽÁDNÝ

  ai_runtime/agents/agent_registry.py:
    action: "Zapíše agent_registry.json do ~/STARCORE/runtime/ai/ + print"
    real_lifecycle: ŽÁDNÝ
```

---

## PLÁNOVANÝ LIFECYCLE (SPOS-014 návrhy)

```yaml
planned_features:
  LIFECYCLE-P01:
    name: "Agent Health Monitor"
    description: "Periodická kontrola health stavu všech aktivních agentů"
    trigger: "Scheduled (cron nebo asyncio.sleep loop)"
    status: PLÁNOVANÝ

  LIFECYCLE-P02:
    name: "Agent Retry Policy"
    description: "Automatický retry pro AGENT-001 při API rate limit (429)"
    current: "RetryConfig existuje v provider_sdk/retry.py ale NENÍ napojeno na AI providers"
    status: PLÁNOVANÝ

  LIFECYCLE-P03:
    name: "Agent State Persistence"
    description: "Ukládání mezivýsledků agentů do Redis (TTL-based)"
    prerequisite: "Redis scaffold profile (docker-compose.yml)"
    status: PLÁNOVANÝ
```
