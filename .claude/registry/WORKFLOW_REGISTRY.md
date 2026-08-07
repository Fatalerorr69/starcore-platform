# WORKFLOW REGISTRY

Standard: SPOS-011 §4 | Aktualizováno: 2026-08-07

Registr workflow dostupných v STARCORE ekosystému. Stav vychází z živého auditu.

---

## FORMÁT

```yaml
id: WF-XXX
name: ""
trigger: ""
steps: []
agents: []
status: AKTIVNÍ|PLÁNOVANÝ|ČÁSTEČNÝ
owner: ""
```

---

## AKTIVNÍ WORKFLOW

### WF-001 — CI Validation Pipeline

```yaml
id: WF-001
name: "CI Validation Pipeline"
trigger: "git push / PR (GitHub Actions ci.yml)"
steps:
  - "uv sync --extra dev"
  - "pytest -q (796 passed, 9 skipped)"
  - "ruff check ."
  - "pyright"
  - "bandit -r packages/ apps/ scripts/ -ll"
  - "pip-audit"
  - "alembic check"
agents: [AGENT-003]
tools: [pytest, ruff, pyright, bandit, pip-audit, alembic]
status: AKTIVNÍ
owner: platform
file: ".github/workflows/ci.yml"
last_verified: "2026-08-06 (SPOS-005)"
```

### WF-002 — Blueprint Generation + Execution

```yaml
id: WF-002
name: "AI Blueprint Generation and Execution"
trigger: "POST /ai/generate-blueprint (FastAPI)"
steps:
  - "Accept natural language description"
  - "Route to AIProvider (Anthropic or OpenAI-compat)"
  - "Generate YAML blueprint"
  - "Validate via BlueprintLoader + Pydantic"
  - "Build TaskGraph (dependency-sorted)"
  - "Scheduler.execute(graph) — parallel async execution"
  - "Provider.execute() per task (Docker/Proxmox/K8s)"
  - "Emit run.completed event"
agents: [AGENT-001, AGENT-002]
tools: [Anthropic API, OpenAI-compat API, Docker provider, Proxmox provider]
status: AKTIVNÍ (kód) / NEOVĚŘITELNÝ (providers offline)
owner: platform
```

### WF-003 — Security Audit Workflow

```yaml
id: WF-003
name: "Security Scan"
trigger: "git push (starcore-security.yml)"
steps:
  - "gitleaks secret scan"
agents: []
tools: [gitleaks]
status: AKTIVNÍ (CI)
owner: platform
file: ".github/workflows/starcore-security.yml"
```

### WF-004 — Session Lifecycle

```yaml
id: WF-004
name: "Session Management Lifecycle"
trigger: "Manuální (ledger.py CLI)"
steps:
  - "ledger.py start → registrace session"
  - "ledger.py add-request / add-decision / add-risk / add-file"
  - "ledger.py end → archivace session → sessions/archive/"
agents: []
tools: [ledger.py]
status: AKTIVNÍ
owner: platform/.starcore
last_verified: "2026-08-06 (SPOS-002)"
```

### WF-005 — Context Restoration Protocol

```yaml
id: WF-005
name: "AI Context Cold-Start Restoration"
trigger: "Začátek nové Claude Code session"
steps:
  - "STEP 1: Read .claude/context/DIGITAL_TWIN.md"
  - "STEP 2: Read .claude/context/SESSION_CONTEXT.md"
  - "STEP 3: Read .claude/registry/SPOS_REGISTRY.md"
  - "STEP 4: Read platform/.starcore/sessions/current.md"
  - "STEP 5: Read platform/.starcore/memory/current_state.md"
  - "STEP 6: git log --oneline -10"
agents: []
tools: [Read]
status: AKTIVNÍ (dokumentovaný protokol)
owner: .claude
file: ".claude/context/CONTEXT_RESTORATION_PROTOCOL.md"
```

---

## ČÁSTEČNÉ WORKFLOW

### WF-010 — Repository Audit

```yaml
id: WF-010
name: "Repository Audit"
description: "Kompletní audit repozitáře (spuštěn v SPOS-004..009)"
steps:
  - "find/ls + head -1 pro detekci stub vs real"
  - "grep ~/STARCORE pro potvrzení Termux stubs"
  - "qc_engine.py run"
  - "starcore diagnose --json"
  - "bandit / pip-audit / ruff / pyright"
agents: [AGENT-003, AGENT-004]
status: ČÁSTEČNÝ (manuální, bez automatizace)
owner: .claude/spos
```

### WF-011 — Documentation Update

```yaml
id: WF-011
name: "Documentation Build + Validation"
trigger: "Manuální (SPOS-006)"
steps:
  - "mkdocs build --strict"
  - "Aktualizace .claude/registry/*.md"
  - "Aktualizace DIGITAL_TWIN.md"
status: ČÁSTEČNÝ (mkdocs build funguje, ostatní manuální)
```

---

## PLÁNOVANÉ WORKFLOW

| ID | Název | Poznámka |
|---|---|---|
| WF-020 | Deployment Workflow (Proxmox) | Blokováno — chybí credentials |
| WF-021 | Knowledge Sync (RAG indexing) | Chybí vector DB |
| WF-022 | Edge Synchronization (Android) | Záměrně odlišná vývojová linie (Termux) |
| WF-023 | Docker Audit | Docker daemon offline v tomto prostředí |
| WF-024 | Release Validation | release_readiness.py existuje, není v CI |
| WF-025 | AI Pipeline (SPOS-011 §11) | Plánováno, kód neexistuje |

---

## STATISTIKY

```yaml
total_workflows: 14 (5 aktivní + 2 částečné + 7 plánované)
active: 5 (WF-001..005)
partial: 2 (WF-010..011)
planned: 7
```
