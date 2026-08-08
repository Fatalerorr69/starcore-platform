# CODE DUPLICATION REPORT

Standard: SPOS-016 §3 | Aktualizováno: 2026-08-08

Kompletní report duplicitního kódu, konfigurací, workflows a dokumentace.

---

## 1. DUPLICITNÍ KÓD (platform/)

### DUP-001 — _persist_run() exact copy (z SPOS-015)

```yaml
id: DUP-001
severity: MEDIUM
type: EXACT_COPY
files:
  - "platform/packages/core/routers/blueprints.py:177"
  - "platform/packages/core/routers/ws.py:202"
lines: 6
description: "Identická 6-řádková funkce _persist_run() zkopírovaná mezi dvěma routery."
recommendation: MERGE — extrahovat do sdíleného modulu
effort: XS
action: MERGE
```

### DUP-002 — Provider connection boilerplate (z SPOS-015)

```yaml
id: DUP-002
severity: LOW
type: STRUCTURAL_PATTERN
files:
  - "platform/packages/providers/docker/provider.py"
  - "platform/packages/providers/proxmox/provider.py"
  - "platform/packages/providers/kubernetes/provider.py"
lines: ~30
description: "Tři provideři opakují identický connect/disconnect pattern."
recommendation: KEEP — ABC pattern, přijatelné opakování
effort: S
action: KEEP
```

### DUP-003 — get_settings() repeated calls (z SPOS-015)

```yaml
id: DUP-003
severity: LOW
type: ANTIPATTERN
description: "get_settings() voláno opakovaně v rámci jedné funkce."
note: "@lru_cache zajišťuje, že se Settings singleton nevytváří vícekrát. Čistě stylistické."
recommendation: KEEP — funkčně bezproblémové
action: KEEP
```

---

## 2. DUPLICITNÍ ADRESÁŘE (root vs platform/)

### DUP-DIR-001 — core/ vs platform/packages/core/

```yaml
id: DUP-DIR-001
severity: HIGH
type: DIRECTORY_DUPLICATE
root: "core/ (43 .py, 12 subdirs, LEGACY 6.x-7.x)"
platform: "platform/packages/core/ (20+ .py, ACTIVE v0.6.0)"
overlap: "Oba implementují: config, database, logging, CLI, plugins, services, utils"
evidence: "Root core/ → Path.home()/'STARCORE', platform/packages/core/ → pydantic-settings + FastAPI"
imported_by_platform: false
recommendation: ARCHIVE root core/
action: ARCHIVE
```

### DUP-DIR-002 — plugins/ vs platform/plugins/

```yaml
id: DUP-DIR-002
severity: HIGH
type: DIRECTORY_DUPLICATE
root: "plugins/ (202 files, 187 .py Termux stubs)"
platform: "platform/plugins/ (2 plugins: example_provider, run_logger)"
overlap: "Oba implementují plugin system"
evidence: "Root plugins/ → Android/Termux, platform/plugins/ → Python importlib"
imported_by_platform: false
recommendation: ARCHIVE root plugins/
action: ARCHIVE
```

### DUP-DIR-003 — cli/ vs platform/apps/cli/

```yaml
id: DUP-DIR-003
severity: MEDIUM
type: DIRECTORY_DUPLICATE
root: "cli/ (starcore/ package, LEGACY)"
platform: "platform/apps/cli/ (Typer CLI, ACTIVE)"
overlap: "Oba jsou CLI entry points"
imported_by_platform: false
recommendation: ARCHIVE root cli/
action: ARCHIVE
```

### DUP-DIR-004 — sdk/ vs platform/packages/provider_sdk/

```yaml
id: DUP-DIR-004
severity: MEDIUM
type: DIRECTORY_DUPLICATE
root: "sdk/ (4 .py, LEGACY)"
platform: "platform/packages/provider_sdk/ (ACTIVE)"
overlap: "Oba definují SDK/extension framework"
imported_by_platform: false
recommendation: ARCHIVE root sdk/
action: ARCHIVE
```

### DUP-DIR-005 — sessions/ vs platform/.starcore/sessions/

```yaml
id: DUP-DIR-005
severity: LOW
type: DIRECTORY_DUPLICATE
root: "sessions/ (session_memory.json, 1 file)"
platform: "platform/.starcore/sessions/ (ledger.yaml, ACTIVE)"
overlap: "Session management"
imported_by_platform: false
recommendation: ARCHIVE root sessions/
action: ARCHIVE
```

### DUP-DIR-006 — prompts/ vs platform/.starcore/prompts/

```yaml
id: DUP-DIR-006
severity: LOW
type: DIRECTORY_DUPLICATE
root: "prompts/ (4 .md files, LEGACY)"
platform: "platform/.starcore/prompts/registry.yaml (ACTIVE)"
overlap: "Prompt storage"
imported_by_platform: false
recommendation: ARCHIVE root prompts/
action: ARCHIVE
```

---

## 3. DUPLICITNÍ WORKFLOWS (.github/ vs platform/.github/)

### DUP-WF-001 — ci.yml overlap

```yaml
id: DUP-WF-001
severity: CRITICAL
files:
  - ".github/workflows/ci.yml (ACTIVE — GitHub reads this)"
  - "platform/.github/workflows/ci.yml (ORPHANED — GitHub ignores)"
difference: "Root version has working-directory: platform, pinned actions. Platform version lacks working-directory."
recommendation: MIGRATE platform/.github/ unique workflows to root .github/, remove platform/.github/
action: MERGE
```

### DUP-WF-002 — release.yml overlap

```yaml
id: DUP-WF-002
severity: HIGH
files:
  - ".github/workflows/release.yml (ACTIVE)"
  - "platform/.github/workflows/release.yml (ORPHANED)"
difference: "Root version has working-directory, platform version uses v0.2.0 defaults (stale)"
recommendation: MERGE
action: MERGE
```

### DUP-WF-003 — manual-tag.yml overlap

```yaml
id: DUP-WF-003
severity: MEDIUM
files:
  - ".github/workflows/manual-tag.yml (ACTIVE)"
  - "platform/.github/workflows/manual-tag.yml (ORPHANED, uses v0.2.0 default)"
recommendation: MERGE
action: MERGE
```

### Missing in root .github/ (currently ORPHANED in platform/.github/)

| Workflow | Účel | Priority |
|---|---|---|
| `codeql.yml` | CodeQL analysis | HIGH — should be in root |
| `docker-publish.yml` | Docker image publish | HIGH — should be in root |
| `security-nightly.yml` | Nightly security audit | HIGH — should be in root |
| `dependabot-auto-merge.yml` | Auto-merge Dependabot | MEDIUM — should be in root |

---

## 4. DUPLICITNÍ KONFIGURACE

### DUP-CFG-001 — config/ vs pydantic-settings

```yaml
id: DUP-CFG-001
severity: LOW
root: "config/ (ai.json, platform.json, runtime.json, security.json, ai_context.yaml)"
platform: "platform/packages/core/config.py (pydantic-settings, STARCORE_* env vars)"
overlap: "Konfigurační systém"
recommendation: ARCHIVE root config/
action: ARCHIVE
```

---

## 5. DUPLICITNÍ DOKUMENTACE

### DUP-DOC-001 — platform/reports/ legacy reports

```yaml
id: DUP-DOC-001
severity: LOW
files: 12 historical reports in platform/reports/
note: "Tyto reporty z 2026-07-26 jsou předchůdci .claude/reports/. Obsahují užitečný historický kontext."
recommendation: KEEP (historical record) nebo ARCHIVE
action: KEEP
```

---

## STATISTIKY

```yaml
total_duplicates: 16

code_duplicates: 3 (DUP-001..003 z SPOS-015)
directory_duplicates: 6 (DUP-DIR-001..006)
workflow_duplicates: 3 (DUP-WF-001..003)
config_duplicates: 1 (DUP-CFG-001)
doc_duplicates: 1 (DUP-DOC-001)
orphaned_workflows: 4 (codeql, docker-publish, security-nightly, dependabot)

actions:
  MERGE: 5 (DUP-001, DUP-WF-001..003 + orphaned workflows)
  ARCHIVE: 7 (DUP-DIR-001..006, DUP-CFG-001)
  KEEP: 4 (DUP-002, DUP-003, DUP-DOC-001)
```
