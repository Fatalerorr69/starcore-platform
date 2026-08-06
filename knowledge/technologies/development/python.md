# TECHNOLOGY PROFILE — Python

```yaml
name: Python
purpose: Primární implementační jazyk STARCORE Platform
category: Development / Language
version: "3.11.15 (prostředí) / >=3.12 (platform requires)"
official_source: SRC-PYTHON-001
```

## DEPENDENCIES
Žádné (jazyk samotný). Platform závislosti: viz `platform/pyproject.toml` (fastapi, pydantic, sqlalchemy, ...).

## COMPATIBILITY
⚠️ **ZJIŠTĚNÝ NESOULAD:** Aktuální prostředí má Python 3.11.15, ale `platform/pyproject.toml` vyžaduje `requires-python = ">=3.12"`. `uv sync` si stáhne vlastní 3.12 interpreter (uv spravuje verze nezávisle na systémovém Pythonu) — nejde o blokující problém, ale je to zaznamenaná odchylka.

## INSTALLATION
Systémový Python 3.11.15 přítomen. Platform používá `uv` (viz TECHNOLOGY_REGISTRY) pro správu izolovaného 3.12+ prostředí.

## CONFIGURATION
`pyproject.toml` (hatchling build backend), `ruff.toml` (lint), `pyrightconfig.json` (type checking).

## SECURITY
Bandit SAST na `packages/`, `apps/`, `scripts/`. pip-audit pro CVE v závislostech.

## AUTOMATION
Veškerá STARCORE Platform logika, CLI (Typer), testy (pytest).

## INTEGRATION
Jádro celé `platform/` vrstvy — FastAPI, SQLAlchemy, Pydantic, provider SDK.

## STARCORE_USAGE
100 % implementace `platform/packages/*` a `platform/apps/cli`.

## RISKS
Verzový nesoulad (3.11 systém vs 3.12+ požadavek) — mitigováno přes `uv`, ale je třeba ověřit při každém CI běhu v novém prostředí.

## UPDATE_POLICY
Sledovat `requires-python` v `pyproject.toml`; review při Python EOL cyklech (Python 3.11 EOL ~2027).
```
