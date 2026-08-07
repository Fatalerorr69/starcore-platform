# AI COMMUNICATION PROTOCOL

Standard: SPOS-011 §10 | Aktualizováno: 2026-08-07

Definice komunikačního standardu pro AI agenty STARCORE.

---

## EXISTUJÍCÍ PROTOKOLY

### 1. SPOS Session Protocol (Claude Code ↔ STARCORE)

```yaml
protocol: SPOS Session
direction: External AI (Claude Code) → STARCORE
medium: "Prompt (přirozený jazyk) + .claude/ governance dokumenty"
format: "STARCORE PROJECT OPERATING SYSTEM / SPOS-NNN / VERSION 1.0.0"
acknowledgment: "SPOS_REGISTRY.md + Implementation Report + commit + push"
memory: "CONTEXT_RESTORATION_PROTOCOL.md (cold-start)"
```

### 2. Event Bus Protocol (interní)

```yaml
protocol: Event Bus
direction: platform interní (task → event_bus → subscribers)
implementation: "packages/core/events.py"
events:
  - "task.started {resource, provider}"
  - "task.completed {resource, provider, status}"
  - "run.completed {tasks: [{resource, provider, status}]}"
transport: "In-process async (asyncio)"
persistence: ŽÁDNÁ (events nejsou loggovány do souboru)
tracing: "OpenTelemetry span per task (blueprint.execute, task.run)"
```

### 3. Decision Engine Format (governance)

```yaml
protocol: Decision Engine Format
direction: QC Engine → Human / AI
format: |
  STAV: [OK|WARNING|ERROR]
  ZJIŠTĚNO: [seznam nálezů]
  RIZIKA: [seznam rizik]
  DOPORUČENÍ: [seznam doporučení]
  DOPAD: [co se stane pokud se nejedná]
  RIZIKO: [závažnost]
  ROLLBACK: [jak vrátit změnu]
  DALŠÍ KROK: [akce]
implementation: "platform/.starcore/scripts/decision_engine.py"
```

### 4. FastAPI REST Protocol

```yaml
protocol: REST API
authentication: "X-API-Key header"
format: JSON (Pydantic models)
versioning: "Žádné /v1/ prefix (gap ze SES-001)"
key_endpoints:
  - "POST /ai/generate-blueprint"
  - "POST /blueprints/execute"
  - "GET /providers/"
  - "GET /runs/"
  - "WebSocket /ws/"
```

---

## NAVRHOVANÝ MULTI-AGENT PROTOKOL (SPOS-011 §10)

```yaml
# Tento protokol NEEXISTUJE — je to návrh pro budoucí implementaci

proposed_protocol:
  name: "STARCORE Agent Communication Protocol (SACP)"
  version: "1.0.0-draft"

  message_format:
    agent_id: "AGENT-XXX"
    session_id: "uuid"
    timestamp: "ISO 8601"
    message_type: "request|response|event|feedback"
    payload: {}
    trace_id: "OpenTelemetry compatible"

  flow:
    1_request: "Agent → Planner (task definition)"
    2_routing: "Planner → Router (provider selection)"
    3_execution: "Router → Provider/Tool (execute)"
    4_memory: "Provider → Memory Layer (store result)"
    5_feedback: "Memory → Planner (update state)"
    6_learning: "Planner → Knowledge Base (update if significant)"

  transport_options:
    current: "in-process asyncio (event_bus)"
    planned: "NATS message bus (docker-compose scaffold profile)"

  status: PLÁNOVANÝ — vyžaduje multi-agent runtime

estimated_effort: "VYSOKÝ — závisí na NATS nasazení a definici agent contracts"
```
