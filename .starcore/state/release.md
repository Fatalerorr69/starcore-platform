# Release Readiness State

> Stav release readiness. Aktualizovat po každém Phase 9 nebo ekvivalentní validaci.
> **Poslední aktualizace:** 2026-08-01

## Aktuální stav

**STATUS: RELEASED — v0.2.0**

| Gate | Status | Detail |
|------|--------|--------|
| ruff format | PASS | 0 chyb |
| ruff check | PASS | 0 chyb |
| pyright | PASS | 0 chyb |
| pip-audit | PASS | 0 zranitelností |
| bandit | PASS | žádné HIGH/MEDIUM findings |
| pytest | PASS | 580/580, 100.00% coverage |
| alembic check | PASS | migration head matches models |
| mkdocs build | PASS | --strict, 0 chyb |
| uv lock | PASS | lockfile konzistentní (CI runner regeneruje) |
| GitHub Release | PASS | v0.2.0 vydán 2026-08-01T16:07:45Z |

## Vydání v0.2.0

| Pole | Hodnota |
|------|---------|
| Tag | `v0.2.0` |
| GitHub Release | STARCORE Platform v0.2.0 |
| Vydáno | 2026-08-01T16:07:45Z |
| Workflow | release.yml (workflow_dispatch, run #1, success) |
| Commit (main) | `784f3b3` |
| Tests | 580, 100% coverage |
| Všechna rizika | CLOSED (R-001..R-018) |

## Warnings (neblokující)

| Kód | Popis | Priorita |
|-----|-------|---------|
| KI-001 | docker compose config eager interpolation | COSMETIC |
| KI-002 | pre-commit pyright hook (izolované prostředí) | LIMITACE |
| KI-003 | uv.lock na main má stale version 0.1.0 (budoucí PR přepíše) | COSMETIC |

## Podmínky pro NOT_READY pro příští verzi

- Jakýkoli failing CI gate
- pip-audit s >= 1 vulnerabilitou
- Test coverage < 100%
- Alembic check failure
