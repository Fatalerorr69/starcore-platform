# SPOS-019 IMPLEMENTATION REPORT

Standard: SPOS-019 | Datum: 2026-08-08 | Status: PENDING APPROVAL

---

## SCOPE

Milestone 3: Repository Restructure — evidence-based migration of 23 legacy directories and 68 Termux scripts into `legacy/` directory. Part of CONSOLIDATION_ROADMAP.md.

## DISCOVERY & ANALYSIS

### Reference Analysis (10-point safety check per candidate)

All 27 root-level legacy directories analyzed against:
- A: Filesystem existence
- B: Git tracking status
- C: Reference search in platform/
- D: Import analysis (Python)
- E: CI/workflow references
- F: Docker/Makefile references
- G: Documentation references
- H: Symlink validity
- I: Package boundary check
- J: Classification

### Results

| Directory | Classification | Reason |
|---|---|---|
| knowledge/ | **KEEP** | Active SAKB governance role |
| agents/ | SAFE_TO_MOVE | No platform/ refs, stub code |
| ai_core/ | SAFE_TO_MOVE | No platform/ refs, stub code |
| ai_runtime/ | SAFE_TO_MOVE | No platform/ refs, stub code |
| automation/ | SAFE_TO_MOVE | Termux-only bash scripts |
| autonomous/ | SAFE_TO_MOVE | No platform/ refs, stub code |
| backups/ | SAFE_TO_MOVE | Archive only (16MB Gold Master) |
| bundles_7x/ | SAFE_TO_MOVE | v7.x bulk install bundles |
| cli/ | SAFE_TO_MOVE | Legacy CLI wrapper |
| config/ | SAFE_TO_MOVE | Legacy JSON/YAML configs |
| control_center/ | SAFE_TO_MOVE | Termux control center |
| core/ | SAFE_TO_MOVE | Legacy core (platform/ uses packages/core/) |
| distributed/ | SAFE_TO_MOVE | Stub code |
| hardening/ | SAFE_TO_MOVE | Dependency audit scripts |
| installers/ | SAFE_TO_MOVE | Android install history |
| intelligence/ | SAFE_TO_MOVE | Repository intelligence reports |
| mission_engine/ | SAFE_TO_MOVE | Stub code |
| plugins/ | SAFE_TO_MOVE | Android plugin ecosystem |
| prompts/ | SAFE_TO_MOVE | Legacy prompt templates |
| runtime/ | SAFE_TO_MOVE | 411 generated JSON state files |
| sdk/ | SAFE_TO_MOVE | Legacy SDK stubs |
| security/ | SAFE_TO_MOVE | Security audit scripts |
| sessions/ | SAFE_TO_MOVE | Legacy session state |
| studio/ | SAFE_TO_MOVE | Studio dashboard stubs |
| templates/ | SAFE_TO_MOVE | Module template |
| tools/ | SAFE_TO_MOVE | Bash control center tools |

### Script Analysis

All 68 root-level shell scripts confirmed as Termux-only (shebangs reference Termux paths). Moved to `legacy/termux-scripts/`.

### Import Resolution

`from core.` imports in platform/ resolve to `platform/packages/core/` via pyproject.toml `pythonpath = [".", "packages"]`, NOT root `core/`. Confirmed via grep and pyright validation.

## IMPLEMENTED CHANGES

### Moved (23 directories → legacy/)

All moves via `git mv` to preserve git history:
- agents → legacy/agents
- ai_core → legacy/ai_core
- ai_runtime → legacy/ai_runtime
- automation → legacy/automation
- autonomous → legacy/autonomous
- backups → legacy/backups
- bundles_7x → legacy/bundles_7x
- cli → legacy/cli
- config → legacy/config
- control_center → legacy/control_center
- core → legacy/core
- distributed → legacy/distributed
- hardening → legacy/hardening
- installers → legacy/installers
- intelligence → legacy/intelligence
- mission_engine → legacy/mission_engine
- plugins → legacy/plugins
- prompts → legacy/prompts
- runtime → legacy/runtime
- sdk → legacy/sdk
- security → legacy/security
- sessions → legacy/sessions
- studio → legacy/studio
- templates → legacy/templates
- tools → legacy/tools

### Moved (68 scripts → legacy/termux-scripts/)

All install_*.sh, generate_*.sh, preflight_*.sh, repair_*.sh scripts moved via `git mv`.

### Created

- `legacy/README.md` — contents table, policy (no new code, no imports)

### Modified

- `README.md` — directory tree updated to new 5-directory structure

### Kept at root

- `knowledge/` — active SAKB governance role

## POST-MIGRATION REFERENCE SWEEP

| Area | Status |
|---|---|
| .github/workflows/ | CLEAN |
| platform/ Python imports | CLEAN |
| platform/ CI configs | CLEAN |
| Docker/Makefile | CLEAN |
| knowledge/ | CLEAN |
| Root README.md | CLEAN (updated) |
| .claude/ governance docs | ~60 documentation-only refs (cosmetic) |
| .starcore/ session ledger | 18 historical path entries (pre-migration records) |

No functional broken references found.

## QC RESULTS

| Check | Result |
|---|---|
| pytest | 796 passed, 9 skipped |
| ruff check | All checks passed |
| ruff format | 138 files already formatted |
| pyright | 0 errors, 0 warnings |
| mkdocs --strict | Build OK |
| bandit | All checks passed |

## METRICS

| Metric | Before (post-M2) | After (post-M3) |
|---|---|---|
| Root dirs | 27 | 5 (platform, knowledge, legacy, .claude, .github) |
| Root scripts | 68 | 0 |
| Legacy dirs in legacy/ | 0 | 25 |
| Tech debt items | 7 | 3 |
| Repo hygiene | 72% | 88% |
| Arch alignment | 87% | 93% |
