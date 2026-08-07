# AUTOMATION RECOMMENDATIONS

Standard: SPOS-013 §11 | Aktualizováno: 2026-08-07

Konkrétní doporučení pro zlepšení automatizační infrastruktury STARCORE. Navazuje na AUTOMATION_GAP_ANALYSIS.md.

---

## LEGENDA

```yaml
priority: [CRITICAL, HIGH, MEDIUM, LOW]
effort: [XS (<1h), S (1-2h), M (2-4h), L (4-8h), XL (>8h)]
impact: [CRITICAL, HIGH, MEDIUM, LOW]
status: [NAVRHOVÁNO, V PŘÍPRAVĚ, IMPLEMENTOVÁNO]
```

---

## KRITICKÉ DOPORUČENÍ

### REC-A01 — Fix nebo smazat starcore-integrity.yml

```yaml
id: REC-A01
priority: CRITICAL
effort: XS
impact: MEDIUM
gap_reference: GAP-001
title: "Opravit nebo smazat broken CI workflow"
problem: |
  .github/workflows/starcore-integrity.yml je nakonfigurován jako CI gate
  pro push/PR → main, ale referuje neexistující root core/ adresář.
  Způsobuje CI noise a snižuje důvěryhodnost CI systému.
recommendation: |
  Option A (doporučeno): Smazat starcore-integrity.yml
    - Pokud žádné unikátní checks neobsahuje (vs ci.yml)
    - Okamžitá akce, čistá CI pipeline
  Option B: Aktualizovat paths
    - Nahradit core/ → platform/packages/core/
    - Přidat smysluplné integrity checks
action_steps:
  1. Ověřit obsah starcore-integrity.yml
  2. Porovnat s ci.yml — jaké unique checks obsahuje
  3. Option A: git rm .github/workflows/starcore-integrity.yml
     Option B: Aktualizovat yaml paths + přidat do ci.yml
  4. Commit + push + ověřit že CI green
status: NAVRHOVÁNO
reference: AUT-003, TRIG-011, TRIG-021
```

### REC-A02 — DockerProvider v CI testování

```yaml
id: REC-A02
priority: CRITICAL
effort: L
impact: CRITICAL
gap_reference: GAP-002
title: "Zprovoznit DockerProvider pro end-to-end blueprint testing"
problem: |
  DockerProvider, ProxmoxProvider, KubernetesProvider jsou offline.
  Blueprint execution engine je DEGRADED — žádné reálné runs.
  Core value proposition (infrastructure automation) nelze demonstrovat.
recommendation: |
  Fáze 1 (krátkodobá): Mock DockerProvider
    - Implementovat DockerProviderMock ve tests/
    - Pytest fixtures pro provider simulation
    - E2E test: NL → Blueprint → TaskGraph → Mock execution → SQLite
  Fáze 2 (střednědobá): Real Docker v CI
    - GitHub Actions: Docker in Docker (DinD) service
    - Real docker build/run v blueprint execution tests
action_steps:
  1. Implementovat tests/providers/test_docker_mock.py
  2. DockerProviderMock: BaseProvider subclass s fake execute()
  3. E2E test: celý blueprint pipeline s mock providers
  4. Volitelně: DinD v ci.yml pro real Docker testing
status: NAVRHOVÁNO
reference: AUT-070..073, AUTOMATION_HEALTH.md HIGH-002
```

### REC-A03 — Scheduled QC Automation

```yaml
id: REC-A03
priority: CRITICAL
effort: M
impact: HIGH
gap_reference: GAP-003
title: "Automatizovat QC governance bez AI session dependency"
problem: |
  Celý QC Engine (regression_sentinel, release_readiness, qc_engine)
  je MANUÁLNÍ — vyžaduje manuální spuštění nebo AI session.
  Governance drift může zůstat nedetekován týdny.
recommendation: |
  Přidat scheduled GitHub Actions workflow:
  name: weekly-qc.yml
  trigger: schedule (0 9 * * 1) — pondělí 09:00 UTC
  steps:
    - qc_engine.py run --quick
    - decision_engine.py format
    - Uložit report jako GitHub Actions artifact
    - [future] Push report do .claude/reports/
action_steps:
  1. Vytvořit .github/workflows/weekly-qc.yml
  2. Nakonfigurovat uv + python 3.12
  3. Spustit qc_engine.py run --quick
  4. Upload artifact: weekly-qc-report.txt
  5. [optional] GitHub issue při FAIL verdict
status: NAVRHOVÁNO
reference: AUT-057, AE-COMP-002, GAP-003
```

---

## VYSOKÁ PRIORITA DOPORUČENÍ

### REC-A04 — Přesunout klíčové workflows z platform/.github/

```yaml
id: REC-A04
priority: HIGH
effort: M
impact: HIGH
gap_reference: GAP-004
title: "Aktivovat orphaned workflows přesunem do root .github/"
problem: |
  7 workflows v platform/.github/workflows/ nikdy nespouštěno.
  Obsahují nejúplnější implementace CI/CD:
  - codeql.yml: CodeQL static analysis (nikdy nespuštěno)
  - dependabot-auto-merge.yml: auto-merge patch updates
  - docker-publish.yml: GHCR publish + SBOM + cosign
  - security-nightly.yml: backup security scan 02:00 UTC
recommendation: |
  Prioritizované pořadí přesunu (deduplicate s root):
  1. codeql.yml → .github/workflows/codeql.yml
     Merge s existujícím ci.yml trigger config
  2. dependabot-auto-merge.yml → .github/workflows/dependabot-auto-merge.yml
  3. docker-publish.yml → .github/workflows/docker-publish.yml
     Update: ghcr.io/fatalerorr69/starcore-platform
  4. security-nightly.yml → merge do starcore-security.yml
  Smazat nebo archivovat platform/.github/ po migraci
action_steps:
  1. Review každý workflow v platform/.github/
  2. Porovnat s root .github/ equivalentem
  3. Merge/přesunout (update paths: platform/ prefix kde potřeba)
  4. Test na feature branch
  5. Smazat platform/.github/ po ověření
status: NAVRHOVÁNO
reference: AUT-010..016, GAP-004
```

### REC-A05 — Digital Twin Auto-updater

```yaml
id: REC-A05
priority: HIGH
effort: L
impact: HIGH
gap_reference: GAP-006
title: "Implementovat digital_twin_updater.py pro automatický sync"
problem: |
  DIGITAL_TWIN.md je klíčový governance dokument.
  Aktualizován manuálně → může být N dní stale.
  AI sessions začínají se stale context → horší governance rozhodnutí.
recommendation: |
  Implementovat platform/.starcore/scripts/digital_twin_updater.py:
  - Input: project_state.json + ledger.yaml + registry/*.md
  - Output: diff DIGITAL_TWIN.md sekcí
  - Trigger: GitHub Actions po merge do main
  Workflow: .github/workflows/digital-twin-sync.yml
    trigger: push → main (paths: .claude/**)
    steps:
      - uv run digital_twin_updater.py
      - git commit DIGITAL_TWIN.md "chore: auto-sync digital twin"
      - git push
action_steps:
  1. Implementovat digital_twin_updater.py
  2. Přidat do Makefile: make update-twin
  3. Vytvořit .github/workflows/digital-twin-sync.yml
  4. Test na feature branch
status: NAVRHOVÁNO
reference: WF-P01, SME-005, GAP-006
```

### REC-A06 — Aktivovat CodeQL Security Scan

```yaml
id: REC-A06
priority: HIGH
effort: S
impact: HIGH
gap_reference: GAP-007
title: "Přesunout codeql.yml do root .github/ pro aktivní CodeQL scanning"
problem: |
  CodeQL je nejlepší static security analysis pro Python/GitHub.
  codeql.yml existuje v platform/.github/ ale je ORPHANED.
  CodeQL findings nikdy nedetekována.
recommendation: |
  Přesunout/přizpůsobit codeql.yml do .github/workflows/codeql.yml:
  - Trigger: push/PR → main, schedule (neděle 13:40 UTC)
  - Language: python
  - Paths: platform/packages/**/*.py
  Výsledky viditelné v GitHub Security tab.
action_steps:
  1. cp platform/.github/workflows/codeql.yml .github/workflows/codeql.yml
  2. Aktualizovat paths na platform/ prefix
  3. Test na feature branch
  4. Ověřit GitHub Security tab po merge
status: NAVRHOVÁNO
reference: AUT-011, GAP-007
```

### REC-A07 — Knowledge Validator

```yaml
id: REC-A07
priority: HIGH
effort: M
impact: MEDIUM
gap_reference: GAP-005
title: "Implementovat sakb_validator.py pro automatickou validaci knowledge profilů"
problem: |
  knowledge/ profily (SAKB-000 formát) nejsou automaticky validovány.
  Formátové chyby detekované jen manuálně.
recommendation: |
  Implementovat platform/.starcore/scripts/sakb_validator.py:
  - Validuje SAKB-000 required fields (name, version, capabilities, ...)
  - Spuštěn v CI při change knowledge/**/*.md
  - Nebo jako pre-commit hook pro .md soubory
action_steps:
  1. Implementovat sakb_validator.py
  2. Přidat do CI quality job: "if knowledge/ changed"
  3. Nebo pre-commit: types_or: [markdown] paths: knowledge/
status: NAVRHOVÁNO
reference: WF-P02, GAP-005
```

### REC-A08 — Docker Publish Pipeline

```yaml
id: REC-A08
priority: HIGH
effort: S
impact: HIGH
gap_reference: GAP-008
title: "Aktivovat docker-publish.yml pro GHCR release publishing"
problem: |
  docker-publish.yml (SBOM attestation, cosign keyless signing) ORPHANED.
  Release artifacts neobsahují Docker image.
  GHCR: ghcr.io/fatalerorr69/starcore-platform nikdy publikován.
recommendation: |
  Přesunout do .github/workflows/docker-publish.yml:
  - Trigger: push tags v*.*.*
  - Update GHCR registry path
  - Ověřit cosign setup (GitHub OIDC)
action_steps:
  1. cp platform/.github/workflows/docker-publish.yml .github/workflows/
  2. Update: ghcr.io/fatalerorr69/starcore-platform
  3. Ověřit GITHUB_TOKEN permissions (packages: write)
  4. Test na test tag
status: NAVRHOVÁNO
reference: AUT-013, GAP-008
```

### REC-A09 — EventBus Persistence

```yaml
id: REC-A09
priority: HIGH
effort: L
impact: MEDIUM
gap_reference: GAP-009
title: "Přidat event persistence do EventBus"
problem: |
  EventBus je pure in-process — events lost na restart.
  Audit trail neúplný. Debugging obtížný.
recommendation: |
  SQLite event log (nejjednodušší, bez nových deps):
  - EventBus.emit() → additionally INSERT INTO events (event, data, ts)
  - Použít existující SQLite (platform/data/starcore.db)
  - GET /events endpoint pro audit log
action_steps:
  1. Přidat events tabulku do Alembic migration
  2. EventBus._persist(event, data) → SQLite insert
  3. GET /events?type=&limit= endpoint
  4. Tests pro event persistence
status: NAVRHOVÁNO
reference: AUT-075, GAP-009
```

---

## STŘEDNÍ PRIORITA DOPORUČENÍ

### REC-A10 — Provider Health Monitor

```yaml
id: REC-A10
priority: MEDIUM
effort: M
impact: MEDIUM
gap_reference: GAP-010
title: "Implementovat kontinuální provider health monitoring"
recommendation: |
  FastAPI background task (asyncio.create_task):
  - každých 5 minut: GET /providers/{name}/health
  - EventBus.emit("provider.connected") / ("provider.disconnected")
  - Update providers status v SQLite
  - GET /providers/health/summary endpoint
status: NAVRHOVÁNO
reference: WF-P03, SME-006
```

### REC-A11 — Dependabot Auto-merge Activation

```yaml
id: REC-A11
priority: MEDIUM
effort: XS
impact: MEDIUM
gap_reference: GAP-011
title: "Aktivovat dependabot-auto-merge pro patch/minor updates"
recommendation: |
  Přesunout platform/.github/workflows/dependabot-auto-merge.yml
  do .github/workflows/dependabot-auto-merge.yml
  Podmínka: update-type IN [version-update:semver-patch, version-update:semver-minor]
status: NAVRHOVÁNO
reference: AUT-012, GAP-011
```

### REC-A12 — Scheduled Weekly Health Report

```yaml
id: REC-A12
priority: MEDIUM
effort: S
impact: MEDIUM
gap_reference: GAP-013
title: "Automatický týdenní QC + health report"
recommendation: |
  .github/workflows/weekly-qc.yml (trigger: pondělí 09:00 UTC):
  - qc_engine.py run --quick
  - regression_sentinel.py check
  - release_readiness.py evaluate --quick
  - Upload jako GitHub Actions artifact
  - [optional] Otevřít GitHub Issue pokud FAIL
status: NAVRHOVÁNO
reference: GAP-013, TRIG-P04
```

### REC-A13 — Registry Cross-validator

```yaml
id: REC-A13
priority: MEDIUM
effort: M
impact: MEDIUM
gap_reference: GAP-012
title: "Implementovat cross-check validátor registry konzistence"
recommendation: |
  registry_validator.py:
  - Porovnává IDs v SPOS_REGISTRY vs DOCUMENTATION_REGISTRY vs SES-INDEX
  - Detekuje duplicitní IDs, chybějící cross-references
  - Validuje timestamp konzistenci (updated_at)
  - Spouštěn v CI nebo jako pre-commit
status: NAVRHOVÁNO
reference: GAP-012, TRIG-P03
```

---

## NÍZKÁ PRIORITA DOPORUČENÍ

### REC-A14 — Makefile QC Targets

```yaml
id: REC-A14
priority: LOW
effort: XS
impact: LOW
gap_reference: GAP-018
title: "Přidat Makefile targets pro QC Engine"
recommendation: |
  Přidat do platform/Makefile:
  make qc:         qc_engine.py run --quick
  make sentinel:   regression_sentinel.py check
  make readiness:  release_readiness.py evaluate --quick
  make twin:       digital_twin_updater.py (po implementaci)
status: NAVRHOVÁNO
```

### REC-A15 — Pre-commit Secret Scanning

```yaml
id: REC-A15
priority: LOW
effort: XS
impact: MEDIUM
gap_reference: GAP-017
title: "Přidat gitleaks do pre-commit hooks"
recommendation: |
  .pre-commit-config.yaml:
    - repo: https://github.com/gitleaks/gitleaks
      rev: v8.x.x
      hooks:
        - id: gitleaks
  Detekuje secrets PŘED commitem, ne až v CI.
status: NAVRHOVÁNO
```

### REC-A16 — Termux Stubs Archivace

```yaml
id: REC-A16
priority: LOW
effort: S
impact: LOW
gap_reference: GAP-016
title: "Archivovat nebo smazat ~70 Termux install stubs"
recommendation: |
  Ověřit, že install_*.sh soubory nejsou aktivně používány.
  Přesunout do legacy/termux/ nebo smazat.
  Výsledek: čistší repo structure, snazší navigace.
status: NAVRHOVÁNO
```

---

## IMPLEMENTAČNÍ ROADMAP

```yaml
mesic_1:
  sprint_A: [REC-A01, REC-A11, REC-A15, REC-A14]  # < 3h total
  sprint_B: [REC-A04, REC-A06, REC-A08]            # workflow migrations

mesic_2:
  sprint_C: [REC-A03, REC-A05, REC-A12]            # scheduled automation
  sprint_D: [REC-A02, REC-A07]                     # providers + validators

mesic_3:
  sprint_E: [REC-A09, REC-A10, REC-A13]            # runtime improvements
  sprint_F: [REC-A16]                              # cleanup

automation_maturity_po_implementaci: "Level 4.5 / 5"
estimated_health_score_improvement: "61% → 85%+"
```

---

## STATISTIKY DOPORUČENÍ

```yaml
total_recommendations: 16
critical: 3  (REC-A01..A03)
high: 6      (REC-A04..A09)
medium: 4    (REC-A10..A13)
low: 3       (REC-A14..A16)

effort_distribution:
  XS: 4  (< 1 hodina)
  S:  4  (1-2 hodiny)
  M:  5  (2-4 hodiny)
  L:  3  (4-8 hodin)
  XL: 0

total_estimated_effort: "40-60 hodin (1.5-2 týdny full-time)"
quick_wins: [REC-A01, REC-A11, REC-A15, REC-A14, REC-A06]
```
