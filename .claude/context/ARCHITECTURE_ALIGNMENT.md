# ARCHITECTURE ALIGNMENT

Standard: SPOS-016 §5 | Aktualizováno: 2026-08-08

Porovnání skutečného stavu repozitáře s governance dokumenty (SES, SAKB, SPOS, ADR).

---

## 1. ALIGNMENT S SES-000 (Engineering Constitution)

| Princip | Specifikace | Skutečný stav | Alignment |
|---|---|---|---|
| P001 Architecture First | Dokumentovat před implementací | ADR-001..017 existují | ✅ ALIGNED |
| P002 Documentation First | Vše dokumentováno | platform/docs/ (56 files), .claude/ (107 files) | ✅ ALIGNED |
| P003 Test First | 100% coverage | 796 testů, 100% coverage | ✅ ALIGNED |
| P004 Security First | CI security gates | bandit + pip-audit + gitleaks | ✅ ALIGNED |
| P005 Minimal Change | Atomické commity | Dodržováno | ✅ ALIGNED |
| P006 Evidence Based | Žádná fabrikace | Všechny health scores z auditů | ✅ ALIGNED |
| P007 No Secrets | Nikdy ukládat hesla/klíče | `STARCORE_*` env vars, .env gitignored | ✅ ALIGNED |
| P008 Digital Twin | Synchronní governance | DIGITAL_TWIN.md aktualizován | ✅ ALIGNED |
| P009 Reuse First | Netvořit duplikáty | ⚠️ 6 duplicitních root dirs (legacy) | ⚠️ PARTIAL |
| P010 Transparent Decisions | Decision log | Ledger + decisions dokumentovány | ✅ ALIGNED |

**Alignment score: 90%** (1 odchylka — legacy duplicity neodstraněna)

---

## 2. ALIGNMENT S SES-001 (Technical Standard)

| Oblast | Specifikace | Skutečný stav | Alignment |
|---|---|---|---|
| Repository structure | Monorepo s platform/ | platform/ je active, root je legacy chaos | ⚠️ PARTIAL |
| Module standard | `packages/` struktura | platform/packages/ dodržuje | ✅ ALIGNED |
| Naming conventions | snake_case, SCREAMING_CASE | Dodržováno v platform/ | ✅ ALIGNED |
| Dependency management | uv + pyproject.toml | platform/ OK, root requirements.txt redundantní | ⚠️ PARTIAL |
| API standard | FastAPI, OpenAPI | /docs endpoint, Pydantic models | ✅ ALIGNED |
| Testing standard | pytest, 100% coverage | 796 testů + 12 property-based | ✅ ALIGNED |
| CI/CD standard | GitHub Actions | Workflows existují, ale 7 ORPHANED v platform/.github/ | ⚠️ DEVIANCE |
| Documentation | MkDocs | mkdocs build --strict PASS | ✅ ALIGNED |

**Alignment score: 75%** (3 odchylky)

### DEVIANCE-SES001-001: Repository structure

```yaml
id: DEVIANCE-SES001-001
severity: HIGH
description: "Root repozitáře obsahuje 24 legacy/termux/dead adresářů vedle aktivního platform/. SES-001 předpokládá čistou monorepo strukturu."
recommendation: "Přesunout legacy do legacy/ subdirectory nebo archivovat do tagu."
```

### DEVIANCE-SES001-002: Duplicitní dependency management

```yaml
id: DEVIANCE-SES001-002
severity: LOW
description: "Root requirements.txt (packaging/setuptools/wheel) je redundantní vůči platform/pyproject.toml."
recommendation: "Odstranit root requirements.txt."
```

### DEVIANCE-SES001-003: Orphaned CI/CD workflows

```yaml
id: DEVIANCE-SES001-003
severity: HIGH
description: "7 workflows v platform/.github/ jsou ORPHANED — GitHub Actions čte pouze root .github/workflows/. 4 workflows (codeql, docker-publish, security-nightly, dependabot-auto-merge) chybí v root .github/."
recommendation: "Přesunout unique workflows do root .github/workflows/, smazat duplikáty."
```

---

## 3. ALIGNMENT S ADR (17 ADRs)

| ADR | Status | Alignment | Odchylka |
|---|---|---|---|
| ADR-001 Blueprint Dependency Execution | Accepted | ✅ Implementováno | — |
| ADR-002 Provider Lifecycle | Accepted | ✅ Implementováno | — |
| ADR-003 Rate Limiting | Accepted | ✅ Implementováno | — |
| ADR-004 Dependency Scanning | Accepted | ✅ CI gate aktivní | — |
| ADR-005 Unified Schema Mgmt | Accepted | ✅ Alembic funguje | — |
| ADR-006 Observability | Accepted | ✅ Prometheus + loguru | — |
| ADR-007 AI Provider Abstraction | Accepted | ✅ Implementováno | — |
| ADR-008 CI Security Gates | Accepted | ⚠️ gitleaks JEN v starcore-security.yml (root), ne v nightly | ⚠️ |
| ADR-009 Environment Detection | Accepted | ✅ Implementováno | — |
| ADR-010 Dependency Failure Semantics | Accepted | ✅ Implementováno | — |
| ADR-011 Plugin Trust Boundary | Accepted | ✅ Dokumentováno | — |
| ADR-012 API Authentication | Amended | ✅ JWT+RBAC přidáno | — |
| ADR-013 Provider Concurrency | Accepted | ✅ Žádný semaphore (per ADR) | — |
| ADR-014 Task Timeout | Accepted | ✅ Implementováno | — |
| ADR-015 Request Correlation | Accepted | ✅ Implementováno | — |
| ADR-016 Task Timeout Integration | Implemented | ✅ Implementováno | — |
| ADR-017 Plugin Operator Controls | Accepted | ✅ Implementováno | — |

**Alignment score: 94%** (1 minor odchylka — gitleaks distribution across workflows)

### DEVIANCE-ADR-001: Security nightly incomplete coverage

```yaml
id: DEVIANCE-ADR-001
severity: MEDIUM
description: "ADR-008 definuje CI gates: bandit, gitleaks, nightly audit. security-nightly.yml je v platform/.github/ (ORPHANED), ne v root .github/. Root starcore-security.yml má jen gitleaks, ne celý nightly suite."
recommendation: "Přesunout security-nightly.yml do root .github/workflows/."
```

---

## 4. ALIGNMENT S SPOS

| SPOS Modul | Status | Alignment | Odchylka |
|---|---|---|---|
| SPOS-001 Memory | ✅ | ✅ project_state.json, current_state.md, project_snapshot.md živé | — |
| SPOS-002 Sessions | ✅ | ✅ ledger.yaml aktivní | — |
| SPOS-003 Prompts | ✅ | ✅ registry.yaml PROM-001..011 | — |
| SPOS-004 Intelligence | ✅ | ✅ QC engines fungují | — |
| SPOS-005 Audit | ✅ | ✅ CI toolchain živý | — |
| SPOS-006 Documentation | ✅ | ✅ mkdocs --strict PASS | — |
| SPOS-007 Infrastructure | ✅ | ⚠️ `starcore diagnose` vyžaduje offline providers | Minor |
| SPOS-008 Deployment | ✅ | ⚠️ 65 install skriptů = Termux, ne produkce | Acknowledged |
| SPOS-009 Security | ✅ | ✅ CI gates živé | — |
| SPOS-010/011 AI Orchestration | ✅ | ⚠️ AAOS Level 2/5 | Acknowledged |
| SPOS-012 Integration | ✅ | ✅ Health 64% | — |
| SPOS-013 Automation | ✅ | ✅ Health 61% | — |
| SPOS-014 AAOS | ✅ | ✅ Dokumentováno, health 38% | — |
| SPOS-015 Ecosystem Hygiene | ✅ | ✅ Health 58%, všechny findings dokumentovány | — |

**SPOS Alignment score: 86%** (2 acknowledged limitations, 1 minor)

---

## 5. WORKFLOW ALIGNMENT

### GitHub Actions — skutečný stav

| Workflow | Lokace | GitHub vidí? | Status |
|---|---|---|---|
| ci.yml | ROOT ✅ | ✅ ANO | ACTIVE |
| release.yml | ROOT ✅ | ✅ ANO | ACTIVE |
| manual-tag.yml | ROOT ✅ | ✅ ANO | ACTIVE |
| starcore-security.yml | ROOT ✅ | ✅ ANO | ACTIVE |
| starcore-integrity.yml | ROOT ✅ | ✅ ANO | BROKEN (refs `core/`) |
| starcore-release.yml | ROOT ✅ | ✅ ANO | LEGACY (just git status) |
| ci.yml | platform/ ❌ | ❌ NE | ORPHANED |
| release.yml | platform/ ❌ | ❌ NE | ORPHANED |
| manual-tag.yml | platform/ ❌ | ❌ NE | ORPHANED |
| codeql.yml | platform/ ❌ | ❌ NE | ORPHANED — needs root |
| docker-publish.yml | platform/ ❌ | ❌ NE | ORPHANED — needs root |
| security-nightly.yml | platform/ ❌ | ❌ NE | ORPHANED — needs root |
| dependabot-auto-merge.yml | platform/ ❌ | ❌ NE | ORPHANED — needs root |

**Workflow alignment: 50%** — 7 workflows ORPHANED, 1 BROKEN, 1 LEGACY

---

## 6. SOUHRNNÉ METRIKY

```yaml
ses_000_alignment: "90%"
ses_001_alignment: "75%"
adr_alignment: "94%"
spos_alignment: "86%"
workflow_alignment: "50%"

overall_architecture_alignment: "79%"

total_deviances: 7
  critical: 1 (DEVIANCE-SES001-001 — repository structure)
  high: 2 (DEVIANCE-SES001-003, DEVIANCE-ADR-001 — orphaned workflows)
  medium: 1 (DUP-001 code duplication)
  low: 3 (requirements.txt, psutil dep, legacy docs)
```
