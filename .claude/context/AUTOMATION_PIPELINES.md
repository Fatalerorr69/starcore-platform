# AUTOMATION PIPELINES

Standard: SPOS-013 §4 | Aktualizováno: 2026-08-07

Kompletní popis automatizačních pipeline v STARCORE ekosystému.

---

## PIPELINE 1 — Repository Change Pipeline

**Trigger:** Git push / PR → main branch

```
git push / PR → main
        ↓
GitHub Actions CI Gate (AUT-001, ci.yml)
        ↓ [parallel jobs]
┌─────────────────────────────────────────────────────┐
│ JOB: quality                                        │
│   uv lock --check           → lockfile integrity    │
│   ruff format --check .     → formatting gate       │
│   ruff check .              → lint gate             │
│   pyright                   → type gate             │
│   pip-audit                 → CVE gate              │
│   bandit -r packages/ -ll   → SAST gate             │
│   gitleaks-action           → secrets gate          │
│   pytest --cov              → test gate (100%)      │
│   alembic check             → migration gate        │
│   mkdocs build --strict     → docs gate             │
│   release.py check-changelog → changelog gate       │
├─────────────────────────────────────────────────────┤
│ JOB: postgres_smoke                                 │
│   postgres service up       → real DB               │
│   alembic upgrade head      → migration check       │
│   pytest tests/postgres/    → PostgreSQL tests      │
├─────────────────────────────────────────────────────┤
│ JOB: docker_build                                   │
│   docker build              → image gate            │
│   curl /health              → smoke test            │
└─────────────────────────────────────────────────────┘
        ↓
GitHub Status Check → [PASS: merge allowed / FAIL: merge blocked]

NAVRHOVANÉ ROZŠÍŘENÍ:
        ↓ (po merge do main)
Impact Analyzer (AUT-054) → identifikuj změněné moduly
        ↓
[if .claude/ změněno] → Digital Twin update
        ↓
[if knowledge/ změněno] → Knowledge validation
```

**Status aktuálního stavu:** AKTIVNÍ — 3 jobs, všechny funkční v CI

---

## PIPELINE 2 — Blueprint Execution Pipeline

**Trigger:** POST /ai/generate-blueprint nebo POST /blueprints/run

```
NL Input (text description)
        ↓
POST /ai/generate-blueprint
        ↓
AnthropicProvider (AUT-074)
  STARCORE_ANTHROPIC_API_KEY → claude-sonnet-5
  System prompt → Blueprint YAML format
  Response → YAML text
        ↓
BlueprintLoader.load_from_string() (AUT-072)
  Pydantic validation → Blueprint model
  Template alias resolution (Proxmox)
        ↓
ExecutionPlanner.create_graph() (AUT-072)
  depends_on validation → ValueError if circular/unknown
  Topological sort → TaskGraph (DAG)
        ↓
POST /blueprints/run [?parallel=true]
        ↓
Scheduler.execute(graph) (AUT-070)
  Wave 1: tasks without dependencies
  Wave 2: tasks whose deps COMPLETED successfully
  asyncio.gather() per wave
        ↓
BaseProvider.execute(action, resource, payload)
  DockerProvider [OFFLINE]
  ProxmoxProvider [OFFLINE]
  KubernetesProvider [OFFLINE]
        ↓
EventBus.emit("task.started") → SSE/WS stream
EventBus.emit("task.completed") → SSE/WS + metrics
EventBus.emit("run.completed") → run_logger + SSE/WS
        ↓
RunRecord → SQLite (platform/data/starcore.db)
        ↓
GET /runs/{run_id} → výsledek dostupný
```

**Status:** AKTIVNÍ (kód) / DEGRADED (providers offline — viz REC-001)

---

## PIPELINE 3 — Security Audit Pipeline

**Trigger A:** Git push/PR → main (součást CI)
**Trigger B:** Schedule 05:00 UTC (starcore-security.yml)
**Trigger C:** Schedule 02:00 UTC (security-nightly.yml, ORPHANED)

```
Trigger
        ↓
[A - CI] Paralelně v quality job:
  pip-audit → CVE scan (DEPENDENCIES gate)
  bandit -r packages/ -ll → SAST (SECURITY gate)
  gitleaks-action → secret scan (SECURITY gate)
        ↓
[B - Nightly] STARCORE Security (AUT-002):
  gitleaks-action → secret scan
  find *.pyc/__pycache__ → file audit
        ↓
GitHub Status Check (A) / Workflow log (B)

LOKÁLNĚ:
  make security → pip-audit + bandit
  make sast → bandit only
  make audit → pip-audit only

NAVRHOVANÉ:
  bandit finding → auto-create VULNERABILITY_REGISTRY entry
  pip-audit CVE → alert + VULNERABILITY_REGISTRY update
```

**Status:** AKTIVNÍ (CI + nightly)

---

## PIPELINE 4 — QC & Governance Pipeline

**Trigger:** MANUAL (session start, post-implementation)

```
Nová session / post-commit
        ↓
startup_protocol.py --quick (AUT-050)
  Step 1: identify repo + branch
  Step 2: HEAD commit
  Step 3: worktree status
  Step 4: project_state.json
  Step 5: last session (ledger.yaml)
  Step 6: risks.md
  Step 7: pending_work.md
  Step 8: decisions
  Step 9: regression_sentinel.py check
  Step 10: GitHub state
  Step 11: Czech report
  Step 12: 6-option decision menu
        ↓
qc_engine.py run --quick (AUT-057)
        ├── regression_sentinel.py → 7 dimensions vs baseline
        └── release_readiness.py → 12 gates
        ↓
Decision Engine Format (AUT-053)
  STAV / CO BYLO ZJIŠTĚNO / RIZIKA / DOPORUČENÍ / DALŠÍ KROK
        ↓
ledger.py add-decision (AUT-051)
  Persistováno do sessions/ledger.yaml
        ↓
[if major change] → DIGITAL_TWIN.md update
        ↓
[if new prompt] → registry.py register (AUT-052)
```

**Status:** AKTIVNÍ (all scripts functional)

---

## PIPELINE 5 — Release Pipeline

**Trigger A:** Manual tag creation via manual-tag.yml
**Trigger B:** Tag push (v*.*.*)

```
Developer: release.py bump X.Y.Z (AUT-060)
  validate CHANGELOG [Unreleased] non-empty
  move [Unreleased] → ## [X.Y.Z] — YYYY-MM-DD
  insert fresh [Unreleased] placeholder
  update pyproject.toml version = "X.Y.Z"
  update core/tracing.py _SERVICE_VERSION
        ↓ [does NOT commit automatically]
git commit + git tag vX.Y.Z
        ↓
manual-tag.yml (AUT-006, TRIG-030)
  Create tag on main
  Dispatch release.yml via workflow_dispatch
        ↓
release.yml (AUT-004)
  uv python install 3.12
  uv sync --extra dev
  Build release artifacts
  GitHub Release creation
        ↓
[parallel] docker-publish.yml (AUT-013, ORPHANED)
  Docker build
  GHCR push (ghcr.io/...)
  SBOM attestation
  cosign keyless signing

LOKÁLNĚ:
  release_readiness.py evaluate → 12-gate check
  release_readiness.py gate TEST → jednotlivé gate
```

**Status:** AKTIVNÍ (release.yml) / ORPHANED (docker-publish.yml)

---

## PIPELINE 6 — Knowledge & Memory Pipeline

**Trigger:** MANUAL (SPOS governance sessions)

```
SPOS Prompt (uživatel)
        ↓
Discovery (read existing files — Discovery First principle)
        ↓
Analysis (verify with live tools where possible)
        ↓
Registry Creation (.claude/registry/*.md)
        ↓
Digital Twin Update (DIGITAL_TWIN.md)
        ↓
SES-INDEX + SPOS_REGISTRY update
        ↓
SPOS-XXX-IMPLEMENTATION-REPORT.md
        ↓
ledger.py add-decision
registry.py register
        ↓
git commit + push (po explicitním schválení)
```

**Status:** MANUAL — vyžaduje AI session (SPOS protokol)

---

## NAVRHOVANÉ NOVÉ PIPELINES

### PIPELINE P1 — Auto Digital Twin Update

```
git commit → GitHub Actions
        ↓
check if .claude/ files changed
        ↓ [if yes]
Run digital_twin_updater.py (navrhovaný)
        ↓
git commit --amend DIGITAL_TWIN.md (nebo nový commit)
        ↓
Push to branch
```

### PIPELINE P2 — Knowledge Sync Pipeline

```
knowledge/ file changed
        ↓
Validate SAKB-000 format
        ↓
Update KNOWLEDGE_REGISTRY.md
        ↓
[future] Generate embeddings → Qdrant index
        ↓
Digital Twin update (knowledge_score)
```

### PIPELINE P3 — Provider Health Monitor

```
Schedule: every 5 minutes (navrhovaný)
        ↓
GET /providers/{name}/health
        ↓
[if status changed] → EventBus emit provider.connected/disconnected
        ↓
Update INTEGRATION_HEALTH.md
        ↓
Alert (Slack/webhook — future)
```
