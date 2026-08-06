# Current State — STARCORE Platform

> Lehký, často aktualizovaný "kde právě jsme" pointer. Na rozdíl od `project_snapshot.md`
> (plná referenční karta, aktualizovaná při strukturálních změnách) je tento soubor
> aktualizován při **každém** významném kroku (SPOS-001 §9).
>
> **Ekosystémový** (root-level, SES/SAKB/SPOS governance) stav je v
> `.claude/context/DIGITAL_TWIN.md` — tento soubor je **platform-scoped** doplněk.

---

## Aktuální fáze

```yaml
governance_layer: SES/SAKB/SPOS bootstrap (probíhá přes .claude/)
active_document: SPOS-001 — Project Memory Engine
branch: claude/starcore-ai-bootstrap-fkyb96
last_governance_commit: "viz .claude/context/DIGITAL_TWIN.md → repository_state"
```

## Platform runtime stav (ke dni poslední aktualizace tohoto souboru)

⚠️ **Známá nekonzistence (zjištěno SPOS-001 audit, 2026-08-06):** `project_snapshot.md` (v0.4.0)
a `state/release.md` (v0.2.0) jsou obě zastaralé vůči aktuální `pyproject.toml` (v0.6.0).
Přesné testovací metriky (počet testů, coverage) proto NELZE přebírat z těchto souborů bez
opětovného spuštění `uv run pytest` — nejsou zde znovu ověřeny nasucho (vyžaduje instalaci
závislostí, mimo scope tohoto governance kroku).

## Odkud pokračovat (cold start)

1. `.claude/context/DIGITAL_TWIN.md` — ekosystémový stav (SES/SAKB/SPOS)
2. `platform/.starcore/memory/project_snapshot.md` — poslední známý platform stav (STALE, viz výše)
3. `platform/.starcore/sessions/current.md` — poslední zaznamenaná session
4. `.claude/registry/SPOS_REGISTRY.md` — stav SPOS-001..010 modulů
5. Tento soubor — rychlý current-state pointer

## Next Action

Viz `.claude/reports/SPOS-001-IMPLEMENTATION-REPORT.md` → doporučený další krok.
