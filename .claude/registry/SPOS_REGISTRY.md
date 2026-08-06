# SPOS REGISTRY

Aktualizováno: 2026-08-06 | Standard: SPOS-000

Registr operačních modulů Project Operating System. Fyzická implementace primárně v `platform/.starcore/` (viz SPOS-000 rozhodnutí — adoptováno, ne duplikováno).

---

| Modul | Název | Implementace | Status |
|---|---|---|---|
| SPOS-001 | Project Memory | `platform/.starcore/memory/*.md` | ✅ AKTIVNÍ |
| SPOS-002 | Session Management | `platform/.starcore/sessions/` + `scripts/ledger.py` | ✅ AKTIVNÍ |
| SPOS-003 | Prompt Registry | `platform/.starcore/prompts/registry.yaml` + `scripts/registry.py` | ✅ AKTIVNÍ |
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
