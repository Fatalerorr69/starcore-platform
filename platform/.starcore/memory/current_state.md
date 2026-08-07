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
active_document: SPOS-014 — AI Agent Operating System (DOKONČENO)
next_document: SPOS-015+ (ČEKÁ)
branch: claude/starcore-ai-bootstrap-fkyb96
last_governance_commit: "pending — SPOS-014 AAOS"
last_updated: "2026-08-07"
spos_completed: [SPOS-001, SPOS-002, SPOS-003, SPOS-004, SPOS-005, SPOS-006, SPOS-007, SPOS-008, SPOS-009, SPOS-010/011, SPOS-012, SPOS-013, SPOS-014]
integration_health_score: "64% (ČÁSTEČNĚ_ZDRAVÝ)"
automation_health_score: "61% (ČÁSTEČNĚ_ZDRAVÝ)"
aaos_health_score: "38% (KRITICKÝ)"
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
