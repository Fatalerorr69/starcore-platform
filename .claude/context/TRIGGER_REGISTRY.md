# TRIGGER REGISTRY

Standard: SPOS-013 §6 | Aktualizováno: 2026-08-07

Registr všech triggerů automatizací v STARCORE ekosystému.

---

## TRIGGER TYPY

| Typ | Popis | Příklady v projektu |
|---|---|---|
| MANUAL | Ruční spuštění | Makefile targets, CLI scripts |
| GIT_PUSH | Push do větve | ci.yml, starcore-integrity.yml |
| GIT_PR | Pull Request | ci.yml, dependabot-auto-merge.yml |
| GIT_MERGE | Merge do main | docker-publish.yml |
| GIT_TAG | Tag push | release.yml, docker-publish.yml |
| SCHEDULE | Časovač (cron) | starcore-security.yml, security-nightly.yml |
| WEBHOOK | GitHub webhook | workflow_dispatch |
| FILE_CHANGE | Změna souboru | pre-commit hooks |
| API_EVENT | API volání | EventBus (task.started, task.completed) |
| PROVIDER_EVENT | Provider stav | EventBus (run.completed) |
| PLUGIN_EVENT | Plugin akce | run_logger plugin |
| SESSION_START | Spuštění session | startup_protocol.py |
| INFRA_EVENT | Infrastructure | BaseProvider lifecycle |

---

## TRIGGER KATALOG

### SCHEDULE Triggers (Cron)

| TRIG-ID | Workflow | Cron | UTC Time | Status |
|---|---|---|---|---|
| TRIG-001 | STARCORE Security (starcore-security.yml) | `0 5 * * *` | 05:00 každý den | ✅ AKTIVNÍ |
| TRIG-002 | Security Nightly (security-nightly.yml) | `0 2 * * *` | 02:00 každý den | ⚠️ ORPHANED |
| TRIG-003 | CodeQL (codeql.yml) | `40 13 * * 0` | neděle 13:40 | ⚠️ ORPHANED |

### GIT_PUSH Triggers

| TRIG-ID | Workflow | Branch | Status |
|---|---|---|---|
| TRIG-010 | ci.yml | main | ✅ AKTIVNÍ |
| TRIG-011 | starcore-integrity.yml | main | ❌ BROKEN |
| TRIG-012 | release.yml | tags v*.*.* | ✅ AKTIVNÍ |
| TRIG-013 | starcore-release.yml | tags | ✅ AKTIVNÍ |
| TRIG-014 | docker-publish.yml | main + tags | ⚠️ ORPHANED |
| TRIG-015 | platform/ci.yml | main | ⚠️ ORPHANED |
| TRIG-016 | codeql.yml | main | ⚠️ ORPHANED |

### GIT_PR Triggers

| TRIG-ID | Workflow | Target | Status |
|---|---|---|---|
| TRIG-020 | ci.yml | main | ✅ AKTIVNÍ |
| TRIG-021 | starcore-integrity.yml | main | ❌ BROKEN |
| TRIG-022 | dependabot-auto-merge.yml | any | ⚠️ ORPHANED |
| TRIG-023 | platform/ci.yml | main | ⚠️ ORPHANED |
| TRIG-024 | codeql.yml | main | ⚠️ ORPHANED |

### WEBHOOK / workflow_dispatch Triggers

| TRIG-ID | Workflow | Podmínka | Status |
|---|---|---|---|
| TRIG-030 | manual-tag.yml | workflow_dispatch (tag input) | ✅ AKTIVNÍ |
| TRIG-031 | release.yml | workflow_dispatch (tag input) | ✅ AKTIVNÍ |
| TRIG-032 | starcore-security.yml | workflow_dispatch | ✅ AKTIVNÍ |
| TRIG-033 | security-nightly.yml | workflow_dispatch | ⚠️ ORPHANED |

### FILE_CHANGE Triggers (pre-commit)

| TRIG-ID | Hook | Soubory | Status |
|---|---|---|---|
| TRIG-040 | ruff lint+fix | *.py | AKTIVNÍ (local) |
| TRIG-041 | ruff format | *.py | AKTIVNÍ (local) |
| TRIG-042 | pyright | *.py | AKTIVNÍ (local) |

### API_EVENT Triggers (EventBus)

| TRIG-ID | Event | Emitter | Subscribers | Status |
|---|---|---|---|---|
| TRIG-050 | task.started | Scheduler | SSE/WS handlers | ✅ AKTIVNÍ |
| TRIG-051 | task.completed | Scheduler | SSE/WS handlers, metrics | ✅ AKTIVNÍ |
| TRIG-052 | run.completed | Scheduler | run_logger plugin, SSE/WS | ✅ AKTIVNÍ |

### SESSION_START Triggers

| TRIG-ID | Script | Popis | Status |
|---|---|---|---|
| TRIG-060 | startup_protocol.py | Cold-start 12-step init | MANUAL |
| TRIG-061 | ledger.py start | Nová session v ledgeru | MANUAL |

### MANUAL Triggers (Makefile / CLI)

| TRIG-ID | Command | Spouští | Status |
|---|---|---|---|
| TRIG-070 | `make ci` | Full CI locally | MANUAL |
| TRIG-071 | `make test` | pytest | MANUAL |
| TRIG-072 | `make security` | pip-audit + bandit | MANUAL |
| TRIG-073 | `make docs-build` | mkdocs --strict | MANUAL |
| TRIG-074 | `qc_engine.py run` | QC report | MANUAL |
| TRIG-075 | `impact_analyzer.py analyze` | Impact analysis | MANUAL |
| TRIG-076 | `regression_sentinel.py check` | Drift detection | MANUAL |
| TRIG-077 | `release_readiness.py evaluate` | 12-gate readiness | MANUAL |

---

## TRIGGER COVERAGE MATRIX

```
Trigger Type       | Active | Orphaned | Broken | Manual
-------------------+--------+----------+--------+-------
Schedule (cron)    |   1    |    2     |   0    |   0
Git Push           |   3    |    4     |   1    |   0
Git PR             |   1    |    3     |   1    |   0
Webhook/dispatch   |   3    |    1     |   0    |   0
File Change        |   3    |    0     |   0    |   0
API Event          |   3    |    0     |   0    |   0
Session Start      |   0    |    0     |   0    |   2
Manual CLI         |   0    |    0     |   0    |   8
-------------------+--------+----------+--------+-------
TOTAL             |  14    |   10     |   2    |  10
```

---

## CHYBĚJÍCÍ TRIGGERY (GAP)

```yaml
missing_triggers:
  - "Webhook při Git Push → auto update Digital Twin (TRIG-P01)"
  - "Trigger při nové knowledge/ file → auto validate + index (TRIG-P02)"
  - "Trigger při registry change → auto cross-check duplicates (TRIG-P03)"
  - "Scheduled Weekly Health Report → auto send (TRIG-P04)"
  - "Provider connected/disconnected event → update INTEGRATION_HEALTH (TRIG-P05)"
  - "Release tag → auto bump CHANGELOG + project_snapshot (TRIG-P06)"
```
