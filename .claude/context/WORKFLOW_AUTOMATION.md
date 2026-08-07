# WORKFLOW AUTOMATION

Standard: SPOS-013 §7 | Aktualizováno: 2026-08-07

Popis Workflow Engine a jednotlivých automatizovaných workflows v STARCORE.

---

## WORKFLOW ENGINE OVERVIEW

```yaml
primary_engine: "GitHub Actions (CI/CD workflows)"
secondary_engine: "asyncio Scheduler (blueprint execution)"
tertiary_engine: "Python QC scripts (governance workflows)"
local_engine: "GNU Make (developer shortcuts)"
hook_engine: "pre-commit (file change workflows)"
```

---

## DEFINOVANÉ WORKFLOWS

### WF-A01 — Full CI Workflow

```yaml
name: Full CI Workflow
goal: "Ověřit kvalitu kódu a bezpečnost před merge"
trigger: GIT_PUSH, GIT_PR (main)
actors: [GitHub Actions Runner, uv, pytest, ruff, pyright, bandit, gitleaks, docker]
inputs:
  - source_code (all packages)
  - platform/Dockerfile
  - uv.lock
  - pyproject.toml
outputs:
  - GitHub Status Check (PASS/FAIL)
  - Coverage report
  - Docker image (ci-test, ephemeral)
steps:
  1. Checkout (fetch-depth: 0)
  2. Install uv + Python 3.12
  3. uv sync --extra dev
  4. uv lock --check
  5. ruff format --check
  6. ruff check
  7. pyright
  8. pip-audit
  9. bandit
  10. gitleaks
  11. pytest --cov --cov-fail-under=100
  12. alembic check
  13. mkdocs build --strict
  14. release.py check-changelog
  [parallel] PostgreSQL smoke tests
  [parallel] Docker build + /health smoke test
dependencies: [GitHub Actions, uv, all dev tools]
failure_handling: "Job failure → merge blocked"
recovery: "Fix failing gate, push new commit"
status: AKTIVNÍ
```

### WF-A02 — Nightly Security Workflow

```yaml
name: Nightly Security Workflow
goal: "Denní bezpečnostní kontrola mimo PR cyklus"
trigger: SCHEDULE (05:00 UTC daily)
actors: [GitHub Actions Runner, gitleaks]
inputs: [source_code, .gitleaks.toml]
outputs: [Workflow log, GitHub Actions result]
steps:
  1. Checkout
  2. gitleaks secret scan
  3. find *.pyc/__pycache__ (file audit)
failure_handling: "Alert via GitHub Actions notification"
recovery: "Investigate finding, add to VULNERABILITY_REGISTRY"
status: AKTIVNÍ
```

### WF-A03 — Release Workflow

```yaml
name: Release Workflow
goal: "Vytvoření GitHub Release z tagu"
trigger: GIT_TAG (v*.*.*)
actors: [GitHub Actions Runner, uv, release.py]
inputs: [git tag, CHANGELOG.md, pyproject.toml]
outputs: [GitHub Release, release artifacts]
steps:
  1. Checkout (at tag)
  2. Set RELEASE_TAG env
  3. Install uv + Python 3.12
  4. Install dependencies
  5. Build release artifacts
  6. Create GitHub Release
dependencies: [release.yml, manual-tag.yml]
failure_handling: "Workflow failure → release not created"
status: AKTIVNÍ
```

### WF-A04 — Blueprint Execution Workflow

```yaml
name: Blueprint Execution Workflow
goal: "Vykonat infrastructure blueprint přes AI + providers"
trigger: API_EVENT (POST /blueprints/run)
actors: [FastAPI, AnthropicProvider, Scheduler, BaseProvider implementations]
inputs:
  - Blueprint YAML (or NL description for /ai/generate-blueprint)
outputs:
  - RunRecord (SQLite)
  - Task results per provider
  - SSE/WS event stream
steps:
  1. [Optional] /ai/generate-blueprint → YAML generation
  2. BlueprintLoader validation
  3. ExecutionPlanner → TaskGraph
  4. Scheduler wave execution (parallel per wave)
  5. BaseProvider.execute() per task
  6. EventBus.emit() per state change
  7. RunRecord persistence
failure_handling:
  - Task FAILED → dependents SKIPPED_DEPENDENCY_FAILED
  - Timeout exceeded → task FAILED (TimeoutStrategy.CANCEL)
  - Provider error → task FAILED + logged
recovery: "Retry blueprint via new run; fix provider offline issue"
status: AKTIVNÍ (kód) / DEGRADED (providers offline)
```

### WF-A05 — QC Governance Workflow

```yaml
name: QC Governance Workflow
goal: "Komplexní quality check po každé implementaci"
trigger: MANUAL (session start / post-SPOS implementation)
actors: [qc_engine.py, regression_sentinel.py, release_readiness.py]
inputs:
  - git repository state
  - regression_baseline.json
outputs:
  - Decision Engine formatted report
  - WARNING / FAIL / PASS verdict
steps:
  1. regression_sentinel.py check → 7 dimensions
  2. release_readiness.py evaluate --quick → 12 gates
  3. decision_engine.py format → structured report
  4. ledger.py add-decision → persistence
failure_handling: "FAIL verdict → document in ledger, fix before release"
recovery: "Fix detected drift, re-run sentinel, update baseline if intentional"
status: AKTIVNÍ
```

### WF-A06 — Session Lifecycle Workflow

```yaml
name: Session Lifecycle Workflow
goal: "Správa AI session kontextu napříč sezeními"
trigger: SESSION_START / SESSION_END
actors: [startup_protocol.py, ledger.py, registry.py]
inputs: [previous ledger.yaml, project_state.json, DIGITAL_TWIN.md]
outputs:
  - Czech status report
  - Active session in ledger.yaml
  - session archive on end
steps:
  START:
    1. startup_protocol.py --quick
    2. ledger.py start (if new session)
    3. Read DIGITAL_TWIN.md + SPOS_REGISTRY
  END:
    1. ledger.py end → archive
    2. Update current_state.md
    3. Update DIGITAL_TWIN.md (if major changes)
failure_handling: "Orphaned session detected → close via ledger.py end"
status: AKTIVNÍ
```

### WF-A07 — Pre-commit Developer Workflow

```yaml
name: Pre-commit Developer Workflow
goal: "Automatická kontrola kvality před každým commitem"
trigger: FILE_CHANGE (git commit)
actors: [pre-commit, ruff, pyright]
inputs: [staged .py files]
outputs: [fixed/formatted files OR commit blocked]
steps:
  1. ruff --fix (autofix lint issues)
  2. ruff-format (autoformat)
  3. pyright (type check — blocks commit if errors)
failure_handling:
  - ruff autofix → commit continues with fixes
  - pyright errors → commit BLOCKED
recovery: "Fix type errors manually, re-stage, re-commit"
status: AKTIVNÍ (lokální developer workflow)
```

### WF-A08 — Dependabot Auto-merge Workflow

```yaml
name: Dependabot Auto-merge Workflow
goal: "Automatické mergování patch/minor dependency updates"
trigger: GIT_PR (dependabot[bot])
actors: [GitHub Actions, dependabot, gh CLI]
inputs: [Dependabot PR, semver update type]
outputs: [merged PR OR skipped (major updates)]
condition: "package-ecosystem == pip AND update-type IN [patch, minor]"
failure_handling: "Major updates → skip, require manual review"
status: ORPHANED (platform/.github/ not read by GitHub)
```

---

## NAVRHOVANÉ WORKFLOWS (GAP)

### WF-P01 — Auto Digital Twin Sync

```yaml
name: Auto Digital Twin Sync
goal: "Automatická synchronizace DIGITAL_TWIN.md po každém commitu"
trigger: GIT_PUSH (main)
actors: [GitHub Actions, Python script]
effort: STŘEDNÍ
prerequisite: "Implementovat digital_twin_updater.py"
impact: "Eliminuje manuální aktualizaci Digital Twin"
```

### WF-P02 — Knowledge Validation Workflow

```yaml
name: Knowledge Validation Workflow
goal: "Validace knowledge/ profilů při každém commitu"
trigger: FILE_CHANGE (knowledge/**/*.md)
actors: [GitHub Actions, SAKB validator]
effort: NÍZKÁ
prerequisite: "Implementovat sakb_validator.py"
impact: "Automatické ověření formátu knowledge profiles"
```

### WF-P03 — Provider Health Monitor Workflow

```yaml
name: Provider Health Monitor
goal: "Průběžné sledování stavu providers"
trigger: SCHEDULE (každých 5 min) nebo EventBus
actors: [FastAPI /providers/{name}/health, EventBus]
effort: STŘEDNÍ
prerequisite: "Persistent EventBus nebo NATS"
impact: "Real-time provider health v INTEGRATION_HEALTH.md"
```
