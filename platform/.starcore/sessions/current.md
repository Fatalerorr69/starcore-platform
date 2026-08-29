# Session Ledger — Current

> Aktivní session ledger. Archivovat do `sessions/archive/` na konci sezení.
> **Sezení ID:** claude/session-76mlz8
> **Datum:** 2026-08-06
> **Větev:** claude/session-76mlz8
> Předchozí sezení (`starcore-autonomous-engineering-4p3tlj`) bylo uzavřeno
> a archivováno: `sessions/archive/2026-07-26-starcore-autonomous-engineering-4p3tlj.md`

---

## Stav sezení

| Pole | Hodnota |
|------|---------|
| Status | CONSISTENCY_RECOVERY_WAVE_01_IN_PROGRESS |
| Fáze | Post-Architecture-Governance (ADR-018–025 committed + pushed) |
| Poslední commit (pushed) | `134a939` (předchozí sezení) — fix(timeout): replace coroutine reuse |
| Testy | 805 collected / 100% coverage |
| CI gates | Všechny zelené |

---

## Co bylo provedeno v tomto sezení (claude/session-76mlz8)

### STARCORE Architecture Governance (ADR-018–025)
- ADR-018: Repository Root vs. `platform/` Boundary
- ADR-019: `platform/` Extension Policy
- ADR-020: Legacy Root Layer Freeze
- ADR-021: AI Layer Consolidation
- ADR-022: Documentation Boundary
- ADR-023: SAEF as Workflow Protocol
- ADR-024: Android/Termux Edge Node
- ADR-025: STARCORE Change Governance Lifecycle
- Vše committed + pushed na `claude/session-76mlz8`

### Dokumentace
- `platform/docs/ROADMAP.md` — vytvoření + oprava mkdocs strict chyby
- `platform/docs/architecture/edge-node.md` — Edge Node architektura
- `platform/docs/governance/repository-history.md` — historická restrukturalizace (`0af3560`)
- `platform/mkdocs.yml` — nav rozšíření (ADR-017–025, ROADMAP, edge-node)

### Scripts
- `platform/.starcore/scripts/repository_map.py` — governance discovery tool (scan + diff)
- `platform/.starcore/scripts/tests/test_repository_map.py` — 19 unittest testů

### Governance metadata
- `platform/.starcore/prompts/registry.yaml` — PROM-009–012
- `platform/.starcore/state/regression_baseline.json` — adr_count 17→25, test_count 801→805
- `platform/.starcore/sessions/ledger.yaml` — cleanup: stale session uzavřena, nová zahájena

### Dokumentace historie
- `platform/.starcore/memory/completed_work.md` — CHECKPOINT B záznam

### CONSISTENCY RECOVERY WAVE 01 (probíhá)
- BLOCK 1: `memory/project_snapshot.md` — resync (verze, branch, metriky) ✓
- BLOCK 2: `memory/user_preferences.md` — dev branch aktualizace ✓
- BLOCK 3: `sessions/current.md` — tato aktualizace ✓
- BLOCK 4A: `docs/ROADMAP.md` — verze 0.4.0→0.6.0 ✓

---

## Otevřené položky pro příští sezení

1. **WAVE 01 RELEASE** — commit BLOCK 1+2+3+4A, push
2. **PR #128** — test addition: `test_git_activity_untracked_path`
3. **PR #128** — opengrep false positive komentář (subprocess.run, shell=False)
4. **ADR-013 Kubernetes** — concurrency poznámka (P2, nízká priorita)
5. **R-001** (SHA pinning) — P1, otevřené riziko

## Startup instrukce pro nové sezení

```bash
# 1. Ověř git stav
git status
git log --oneline -5
git branch -vv

# 2. Ověř testy
uv run pytest -q --tb=no 2>&1 | tail -3

# 3. Přečti pending work
cat .starcore/memory/pending_work.md

# 4. Pokračuj dle instrukcí uživatele
```

**Kritické připomenutí:**
- Branch: `claude/session-76mlz8` — veškerá práce sem
- Push vyžaduje souhlas uživatele
- Czech language pro komunikaci
- Viz `memory/user_preferences.md` pro kompletní pravidla
