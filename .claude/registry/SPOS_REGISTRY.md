# SPOS REGISTRY

Aktualizováno: 2026-08-06 | Standard: SPOS-003

Registr operačních modulů Project Operating System. Fyzická implementace primárně v `platform/.starcore/` (viz SPOS-000 rozhodnutí — adoptováno, ne duplikováno).

---

| Modul | Název | Implementace | Status |
|---|---|---|---|
| SPOS-001 | Project Memory | `platform/.starcore/memory/*.md` (+ nově `current_state.md`, `state/project_state.json`) | ✅ AKTIVNÍ — ROZŠÍŘENO |
| SPOS-002 | Session Management | `platform/.starcore/sessions/` + `scripts/ledger.py` (+ nově `.claude/registry/SESSION_REGISTRY.md`, `.claude/context/SESSION_CONTEXT.md`) | ✅ AKTIVNÍ — ROZŠÍŘENO, ŽIVĚ OTESTOVÁNO |
| SPOS-003 | Prompt Registry | `platform/.starcore/prompts/registry.yaml` + `scripts/registry.py` (+ nově `.claude/registry/PROMPT_REGISTRY.md`, 7 SES/SAKB/SPOS promptů zaregistrováno) | ✅ AKTIVNÍ — ROZŠÍŘENO, ŽIVĚ OTESTOVÁNO |
| SPOS-004 | Project Intelligence | `scripts/impact_analyzer.py` | ⚠️ ČÁSTEČNÉ |
| SPOS-005 | Audit Engine | `scripts/qc_engine.py`, `regression_sentinel.py`, `release_readiness.py` | ✅ AKTIVNÍ |
| SPOS-006 | Documentation Engine | manuální (`.claude/registry/DOCUMENTATION_REGISTRY.md`) | ❌ NEAUTOMATIZOVÁNO |
| SPOS-007 | Infrastructure Control | rozptýleno (`platform/packages/providers`) | ❌ NENÍ SAMOSTATNÝ MODUL |
| SPOS-008 | AI Orchestration | částečně (`scripts/decision_engine.py`) | ⚠️ ČÁSTEČNÉ |
| SPOS-009 | Evolution Engine | — | ❌ NEEXISTUJE |
| SPOS-010 | Digital Twin Runtime | `.claude/context/DIGITAL_TWIN.md` (ekosystém) + `platform/.starcore/memory/project_snapshot.md` (platform, ZASTARALÉ) | ⚠️ DUPLICITNÍ SCOPE |

---

## AUTOMATION CLI (dostupné v `platform/.starcore/scripts/`)

| Nástroj | Účel |
|---|---|
| `registry.py` | Prompt Registry CLI (register/list/search/supersede/validate) |
| `ledger.py` | Session Ledger CLI (start/end/current/add-decision/add-risk) |
| `decision_engine.py` | Interaktivní rozhodovací formát (format/render/check-safety/log) |
| `impact_analyzer.py` | Analýza dopadu změn (soubor → modul → dopad) |
| `regression_sentinel.py` | Detekce regresí vs. baseline |
| `release_readiness.py` | 12-gate release readiness evaluace |
| `qc_engine.py` | Sjednocený QC orchestrátor |
| `startup_protocol.py` | 12-step cold-start session inicializace |

---

## ZNÁMÉ MEZERY (viz SPOS-000-RUNTIME-BOOTSTRAP.md pro detail)

1. SPOS-006 Documentation Engine — dokumentace se aktualizuje manuálně, ne automatizovaným skenováním/validací
2. SPOS-007 Infrastructure Control — Proxmox/Docker control existuje jako Provider SDK, ale ne jako řídicí SPOS vrstva s inventářem
3. SPOS-009 Evolution Engine — chybí mechanismus pro řízenou evoluci promptů/architektury v čase
4. SPOS-010 — dva paralelní "digital twin" dokumenty s odlišným scope (ekosystém vs. platform), zastaralost platform snapshotu (v0.4.0 → realita v0.6.0)

---

## SPOS-001 IMPLEMENTACE (2026-08-06)

**Přístup:** Adoptovat existující `platform/.starcore/memory/`, doplnit pouze chybějící kusy — žádná paralelní implementace.

Doplněno:
- `platform/.starcore/memory/current_state.md` — lehký "kde právě jsme" pointer (chyběl, spec §4/§8 ho vyžadovala)
- `platform/.starcore/state/project_state.json` — strojově čitelný PROJECT_STATE ENGINE (VERSION, CURRENT_PHASE, ACTIVE_TASK, COMPLETED_TASKS, BLOCKERS, RISKS, NEXT_ACTIONS dle §8)
- `.claude/context/CONTEXT_RESTORATION_PROTOCOL.md` — implementace §12 AI Context Restoration, formálně propojuje `.claude/` (SES/SAKB/SPOS) s `platform/.starcore/` (runtime paměť) — dosud o sobě nevěděly
- Aditivní odkazy v `platform/CLAUDE.md` a `platform/.starcore/README.md` na nové soubory a na `.claude/` vrstvu

Funkčně ověřeno: `startup_protocol.py --quick --json` běží bez chyby po přidání nových souborů (žádný existující kód nebyl změněn).

CHANGE MEMORY (§7): nebyla vytvořena samostatná struktura — spec explicitně odkazuje na Git history/GitHub/ADR jako zdroj, což už je pokryto (`git log`, ADR-001..017). Nejde o mezeru.

---

## SPOS-002 IMPLEMENTACE (2026-08-06)

**Přístup:** Audit → adopce → živé otestování (ne jen statická analýza).

Zjištění:
- `platform/.starcore/sessions/ledger.yaml` obsahoval 1 session s `end_time: null` od 2026-07-26 — **nikdy neuzavřena** (porušení §3 lifecycle, session zůstala navždy v ACTIVE stavu)
- `_archive_session()` v `ledger.py` **již plně implementuje** §8 HANDOVER REPORT formát (Summary, Decisions, Files, Tests, Next Action) — žádná mezera
- `sessions/current.md` je **manuálně** udržovaný soubor — `ledger.py` ho needituje automaticky

Provedeno (živě, ne jen navrženo):
1. `ledger.py end` — retroaktivně uzavřena osiřelá session, archivována do `sessions/archive/2026-07-26-*.md`
2. `ledger.py start` — zaregistrována aktuální bootstrap session (`claude/starcore-ai-bootstrap-fkyb96`)
3. `ledger.py add-request/add-decision/add-risk/add-file` (×16 volání) — naplněn session record dle §4
4. `ledger.py validate` — potvrzeno: 2 sezení, 1 aktivní, 1 uzavřeno, žádná chyba integrity
5. `sessions/current.md` ručně aktualizován (mimo automatizaci skriptu)
6. Vytvořeny `.claude/context/SESSION_CONTEXT.md` (§6) a `.claude/registry/SESSION_REGISTRY.md` (§18)

Žádný Python skript nebyl změněn — pouze použit jeho existující CLI.

---

## SPOS-003 IMPLEMENTACE (2026-08-06)

**Přístup:** Registr `prompts/registry.yaml` už existoval s 8 prompty (PROM-001..008) z předchozí session — ale **žádný SES/SAKB/SPOS prompt této bootstrap session nebyl registrován**. To byla hlavní mezera.

Provedeno (živě, přes `registry.py` CLI, ne ruční YAML editace):
1. `registry.py register` (×7) — zaregistrovány SES-000, SES-001, SAKB-000, SPOS-000, SPOS-001, SPOS-002, SPOS-003 s korektním dependency chainem (přesně dle §8 příkladu: SPOS-003 depends SPOS-000/001/002)
2. `ledger.py add-prompt` (×7) — propojeny s aktuální session (§12 Prompt Memory Integration)
3. `registry.py validate` — potvrzeno: 15 promptů, žádné chyby
4. `registry.py list/search/get` — funkčně otestováno

Nalezená mezera: `PromptEntry` model nemá `RELATED_FILES`/`RELATED_COMMITS`/`VALIDATION_STATUS`/`INPUTS`/`OUTPUTS` z §5 — zaznamenáno v `PROMPT_REGISTRY.md`, dataclass vědomě nerozšiřován (riziko zásahu do 384řádkového otestovaného skriptu).

Vytvořeny: `.claude/registry/PROMPT_REGISTRY.md` (ekosystémový index, §19 povinný registr).
