# AUTOMATION ENGINE

Standard: SPOS-013 §5 | Aktualizováno: 2026-08-07

Architektura, komponenty a životní cyklus Automation Engine STARCORE.

---

## AUTOMATION ARCHITECTURE

```
╔══════════════════════════════════════════════════════════════╗
║                  AUTOMATION LAYER                            ║
╠══════════════════════════════════════════════════════════════╣
║  TRIGGER LAYER                                               ║
║  Schedule | Git Events | File Events | API Events | Manual   ║
╠══════════════════════════════════════════════════════════════╣
║  ORCHESTRATION LAYER                                         ║
║  GitHub Actions CI/CD | EventBus | Blueprint Scheduler       ║
╠══════════════════════════════════════════════════════════════╣
║  EXECUTION LAYER                                             ║
║  Python Scripts | Makefile | Pre-commit | Plugins            ║
╠══════════════════════════════════════════════════════════════╣
║  TOOL LAYER                                                  ║
║  pytest | ruff | pyright | bandit | pip-audit | mkdocs       ║
║  alembic | gitleaks | docker | uv | starcore CLI             ║
╠══════════════════════════════════════════════════════════════╣
║  PERSISTENCE LAYER                                           ║
║  SQLite | ledger.yaml | registry.yaml | regression_baseline  ║
╚══════════════════════════════════════════════════════════════╝
```

---

## AUTOMATION COMPONENTS

### Komponenta 1 — GitHub Actions Orchestrator

```yaml
id: AE-COMP-001
name: GitHub Actions Orchestrator
location: .github/workflows/
type: CI_CD_ORCHESTRATOR
technology: YAML + GitHub Actions Runner
status: AKTIVNÍ (2 workflows) / ORPHANED (7 workflows v platform/)

active_workflows:
  - ci.yml: Full CI gate (lint+types+security+tests+docker)
  - starcore-security.yml: Nightly secret scan

broken:
  - starcore-integrity.yml: References non-existent core/

orphaned:
  - platform/.github/workflows/* (7 files, not read by GitHub)

capabilities:
  - Parallel job execution (quality + postgres_smoke + docker_build)
  - Matrix testing (services: postgres)
  - Docker image build and smoke test
  - Changelog gate enforcement
  - Action pinning by SHA (security best practice)
```

### Komponenta 2 — .starcore QC Engine

```yaml
id: AE-COMP-002
name: .starcore QC Engine Stack
location: platform/.starcore/scripts/
type: AUDIT_ORCHESTRATOR
technology: Python 3.12 (standalone, no framework)

scripts:
  startup_protocol.py:
    purpose: "12-step cold-start session initialization"
    output: "Czech session report + 6-option decision menu"
    trigger: MANUAL (session start)
  
  qc_engine.py:
    purpose: "Unified QC orchestrator — runs Sentinel + Release Readiness"
    output: "Decision Engine formatted report"
    trigger: MANUAL
    modes: [--quick, --impact, --full]
  
  regression_sentinel.py:
    purpose: "Drift detection across 7 dimensions vs baseline"
    dimensions: [test_count, api_routes, cli_commands, config_fields, adr_count, workflow_count, lock_sync]
    baseline: ".starcore/state/regression_baseline.json"
    trigger: MANUAL / called by qc_engine.py
  
  release_readiness.py:
    purpose: "12-gate release readiness evaluation"
    gates: [BUILD, TEST, SECURITY, DEPENDENCIES, PACKAGE, ARTIFACT, DOCUMENTATION, GITHUB, GOVERNANCE, DEPLOYMENT, BACKUP, RECOVERY]
    trigger: MANUAL / called by qc_engine.py
  
  impact_analyzer.py:
    purpose: "Git diff → module → impact categories mapping"
    trigger: MANUAL / can be called with --since HEAD~1
  
  ledger.py:
    purpose: "Session lifecycle management (start/end/add-decision/add-risk)"
    persistence: "sessions/ledger.yaml"
    trigger: MANUAL (session events)
  
  registry.py:
    purpose: "Prompt catalog management (register/list/search/validate)"
    persistence: "prompts/registry.yaml"
    trigger: MANUAL
  
  decision_engine.py:
    purpose: "Structured decision format rendering and logging"
    trigger: MANUAL (post-audit/post-implementation)
```

### Komponenta 3 — Blueprint Execution Engine

```yaml
id: AE-COMP-003
name: Blueprint Execution Engine
location: platform/packages/orchestrator/ + blueprints/ + ai/
type: WORKFLOW_SCHEDULER
technology: Python asyncio

pipeline:
  1. NL Input → AnthropicProvider.generate_blueprint_yaml()
  2. BlueprintLoader.load_from_string(yaml_text) → Pydantic Blueprint
  3. ExecutionPlanner.create_graph(blueprint) → TaskGraph (DAG)
  4. Scheduler.execute(graph) → asyncio.gather() parallel waves
  5. BaseProvider.execute(action, resource) → task results
  6. EventBus.emit("run.completed") → SSE/WS + run_logger

scheduling_model: "Wave-based parallel execution with depends_on success gate"
timeout_support: true (TimeoutStrategy.CANCEL per task)
failure_semantics: "SKIPPED_DEPENDENCY_FAILED propagates transitively"
concurrent_runs: "Isolated via _STREAM_CTX ContextVar"
```

### Komponenta 4 — Makefile Automation Hub

```yaml
id: AE-COMP-004
name: Makefile Automation Hub
location: platform/Makefile
type: TASK_RUNNER
technology: GNU Make
targets: 21 (install, lint, format, test, security, docs, dev, clean, health, doctor, diagnose, migrations...)
trigger: MANUAL (make <target>)
purpose: "Developer-facing shortcuts for common tasks; local CI simulation via make ci"
```

### Komponenta 5 — Pre-commit Hook System

```yaml
id: AE-COMP-005
name: Pre-commit Hook System
location: platform/.pre-commit-config.yaml
type: FILE_CHANGE_AUTOMATION
technology: pre-commit framework
hooks:
  - ruff (lint + autofix) on every .py commit
  - ruff-format on every .py commit
  - pyright (type check) always
trigger: FILE_CHANGE (git commit)
status: AKTIVNÍ (lokální developer workflow)
```

### Komponenta 6 — EventBus Runtime Automation

```yaml
id: AE-COMP-006
name: EventBus Runtime Automation
location: platform/packages/core/events.py
type: API_EVENT_ORCHESTRATOR
technology: asyncio pub/sub

events:
  task.started: Scheduler → SSE/WS handlers
  task.completed: Scheduler → SSE/WS + metrics.py
  run.completed: Scheduler → run_logger plugin + SSE/WS

stream_isolation: "_STREAM_CTX ContextVar per concurrent run"
persistence: "ŽÁDNÁ (events jsou in-process only)"
```

### Komponenta 7 — Plugin Automation System

```yaml
id: AE-COMP-007
name: Plugin Automation System
location: platform/plugins/ + packages/core/plugin_manager.py
type: EXTENSIBLE_AUTOMATION
plugins:
  run_logger:
    purpose: "Captures run.completed → writes log file"
    trigger: run.completed event
  example_provider:
    purpose: "Reference implementation for custom providers"
```

---

## AUTOMATION LIFECYCLE

```
TRIGGER (Schedule/Git/Manual/API)
        ↓
DISPATCH (GitHub Actions / EventBus / CLI / pre-commit)
        ↓
ORCHESTRATE (Workflow / Scheduler / QC Engine / Makefile)
        ↓
EXECUTE (Tools: pytest, ruff, bandit, pip-audit, mkdocs, docker)
        ↓
OBSERVE (Metrics, Logs, EventBus events, Session Ledger)
        ↓
PERSIST (SQLite, ledger.yaml, registry.yaml, baseline.json)
        ↓
REPORT (Decision Engine format, CI status, QC report)
        ↓
ACT (Merge block/allow, Alert, Notify, Update registry)
```

---

## AUTOMATION STATES

| State | Popis | Příklady |
|---|---|---|
| PENDING | Čeká na trigger | Scheduled job before cron fires |
| TRIGGERED | Trigger nastaven | GitHub event received |
| RUNNING | Aktivně běží | pytest, docker build |
| SUCCESS | Dokončeno úspěšně | CI green, QC pass |
| FAILED | Selhalo | Tests fail, bandit finding |
| SKIPPED | Přeskočeno (dependency failed) | Downstream jobs |
| BLOCKED | Blokováno governance gate | Safety gate approval needed |
| ORPHANED | Konfigurováno, nespouštěno | platform/.github/ workflows |
| BROKEN | Konfigurováno, vždy selhává | starcore-integrity.yml |
| STUB | Nikdy nespouštěno (stubs) | Termux scripts |

---

## AUTOMATION DEPENDENCIES

```
GitHub Actions CI (AUT-001)
    ├── uv + Python 3.12
    ├── pytest (→ SQLite, STARCORE_API_KEY)
    ├── ruff
    ├── pyright
    ├── pip-audit
    ├── bandit
    ├── gitleaks-action
    ├── alembic
    ├── mkdocs
    ├── docker
    └── release.py check-changelog

QC Engine (AUT-057)
    ├── regression_sentinel.py
    │       └── regression_baseline.json
    └── release_readiness.py
            └── external tools (optional)

Blueprint Engine (AUT-070..079)
    ├── AnthropicProvider → STARCORE_ANTHROPIC_API_KEY
    ├── TaskGraph → BaseProvider implementations
    └── EventBus → SSE/WS connections
```
