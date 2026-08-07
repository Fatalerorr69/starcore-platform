# AUTOMATION HEALTH

Standard: SPOS-013 §9 | Aktualizováno: 2026-08-07

Zdravotní report automatizační infrastruktury STARCORE. Vychází z Discovery auditu 2026-08-07.

---

## AUTOMATION HEALTH SCORE

```yaml
automation_health_score: 61%
score_date: 2026-08-07
methodology: "Vážený průměr 6 zdravotních dimenzí"
```

### Dimenze zdraví

| Dimenze | Skóre | Váha | Zdůvodnění |
|---|---|---|---|
| CI/CD Coverage | 75% | 25% | 3 aktivní CI jobs, ale 7 workflows ORPHANED |
| Security Automation | 80% | 20% | pip-audit + bandit + gitleaks v CI, nightly scan |
| Test Automation | 95% | 20% | 100% coverage gate enforced, 805+ tests |
| Governance Automation | 45% | 15% | QC scripts MANUÁLNÍ, žádný scheduled QC |
| Self-Maintenance | 20% | 10% | Téměř žádný self-repair, DIGITAL_TWIN manuální |
| Observability | 50% | 10% | EventBus in-process, žádný external monitoring |
| **CELKEM** | **61%** | 100% | |

---

## ZDRAVOTNÍ STAV KOMPONENT

### GitHub Actions CI/CD

```yaml
component: GitHub Actions (AUT-001..006)
health: 70%
active_workflows: 2 (ci.yml, starcore-security.yml)
broken_workflows: 1 (starcore-integrity.yml)
orphaned_workflows: 7 (platform/.github/workflows/*)
issues:
  - BROKEN: starcore-integrity.yml referuje neexistující core/ adresář
  - ORPHANED: 7 workflows v platform/.github/ nikdy nespouštěno
  - MISSING: CodeQL security scan (codeql.yml ORPHANED)
  - MISSING: Dependabot auto-merge (ORPHANED)
  - MISSING: Docker publish pipeline (ORPHANED)
strengths:
  - Full CI gate (lint+types+security+tests+docker) funkční
  - Paralelní jobs (quality + postgres_smoke + docker_build)
  - 100% coverage gate enforced
  - Secret scanning aktivní (gitleaks)
```

### Blueprint Execution Engine

```yaml
component: Blueprint Execution Engine (AUT-070..079)
health: 55%
code_status: AKTIVNÍ (kód funkční, testy pass)
runtime_status: DEGRADED (všechny providers offline)
issues:
  - DockerProvider: offline (Docker daemon nedostupný v CI)
  - ProxmoxProvider: offline (žádná Proxmox instance)
  - KubernetesProvider: offline (žádný K8s cluster)
  - EventBus: in-process only, žádná persistence
strengths:
  - Asyncio wave scheduler funkční
  - TaskGraph (DAG) s depends_on validací
  - SKIPPED_DEPENDENCY_FAILED propagace
  - TimeoutStrategy.CANCEL per task
  - SSE/WS event stream funkční
  - AnthropicProvider aktivní (AI blueprint generation)
```

### QC Engine Stack

```yaml
component: QC Engine Stack (AUT-050..057)
health: 65%
scripts_functional: 8/8 (všechny fungují)
trigger_type: MANUÁLNÍ (žádná automatizace)
issues:
  - Žádný scheduled QC report
  - regression_sentinel.py update vyžaduje manuální rozhodnutí
  - DIGITAL_TWIN staleness (žádná auto-sync)
strengths:
  - startup_protocol.py: 12-krokový cold-start
  - regression_sentinel.py: 7 dimenzí drift detection
  - release_readiness.py: 12 gates
  - qc_engine.py: unified orchestrator
  - ledger.py: session lifecycle management
  - decision_engine.py: structured decision format
```

### Makefile Automation Hub

```yaml
component: Makefile Automation Hub (AUT-020..041)
health: 90%
targets_defined: 21
targets_functional: "Většina funkční (závisí na uv + tools)"
issues:
  - make ci: lokální ekvivalent CI, ale ne 1:1 s GitHub Actions
  - Žádný target pro spuštění QC Engine
strengths:
  - Komprehenzivní developer shortcuts
  - make ci: full local CI simulation
  - make security: pip-audit + bandit v jednom
  - make doctor: diagnose local environment
```

### Pre-commit Hook System

```yaml
component: Pre-commit Hook System (AUT-045..047)
health: 85%
hooks_configured: 3 (ruff lint+fix, ruff-format, pyright)
issues:
  - Vyžaduje lokální instalaci (pre-commit install)
  - Pyright může zpomalit commit cycle
  - Žádný hook pro secret scanning (gitleaks jen v CI)
strengths:
  - Automatická oprava lint issues (ruff --fix)
  - Blokuje commit při type errors (pyright)
  - Rychlá feedback loop pro vývojáře
```

### EventBus Runtime

```yaml
component: EventBus Runtime (AUT-075)
health: 40%
events_defined: 3 (task.started, task.completed, run.completed)
issues:
  - In-process only — žádná persistence
  - Žádný external monitoring integrace
  - Provider events (provider.connected/disconnected) nejsou emitovány
  - Žádný dead letter queue pro failed events
strengths:
  - asyncio pub/sub funkční
  - _STREAM_CTX ContextVar pro concurrent run isolation
  - SSE/WS stream support
  - run_logger plugin zachytává run.completed
```

---

## ZDRAVOTNÍ TRENDY

```yaml
trend_period: "Baseline session 2026-08-07 (první health assessment)"
previous_score: "N/A (první měření)"
current_score: 61%
trajectory: "STABILNÍ (žádný předchozí baseline)"

risk_trajectory:
  increasing_risks:
    - ORPHANED workflows jsou kumulované technicke dluhy
    - Providers zůstávají offline → DEGRADED runtime
    - DIGITAL_TWIN manuální sync → zvyšující se staleness
  stable_risks:
    - CI gate funkční, 100% coverage
    - Security scanning aktivní
  decreasing_risks:
    - "N/A (první měření)"
```

---

## KRITICKÉ ZDRAVOTNÍ PROBLÉMY

### KRITICKÉ (okamžitá akce)

```yaml
CRIT-001:
  issue: "starcore-integrity.yml BROKEN"
  impact: "CI noise, může maskovat reálné failures"
  fix: "Opravit nebo smazat workflow"
  effort: 30 min
  reference: "REC-002 v AUTOMATION_RECOMMENDATIONS.md"
```

### VYSOKÁ PRIORITA

```yaml
HIGH-001:
  issue: "7 workflows ORPHANED v platform/.github/"
  impact: "CodeQL, Dependabot, Docker publish, security-nightly neprobíhají"
  fix: "Přesunout klíčové workflows do root .github/workflows/"
  effort: 2-4 hodiny
  reference: "REC-003"

HIGH-002:
  issue: "Všechny infrastructure providers offline"
  impact: "Blueprint execution vždy DEGRADED, žádné reálné runs"
  fix: "DockerProvider v CI (mock nebo real Docker socket)"
  effort: 4-8 hodin
  reference: "REC-001"
```

### STŘEDNÍ PRIORITA

```yaml
MED-001:
  issue: "QC Engine čistě manuální — žádný scheduled QC"
  impact: "Governance drift může zůstat nedetekován mezi sezeními"
  fix: "Scheduled GitHub Actions: qc_engine.py run --quick"
  effort: 2 hodiny

MED-002:
  issue: "DIGITAL_TWIN manuální sync"
  impact: "Context pro AI sessions může být stale"
  fix: "Implementovat digital_twin_updater.py"
  effort: 4 hodiny

MED-003:
  issue: "Provider health monitoring chybí"
  impact: "Runtime DEGRADED stav není kontinuálně sledován"
  fix: "Scheduled health check + EventBus provider events"
  effort: 3 hodiny
```

---

## AUTOMATION HEALTH REPORT KARTA

```
╔══════════════════════════════════════════════════════════════╗
║         STARCORE AUTOMATION HEALTH REPORT                    ║
║                  2026-08-07                                  ║
╠══════════════════════════════════════════════════════════════╣
║  CELKOVÉ SKÓRE: 61% / 100%   [███████░░░░]                  ║
╠══════════════════════════════════════════════════════════════╣
║  CI/CD Coverage:      75%  [███████░░░]  DOBRÝ              ║
║  Security:            80%  [████████░░]  DOBRÝ              ║
║  Test Automation:     95%  [█████████░]  VÝBORNÝ            ║
║  Governance:          45%  [████░░░░░░]  SLABÝ              ║
║  Self-Maintenance:    20%  [██░░░░░░░░]  KRITICKÝ           ║
║  Observability:       50%  [█████░░░░░]  USPOKOJIVÝ         ║
╠══════════════════════════════════════════════════════════════╣
║  KRITICKÉ PROBLÉMY: 1  VYSOKÁ PRIORITA: 2  STŘEDNÍ: 3      ║
║  CELKEM AUTOMATIZACÍ: 51 (29 AKTIVNÍ, 7 ORPHANED, 1 BROKEN)║
╚══════════════════════════════════════════════════════════════╝
```

---

## DOPORUČENÁ AKCE

Viz AUTOMATION_RECOMMENDATIONS.md pro úplný seznam doporučení.

Pořadí akce:
1. CRIT-001: Fix starcore-integrity.yml (30 min)
2. HIGH-001: Přesunout klíčové workflows (2-4h)
3. HIGH-002: DockerProvider v CI (4-8h)
4. MED-001: Scheduled QC (2h)
5. MED-002: Digital Twin auto-sync (4h)
