# QC Engines — Protokol a reference

STARCORE Quality Control Engines tvoří tři nástroje pro autonomní kontrolu kvality.
Spouštěj je před každým releasem a po každé větší změně.

## Přehled engines

| Engine | Soubor | Účel |
|--------|--------|------|
| Change Impact Analyzer | `impact_analyzer.py` | Mapování změněných souborů na dopad |
| Regression Sentinel | `regression_sentinel.py` | Detekce regresí oproti baseline |
| Release Readiness Engine | `release_readiness.py` | 12 release gates |
| QC Orchestrátor | `qc_engine.py` | Sjednocený report ze všech engines |

## 1. Change Impact Analyzer

Mapuje `git diff` → modul → kategorii dopadu na základě skutečných důkazů.

```bash
# Analyzovat aktuální uncommitted změny
uv run python .starcore/scripts/impact_analyzer.py analyze

# Analyzovat změny od konkrétního commitu
uv run python .starcore/scripts/impact_analyzer.py analyze --since HEAD~1

# Analyzovat konkrétní soubory
uv run python .starcore/scripts/impact_analyzer.py analyze --files packages/core/main.py

# Zjistit modul a dopad pro soubor
uv run python .starcore/scripts/impact_analyzer.py module packages/orchestrator/timeout.py
```

### Kategorie dopadu

| Kategorie | Příklady modulů |
|-----------|----------------|
| API | core.main, core.config, blueprints.executor |
| CLI | cli.main, blueprints.planner |
| CONFIGURATION | core.config, core.environment |
| SECURITY | core.security |
| DATABASE | core.database, core.models_db, migrations |
| DEPLOYMENT | providers.docker, providers.proxmox, packaging |
| RECOVERY | orchestrator.timeout, provider_sdk.retry |
| CI | ci (workflows) |
| DOCUMENTATION | docs, docs.adr |
| GOVERNANCE | docs.adr, governance (CLAUDE.md) |

### Pravidla

- Nikdy negeneruje spekulativní seznam dopadu
- Používá `grep -rl "from {module}"` pro nalezení skutečných závislostí
- Kategorie API/CLI/DEPLOYMENT/SECURITY/DATABASE → CheckState.WARNING (kritické oblasti)
- Ostatní kategorie → CheckState.PASS

## 2. Regression Sentinel

Porovnává aktuální stav repozitáře s uloženým baseline.

```bash
# Porovnat s baseline (7 dimenzí)
uv run python .starcore/scripts/regression_sentinel.py check

# Aktualizovat baseline (po potvrzeném CI průchodu)
uv run python .starcore/scripts/regression_sentinel.py update

# Zobrazit diff aktuální vs baseline
uv run python .starcore/scripts/regression_sentinel.py diff
```

### Sledované dimenze

| Dimenze | Probe | Regrese |
|---------|-------|---------|
| test_count | `pytest --collect-only -q` | pokles |
| api_routes | `grep @app.` v core/main.py | změna |
| cli_commands | `grep @*.command()` v cli/main.py | změna |
| config_fields | `grep 4-space fields` v config.py | změna |
| adr_count | `glob docs/adr/ADR-*.md` | pokles |
| workflow_count | `glob .github/workflows/*.yml` | pokles |
| lock_sync | `uv lock --check` | nesoulad |

### Baseline umístění

`.starcore/state/regression_baseline.json` — sekce `"sentinel"`:
```json
{
  "sentinel": {
    "test_count": 569,
    "api_routes": 17,
    "cli_commands": 4,
    "config_fields": 21,
    "adr_count": 16,
    "workflow_count": 7,
    "lock_sync": true
  }
}
```

**NIKDY neaktualizuj baseline automaticky** — pouze po ověřeném CI průchodu.

## 3. Release Readiness Engine

Vyhodnocuje 12 release gates.

```bash
# Plná evaluace (spouští pomalé kontroly)
uv run python .starcore/scripts/release_readiness.py evaluate

# Rychlá evaluace (používá baseline)
uv run python .starcore/scripts/release_readiness.py evaluate --quick

# Vyhodnotit jeden gate
uv run python .starcore/scripts/release_readiness.py evaluate --gate SECURITY
uv run python .starcore/scripts/release_readiness.py gate SECURITY
```

### 12 Gates

| Gate | Kontroluje | Poznámka |
|------|-----------|----------|
| BUILD | Dockerfile, docker-compose.yml, Docker build | Docker build → UNKNOWN (CI) |
| TEST | Počet testů, selhání, coverage | Porovnává s baseline |
| SECURITY | pip-audit, bandit, gitleaks | gitleaks → UNKNOWN (CI) |
| DEPENDENCIES | uv.lock sync | Vždy live check |
| PACKAGE | pyproject.toml, alembic migrations | Vždy live check |
| ARTIFACT | dist/ artefakty | NOT_APPLICABLE pokud dist/ prázdné |
| DOCUMENTATION | mkdocs.yml, key docs, mkdocs build | |
| GITHUB | Required workflows, SHA pinning (R-001) | |
| GOVERNANCE | CLAUDE.md sekce, ADR count ≥ 16 | |
| DEPLOYMENT | Dockerfile, docker-compose, env vars | |
| BACKUP | baseline.json, release.md, ledger.yaml | |
| RECOVERY | ADR-016, rollback docs, cold-start | |

### Verdikty

| Verdict | Podmínka |
|---------|----------|
| RELEASE_READY | Žádné FAIL, UNKNOWN, WARNING |
| RELEASE_READY_WITH_WARNINGS | UNKNOWN nebo WARNING přítomno |
| NOT_RELEASE_READY | Alespoň jedno FAIL |
| BLOCKED | Kritický blokér |

**Pravidlo: UNKNOWN ≠ PASS** — UNKNOWN způsobí RELEASE_READY_WITH_WARNINGS, ne RELEASE_READY.

## 4. QC Orchestrátor

Sjednocuje všechny tři engines do jednoho reportu.

```bash
# Spustit Sentinel + Readiness (quick)
uv run python .starcore/scripts/qc_engine.py run --quick

# Spustit vše včetně Impact Analyzer
uv run python .starcore/scripts/qc_engine.py run --impact

# Spustit impact pro konkrétní commit
uv run python .starcore/scripts/qc_engine.py run --impact --since HEAD~3

# Proxy příkazy
uv run python .starcore/scripts/qc_engine.py sentinel
uv run python .starcore/scripts/qc_engine.py readiness --quick
uv run python .starcore/scripts/qc_engine.py impact --since HEAD~1
```

### Výstupní menu

Po každém `run` se zobrazí:
```
VOLBY:
  [1] Release ready — přistoupit k releasu
  [2] Opravit blokery — automatická oprava dostupných problémů
  [3] Zobrazit detail — zobrazit detail jednotlivých gates
  [4] Pokračovat v hardeningu — spustit security/governance audit
  [5] Vlastní instrukce
```

## Aktuální stav (2026-07-27)

Po spuštění na aktuálním repozitáři:

- **Sentinel**: ✓ PASS (7/7 dimenzí bez regrese)
- **Readiness**: ⚠ RELEASE_READY_WITH_WARNINGS
  - BUILD: UNKNOWN (docker build CI only)
  - SECURITY: UNKNOWN (gitleaks CI only)
  - GITHUB: WARNING — R-001: 23 mutable Actions tags (supply-chain riziko)
- **Testy**: 569/569 PASS, coverage 100%

## Testy

```bash
# 68 standalone testů (bez závislostí na packages/)
uv run python .starcore/scripts/tests/test_qc_engines.py
```
