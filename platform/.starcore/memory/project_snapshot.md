# Project Snapshot — STARCORE Platform

> Kanonická referenční karta pro cold-start. Aktualizovat při každé strukturální změně.
> **Poslední aktualizace:** 2026-08-08 (sezení: spos-016-20260808)

## Identita projektu

| Pole | Hodnota |
|------|---------|
| Název | starcore-platform |
| Verze | 0.6.0 |
| Popis | AI-powered infrastructure orchestration for homelabs |
| Licence | Apache-2.0 |
| Python | >=3.12 (vývoj na 3.12.3) |
| Package manager | uv |
| Repo | github.com/Fatalerorr69/starcore-platform |
| Výchozí větev | main |
| Dev větev | claude/starcore-ai-bootstrap-fkyb96 |

## Klíčové metriky (stav 2026-08-07)

| Metrika | Hodnota |
|---------|---------|
| Testy | 796 passed, 0 failed (9 skipped — postgres) |
| Coverage | 100.00% |
| Ruff | 0 chyb |
| Pyright | 0 chyb |
| pip-audit | 0 zranitelností |
| Bandit | čistý |
| mkdocs | --strict PASS |
| ADR záznamy | ADR-001 až ADR-017 |
| Regression sentinel | PASS (baseline: 805 testy, 21 routes, 32 config fields, 17 ADRs) |

## Health Scores (stav 2026-08-08)

| Dimenze | Score | Stav |
|---------|-------|------|
| Integration | 64% | ČÁSTEČNĚ_ZDRAVÝ |
| Automation | 61% | ČÁSTEČNĚ_ZDRAVÝ |
| AAOS (AI) | 38% | KRITICKÝ |
| Architecture Alignment | 93% | ALIGNED |
| Repository Hygiene | 90% | ZDRAVÝ |
| Technical Debt | 1 item | NÍZKÝ |
| Workflow Coverage | 100% (7/7 active) | ZDRAVÝ |
| Security | CI clean (bandit/pip-audit/gitleaks) | DOBRÝ |
| Documentation | 126+ docs, mkdocs PASS | DOBRÝ |
| Intelligence (QC) | 88.2% (4 engines) | DOBRÝ |
| **Overall Project Maturity** | **~60%** | **ČÁSTEČNĚ_ZDRAVÝ** |

## SPOS Governance (stav 2026-08-08)

| Module | Status |
|--------|--------|
| SPOS-001..015 | DOKONČENO |
| SPOS-016 (Consolidation) | DOKONČENO |
| SPOS-017 (CI/CD) | DOKONČENO |
| SPOS-018 (Hygiene) | DOKONČENO |
| SPOS-019 (Restructure) | DOKONČENO |
| SPOS-020 (Code Quality) | DOKONČENO |
| SPOS-021+ | ČEKÁ |

## Architektura (přehled)

```
apps/cli (Typer)           packages/core/main.py (FastAPI)
        \                          /
         v                        v
   packages/blueprints      packages/core
   packages/orchestrator
         |
         v
   packages/provider_sdk    ← port (BaseProvider ABC)
         |
         v
   packages/providers/*     ← adapters (docker, proxmox, kubernetes)
```

**Klíčové moduly:**
- `packages/orchestrator/timeout.py` — TimeoutConfig/Strategy/execute_with_timeout (OPRAVENO R-005; není zapojen do Scheduler/BlueprintExecutor — viz ADR-016)
- `packages/core/security.py` — jediné místo pro redakci secrets
- `packages/core/correlation.py` — ContextVar-based request ID (ADR-015)
- `packages/provider_sdk/retry.py` — RetryConfig / attempt_with_retry
- `packages/blueprints/executor.py` — sekvenční ExecutionPath
- `packages/orchestrator/scheduler.py` — paralelní ExecutionPath s waves

**`depends_on` je success gate (ADR-010):** neúspěšná závislost → `SKIPPED_DEPENDENCY_FAILED`, nesputí se `provider.execute()`.

## Execution paths

- **Sekvenční**: `BlueprintExecutor.execute(blueprint)` — jeden task za druhým
- **Paralelní**: `Scheduler.execute(graph)` — `asyncio.gather` over waves

## API endpoints (přehled)

- Bez autentizace: `GET /`, `GET /health`, `GET /ui/*`
- S `X-API-Key`: vše ostatní (viz CLAUDE.md pro kompletní tabulku)

## Databáze

- SQLite default; SQLAlchemy + Alembic; jedna revize `0001_initial_schema`
- `init_db()` vynucuje fresh/existing schema na startu

## Docker

- Multi-stage build; non-root; healthcheck; `--no-dev`; `--no-sync`

## CI gates (všechny musí projít)

```bash
uv lock --check
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pip-audit
uv run bandit -r packages/ apps/ scripts/ -ll -q
uv run pytest -q --cov --cov-report=term-missing --cov-fail-under=100
uv run alembic upgrade head && uv run alembic check
uv run mkdocs build --strict
```

## Kritická omezení

- **NIKDY** necommitovat secrets ani `.env`
- **NIKDY** force-push bez explicitního schválení
- **NIKDY** přidávat `STARCORE_TASK_TIMEOUT_SECONDS` global timeout — ADR-016 to explicitně zamítlo
- Pluginy nejsou sandboxované — `importlib.import_module()` spouští kód s plnými právy
