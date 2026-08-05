# Architecture Reference — STARCORE Platform

> Rychlý přehled architektury pro cold-start. Autoritativní zdroj: CLAUDE.md.
> **Poslední aktualizace:** 2026-07-27

## Execution model

STARCORE je **modulární monolit** — jeden deployovatelný process, dvě delivery vrstvy (CLI a HTTP API), obě volají stejné domain packages. Business logika není nikdy duplicitní.

```
apps/cli (Typer)           packages/core/main.py (FastAPI)
        \                          /
         v                        v
   packages/blueprints      packages/core
   packages/orchestrator
         |
         v
   packages/provider_sdk    ← port (BaseProvider ABC, ProviderRegistry, retry)
         |
         v
   packages/providers/*     ← adapters (docker, proxmox)
```

## Execution paths (oba používají stejnou logiku)

| Path | Entry point | Kdy |
|------|-------------|-----|
| Sekvenční | `BlueprintExecutor.execute(blueprint)` | Default |
| Paralelní | `Scheduler.execute(graph)` | `--parallel` flag |

**Kritické:** Oba execution paths musí produkovat identické dependency ordering a failure semantics.

## depends_on je SUCCESS GATE (ADR-010)

Pokud závislost skončí `FAILED`/`SKIPPED`/`SKIPPED_DEPENDENCY_FAILED`:
- Závislý task dostane status `TaskStatus.SKIPPED_DEPENDENCY_FAILED`
- `provider.execute()` se NESPUSTÍ
- Propaguje se tranzitivně přes waves

## Klíčové moduly a jejich role

| Modul | Role |
|-------|------|
| `packages/provider_sdk/base.py` | BaseProvider ABC: connect, disconnect, health, list_resources, execute |
| `packages/provider_sdk/retry.py` | RetryConfig / attempt_with_retry — exponential backoff |
| `packages/blueprints/planner.py` | ExecutionPlanner: topological sort, create_plan(), create_graph() |
| `packages/blueprints/executor.py` | BlueprintExecutor — sekvenční path |
| `packages/orchestrator/scheduler.py` | Scheduler — paralelní path (waves, asyncio.gather) |
| `packages/orchestrator/timeout.py` | TimeoutConfig/Strategy/execute_with_timeout — implementováno, není zapojeno (ADR-016) |
| `packages/core/config.py` | Settings singleton (pydantic-settings, LRU-cached) |
| `packages/core/database.py` | SQLite + SQLAlchemy + Alembic init |
| `packages/core/security.py` | redact_database_url(), scrub_configured_secrets() |
| `packages/core/correlation.py` | ContextVar request ID propagation (ADR-015) |
| `packages/core/events.py` | In-process EventBus (task.started, task.completed, run.completed) |
| `packages/core/metrics.py` | Prometheus (dedicated CollectorRegistry, ne global) |
| `packages/core/logger.py` | Loguru sink, JSON mode, request_id extra |
| `packages/core/plugin_manager.py` | Plugin discovery z plugins/ (NOT sandboxed!) |

## Klíčová designová omezení

1. **Global timeout (`STARCORE_TASK_TIMEOUT_SECONDS`) je ZAKÁZÁN** — ADR-016 explicitně zamítlo
2. **Metrics musí používat dedicated CollectorRegistry** — ne global, kvůli duplicate-registration v testech
3. **`init_db()` je jediné místo kde smí běžet `create_all()`**
4. **`core/security.py` je jediné místo pro secret redakci** — neimplementuj lokálně jinde
5. **Pluginy nejsou sandboxované** — `importlib.import_module()` spouští kód s plnými právy

## Test isolation (conftest.py — 5 autouse fixtures)

1. `_no_dotenv_file` — žádný reálný `.env` file
2. `_isolated_database` — fresh SQLite DB v `tmp_path` pro každý test
3. `_api_key` — `STARCORE_API_KEY=test-api-key` via monkeypatch
4. `_clean_event_bus` — čistí `event_bus._subscribers` před/po každém testu
5. `_reset_rate_limiter` — čistí slowapi counters

**Kritické:** Při `monkeypatch.setenv`/`delenv` vždy zavolat `get_settings.cache_clear()`.

## Konfigurace

Všechny env vars mají prefix `STARCORE_`. Settings je singleton za `get_settings()` (LRU-cached).
Viz CLAUDE.md pro kompletní tabulku.

## Blueprint schema

YAML soubory popisující infrastrukturu. Klíčové pole: `depends_on` (success gate, ne jen ordering).
`ExecutionPlanner` validuje: neznámé nebo cirkulární závislosti → ValueError.

## ADR index

| ADR | Klíčové rozhodnutí |
|-----|---------------------|
| ADR-010 | depends_on jako success gate |
| ADR-011 | Pluginy nejsou sandboxované |
| ADR-012 | API key autentizace (X-API-Key) |
| ADR-013 | Žádný per-provider semaphore zatím |
| ADR-014 | Task timeout support (implementováno) |
| ADR-015 | Request correlation (ContextVar) |
| ADR-016 | Task timeout deferral (nezapojeno) |
