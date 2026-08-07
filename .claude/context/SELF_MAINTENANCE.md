# SELF MAINTENANCE ENGINE

Standard: SPOS-013 §8 | Aktualizováno: 2026-08-07

Design samoudržovacích mechanismů STARCORE Automation Engine.

---

## DEFINICE

Self Maintenance Engine (SME) je sada mechanismů, které zajišťují, že automatizační infrastruktura STARCORE se udržuje bez trvalé manuální intervence. Zahrnuje: detekci degradace, automatické opravy, audit konzistence a eskalaci anomálií.

---

## SOUČASNÝ STAV SELF MAINTENANCE

```yaml
self_maintenance_level: PARTIAL (Level 2/5)
automated_self_repair: ŽÁDNÝ
automated_health_checks: CI gate (per commit), nightly security
automated_drift_detection: regression_sentinel.py (MANUÁLNÍ)
automated_cleanup: ŽÁDNÝ
automated_notifications: GitHub Actions failures only
escalation_paths: GitHub Actions email / repo notification
```

### Co funguje automaticky

| Mechanismus | Trigger | Co kontroluje |
|---|---|---|
| CI Gate (AUT-001) | Každý push/PR | Lint, types, security, tests, docker |
| Nightly Security (AUT-002) | 05:00 UTC daily | Secrets scan + file audit |
| regression_sentinel.py | MANUÁLNÍ | 7 dimensí drift od baseline |
| release_readiness.py | MANUÁLNÍ | 12 release gates |
| pre-commit hooks | git commit | Lint + format + types |

### Co chybí

- Automatická oprava degradovaných automatizací
- Scheduled QC report (bez manuálního spuštění)
- Automatická aktualizace DIGITAL_TWIN po commitu
- Provider health monitoring (continuous)
- Detekce orphaned automations po refaktoru

---

## NAVRHOVANÝ SELF MAINTENANCE ARCHITECTURE

```
╔══════════════════════════════════════════════════════════════╗
║              SELF MAINTENANCE ENGINE (navrhovaný)            ║
╠══════════════════════════════════════════════════════════════╣
║  DETECTION LAYER                                             ║
║  CI Gate | Nightly Scan | Scheduled QC | Drift Sentinel      ║
╠══════════════════════════════════════════════════════════════╣
║  ANALYSIS LAYER                                              ║
║  Impact Analyzer | Regression Sentinel | Release Readiness   ║
╠══════════════════════════════════════════════════════════════╣
║  REPAIR LAYER (navrhovaný)                                   ║
║  Auto-fix lint | Auto-update lockfile | Auto-close orphans   ║
╠══════════════════════════════════════════════════════════════╣
║  NOTIFICATION LAYER                                          ║
║  GitHub Actions | (future: Slack/webhook)                    ║
╠══════════════════════════════════════════════════════════════╣
║  PERSISTENCE LAYER                                           ║
║  ledger.yaml | regression_baseline.json | DIGITAL_TWIN.md   ║
╚══════════════════════════════════════════════════════════════╝
```

---

## SELF MAINTENANCE SCÉNÁŘE

### SME-001 — Lockfile Drift

```yaml
id: SME-001
name: Lockfile Drift Detection & Repair
trigger: CI gate (uv lock --check)
current_state: "CI selhává pokud uv.lock !== pyproject.toml"
detection: "uv lock --check v quality job"
repair_manual: "Vývojář spustí uv lock, commituje"
repair_auto_proposed: "GitHub Actions: uv lock + git commit --amend (or PR)"
risk: LOW (žádná ztráta dat)
effort: NÍZKÁ
```

### SME-002 — Broken Workflow Detection

```yaml
id: SME-002
name: Broken GitHub Actions Detection
trigger: CI push → main
current_state: "starcore-integrity.yml BROKEN — referuje neexistující core/"
detection: "Workflow syntax valid, ale job failuje při checkout steps"
repair_manual: "Fix workflow YAML referovat skutečné paths"
repair_auto_proposed: "Workflow validator script: check all referenced paths exist"
risk: MEDIUM (CI noise, masks failures)
effort: NÍZKÁ
```

### SME-003 — Test Coverage Drift

```yaml
id: SME-003
name: Test Coverage Enforcement
trigger: CI gate (pytest --cov-fail-under=100)
current_state: "AKTIVNÍ — CI blokuje merge při < 100% coverage"
detection: "pytest --cov --cov-fail-under=100"
repair_manual: "Vývojář přidá chybějící testy"
repair_auto_proposed: "N/A — výsledky testů vyžadují lidský úsudek"
risk: HIGH (degradace quality gate)
effort: VYSOKÁ (nelze plně automatizovat)
```

### SME-004 — Dependency CVE Response

```yaml
id: SME-004
name: CVE Vulnerability Auto-response
trigger: CI gate (pip-audit) nebo Dependabot PR
current_state: "Manuální — pip-audit failuje CI, vývojář musí aktualizovat"
detection: "pip-audit v CI quality job"
repair_manual: "uv add <package>@latest, commit, push"
repair_auto_proposed: |
  Dependabot auto-merge (AUT-012 — ORPHANED).
  Přesun dependabot-auto-merge.yml do root .github/workflows/ by umožnil
  automatické mergování patch/minor updates.
risk: HIGH (CVE nezaplátované)
effort: NÍZKÁ (stačí přesunout existující workflow)
```

### SME-005 — DIGITAL_TWIN Staleness

```yaml
id: SME-005
name: Digital Twin Auto-sync
trigger: GIT_PUSH (main) nebo FILE_CHANGE (.claude/)
current_state: "MANUÁLNÍ — aktualizace DIGITAL_TWIN.md vyžaduje AI session"
detection: "Žádná — DIGITAL_TWIN může být out-of-date neurčenou dobu"
repair_manual: "AI session → DIGITAL_TWIN.md update"
repair_auto_proposed: |
  digital_twin_updater.py (navrhovaný):
    - Čte project_state.json + ledger.yaml + registry files
    - Generuje diff DIGITAL_TWIN.md sections
    - Spouštěno z GitHub Actions po merge do main
risk: MEDIUM (stale governance context)
effort: STŘEDNÍ
```

### SME-006 — Provider Offline Detection

```yaml
id: SME-006
name: Provider Health Auto-monitor
trigger: SCHEDULE nebo EventBus provider.connected/disconnected
current_state: "MANUÁLNÍ — GET /providers/{name}/health jen na požádání"
detection: "Žádná kontinuální — providers vždy OFFLINE (Docker, Proxmox, K8s)"
repair_manual: "Spuštění skutečné infrastruktury"
repair_auto_proposed: |
  Provider Health Monitor (WF-P03):
    - Schedule: každých 5 minut
    - GET /providers/{name}/health
    - EventBus emit provider.connected/disconnected
    - Update INTEGRATION_HEALTH.md
risk: LOW (dev env — providers záměrně offline)
effort: STŘEDNÍ
```

### SME-007 — Regression Baseline Drift

```yaml
id: SME-007
name: Regression Baseline Auto-update
trigger: MANUAL (post-intentional change)
current_state: |
  regression_sentinel.py check porovnává aktuální stav s regression_baseline.json.
  Při záměrné změně (např. nové testy) musí vývojář manuálně spustit
  regression_sentinel.py update --reason "added X tests"
detection: "regression_sentinel.py check — 7 dimenzí"
repair_manual: "regression_sentinel.py update --reason <důvod>"
repair_auto_proposed: |
  CI integration: automatická kontrola, ale update vždy MANUÁLNÍ
  (záměrné vs nezáměrné změny musí rozlišit člověk)
risk: MEDIUM (false positives z intentional changes)
effort: NÍZKÁ
```

---

## SELF MAINTENANCE ROADMAP

```yaml
fase_1_immediate:
  effort: NÍZKÁ
  actions:
    - SME-002: Fix starcore-integrity.yml (broken workflow)
    - SME-004: Přesunout dependabot-auto-merge.yml do root .github/
  status: DOPORUČENO pro SPOS-014

fase_2_short_term:
  effort: STŘEDNÍ
  actions:
    - SME-005: Implementovat digital_twin_updater.py
    - SME-006: Implementovat Provider Health Monitor
  status: NAVRHOVÁNO (WF-P01, WF-P03)

fase_3_long_term:
  effort: VYSOKÁ
  actions:
    - Plně automatizovaný QC report (scheduled, ne jen manuální)
    - Self-healing CI (auto-fix na minor drift)
    - Centralizovaný alert systém (Slack/webhook)
  status: VÝHLED (SPOS-016+)
```

---

## SELF MAINTENANCE METRIKY

| Metrika | Současný stav | Cíl |
|---|---|---|
| Automated health checks / týden | ~7 (nightly CI) | 49+ |
| Mean Time to Detection (MTTDetect) | ≤24h (nightly) | ≤1h |
| Mean Time to Repair (MTTRepair) | MANUÁLNÍ (undefined) | ≤4h automated |
| Self-repair rate | 0% | 30%+ |
| Staleness of DIGITAL_TWIN | 0-N days (manuální) | ≤1 den |
| Orphaned automations detected | MANUÁLNÍ | automaticky |

---

## INTEGRACE S EXISTUJÍCÍM SYSTÉMEM

```
Self Maintenance Engine
    ├── Detection: CI Gate (AUT-001) [AKTIVNÍ]
    ├── Detection: Nightly Security (AUT-002) [AKTIVNÍ]
    ├── Detection: regression_sentinel.py (AUT-055) [MANUÁLNÍ]
    ├── Analysis: impact_analyzer.py (AUT-054) [MANUÁLNÍ]
    ├── Repair: pre-commit autofix (AUT-045, AUT-046) [AKTIVNÍ]
    ├── Repair: Dependabot (AUT-012) [ORPHANED]
    ├── Persistence: ledger.yaml [AKTIVNÍ]
    ├── Persistence: regression_baseline.json [AKTIVNÍ]
    └── Notification: GitHub Actions email [AKTIVNÍ]
```
