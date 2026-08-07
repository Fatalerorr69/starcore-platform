# SPOS-015 DISCOVERY REPORT

Standard: SES-000 §3 | Datum: 2026-08-07

---

## EXECUTIVE SUMMARY

Discovery pro SPOS-015 odhalila zásadní governance gap: **25 nezdokumentovaných root-level adresářů**, kopírovaný kód, mrtvý kód, orphaned komponenty a prázdné registry. Repozitář obsahuje rozsáhlou legacy vrstvu (Termux install skripty, studio/, control_center/, mission_engine/) vedle živého platform/ monolitu, ale tato legacy vrstva nemá žádnou formální klasifikaci ani governance.

**Doporučení:** SPOS-015 by měl být **Ecosystem Hygiene Engine** — kompletní katalogizace a klasifikace celého repozitáře.

---

## DISCOVERY NÁLEZY

### 1. NEZDOKUMENTOVANÉ ROOT-LEVEL ADRESÁŘE (25)

| Adresář | Obsah | Klasifikace |
|---|---|---|
| `api_gateway/` | 1 soubor: `api_gateway.py` | STUB |
| `backups/` | `releases/` subdir | LEGACY |
| `bin/` | CLI entry points: starcore, starcore-status, starcore-verify, control-center | LEGACY |
| `bundles_7x/` | 5 shell skriptů: batch install bundles pro 7.x sérii | LEGACY/STUB |
| `cli/` | `starcore/` subdir (CLI package) | LEGACY |
| `config/` | JSON/YAML: ai.json, ai_context.yaml, platform.json, runtime.json, security.json | LEGACY |
| `control_center/` | backups/, bin/, config/, modules/ | LEGACY |
| `core/` | Plný Python package: bin/, cli/, config/, database/, installer/, lib/, logging/, modules/, plugins/, runtime/, services/, utils/ | LEGACY (rozsáhlý) |
| `github_intelligence/` | 1 soubor: github_scanner.py | DEAD CODE |
| `hardening/` | dependencies/, environment/ | LEGACY |
| `installers/` | android/ subdir | LEGACY/STUB |
| `knowledge_engine/` | 1 soubor: knowledge_core.py | DEAD CODE |
| `mission_engine/` | execution/, missions/, workflows/ | LEGACY |
| `performance/` | 1 soubor: performance_analyzer.py | DEAD CODE |
| `plugins/` | enabled/, registry/ | LEGACY |
| `prompts/` | generated/, master_context.md, proxmox_operator.md, repository_audit.md | LEGACY |
| `registry/` | commands.json, modules.json (prázdné!), sdk_registry.json (prázdný!) | LEGACY/EMPTY |
| `sdk/` | core/ subdir | LEGACY |
| `sessions/` | 1 soubor: session_memory.json | LEGACY |
| `studio/` | dashboard/, module_control/, system_view/ | LEGACY |
| `templates/` | module_template/ subdir | LEGACY |
| `tools/` | access/, context/, control_center/, engineering/, intelligence/, remote_bridge/ | LEGACY |
| `ai_runtime/` | 3 Termux stubs (SPOS-014 dokumentováno) | STUB |
| `autonomous/` | 9 Termux stubs (SPOS-014 dokumentováno) | STUB |
| `distributed/` | 9 Termux stubs (SPOS-014 dokumentováno) | STUB |

**Poznámka:** ai_runtime/, autonomous/, distributed/ jsou již dokumentovány v AGENT_REGISTRY.md (SPOS-014). Zbývajících 22 adresářů nemá žádnou governance dokumentaci.

### 2. ORPHANED KOMPONENTY V platform/

| Cesta | Popis | Stav |
|---|---|---|
| `platform/data/` | SQLite databáze (starcore.db) | NEDOKUMENTOVÁNO |
| `platform/reports/` | 12 markdown/JSON reportů | NEDOKUMENTOVÁNO |
| `platform/site/` | MkDocs-generated HTML | NEDOKUMENTOVÁNO (build artifact) |
| `platform/scripts/make-executable.sh` | — | NEDOKUMENTOVÁNO |
| `platform/scripts/quickstart.sh` | — | NEDOKUMENTOVÁNO |
| `platform/scripts/release.py` | — | NEDOKUMENTOVÁNO |

### 3. MRTVÝ KÓD

| Soubor | Důkaz |
|---|---|
| `github_intelligence/github_scanner.py` | Zero imports/references anywhere |
| `knowledge_engine/knowledge_core.py` | Zero imports (zmíněn pouze v .starcore memory) |
| `api_gateway/api_gateway.py` | Zero registry references |
| `performance/performance_analyzer.py` | Zero registry references |
| `security/backup_engine.py` | Zero registry references |
| `security/github_intelligence_upgrade.py` | Zero registry references |
| `security/security_audit.py` | Zero registry references |

### 4. CHYBĚJÍCÍ ADR

| Téma | Kód kde se vyskytuje | Status |
|---|---|---|
| Database migration strategy (create-then-stamp) | `packages/core/database.py` L65, L96 | NO ADR |
| WebSocket run streaming | `packages/core/routers/ws.py` | NO ADR |

### 5. NEZDOKUMENTOVANÉ SKRIPTY

- **64+ root-level shell skriptů** — install_6B*, install_7_*, install_8*, install_STARCORE_*, install_TERMUX_* (SPOS-008 je katalogizoval jako "Termux stubs", ale individuální registry chybí)
- **5 bundles_7x/ skriptů** — batch install bundles
- **3 platform/scripts/ skriptů** — make-executable.sh, quickstart.sh, release.py

### 6. DUPLICITNÍ LOGIKA

| Duplicita | Soubory | Řádky |
|---|---|---|
| `_persist_run()` — identická kopie | `core/routers/blueprints.py:177` + `core/routers/ws.py:202` | 6 řádků |
| Provider connection-failure boilerplate | docker/proxmox/kubernetes provider.py | ~10 řádků × 3 |
| `get_settings()` opakované volání | diagnostics.py (4×), 10+ dalších souborů | Bez cachování |

### 7. PRÁZDNÉ REGISTRY

| Soubor | Stav |
|---|---|
| `registry/modules.json` | `modules: []` — prázdný |
| `registry/sdk_registry.json` | prázdný |
| `runtime/marketplace/registry.json` | `plugins: []` — prázdný |

---

## SPOS-015 NÁVRH: ECOSYSTEM HYGIENE ENGINE

### Cíl

Kompletní katalogizace a klasifikace celého repozitáře. Formální oddělení živého platform/ kódu od legacy/stub/dead vrstev. Vytvoření ECOSYSTEM_MAP jako definitivní referenční mapy.

### Navrhované výstupy

| # | Soubor | Popis |
|---|---|---|
| 1 | `ECOSYSTEM_MAP.md` | Definitivní mapa celého repozitáře (adresáře → klasifikace) |
| 2 | `LEGACY_REGISTRY.md` | Registr 22 nezdokumentovaných legacy adresářů |
| 3 | `DEAD_CODE_REGISTRY.md` | Registr mrtvého kódu s doporučením (keep/archive/delete) |
| 4 | `DUPLICATE_REGISTRY.md` | Registr duplicitní logiky s refactoring doporučeními |
| 5 | `SCRIPT_REGISTRY.md` | Registr 70+ shell skriptů s klasifikací |
| 6 | `ECOSYSTEM_HEALTH.md` | Health score celého ekosystému |
| 7 | `ECOSYSTEM_GAP_ANALYSIS.md` | Gap analýza ekosystém-wide |
| 8 | `ECOSYSTEM_RECOMMENDATIONS.md` | Doporučení (cleanup, archivace, refactoring) |
| 9 | `SPOS-015-IMPLEMENTATION-REPORT.md` | Implementační report |

### Rozšíření existujících registrů

- SPOS_REGISTRY — SPOS-015 řádek
- DOCUMENTATION_REGISTRY — DR-054+ entries
- SES-INDEX — SPOS-015 AKTIVNÍ
- DIGITAL_TWIN — spos_015 blok
- Session Ledger — aktualizace spos-015 session
- Prompt Registry — PROM-011

### Principy

- Discovery First — žádná fabrikace
- Rozšíření existujících registrů, ne duplicity
- Žádný kód nebude vytvořen ani modifikován (čistě governance)
- Transparentní klasifikace: ACTIVE / LEGACY / STUB / DEAD / EMPTY

---

```yaml
prepared_by: Claude Code
datum: 2026-08-07
session: spos-015-20260807
```
