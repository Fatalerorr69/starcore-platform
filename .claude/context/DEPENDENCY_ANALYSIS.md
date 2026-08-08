# DEPENDENCY ANALYSIS

Standard: SPOS-016 §4 | Aktualizováno: 2026-08-08

Kompletní analýza závislostí celého STARCORE repozitáře.

---

## 1. CORE DEPENDENCIES (platform/pyproject.toml)

### Runtime dependencies (24)

| Balíček | Verze | Použit v | Typ |
|---|---|---|---|
| `fastapi` | >=0.116.0 | core/main.py, routers/ | WEB |
| `uvicorn[standard]` | >=0.35.0 | server runtime | WEB |
| `typer` | >=0.17.0 | apps/cli/main.py | CLI |
| `pydantic` | >=2.11.0 | models, config | CORE |
| `pydantic-settings` | >=2.10.0 | core/config.py | CORE |
| `sqlalchemy` | >=2.0.42 | core/database.py, models_db.py | DB |
| `alembic` | >=1.16.0 | migrations/ | DB |
| `httpx` | >=0.28.1 | ai/providers, tests | HTTP |
| `rich` | >=14.0.0 | CLI output formatting | CLI |
| `loguru` | >=0.7.3 | core/logger.py | LOGGING |
| `pyyaml` | >=6.0.2 | blueprints YAML parsing | CORE |
| `psutil` | >=7.0.0 | **TRANSITIVE ONLY** | ⚠️ |
| `docker` | >=7.2.0 | providers/docker/ | PROVIDER |
| `proxmoxer` | >=2.3.0 | providers/proxmox/ | PROVIDER |
| `anthropic` | >=0.116.0 | ai/anthropic provider | AI |
| `slowapi` | >=0.1.10 | core/main.py rate limiting | SECURITY |
| `prometheus-client` | >=0.21.0 | core/metrics.py | OBSERVABILITY |
| `jinja2` | >=3.1.0 | templating | CORE |
| `opentelemetry-api` | >=1.27.0 | core/tracing.py | OBSERVABILITY |
| `opentelemetry-sdk` | >=1.27.0 | core/tracing.py | OBSERVABILITY |
| `opentelemetry-exporter-otlp-proto-http` | >=1.27.0 | core/tracing.py | OBSERVABILITY |
| `pyjwt` | >=2.8.0 | core/auth.py | AUTH |
| `bcrypt` | >=4.0.0 | core/auth.py | AUTH |
| `kubernetes` | >=36.0.3 | providers/kubernetes/ | PROVIDER |

### Dev dependencies (10)

| Balíček | Účel |
|---|---|
| `pytest` | Test framework |
| `pytest-cov` | Coverage reporting |
| `pytest-asyncio` | Async test support |
| `ruff` | Linting + formatting |
| `pyright` | Type checking |
| `mkdocs` | Documentation build |
| `mkdocs-material` | Docs theme |
| `pip-audit` | Vulnerability scanning |
| `hypothesis` | Property-based testing |
| `psycopg2-binary` | PostgreSQL driver |

### Optional dependencies

| Skupina | Balíček | Účel |
|---|---|---|
| `postgres` | `psycopg2-binary` | PostgreSQL support |

---

## 2. DEPENDENCY FINDINGS

### FINDING-DEP-001: psutil je transitivní závislost

```yaml
severity: LOW
description: "psutil je v pyproject.toml dependencies, ale ŽÁDNÝ soubor v platform/packages/ nebo platform/apps/ ho přímo importuje."
evidence: "grep -r 'import psutil' platform/packages/ platform/apps/ → 0 výsledků"
note: "opentelemetry-sdk ho používá interně pro resource detection. Lze bezpečně odebrat z přímých dependencies."
recommendation: REMOVE_FROM_DIRECT_DEPS
effort: XS
```

### FINDING-DEP-002: requirements.txt v root je redundantní

```yaml
severity: LOW
description: "Root requirements.txt obsahuje jen packaging/setuptools/wheel — tyto jsou build-time dependencies, ne runtime."
evidence: "cat requirements.txt → packaging==26.3, setuptools==83.0.0, wheel==0.47.0"
note: "platform/ používá uv + pyproject.toml. Root requirements.txt není nikde referován."
recommendation: REMOVE
effort: XS
```

### FINDING-DEP-003: Žádné cyklické závislosti

```yaml
severity: NONE
evidence: "pyright 0 errors, pytest 796 passed, dependency graph je DAG"
status: CLEAN
```

---

## 3. DEPENDENCY GRAPH (platform/)

```
apps/cli/ ──────────────────┐
                            v
packages/core/ (FastAPI) ◄──┘
    │
    ├── packages/blueprints/
    │       └── packages/orchestrator/
    │               └── packages/provider_sdk/
    │                       ├── providers/docker/
    │                       ├── providers/proxmox/
    │                       └── providers/kubernetes/
    │
    ├── packages/ai/
    │       ├── anthropic [EXTERNAL]
    │       └── openai-compat [EXTERNAL]
    │
    └── plugins/
            ├── example_provider/
            └── run_logger/
```

**Cykly:** 0
**Maximální hloubka:** 4 (CLI → core → blueprints → orchestrator → provider_sdk)

---

## 4. RUNTIME/BUILD/CI DEPENDENCIES

### CI Dependencies (GitHub Actions)

| Workflow | Lokace | Závislosti | Status |
|---|---|---|---|
| `ci.yml` | `.github/workflows/` | uv, python 3.12 | ACTIVE (autoritativní) |
| `ci.yml` | `platform/.github/workflows/` | uv, python 3.12 | ORPHANED (GitHub nečte) |
| `release.yml` | `.github/workflows/` | uv, python 3.12, cosign | ACTIVE |
| `release.yml` | `platform/.github/workflows/` | uv, python 3.12 | ORPHANED |
| `starcore-security.yml` | `.github/workflows/` | gitleaks | ACTIVE |
| `security-nightly.yml` | `platform/.github/workflows/` | uv, bandit, pip-audit, gitleaks | ORPHANED |
| `codeql.yml` | `platform/.github/workflows/` | CodeQL | ORPHANED |
| `docker-publish.yml` | `platform/.github/workflows/` | Docker, cosign | ORPHANED |
| `dependabot-auto-merge.yml` | `platform/.github/workflows/` | Dependabot | ORPHANED |
| `starcore-integrity.yml` | `.github/workflows/` | python | BROKEN (refs root `core/`) |
| `starcore-release.yml` | `.github/workflows/` | — | LEGACY (just git status) |
| `manual-tag.yml` | both | git tag | OVERLAP |

### Docker Dependencies

| Soubor | Lokace | Status |
|---|---|---|
| `Dockerfile` | `platform/` | ACTIVE |
| `docker-compose.yml` | `platform/` | ACTIVE (postgres, redis, NATS) |

### Build Dependencies

| Nástroj | Účel | Status |
|---|---|---|
| `uv` | Package manager | ACTIVE |
| `hatchling` | Build backend | ACTIVE |
| `python 3.12` | Runtime | ACTIVE |

---

## 5. CROSS-BOUNDARY DEPENDENCIES

### Root → platform/ dependencies

```yaml
count: 0
evidence: "Žádný root-level soubor neimportuje kód z platform/"
note: "Root install skripty generují soubory do ~/STARCORE/, ne do platform/"
```

### platform/ → root dependencies

```yaml
count: 0
evidence: "pythonpath = ['.', 'packages'] — platform/ vidí jen sebe a packages/"
note: "'from core.' v platform/ odkazuje na packages/core/, NE root core/"
```

### Governance (.claude/) → platform/ dependencies

```yaml
count: READ_ONLY
evidence: ".claude/ governance dokumenty REFERUJÍ platform/ stav, ale neimportují kód"
```

---

## 6. NEVYUŽITÉ ZÁVISLOSTI

| Závislost | Typ | Důvod | Doporučení |
|---|---|---|---|
| `psutil` | Direct dep | Pouze transitivní (via opentelemetry) | Odebrat z přímých deps |

---

## 7. CHYBĚJÍCÍ ZÁVISLOSTI

```yaml
count: 0
evidence: "uv sync --extra dev úspěšný, všechny importy resolvují, pyright 0 errors"
```
