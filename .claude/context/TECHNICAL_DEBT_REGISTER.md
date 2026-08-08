# TECHNICAL DEBT REGISTER

Standard: SPOS-016 §6 | Aktualizováno: 2026-08-08

Centrální registr veškerého technického dluhu identifikovaného v STARCORE repozitáři.

---

## PRIORITIZACE

```yaml
CRITICAL: Blokuje CI/CD, způsobuje false-positive/negative, ohrožuje integritu
HIGH:     Matoucí pro nové vývojáře, zdvojuje údržbu, degraduje metriky
MEDIUM:   Stylistické problémy, neoptimální patterns, potenciální budoucí problémy
LOW:      Kosmetické, dokumentační, nice-to-have
```

---

## CRITICAL DEBT

### TD-001 — 7 Orphaned GitHub workflows

```yaml
id: TD-001
severity: CRITICAL
category: CI/CD
description: "7 workflows v platform/.github/workflows/ jsou ORPHANED — GitHub je nikdy nespustí. 4 z nich (codeql, docker-publish, security-nightly, dependabot-auto-merge) chybí v root .github/ a NEBĚŽÍ vůbec."
impact: "Chybí CodeQL analýza, Docker publish, nightly security audit, Dependabot auto-merge."
files:
  - platform/.github/workflows/ci.yml (duplicate)
  - platform/.github/workflows/release.yml (duplicate)
  - platform/.github/workflows/manual-tag.yml (duplicate)
  - platform/.github/workflows/codeql.yml (MISSING in root)
  - platform/.github/workflows/docker-publish.yml (MISSING in root)
  - platform/.github/workflows/security-nightly.yml (MISSING in root)
  - platform/.github/workflows/dependabot-auto-merge.yml (MISSING in root)
effort: S (2-3h)
recommendation: "Přesunout codeql, docker-publish, security-nightly, dependabot-auto-merge do root .github/workflows/ (s working-directory: platform). Smazat 3 duplikáty z platform/.github/."
source: SPOS-016, SPOS-012
```

### TD-002 — starcore-integrity.yml BROKEN

```yaml
id: TD-002
severity: CRITICAL
category: CI/CD
description: "starcore-integrity.yml v root .github/ spouští 'python -m compileall core platform || true'. Root core/ je legacy Python 6.x-7.x kód — compileall na něm vždy failne, ale || true to maskuje."
impact: "False positive — workflow reportuje OK i když integrity check je nefunkční."
files:
  - .github/workflows/starcore-integrity.yml:26
effort: XS (30 min)
recommendation: "Opravit na 'python -m compileall platform/' nebo smazat celý workflow (root ci.yml již pokrývá linting/types)."
source: SPOS-012, SPOS-016
```

### TD-003 — starcore-release.yml LEGACY

```yaml
id: TD-003
severity: MEDIUM
category: CI/CD
description: "starcore-release.yml v root .github/ jen spouští 'git status && git branch'. Neprovádí žádnou validaci."
impact: "Zbytečný workflow, matoucí název (vypadá jako release pipeline)."
effort: XS (15 min)
recommendation: "Smazat — root release.yml je skutečný release workflow."
source: SPOS-016
```

---

## HIGH DEBT

### TD-004 — 24 Legacy/Termux root directories

```yaml
id: TD-004
severity: HIGH
category: REPOSITORY_HYGIENE
description: "24 root-level adresářů (18 legacy + 5 termux + 1 broken) zůstává v repo bez governance. Žádný z nich není importován platform/ kódem."
impact: "Matoucí navigace, zvětšuje clone size, zavádějící pro nové contributory."
directories: [core/, control_center/, mission_engine/, studio/, sdk/, hardening/, cli/, config/, bin/, plugins/, sessions/, prompts/, backups/, installers/, templates/, bundles_7x/, security/, intelligence/, automation/, agents/, ai_core/, ai_runtime/, autonomous/, distributed/]
effort: M (4-6h pro archivaci)
recommendation: "Přesunout do legacy/ subdirectory nebo archivovat do git tagu a smazat."
source: SPOS-015, SPOS-016
```

### TD-005 — 65 Root-level install scripts

```yaml
id: TD-005
severity: HIGH
category: REPOSITORY_HYGIENE
description: "65 install_*.sh skriptů v root — všechny Termux-specific (#!/data/data/com.termux/...). Zabírají root namespace."
impact: "Root je nepřehledný. ls zobrazí 65 skriptů + 35 adresářů."
effort: S (přesunout do legacy/install/ nebo scripts/termux/)
recommendation: "Přesunout do legacy/termux-installers/."
source: SPOS-008, SPOS-015, SPOS-016
```

### TD-006 — 411 runtime/ JSON state files

```yaml
id: TD-006
severity: HIGH
category: REPOSITORY_HYGIENE
description: "runtime/ obsahuje 411 JSON souborů generovaných Termux install skripty. Jsou runtime state, ne source code."
impact: "3.1MB zbytečných souborů v repo, matoucí struktura."
effort: S (přesunout do legacy/ nebo .gitignore)
recommendation: "Přesunout do legacy/runtime-state/ nebo přidat do .gitignore."
source: SPOS-015, SPOS-016
```

### TD-007 — 16MB Gold Master backup v repo

```yaml
id: TD-007
severity: HIGH
category: REPOSITORY_SIZE
description: "backups/releases/STARCORE_8.10_GOLD_MASTER.tar.gz (16MB) — binární archiv v git repo."
impact: "Zvětšuje clone, nikdy se nemění ale zůstává v git history."
effort: XS (smazat, case git filter-branch)
recommendation: "Smazat z repo. Pokud potřeba, vytvořit GitHub release asset."
source: SPOS-016
```

---

## MEDIUM DEBT

### TD-008 — DUP-001 _persist_run() copy ✅ RESOLVED (SPOS-020, commit 87a0ede)

```yaml
id: TD-008
severity: MEDIUM
category: CODE_QUALITY
description: "Identická _persist_run() v blueprints.py:177 a ws.py:202."
effort: XS
recommendation: "Extrahovat do sdíleného modulu."
source: SPOS-015
status: RESOLVED
resolved_by: SPOS-020
resolution: "persist_run() extracted to packages/core/repository.py. Both local copies removed."
resolved_date: "2026-08-08"
```

### TD-009 — psutil jako přímá závislost ✅ RESOLVED (SPOS-020, commit 87a0ede)

```yaml
id: TD-009
severity: LOW
category: DEPENDENCY_MANAGEMENT
description: "psutil je v pyproject.toml dependencies, ale žádný platform/ kód ho přímo neimportuje. Je transitivní dependency opentelemetry."
effort: XS
recommendation: "Odebrat z přímých dependencies."
source: SPOS-016
status: RESOLVED
resolved_by: SPOS-020
resolution: "psutil>=7.0.0 removed from pyproject.toml. uv.lock regenerated. uv sync clean."
resolved_date: "2026-08-08"
```

### TD-010 — platform/reports/ stale historical reports

```yaml
id: TD-010
severity: LOW
category: DOCUMENTATION
description: "12 historických reportů z 2026-07-26 v platform/reports/. Předchůdci .claude/reports/."
effort: XS
recommendation: "KEEP jako historický kontext nebo přesunout do legacy/."
source: SPOS-016
```

### TD-011 — bin/control-center broken symlink

```yaml
id: TD-011
severity: MEDIUM
category: BROKEN
description: "bin/control-center je symlink na /data/data/com.termux/... — Termux path, nefunkční mimo Termux."
effort: XS
recommendation: "Smazat nebo archivovat s celým bin/."
source: SPOS-015
```

---

## LOW DEBT

### TD-012 — requirements.txt redundantní

```yaml
id: TD-012
severity: LOW
description: "Root requirements.txt (packaging/setuptools/wheel) nepoužíván. Platform/ používá uv."
effort: XS
recommendation: REMOVE
```

### TD-013 — .envrc stale

```yaml
id: TD-013
severity: LOW
description: "Root .envrc odkazuje .venv/ v rootu, ale venv je v platform/.venv/."
effort: XS
recommendation: REMOVE nebo opravit path
```

### TD-014 — config.yaml stale

```yaml
id: TD-014
severity: LOW
description: "Root config.yaml definuje paths (workspace, logs, reports, backups) — tyto paths neexistují v aktuální architektuře."
effort: XS
recommendation: ARCHIVE
```

### TD-015 — 4 Dead code directories

```yaml
id: TD-015
severity: LOW
description: "github_intelligence/, knowledge_engine/, performance/, api_gateway/ — zero references."
effort: XS
recommendation: REMOVE
```

### TD-016 — 3 Empty registry files

```yaml
id: TD-016
severity: LOW
description: "registry/modules.json, registry/sdk_registry.json, runtime/marketplace/registry.json — prázdné."
effort: XS
recommendation: REMOVE
```

---

## SOUHRNNÉ METRIKY

```yaml
total_debt_items: 16
resolved_items: 15 (TD-001..TD-009, TD-011..TD-016)
open_items: 1 (TD-010)

critical: 3 (TD-001, TD-002, TD-003) — ALL RESOLVED by SPOS-017
high: 4 (TD-004, TD-005, TD-006, TD-007) — ALL RESOLVED by SPOS-018/019
medium: 3 (TD-008, TD-009, TD-011) — ALL RESOLVED by SPOS-018/020
low: 6 (TD-010, TD-012..TD-016) — TD-010 OPEN, rest RESOLVED by SPOS-018

estimated_total_effort: "M (10-15h pro plnou konsolidaci)"
estimated_quick_wins: "XS (2-3h pro TD-002, TD-003, TD-008, TD-009, TD-011..TD-016)"

debt_by_category:
  CI/CD: 3 (TD-001, TD-002, TD-003)
  REPOSITORY_HYGIENE: 3 (TD-004, TD-005, TD-006)
  REPOSITORY_SIZE: 1 (TD-007)
  CODE_QUALITY: 1 (TD-008)
  DEPENDENCY_MANAGEMENT: 1 (TD-009)
  DOCUMENTATION: 1 (TD-010)
  BROKEN: 1 (TD-011)
  STALE_CONFIG: 3 (TD-012, TD-013, TD-014)
  DEAD_CODE: 2 (TD-015, TD-016)
```
