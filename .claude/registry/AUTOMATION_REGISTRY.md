# AUTOMATION REGISTRY

Standard: SPOS-013 §3 | Aktualizováno: 2026-08-07

Kompletní katalog automatizací STARCORE ekosystému. Vychází z Discovery auditu.

---

## LEGENDA

```yaml
status:
  AKTIVNÍ: Funguje a je aktivně spouštěno
  ORPHANED: Existuje ale není čteno/spouštěno (platform/.github/)
  BROKEN: Existuje ale selhává
  MANUAL: Vyžaduje ruční spuštění
  STUB: Termux/Android shebang stub
categories:
  CI | BUILD | TEST | DEPLOY | DOCS | MEMORY | KNOWLEDGE
  AUDIT | SECURITY | MAINTENANCE | SCHEDULER | WORKFLOW | AI | LEGACY | STUB
```

---

## CI/CD AUTOMATIONS

### GitHub Actions — Root (.github/workflows/)

| ID | Name | Trigger | Category | Status |
|---|---|---|---|---|
| AUT-001 | CI Gate | push/PR → main | CI, TEST, BUILD, SECURITY, DOCS | ✅ AKTIVNÍ |
| AUT-002 | STARCORE Security Nightly | schedule 05:00 UTC daily | SECURITY | ✅ AKTIVNÍ |
| AUT-003 | STARCORE Integrity | push/PR → main | CI | ❌ BROKEN |
| AUT-004 | Release | tag push / workflow_dispatch | BUILD, DEPLOY | ✅ AKTIVNÍ |
| AUT-005 | STARCORE Release | workflow_dispatch | DEPLOY | ✅ AKTIVNÍ |
| AUT-006 | Manual Tag | workflow_dispatch | CI | ✅ AKTIVNÍ |

#### AUT-001 — CI Gate (detail)

```yaml
id: AUT-001
name: "CI Gate"
file: ".github/workflows/ci.yml"
trigger: "push/PR to main"
frequency: per_commit
inputs: [source_code, uv.lock, Dockerfile]
outputs: [pass/fail status, coverage report, docker image (ci-test)]
jobs:
  quality:
    - lockfile check (uv lock --check)
    - ruff format check
    - ruff lint check
    - pyright type check
    - pip-audit CVE scan
    - bandit SAST
    - gitleaks secret scan
    - pytest (100% coverage)
    - alembic migration check
    - mkdocs build --strict
    - changelog gate check
  postgres_smoke:
    - alembic upgrade head (PostgreSQL)
    - PostgreSQL smoke tests
  docker_build:
    - docker build
    - /health smoke test
dependencies: [uv, python 3.12, platform/Dockerfile]
risk: HIGH (blocks merge)
health: OK
```

#### AUT-002 — STARCORE Security Nightly (detail)

```yaml
id: AUT-002
name: "STARCORE Security"
file: ".github/workflows/starcore-security.yml"
trigger: "schedule 0 5 * * * (05:00 UTC)"
frequency: daily
inputs: [source_code, .gitleaks.toml]
outputs: [security report]
steps:
  - gitleaks secret scan
  - file audit (find *.pyc, __pycache__)
dependencies: [gitleaks-action]
risk: MEDIUM
health: OK
```

#### AUT-003 — STARCORE Integrity (BROKEN)

```yaml
id: AUT-003
name: "STARCORE Integrity"
file: ".github/workflows/starcore-integrity.yml"
trigger: "push/PR to main"
status: BROKEN
reason: "References non-existent root core/ directory"
fix: "See INTEGRATION_RECOMMENDATIONS.md REC-002"
risk: MEDIUM (CI noise, masks real failures)
```

### GitHub Actions — Platform (platform/.github/workflows/) — ORPHANED

| ID | Name | Trigger | Category | Status |
|---|---|---|---|---|
| AUT-010 | Platform CI Gate | push/PR → main | CI, TEST, BUILD | ⚠️ ORPHANED |
| AUT-011 | CodeQL Analysis | push/PR/schedule Sun 13:40 UTC | SECURITY | ⚠️ ORPHANED |
| AUT-012 | Dependabot Auto-merge | pull_request (Dependabot) | MAINTENANCE | ⚠️ ORPHANED |
| AUT-013 | Docker Publish | push main / tag | DEPLOY, BUILD | ⚠️ ORPHANED |
| AUT-014 | Security Nightly | schedule 02:00 UTC daily | SECURITY, AUDIT | ⚠️ ORPHANED |
| AUT-015 | Platform Release | tag push | DEPLOY | ⚠️ ORPHANED |
| AUT-016 | Platform Manual Tag | workflow_dispatch | CI | ⚠️ ORPHANED |

**Poznámka:** GitHub čte workflows pouze z root `.github/workflows/`. Všechny soubory v `platform/.github/workflows/` jsou ORPHANED — nevykonávají se. Obsahují však nejúplnější implementaci CI/CD (ci.yml = AUT-010 je nejrobustnější workflow v projektu).

---

## MAKEFILE AUTOMATIONS

| ID | Name | Command | Category | Status |
|---|---|---|---|---|
| AUT-020 | Install Dependencies | `make install` | BUILD | MANUAL |
| AUT-021 | Lint | `make lint` | CI | MANUAL |
| AUT-022 | Format | `make format` | CI | MANUAL |
| AUT-023 | Format Check | `make format-check` | CI | MANUAL |
| AUT-024 | Type Check | `make type-check` | CI | MANUAL |
| AUT-025 | All Checks | `make all-checks` | CI | MANUAL |
| AUT-026 | Test | `make test` | TEST | MANUAL |
| AUT-027 | Test with Coverage | `make test-cov` | TEST | MANUAL |
| AUT-028 | Test Watch | `make test-watch` | TEST | MANUAL |
| AUT-029 | Security | `make security` | SECURITY | MANUAL |
| AUT-030 | Audit (pip-audit) | `make audit` | SECURITY | MANUAL |
| AUT-031 | SAST (bandit) | `make sast` | SECURITY | MANUAL |
| AUT-032 | Dev Server | `make dev` | CI | MANUAL |
| AUT-033 | Health Check | `make health` | MONITORING | MANUAL |
| AUT-034 | Doctor | `make doctor` | AUDIT | MANUAL |
| AUT-035 | Diagnose | `make diagnose` | AUDIT | MANUAL |
| AUT-036 | Docs Serve | `make docs` | DOCS | MANUAL |
| AUT-037 | Docs Build | `make docs-build` | DOCS | MANUAL |
| AUT-038 | Clean | `make clean` | MAINTENANCE | MANUAL |
| AUT-039 | Migration Status | `make migrations` | MAINTENANCE | MANUAL |
| AUT-040 | Pre-commit Local | `make pre-commit` | CI | MANUAL |
| AUT-041 | Full CI Local | `make ci` | CI | MANUAL |

---

## PRE-COMMIT AUTOMATIONS

| ID | Name | Hook | Category | Status |
|---|---|---|---|---|
| AUT-045 | Ruff Lint (pre-commit) | `ruff --fix` | CI, SECURITY | AKTIVNÍ (local) |
| AUT-046 | Ruff Format (pre-commit) | `ruff-format` | CI | AKTIVNÍ (local) |
| AUT-047 | Pyright (pre-commit) | `uv run pyright` | CI | AKTIVNÍ (local) |

---

## PYTHON AUTOMATION SCRIPTS (.starcore/scripts/)

| ID | Name | CLI | Category | Status |
|---|---|---|---|---|
| AUT-050 | Startup Protocol | `startup_protocol.py [--quick] [--json]` | MEMORY, AUDIT | ✅ AKTIVNÍ |
| AUT-051 | Session Ledger | `ledger.py start/end/current/add-*` | MEMORY | ✅ AKTIVNÍ |
| AUT-052 | Prompt Registry | `registry.py register/list/search/validate` | MEMORY, KNOWLEDGE | ✅ AKTIVNÍ |
| AUT-053 | Decision Engine | `decision_engine.py format/render/log` | WORKFLOW | ✅ AKTIVNÍ |
| AUT-054 | Impact Analyzer | `impact_analyzer.py analyze/module` | AUDIT, CI | ✅ AKTIVNÍ |
| AUT-055 | Regression Sentinel | `regression_sentinel.py check/diff/update` | AUDIT, CI | ✅ AKTIVNÍ |
| AUT-056 | Release Readiness | `release_readiness.py evaluate/gate` | DEPLOY, AUDIT | ✅ AKTIVNÍ |
| AUT-057 | QC Engine | `qc_engine.py run [--quick] [--impact]` | AUDIT, CI | ✅ AKTIVNÍ |

---

## PLATFORM SCRIPTS (platform/scripts/)

| ID | Name | CLI | Category | Status |
|---|---|---|---|---|
| AUT-060 | Release Helper | `release.py check-changelog / bump VERSION` | DEPLOY | ✅ AKTIVNÍ |
| AUT-061 | Health Check | `health.py [--url]` | MONITORING | ✅ AKTIVNÍ |
| AUT-062 | Doctor (local CI) | `doctor.py` | AUDIT, CI | ✅ AKTIVNÍ |
| AUT-063 | Quickstart | `quickstart.sh` | BUILD | MANUAL |
| AUT-064 | Copilot Setup | `setup-copilot.sh` | CI | MANUAL |
| AUT-065 | Integration Verify | `verify-integration.sh` | CI | MANUAL |

---

## CORE PLATFORM AUTOMATION (packages/)

| ID | Name | Location | Category | Status |
|---|---|---|---|---|
| AUT-070 | Async Scheduler | `packages/orchestrator/scheduler.py` | SCHEDULER, WORKFLOW | ✅ AKTIVNÍ |
| AUT-071 | Task Graph (DAG) | `packages/orchestrator/task_graph.py` | SCHEDULER | ✅ AKTIVNÍ |
| AUT-072 | Blueprint Planner | `packages/blueprints/planner.py` | WORKFLOW, AI | ✅ AKTIVNÍ |
| AUT-073 | Blueprint Executor | `packages/blueprints/executor.py` | WORKFLOW | ✅ AKTIVNÍ |
| AUT-074 | AI Blueprint Generator | `packages/ai/generator.py` | AI, WORKFLOW | ✅ AKTIVNÍ |
| AUT-075 | EventBus | `packages/core/events.py` | SCHEDULER | ✅ AKTIVNÍ |
| AUT-076 | Plugin Manager | `packages/core/plugin_manager.py` | WORKFLOW | ✅ AKTIVNÍ |
| AUT-077 | Provider Registry | `packages/provider_sdk/registry.py` | WORKFLOW, INFRASTRUCTURE | ✅ AKTIVNÍ |
| AUT-078 | Run Logger Plugin | `plugins/run_logger/` | AUDIT, MEMORY | ✅ AKTIVNÍ |
| AUT-079 | Metrics Collector | `packages/core/metrics.py` | MONITORING | ✅ AKTIVNÍ |

---

## LEGACY / STUB AUTOMATIONS

| ID | Name | Category | Status |
|---|---|---|---|
| AUT-090 | install_*.sh (65x) | LEGACY | STUB (Termux) |
| AUT-091 | repair_ENGINEERING_LAYER.sh | MAINTENANCE | STUB (Termux) |
| AUT-092 | generate_7x_bulk_packages.sh | BUILD | STUB (Termux) |
| AUT-093 | control_center/modules/*.sh | INFRASTRUCTURE | STUB (Termux) |
| AUT-094 | runtime/android/ | SCHEDULER | STUB |
| AUT-095 | installers/android/ | DEPLOY | STUB |

---

## STATISTIKY

```yaml
total_automations: 51
active: 29
manual: 16
orphaned: 7
broken: 1
stub: ~70 (legacy Termux)

by_category:
  CI: 10
  TEST: 4
  SECURITY: 6
  BUILD: 4
  DEPLOY: 4
  AUDIT: 6
  MAINTENANCE: 4
  SCHEDULER: 3
  WORKFLOW: 5
  AI: 2
  MEMORY: 3
  MONITORING: 2
  DOCS: 2
  LEGACY/STUB: 70+
```
