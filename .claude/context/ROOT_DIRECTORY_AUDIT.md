# ROOT DIRECTORY AUDIT

Standard: SPOS-016 §1 | Aktualizováno: 2026-08-08

Kompletní audit všech root-level adresářů a souborů v repozitáři starcore-platform.

---

## ROOT-LEVEL ADRESÁŘE (35)

| # | Adresář | Souborů | Py | Sh | Klasifikace | Verze | Akce |
|---|---|---|---|---|---|---|---|
| 1 | `.claude/` | 107 | 0 | 0 | GOVERNANCE | — | KEEP |
| 2 | `.github/` | 6 wf | 0 | 0 | ACTIVE | — | MERGE (s platform/.github/) |
| 3 | `platform/` | 33808 | 6796 | 5 | ACTIVE | 0.6.0 | KEEP |
| 4 | `knowledge/` | 10 | 2 | 0 | ACTIVE | SAKB | KEEP |
| 5 | `agents/` | 4 | 3 | 0 | TERMUX | 6B | ARCHIVE |
| 6 | `ai_core/` | 1 | 1 | 0 | TERMUX | 8A | ARCHIVE |
| 7 | `ai_runtime/` | 3 | 3 | 0 | TERMUX | 8A | ARCHIVE |
| 8 | `autonomous/` | 9 | 9 | 0 | TERMUX | 7.1 | ARCHIVE |
| 9 | `distributed/` | 9 | 9 | 0 | TERMUX | 7.2 | ARCHIVE |
| 10 | `core/` | 63 | 43 | 2 | LEGACY | 6.x-7.x | ARCHIVE |
| 11 | `control_center/` | 21 | 0 | 7 | LEGACY | 7.x | ARCHIVE |
| 12 | `mission_engine/` | 3 | 3 | 0 | LEGACY | 7.x | ARCHIVE |
| 13 | `studio/` | 3 | 1 | 0 | LEGACY | 7.x | ARCHIVE |
| 14 | `sdk/` | 4 | 4 | 0 | LEGACY | 7.x | ARCHIVE |
| 15 | `hardening/` | 2 | 2 | 0 | LEGACY | 7.x-8.x | ARCHIVE |
| 16 | `cli/` | 1 | 0 | 0 | LEGACY | 6.x-7.x | ARCHIVE |
| 17 | `config/` | 5 | 0 | 0 | LEGACY | 7.x | ARCHIVE |
| 18 | `bin/` | 3 | 0 | 0 | BROKEN | 7.x | ARCHIVE |
| 19 | `plugins/` | 202 | 187 | 5 | TERMUX | 6B | ARCHIVE |
| 20 | `sessions/` | 1 | 0 | 0 | LEGACY | 7.x | ARCHIVE |
| 21 | `prompts/` | 4 | 0 | 0 | LEGACY | 7.x-8.x | ARCHIVE |
| 22 | `backups/` | 1 | 0 | 0 | LEGACY | 8.x | ARCHIVE |
| 23 | `installers/` | 10 | 1 | 8 | LEGACY | 8.x | ARCHIVE |
| 24 | `templates/` | 1 | 0 | 0 | LEGACY | 7.x | ARCHIVE |
| 25 | `tools/` | 18 | 0 | 18 | TERMUX | 6B | ARCHIVE |
| 26 | `registry/` | 3 | 0 | 0 | DEPRECATED | 7.x | REMOVE |
| 27 | `runtime/` | 411 | 0 | 0 | GENERATED | 6B-8.x | ARCHIVE |
| 28 | `security/` | 10 | 3 | 0 | LEGACY | 7.x-8.x | ARCHIVE |
| 29 | `intelligence/` | 9 | 0 | 0 | GENERATED | 8.x | ARCHIVE |
| 30 | `automation/` | 22 | 0 | 21 | LEGACY | 7.x | ARCHIVE |
| 31 | `github_intelligence/` | 1 | 1 | 0 | DEAD | — | REMOVE |
| 32 | `knowledge_engine/` | 1 | 1 | 0 | DEAD | — | REMOVE |
| 33 | `performance/` | 1 | 1 | 0 | DEAD | — | REMOVE |
| 34 | `api_gateway/` | 1 | 1 | 0 | DEAD | — | REMOVE |
| 35 | `bundles_7x/` | 5 | 0 | 5 | LEGACY | 7.x | ARCHIVE |

---

## ROOT-LEVEL SOUBORY

| Soubor | Typ | Klasifikace | Akce |
|---|---|---|---|
| `README.md` | Dokumentace | ACTIVE | KEEP |
| `SECURITY.md` | Dokumentace | ACTIVE | KEEP |
| `.gitignore` | Config | ACTIVE | KEEP |
| `.envrc` | Config | LEGACY | ARCHIVE (references `.venv/` at root) |
| `config.yaml` | Config | LEGACY | ARCHIVE (platform uses pydantic-settings) |
| `requirements.txt` | Deps | DEPRECATED | REMOVE (only packaging/setuptools/wheel, not used) |
| `starcore` | Script | TERMUX | ARCHIVE (Termux Python entry point) |
| `generate_7x_bulk_packages.sh` | Script | LEGACY | ARCHIVE |
| `preflight_STARCORE_8_MIGRATION_AUDIT.sh` | Script | LEGACY | ARCHIVE |
| `repair_ENGINEERING_LAYER.sh` | Script | LEGACY | ARCHIVE |
| `install_*.sh` (65 souborů) | Script | TERMUX | ARCHIVE |

---

## KLASIFIKAČNÍ DEFINICE (SPOS-016)

```yaml
ACTIVE:     Živý kód v produkčním/dev workflow, importovaný a testovaný
GOVERNANCE: .claude/ governance vrstva (SES/SAKB/SPOS)
LEGACY:     Historický kód z dřívějších verzí, neimportovaný platformou
TERMUX:     Skripty/moduly specifické pro Termux Android (~/STARCORE path, pkg install)
GENERATED:  Runtime výstup generovaný Termux skripty (JSON state files)
DEPRECATED: Zastaralé soubory bez funkční hodnoty
DEAD:       Kód bez jakéhokoli importu/reference odkudkoli
BROKEN:     Nefunkční (broken symlinks, chybějící závislosti)
PLANNED:    Zamýšlená budoucí funkcionalita
UNKNOWN:    Nezařazeno
```

---

## STATISTIKY

```yaml
total_root_directories: 35
total_root_files: 73+

classification_summary:
  ACTIVE: 3 (platform/, knowledge/, .github/)
  GOVERNANCE: 1 (.claude/)
  LEGACY: 15
  TERMUX: 7 (agents/, ai_core/, ai_runtime/, autonomous/, distributed/, plugins/, tools/)
  GENERATED: 2 (runtime/, intelligence/)
  DEPRECATED: 1 (registry/)
  DEAD: 4 (github_intelligence/, knowledge_engine/, performance/, api_gateway/)
  BROKEN: 1 (bin/)

action_summary:
  KEEP: 4 (platform/, .claude/, knowledge/, 3 root files)
  ARCHIVE: 24 directories + 68 scripts
  REMOVE: 5 (4 dead + registry/)
  MERGE: 1 (.github/ workflows → reconcile with platform/.github/)
```

---

## DŮKAZY PRO KLASIFIKACI

### TERMUX pattern (7 dirs + 65 install scripts + root `starcore`)

Všechny obsahují `#!/data/data/com.termux/files/usr/bin/bash` nebo `Path.home() / "STARCORE"` referenci. Generují JSON soubory do `~/STARCORE/runtime/`. Žádný z nich není importován platform/ kódem.

Potvrzeno:
- `plugins/enabled/android/` — 187 .py souborů, **všech 187** obsahuje `Path.home() / "STARCORE"` pattern
- `agents/` — 3 .py, JSON print stubs
- `ai_core/ai_kernel.py` — JSON print stub
- `ai_runtime/` — 3 .py, Termux stubs
- `autonomous/` — 9 .py, Termux stubs
- `distributed/` — 9 .py, Termux stubs
- `tools/` — 18 .sh, all Termux shell stubs

### GENERATED (runtime/, intelligence/)

- `runtime/` — 411 souborů, 405 JSON, 6 text. Vše generováno Termux install skripty. Obsahuje `runtime/android/` (100+ subdirs), `runtime/termux/`, atd.
- `intelligence/` — 9 souborů (files.txt, issues.txt, python.txt — repository scan outputs). 2.2MB, čistě generovaný obsah.

### DEAD CODE (4 dirs)

- `github_intelligence/github_scanner.py` — zero imports, zero references v celém repo
- `knowledge_engine/knowledge_core.py` — zero imports
- `performance/performance_analyzer.py` — zero imports
- `api_gateway/api_gateway.py` — zero imports

### cross-reference: `from core.` v platform/

`platform/packages/` importuje `from core.config`, `from core.events` atd. — toto odkazuje na `platform/packages/core/` (via `pythonpath = [".", "packages"]` v pyproject.toml), **NE** na root `core/`. Potvrzeno pyright 0 errors.
