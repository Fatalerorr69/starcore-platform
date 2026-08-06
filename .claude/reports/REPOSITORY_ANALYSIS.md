# REPOSITORY ANALYSIS

Datum: 2026-08-06 | Branch: `claude/starcore-ai-bootstrap-fkyb96`

---

## REPOSITORY MAP

```
starcore-platform/
├── .claude/                    ← NOVÉ (Bootstrap 00 výstup)
│   ├── context/
│   ├── prompts/
│   ├── reports/
│   ├── decisions/
│   ├── roadmap/
│   ├── registry/
│   └── sessions/
│
├── platform/                   ← HLAVNÍ PYTHON PLATFORMA (v0.6.0)
│   ├── apps/
│   │   └── cli/                ← Typer CLI entrypoint
│   ├── packages/
│   │   ├── ai/                 ← AI Provider abstrakce
│   │   ├── blueprints/         ← Blueprint engine (YAML → plan → execute)
│   │   ├── core/               ← FastAPI, config, DB, events, plugins
│   │   ├── orchestrator/       ← Task, TaskGraph, Scheduler
│   │   ├── provider_sdk/       ← BaseProvider ABC, ProviderRegistry
│   │   └── providers/          ← Docker, Proxmox implementace
│   ├── tests/                  ← 601 testů (pytest, hypothesis)
│   ├── docs/                   ← MkDocs dokumentace
│   │   ├── adr/                ← 17 Architecture Decision Records
│   │   ├── ses/                ← Long-term vision docs
│   │   └── architecture/
│   ├── migrations/             ← Alembic (SQLite schéma)
│   ├── pyproject.toml          ← Závislosti, verze, build config
│   ├── Makefile
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── reports/                ← Historické audit reporty
│
├── agents/                     ← Agent framework
│   ├── kernel/
│   ├── missions/
│   └── planner/
│
├── runtime/                    ← Rozsáhlý runtime stav (JSON registry)
│   ├── agents/
│   ├── ai_core/
│   ├── autonomous/
│   ├── control_plane/
│   ├── distributed/
│   ├── engineering/
│   ├── knowledge/
│   ├── generated/
│   └── ... (39 adresářů celkem)
│
├── security/                   ← Bezpečnostní vrstva
│   ├── core/
│   ├── rag/
│   └── audit/
│
├── knowledge/                  ← Knowledge base
│   ├── core/
│   └── rag/
│
├── intelligence/               ← Intelligence layer
│
├── control_center/             ← Control centrum
│
├── ai_core/                    ← AI core infrastruktura
│
├── automation/                 ← Automation framework
│
├── config/                     ← Konfigurace
│
├── tools/                      ← Nástroje
│
├── bin/                        ← Binárky / CLI nástroje
│
├── prompts/                    ← Prompt management
│
├── sessions/                   ← Session management
│
├── backups/                    ← Zálohy
│
├── install_6BX*.sh             ← Generace 6 (consolidátor, foundation)
├── install_6BY*.sh             ← Generace 6Y (distributed AI, memory)
├── install_7_0_*.sh            ← Generace 7.0 (platform, hardening)
├── install_7_1_*.sh            ← Generace 7.1 (autonomous core)
├── install_7_2_*.sh            ← Generace 7.2 (distributed intelligence)
├── install_8A-8J_*.sh          ← Generace 8 (AI core, agents, security)
├── install_8_FINAL_*.sh        ← Generace 8 finální skripty
├── install_STARCORE_*.sh       ← STARCORE specifické skripty
├── install_TERMUX_*.sh         ← Termux/Android skripty
│
├── config.yaml                 ← Root config (project metadata)
├── requirements.txt            ← Root Python deps (minimal)
├── starcore                    ← Root CLI wrapper
├── .gitignore
└── SECURITY.md
```

---

## TECHNOLOGY AUDIT

| Kategorie | Technologie | Stav |
|---|---|---|
| Jazyk | Python 3.12+ | Produkční |
| Web framework | FastAPI 0.116+ | Aktivní |
| CLI | Typer 0.17+ | Aktivní |
| Validace | Pydantic v2 | Aktivní |
| DB | SQLite + SQLAlchemy 2 + Alembic | Aktivní |
| AI Providers | Anthropic SDK, OpenAI-compatible | Aktivní |
| Infrastructure | Proxmoxer, docker-py | Aktivní |
| Observability | Prometheus, Loguru, OpenTelemetry | Aktivní |
| Security | PyJWT, bcrypt, Bandit, gitleaks | Aktivní |
| Testy | pytest, hypothesis, ruff, pyright | Aktivní |
| Build | uv, hatchling | Aktivní |
| Docs | MkDocs Material | Aktivní |
| Node.js | v22.22.2 | Dostupný (nižší priorita) |

---

## DEPENDENCY AUDIT

### Platform (pyproject.toml) — klíčové závislosti

```
fastapi>=0.116.0          ← HTTP API
uvicorn[standard]>=0.35.0 ← ASGI server
typer>=0.17.0             ← CLI
pydantic>=2.11.0          ← Validace
sqlalchemy>=2.0.42        ← ORM
alembic>=1.16.0           ← Migrace
httpx>=0.28.1             ← HTTP klient
docker>=7.2.0             ← Docker provider
proxmoxer>=2.3.0          ← Proxmox provider
anthropic>=0.116.0        ← Claude AI
prometheus-client>=0.21.0 ← Metriky
opentelemetry-*           ← Tracing
kubernetes>=36.0.3        ← K8s (budoucí)
```

### Root (requirements.txt) — minimální

```
packaging, setuptools, wheel  ← Build nástroje pouze
```

---

## INSTALL SCRIPTS INVENTURA

| Série | Počet | Popis |
|---|---|---|
| `install_6BX*.sh` | 6 | Generace 6: consolidátor, foundation |
| `install_6BY*.sh` (6BYY) | 13 | Generace 6Y: distributed AI, memory, security |
| `install_7_0_*.sh` | 9 | Generace 7.0: platform, hardening, production |
| `install_7_1_*.sh` | 1 | Generace 7.1: autonomous core |
| `install_7_2_*.sh` | 1 | Generace 7.2: distributed intelligence |
| `install_8A-8J_*.sh` | 10 | Generace 8: AI core, agents, knowledge, security |
| `install_8_*.sh` | 3 | Generace 8 finální (audit, backup, snapshot) |
| `install_STARCORE_*.sh` | 8 | STARCORE specifické moduly |
| `install_TERMUX_*.sh` | 10 | Android/Termux prostředí |
| `generate_7x_bulk_packages.sh` | 1 | Bulk package generátor |
| `preflight_*.sh` | 1 | Pre-flight audit |
| `repair_*.sh` | 1 | Repair skript |
| **CELKEM** | **~64** | |

**PROBLÉM:** Neexistuje centrální registr stavů — není jasné, které skripty byly spuštěny, v jakém pořadí, a s jakým výsledkem.
