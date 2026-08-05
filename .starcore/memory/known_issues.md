# Known Issues — STARCORE Platform

> Aktivní známé problémy, workarounds a omezení.
> **Poslední aktualizace:** 2026-07-27

---

## KI-001 — docker compose config eager interpolation

**Stav:** COSMETIC — neblokuje real usage
**Zjištěno:** Phase 9 validation (2026-07-27)
**Popis:** `docker compose config` vyžaduje hodnoty pro všechny proměnné při evaluaci (eager interpolation). Bez nastaveného `STARCORE_DATABASE_URL` (a ostatních) příkaz selže nebo zobrazí `variable not set` warnings.
**Dopad:** Pouze na `docker compose config` příkaz pro introspekci. `docker compose up` funguje správně.
**Workaround:** `env STARCORE_DATABASE_URL=sqlite:///./data/starcore.db docker compose config`

## KI-002 — pre-commit pyright hook (izolované prostředí)

**Stav:** Limitace prostředí, neblokující
**Zjištěno:** Phase 9 validation
**Popis:** `pre-commit`'s isolated pyright hook vytváří vlastní virtualenv a nevidí `uv`-managed deps → false positive errors
**Dopad:** `pre-commit run --all-files` může selhat pro pyright hook
**Workaround:** `uv run pyright` přímo (viz CI gates v CLAUDE.md)

## KI-003 — GitHub Actions SHA pinning chybí (R-001)

**Stav:** OPEN RISK
**Popis:** Viz `memory/risks.md` R-001
**Dopad:** Supply chain riziko v CI

## KI-004 — `timeout.py` není zapojen do runtime (ADR-016)

**Stav:** ZÁMĚRNĚ — deliberate deferral
**Popis:** `execute_with_timeout()` je implementováno a otestováno, ale Scheduler a BlueprintExecutor ho nevyužívají
**Workaround:** Žádný potřebný — dokumentováno v ADR-016
**Revisit podmínky:** Blueprint schema dostane `timeout_seconds` field

## KI-005 — `.claude/instructions.md` vs `CLAUDE.md` překryv

**Stav:** MITIGATED — 2026-08-05
**Popis:** `.claude/instructions.md` označen deprecation bannerem odkazujícím na CLAUDE.md jako autoritativní zdroj.

## KI-006 — `.claude/commands/health.md` chybí bandit a gitleaks kroky

**Stav:** CLOSED — 2026-08-05
**Oprava:** Přidány kroky 9 (`bandit`) a 10 (`regression_sentinel`) do health commandu.
