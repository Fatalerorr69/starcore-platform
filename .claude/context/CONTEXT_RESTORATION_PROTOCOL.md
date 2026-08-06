# AI CONTEXT RESTORATION PROTOCOL

Standard: SPOS-001 §12 | Aktualizováno: 2026-08-06

Tento dokument definuje, jak má nová AI session obnovit kontext projektu STARCORE. Propojuje dvě dosud oddělené vrstvy:

- **`.claude/`** — SES/SAKB/SPOS governance vrstva (ekosystém, root-level, vytvořeno v tomto bootstrapu)
- **`platform/.starcore/`** — provozní runtime paměť (platform-scoped, pre-existující, otestovaný)

Před SPOS-001 tyto dvě vrstvy o sobě navzájem nevěděly — `platform/.starcore/startup_protocol.py` nezná `.claude/`. Toto je dokumentovaný (ne kódový) most mezi nimi.

---

## STEP 1 — Načti SES

Přečti v pořadí:
1. `.claude/ses/SES-000-ENGINEERING-CONSTITUTION.md` — principy a workflow
2. `.claude/ses/SES-001-TECHNICAL-STANDARD.md` — technický standard + gap analýza
3. `.claude/ses/SES-INDEX.md` — stav implementace všech SES/SAKB/SPOS dokumentů

## STEP 2 — Načti Digital Twin

`.claude/context/DIGITAL_TWIN.md` — živý ekosystémový stav (repository, architektura, infrastruktura, moduly, bezpečnost, dokumentace, knowledge status, SPOS status).

## STEP 3 — Načti Current State

1. `platform/.starcore/memory/current_state.md` — platform-scoped rychlý pointer
2. `platform/.starcore/state/project_state.json` — strojově čitelný stav (VERSION, CURRENT_PHASE, BLOCKERS, RISKS, NEXT_ACTIONS)

⚠️ Ověř datum aktualizace obou — pokud `project_state.json.updated_at` neodpovídá poslednímu commitu, stav může být neaktuální.

## STEP 4 — Načti poslední SESSION

```bash
cd platform && uv run python .starcore/scripts/ledger.py current
# nebo bez uv (pokud venv není synced):
cd platform && python3 .starcore/scripts/ledger.py current
```

Doplňkově: `platform/.starcore/sessions/current.md` (human-readable).

## STEP 5 — Načti PENDING WORK

1. `platform/.starcore/memory/pending_work.md` — platform-scoped úkoly
2. `.claude/registry/SPOS_REGISTRY.md` — SPOS moduly, které zbývá implementovat (SPOS-006, 007, 009 jsou gaps)
3. `.claude/reports/*-IMPLEMENTATION-REPORT.md` — poslední report obsahuje "ČEKÁM NA: ..." s dalším krokem

## STEP 6 — Připrav pracovní kontext

Ověř konzistenci:
- `git status` a `git log --oneline -5`
- Porovnej branch/HEAD s tím, co uvádí `project_state.json` a `.claude/context/DIGITAL_TWIN.md`
- Pokud existuje rozpor → zaznamenej jako riziko, neopravuj tiše

---

## VÝSTUP: STARCORE CONTEXT REPORT

Po dokončení kroků 1-6 shrň (formát dle SES-000 STARCORE PROJECT STATUS bloku):

```
================================================
STARCORE PROJECT STATUS
Aktuální fáze:
Stav:
Dokončeno:
Probíhá:
Blokováno:
Rizika:
Doporučený další krok:
================================================
```

---

## PRAVIDLO PRO BUDOUCÍ SESSIONS

Pokud `platform/.starcore/scripts/startup_protocol.py` bude v budoucnu rozšiřován (SPOS-002+), měl by nativně načítat i `.claude/` soubory (STEP 1-2 výše), aby cold-start protokol nevyžadoval ruční kombinaci dvou systémů. Toto NENÍ implementováno v tomto kroku — vyžadovalo by úpravu otestovaného Python kódu (`startup_protocol.py`, 502 řádků, součást 171 testů) a je mimo scope SPOS-001 (memory, ne session engine — to je SPOS-002).
