# TASK PLANNER

Standard: SPOS-011 §5 | Aktualizováno: 2026-08-07

Dokumentace existujícího Task Planning systému a návrh rozšíření.

---

## EXISTUJÍCÍ IMPLEMENTACE

### BlueprintLoader + planner.py (`platform/packages/blueprints/`)

```yaml
location: platform/packages/blueprints/
files:
  - loader.py      — parsování YAML blueprint → Blueprint model
  - models.py      — Blueprint Pydantic model (steps, depends_on, provider, action)
  - planner.py     — převod Blueprint → TaskGraph
  - executor.py    — sekvenční executor (staré API, Scheduler je nový)
  - template_resolver.py — substituce proměnných v blueprint YAML

flow:
  1. "YAML text → BlueprintLoader.load_from_string()"
  2. "Blueprint model (Pydantic validated)"
  3. "planner.py → TaskGraph (DAG)"
  4. "Scheduler.execute(graph) → list[Task]"
```

### Scheduler rozhodovací logika (`platform/packages/orchestrator/scheduler.py`)

```yaml
priority_model: "Implicitní — řídí depends_on graph (topologické pořadí)"
dependencies: "success gate — task se spustí jen pokud VŠECHNY depends_on dosáhly SUCCESS"
risk_handling: "Pokud dependency selhala → SKIPPED_DEPENDENCY_FAILED (propaguje tranzitivně)"
execution_order:
  - "Wave-based: všechny ready tasks v jedné vlně → asyncio.gather()"
  - "Čeká na dokončení vlny před dispatching další"
rollback: "Žádný automatický rollback — FAILED task zůstane FAILED, závislé jsou SKIPPED"
retry: "RetryConfig v provider_sdk/retry.py (konfigurovatelné per provider)"
timeout:
  - "TimeoutStrategy.CANCEL — task zrušen po timeout"
  - "TimeoutStrategy.FORCE_COMPLETE — task označen SUCCESS i při timeout"
parallel: "asyncio.gather() pro nezávislé tasks v jedné vlně"
sequential: "depends_on zajišťuje sekvenci"
```

---

## TASK LIFECYCLE

```
PENDING
  ↓ (deps satisfied)
RUNNING
  ↓ SUCCESS      ↓ FAILED      ↓ SKIPPED (provider not found)
                               ↓ SKIPPED_DEPENDENCY_FAILED
```

---

## PLANNER ROZŠÍŘENÍ (návrh, neimplementováno)

```yaml
proposed_additions:
  priority_field:
    description: "Explicitní priorita per task (LOW/MEDIUM/HIGH/CRITICAL)"
    status: CHYBÍ — TaskStatus nemá priority pole

  dynamic_replanning:
    description: "Přeplánování za běhu pokud provider selže"
    status: CHYBÍ — aktuálně: FAILED = konec pro danou větev

  cost_estimation:
    description: "Odhad nákladů před spuštěním (Anthropic tokens, infra time)"
    status: CHYBÍ

  human_approval_gate:
    description: "Pauza před destruktivními akcemi a čekání na potvrzení"
    status: CHYBÍ

  audit_log_per_task:
    description: "Strukturovaný audit log každého task.started/completed eventu"
    status: ČÁSTEČNÉ — event_bus emituje events, ale perzistence chybí
```

---

## SCRIPTS/DECISION_ENGINE.PY

```yaml
location: "platform/.starcore/scripts/decision_engine.py"
role: "Interaktivní rozhodovací formát pro AI sessions"
format: "STAV / ZJIŠTĚNO / RIZIKA / DOPORUČENÍ / DOPAD / RIZIKO / ROLLBACK / DALŠÍ KROK"
status: AKTIVNÍ (používán SPOS sekvencí)
note: "Není totéž co Scheduler — je to governance/decision reporting tool, ne task execution"
```
