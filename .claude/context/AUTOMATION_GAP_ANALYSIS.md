# AUTOMATION GAP ANALYSIS

Standard: SPOS-013 §10 | Aktualizováno: 2026-08-07

Analýza mezer v automatizační infrastruktuře STARCORE. Identifikuje chybějící automatizace, redundance a příležitosti ke zlepšení.

---

## METODOLOGIE

Gap analýza porovnává:
1. **Skutečný stav** — co existuje (z AUTOMATION_REGISTRY.md)
2. **Požadovaný stav** — co by mělo existovat pro Level 4/5 automation maturity
3. **Gap** — rozdíl mezi skutečným a požadovaným stavem

Klasifikace gaps:
- `MISSING` — chybí úplně
- `ORPHANED` — existuje ale nefunguje
- `DEGRADED` — funguje ale ne plně
- `MANUAL` — existuje ale vyžaduje manuální trigger

---

## SUMMARY GAPS

```yaml
total_gaps_identified: 18
critical_gaps: 3
high_gaps: 6
medium_gaps: 6
low_gaps: 3
automation_maturity_current: "Level 3.5 / 5"
automation_maturity_target: "Level 4 / 5"
```

---

## KRITICKÉ GAPY (GAP-001..003)

### GAP-001 — Broken CI Workflow

```yaml
id: GAP-001
severity: CRITICAL
category: CI/CD
gap_type: BROKEN
title: "starcore-integrity.yml vždy selhává"
actual_state: |
  starcore-integrity.yml (AUT-003) je nakonfigurován jako CI gate
  (push/PR → main), ale referuje neexistující root core/ adresář.
  Způsobuje CI noise a může maskovat reálné failures.
required_state: "Workflow referuje existující paths NEBO je smazán/opraven"
impact: "MEDIUM — CI noise; merge není blokován (ostatní jobs pass)"
fix: |
  Option A: Smazat starcore-integrity.yml
  Option B: Aktualizovat paths na existující strukturu (platform/packages/)
effort: 30 minut
reference: AUT-003, TRIG-011, TRIG-021
```

### GAP-002 — Infrastructure Providers Offline

```yaml
id: GAP-002
severity: CRITICAL
category: RUNTIME
gap_type: DEGRADED
title: "Všechny 3 infrastructure providers jsou offline"
actual_state: |
  DockerProvider, ProxmoxProvider, KubernetesProvider — všechny OFFLINE.
  Blueprint execution vždy DEGRADED. Žádné reálné infrastructure automation runs.
  AnthropicProvider (AI) je JEDINÝ funkční provider.
required_state: |
  Alespoň 1 provider online pro end-to-end blueprint test.
  DockerProvider je nejsnáze zprovoznitelný (Docker daemon v CI).
impact: |
  HIGH — core value proposition (infrastructure automation) nedemonstrována.
  Všechny /blueprints/run výsledky jsou mock/degraded.
fix: |
  Krátkodobě: DockerProvider mock v CI (fake Docker socket)
  Střednědobě: Real Docker daemon v CI (DinD — Docker in Docker)
  Dlouhodobě: Proxmox/K8s test environment
effort: 4-8 hodin (krátkodobý fix)
reference: REC-001, AUT-070..073
```

### GAP-003 — Zero Self-Maintenance Automation

```yaml
id: GAP-003
severity: CRITICAL
category: SELF_MAINTENANCE
gap_type: MISSING
title: "Žádná automatická self-maintenance — vše MANUÁLNÍ"
actual_state: |
  QC Engine (AUT-057), regression_sentinel.py (AUT-055),
  DIGITAL_TWIN sync — vše MANUÁLNÍ, vyžaduje AI session.
  Governance drift může zůstat nedetekován týdny.
required_state: |
  Scheduled QC report (alespoň denně nebo per-merge).
  Automatická detekce drift bez AI session.
impact: |
  MEDIUM — governance quality degraduje postupně bez detekce.
  DIGITAL_TWIN stale → horší AI session context.
fix: |
  Scheduled GitHub Actions: qc_engine.py run --quick (weekly)
  digital_twin_updater.py (po merge do main)
effort: 4-6 hodin
reference: WF-P01, WF-P02, SME-005
```

---

## VYSOKÁ PRIORITA GAPY (GAP-004..009)

### GAP-004 — Orphaned Workflows nejsou aktivní

```yaml
id: GAP-004
severity: HIGH
category: CI/CD
gap_type: ORPHANED
title: "7 workflows v platform/.github/ nikdy nespuštěno"
actual_state: |
  7 workflow YAMLs v platform/.github/workflows/:
  - ci.yml (nejúplnější CI implementace)
  - codeql.yml (CodeQL security scan)
  - dependabot-auto-merge.yml (auto-merge patch updates)
  - docker-publish.yml (GHCR publish + SBOM + cosign)
  - security-nightly.yml (02:00 UTC security scan)
  - release.yml + manual-tag.yml (release pipeline)
required_state: "Klíčové workflows přesunuty do root .github/workflows/"
impact: |
  HIGH — CodeQL scan, Dependabot auto-merge, Docker publish neexistují.
  security-nightly na 02:00 UTC nefunguje (záloha k 05:00 UTC).
fix: "Přesunout platform/.github/ → root .github/ (merge + deduplicate)"
effort: 2-4 hodiny
reference: AUT-010..016, REC-003
```

### GAP-005 — Knowledge Validation Chybí

```yaml
id: GAP-005
severity: HIGH
category: GOVERNANCE
gap_type: MISSING
title: "Žádná automatická validace knowledge/ profilů"
actual_state: |
  knowledge/ adresář obsahuje SAKB-000 formátované profily.
  Žádná automatická validace při commitu ani v CI.
  Formátové chyby detekované až při manuálním review.
required_state: |
  sakb_validator.py (navrhovaný) spouštěný v CI nebo pre-commit.
  Automatická validace SAKB-000 formátu při každém knowledge/ commitu.
impact: "MEDIUM — knowledge quality degraduje bez validace"
fix: |
  Implementovat sakb_validator.py.
  Přidat do CI quality job nebo pre-commit hook.
effort: 3-4 hodiny
reference: WF-P02, TRIG-P02, REC-007
```

### GAP-006 — Digital Twin Auto-sync Chybí

```yaml
id: GAP-006
severity: HIGH
category: GOVERNANCE
gap_type: MISSING
title: "DIGITAL_TWIN.md nemá automatickou synchronizaci"
actual_state: |
  DIGITAL_TWIN.md aktualizována manuálně v AI sezeních.
  Timestamp aktualizace závisí na frekvenci SPOS sessions.
  Může být N dní/týdnů stale.
required_state: |
  digital_twin_updater.py spouštěný po každém merge do main.
  DIGITAL_TWIN.md max 24h stale.
impact: "MEDIUM — AI sessions začínají se stale governance context"
fix: "Implementovat digital_twin_updater.py + GitHub Actions trigger"
effort: 4-6 hodin
reference: WF-P01, TRIG-P01, SME-005
```

### GAP-007 — Scheduled Security Scans Neúplné

```yaml
id: GAP-007
severity: HIGH
category: SECURITY
gap_type: DEGRADED
title: "Chybí CodeQL scan a security-nightly na 02:00 UTC"
actual_state: |
  Aktivní: starcore-security.yml (05:00 UTC, gitleaks + file audit)
  ORPHANED: codeql.yml (CodeQL static analysis — NIKDY nespuštěno)
  ORPHANED: security-nightly.yml (02:00 UTC backup — NIKDY nespuštěno)
required_state: |
  CodeQL scan aktivní (nejlepší static security analysis pro Python).
  Dual-schedule security (nebo merge do jednoho robustního workflow).
impact: "HIGH — CodeQL findings nikdy nedetekována"
fix: "Přesunout codeql.yml do root .github/workflows/"
effort: 1 hodina
reference: AUT-011, AUT-014, REC-006
```

### GAP-008 — Docker Publish Pipeline Neaktivní

```yaml
id: GAP-008
severity: HIGH
category: DEPLOY
gap_type: ORPHANED
title: "docker-publish.yml (SBOM, cosign) nikdy nespuštěno"
actual_state: |
  platform/.github/workflows/docker-publish.yml existuje ale ORPHANED.
  Obsahuje: GHCR push, SBOM attestation, cosign keyless signing.
  Žádný Docker image publikován na GitHub Container Registry.
required_state: |
  Docker publish pipeline aktivní při release tagech.
  GHCR: ghcr.io/fatalerorr69/starcore-platform:latest
impact: "MEDIUM — release artifacts nekompletní (žádný Docker image)"
fix: "Přesunout docker-publish.yml do root .github/workflows/"
effort: 1-2 hodiny
reference: AUT-013, REC-008
```

### GAP-009 — EventBus Persistence Chybí

```yaml
id: GAP-009
severity: HIGH
category: RUNTIME
gap_type: MISSING
title: "EventBus nemá persistenci — events lost na restart"
actual_state: |
  EventBus (AUT-075) je pure in-process asyncio pub/sub.
  Po restartu FastAPI aplikace jsou všechny emitované events ztraceny.
  run_logger plugin zachytává run.completed do log souboru, ale ostatní events nikoliv.
required_state: |
  Event persistence (SQLite log nebo Redis Streams nebo NATS).
  Event replay pro audit a debugging.
impact: "MEDIUM — audit trail neúplný; events pro monitoring nedostupné"
fix: |
  Option A: SQLite event log (jednoduché, bez dalších deps)
  Option B: Redis Streams (škálovatelné)
  Option C: NATS (enterprise grade, NATS.py dep)
effort: 4-8 hodin (SQLite option)
reference: AUT-075, AE-COMP-006, REC-009
```

---

## STŘEDNÍ PRIORITA GAPY (GAP-010..015)

### GAP-010 — Provider Health Monitoring

```yaml
id: GAP-010
severity: MEDIUM
category: MONITORING
gap_type: MISSING
title: "Žádný kontinuální monitoring stavu providers"
actual_state: "GET /providers/{name}/health jen na manuální požádání"
fix: "Scheduled health check (každých 5 min) + EventBus provider events"
effort: 3 hodiny
reference: WF-P03, SME-006
```

### GAP-011 — Dependabot Auto-merge Neaktivní

```yaml
id: GAP-011
severity: MEDIUM
category: MAINTENANCE
gap_type: ORPHANED
title: "dependabot-auto-merge.yml ORPHANED — patch updates manuálně"
actual_state: "dependabot-auto-merge.yml v platform/.github/ (ORPHANED)"
fix: "Přesunout do root .github/workflows/"
effort: 30 minut
reference: AUT-012
```

### GAP-012 — Registry Cross-check Chybí

```yaml
id: GAP-012
severity: MEDIUM
category: GOVERNANCE
gap_type: MISSING
title: "Žádná automatická cross-check konzistence mezi registry soubory"
actual_state: |
  SPOS_REGISTRY, DOCUMENTATION_REGISTRY, SES-INDEX — manuálně udržovány.
  Duplicity a nekonzistence detekované jen manuálně.
fix: "registry_validator.py: cross-check IDs, timestamps, status consistency"
effort: 4 hodiny
reference: TRIG-P03
```

### GAP-013 — Weekly Health Report Chybí

```yaml
id: GAP-013
severity: MEDIUM
category: GOVERNANCE
gap_type: MISSING
title: "Žádný automatický týdenní health report"
actual_state: "Health report pouze po manuálním spuštění QC Engine"
fix: "Scheduled GitHub Actions (weekly): qc_engine.py run + decision_engine format"
effort: 2 hodiny
reference: TRIG-P04
```

### GAP-014 — Release Auto-bump Chybí

```yaml
id: GAP-014
severity: MEDIUM
category: DEPLOY
gap_type: MISSING
title: "Release tag nevyvolá auto-update CHANGELOG + project_snapshot"
actual_state: "release.py bump musí být spuštěno manuálně před tagem"
fix: "Přidat do release.yml: auto-update project_snapshot.md po release"
effort: 2 hodiny
reference: TRIG-P06
```

### GAP-015 — Vulnerability Registry Auto-update

```yaml
id: GAP-015
severity: MEDIUM
category: SECURITY
gap_type: MISSING
title: "bandit a pip-audit findings nejsou auto-zapisovány do VULNERABILITY_REGISTRY"
actual_state: "CI failuje ale findings nejsou persistovány do registry"
fix: "Post-CI step: parsovat bandit/pip-audit output → update VULNERABILITY_REGISTRY"
effort: 3 hodiny
reference: AUTOMATION_PIPELINES.md Pipeline 3
```

---

## NÍZKÁ PRIORITA GAPY (GAP-016..018)

### GAP-016 — Termux Stubs Cleanup

```yaml
id: GAP-016
severity: LOW
category: MAINTENANCE
gap_type: LEGACY
title: "~70 Termux install stubs v root — never executed"
actual_state: "65+ install_*.sh s Android shebang — mrtvý kód"
fix: "Přesunout do legacy/ nebo smazat (po potvrzení že jsou nepoužívané)"
effort: 1 hodina
```

### GAP-017 — pre-commit Secret Scanning

```yaml
id: GAP-017
severity: LOW
category: SECURITY
gap_type: MISSING
title: "gitleaks není v pre-commit hooks — jen v CI"
actual_state: "gitleaks pouze v CI quality job a nightly schedule"
fix: "Přidat gitleaks do .pre-commit-config.yaml"
effort: 30 minut
```

### GAP-018 — Makefile QC Targets

```yaml
id: GAP-018
severity: LOW
category: MAINTENANCE
gap_type: MISSING
title: "Makefile nemá targets pro QC Engine scripts"
actual_state: "make ci existuje, ale žádný make qc, make sentinel, make readiness"
fix: "Přidat targets: make qc, make sentinel, make readiness"
effort: 30 minut
```

---

## GAP COVERAGE MATRIX

```
                    MISSING  ORPHANED  DEGRADED  MANUAL
CI/CD              |   0   |    7     |    0    |   0   |
Security           |   2   |    2     |    1    |   0   |
Runtime            |   2   |    0     |    1    |   0   |
Governance         |   3   |    0     |    0    |   8   |
Self-Maintenance   |   3   |    0     |    0    |   5   |
Monitoring         |   2   |    0     |    0    |   1   |
Deploy             |   2   |    1     |    0    |   0   |
Maintenance        |   1   |    1     |    0    |   0   |
-----------------------------------------------------------
TOTAL             |  15   |   11     |    2    |  14   |
```

---

## DOPORUČENÉ POŘADÍ ŘEŠENÍ

```yaml
sprint_1_immediate:  # ≤ 2 hodiny
  - GAP-001: Fix/delete starcore-integrity.yml
  - GAP-011: Přesunout dependabot-auto-merge.yml
  - GAP-017: Přidat gitleaks do pre-commit
  - GAP-018: Přidat make qc targets

sprint_2_short_term:  # 1-2 dny
  - GAP-004: Přesunout klíčové workflows z platform/.github/
  - GAP-007: Aktivovat CodeQL scan
  - GAP-008: Aktivovat docker-publish pipeline
  - GAP-013: Scheduled weekly QC report

sprint_3_medium_term:  # 1 týden
  - GAP-002: DockerProvider v CI
  - GAP-006: digital_twin_updater.py
  - GAP-005: sakb_validator.py
  - GAP-003: Scheduled self-maintenance

sprint_4_long_term:  # 2-4 týdny
  - GAP-009: EventBus persistence
  - GAP-010: Provider health monitoring
  - GAP-012: Registry cross-check
  - GAP-015: Vulnerability registry auto-update
```
