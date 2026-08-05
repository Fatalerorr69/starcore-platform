# Working Decisions — STARCORE Platform

> Pracovní rozhodnutí, která ještě nemají formální ADR nebo jsou interní pro agenta.
> Formalizovaná rozhodnutí jsou v `docs/adr/`.
> **Poslední aktualizace:** 2026-07-27

---

## D-001 — Použít `asyncio.create_task + asyncio.shield` pro WAIT_AND_MARK/IGNORE

**Datum:** 2026-07-27
**Kontext:** R-005 bugfix v `orchestrator/timeout.py`
**Rozhodnutí:** WAIT_AND_MARK a IGNORE strategie wrappují coroutine do `asyncio.create_task()` a then `asyncio.shield()` pro `asyncio.wait_for`. CANCEL strategie zůstává na přímém `asyncio.wait_for(coro, ...)` bez create_task — coroutine je spent po prvním TimeoutError a není třeba ji reuse.
**Důvod:** Původní kód re-awaited spent coroutine → RuntimeError. `create_task` vytvoří reálný Task; `shield` chrání před cancellation první wait_for.
**Alternativy odmítnuty:**
- `asyncio.ensure_future()` — deprecated v 3.10+
- Wrapping do nové coroutine funkce — zbytečná složitost
**Formalizováno:** ADR-016 (sekce "Defect fixed")

## D-002 — Testy pro timeout: real async timing, ne monkeypatching

**Datum:** 2026-07-27
**Kontext:** Přepsání `tests/test_timeout.py` jako součást R-005 fixu
**Rozhodnutí:** Všechny testy pro timeout strategie používají skutečné async timings (malá čísla: 0.01s, 0.05s, 0.1s, 0.12s). Monkeypatching `asyncio.wait_for` bylo odstraněno.
**Důvod:** Monkeypatched testy neověřovaly skutečný coroutine lifecycle — skryly původní bug. Real timing testy jsou pomalejší (cca +0.5s) ale ověřují skutečné chování.

## D-003 — `.starcore/` je versionován v repozitáři

**Datum:** 2026-07-27
**Rozhodnutí:** `.starcore/` adresář je commitnut do repozitáře (ne v `.gitignore`).
**Důvod:** Cross-session state musí být persistentní mezi různými Claude Code instancemi. Souborový systém kontejnerů je ephemeral — bez git by se state ztratil.
**Výjimka:** `.starcore/` nesmí nikdy obsahovat secrets, credentials, nebo API klíče.

## D-004 — `sessions/archive/` jako plain Markdown soubory

**Datum:** 2026-07-27
**Rozhodnutí:** Archivovaná sezení jsou uložena jako `sessions/archive/YYYY-MM-DD-<slug>.md`. Žádná databáze, žádný JSON, žádné binárky.
**Důvod:** Human-readable, versionable, diffovatelné v git.

## D-005 — `state/regression_baseline.json` aktualizovat manuálně (ne automaticky)

**Datum:** 2026-07-27
**Rozhodnutí:** Baseline se neaktualizuje automaticky při každém testu — agent jej aktualizuje vědomě po ověření, že nový stav je správný.
**Důvod:** Automatická aktualizace by mohla zamaskovat regresi (baseline by se posunul na nižší stav).

## D-006 — Prompt registry jako YAML (ne JSON)

**Datum:** 2026-07-27
**Rozhodnutí:** `prompts/registry.yaml` používá YAML formát.
**Důvod:** YAML je čitelnější pro humans; multi-line strings jsou přirozenější než JSON.
