# EVENT BUS

Standard: SPOS-012 §7 | Aktualizováno: 2026-08-07

Dokumentace existujícího Event Bus systému a návrh standardních SPOS-012 událostí.

---

## EXISTUJÍCÍ IMPLEMENTACE

```yaml
location: platform/packages/core/events.py
class: EventBus
implementation: "In-process, asyncio-based pub/sub"
persistence: ŽÁDNÁ (events nejsou loggovány do souboru)
transport: "In-process asyncio (coroutines nebo sync callbacks)"
streaming: "_STREAM_CTX ContextVar pro izolaci concurrent SSE/WS runů"
```

### EventBus API

```python
event_bus = EventBus()  # singleton

# Subscribe
event_bus.subscribe("event.name", callback_fn)
event_bus.unsubscribe("event.name", callback_fn)

# Emit (awaitable)
await event_bus.emit("event.name", payload: dict | Any)
```

### Streaming Isolation

```python
# _STREAM_CTX inject pro paralelní blueprint runs
# Každý SSE/WS handler dostane _stream_id filtrem
# Nezávislé concurrent runs se nepromíchají
```

---

## AKTIVNÍ UDÁLOSTI (živě ověřeno v kódu)

| Událost | Emitter | Payload | Subscribers |
|---|---|---|---|
| `task.started` | Scheduler | `{resource, provider, _stream_id?}` | SSE/WS handlers |
| `task.completed` | Scheduler | `{resource, provider, status, _stream_id?}` | SSE/WS handlers |
| `run.completed` | Scheduler | `{tasks: [...], _stream_id?}` | run_logger plugin, SSE/WS |

---

## NAVRHOVANÉ STANDARDNÍ UDÁLOSTI (SPOS-012 §7)

Rozšíření EventBus o governance-level events — návrh pro budoucí implementaci.

| Událost | Kategorie | Emitter (navrhovaný) | Payload |
|---|---|---|---|
| `repository.changed` | Governance | Git hook / CI | `{commit, files_changed}` |
| `documentation.updated` | Governance | mkdocs build | `{files_changed}` |
| `knowledge.updated` | Governance | SAKB update | `{profile_id}` |
| `memory.updated` | Governance | ledger.py | `{session_id, action}` |
| `provider.connected` | Infrastructure | BaseProvider | `{provider_name}` |
| `provider.disconnected` | Infrastructure | BaseProvider | `{provider_name, reason}` |
| `deployment.started` | Deployment | Scheduler | `{blueprint_id, run_id}` |
| `deployment.finished` | Deployment | Scheduler | `{run_id, status, tasks}` |
| `audit.started` | Audit | QC Engine | `{audit_id, mode}` |
| `audit.finished` | Audit | QC Engine | `{audit_id, score, findings}` |
| `workflow.started` | Workflow | Workflow Engine | `{workflow_id}` |
| `workflow.finished` | Workflow | Workflow Engine | `{workflow_id, status}` |
| `agent.started` | AI | Agent Runtime | `{agent_id}` |
| `agent.stopped` | AI | Agent Runtime | `{agent_id, reason}` |
| `security.alert` | Security | Security Engine | `{finding_id, severity}` |
| `infrastructure.changed` | Infrastructure | Provider | `{resource, change_type}` |
| `digital_twin.updated` | Governance | SPOS Engine | `{section, timestamp}` |
| `release.candidate` | Release | Release Readiness | `{version, gates_passed}` |
| `rollback.started` | Operations | Scheduler | `{run_id, reason}` |
| `rollback.finished` | Operations | Scheduler | `{run_id, status}` |

---

## IMPLEMENTAČNÍ MEZERA

```yaml
gap:
  current: "3 in-process events (task.started, task.completed, run.completed)"
  proposed: "20 standardních událostí + persistence + external transport"
  effort: "STŘEDNÍ — EventBus třída je extensible (subscribe/emit API je stabilní)"
  prerequisite:
    - "NATS message bus pro cross-service events (docker-compose scaffold)"
    - "Event persistence (Redis nebo PostgreSQL)"
    - "Definice payload schemas (Pydantic models)"
  blocking: false
  current_mitigations: "run_logger plugin zachytává run.completed → soubor"
```
