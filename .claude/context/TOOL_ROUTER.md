# TOOL ROUTER

Standard: SPOS-011 §7 | Aktualizováno: 2026-08-07

Mapování nástrojů dostupných v STARCORE ekosystému. Stav vychází z živého auditu.

---

## AKTIVNÍ NÁSTROJE (ověřeno v platform/)

### Infrastruktura (provider_sdk)

| Nástroj | Třída | Status | Soubor |
|---|---|---|---|
| Docker | `DockerProvider` | OFFLINE (daemon neběží) | `packages/providers/docker/provider.py` |
| Proxmox VE | `ProxmoxProvider` | OFFLINE (credentials chybí) | `packages/providers/proxmox/provider.py` |
| Kubernetes | `KubernetesProvider` | OFFLINE (žádný cluster) | `packages/providers/kubernetes/provider.py` |

### Databáze

| Nástroj | Status | Poznámka |
|---|---|---|
| SQLite | AKTIVNÍ | `platform/data/starcore.db` (dev) |
| PostgreSQL | PLÁNOVANÝ (scaffold profile) | `docker-compose.yml` |
| Alembic | AKTIVNÍ | `platform/migrations/`, head = 0002 |

### AI Tools

| Nástroj | Status | Poznámka |
|---|---|---|
| Anthropic API | AKTIVNÍ (klíč z env) | `packages/ai/providers/anthropic.py` |
| OpenAI-compat | AKTIVNÍ (kód) / SERVER OFFLINE | `packages/ai/providers/openai_compat.py` |

### FastAPI / REST

| Endpoint | Status |
|---|---|
| `POST /ai/generate-blueprint` | AKTIVNÍ |
| `GET /health` | AKTIVNÍ |
| `GET/POST /providers/*` | AKTIVNÍ |
| `GET/POST /runs/*` | AKTIVNÍ |
| `GET/POST /blueprints/*` | AKTIVNÍ |
| `WebSocket /ws/*` | AKTIVNÍ |

### Platform CLI

| Nástroj | Příkaz | Status |
|---|---|---|
| starcore CLI | `starcore diagnose` | AKTIVNÍ |
| ledger.py | `python ledger.py start/end/list` | AKTIVNÍ |
| registry.py | `python registry.py register/list` | AKTIVNÍ |
| qc_engine.py | `python qc_engine.py run` | AKTIVNÍ |
| impact_analyzer.py | `python impact_analyzer.py analyze` | AKTIVNÍ |
| release_readiness.py | `python release_readiness.py` | AKTIVNÍ |

### Git / GitHub

| Nástroj | Status | Poznámka |
|---|---|---|
| git CLI | AKTIVNÍ | Standardní git operace |
| GitHub Actions | AKTIVNÍ | ci.yml, starcore-security.yml |
| GitHub MCP | AKTIVNÍ (tato session) | mcp__github__* tools |

### Observability

| Nástroj | Status | Poznámka |
|---|---|---|
| event_bus | AKTIVNÍ | `packages/core/events.py` |
| OpenTelemetry | AKTIVNÍ | `packages/core/tracing.py` |
| loguru | AKTIVNÍ | Logging ve všech modulech |

---

## PLÁNOVANÉ NÁSTROJE (neexistují v repozitáři)

| Nástroj | Kategorie | Priorita | Poznámka |
|---|---|---|---|
| Ollama | AI/Local LLM | VYSOKÁ | Plánován v ai-core VM |
| Qdrant | Vector DB / RAG | VYSOKÁ | Chybí v docker-compose |
| Redis | Cache / Queue | STŘEDNÍ | docker-compose scaffold profile |
| NATS | Message Bus | STŘEDNÍ | docker-compose scaffold profile |
| Playwright | Browser Automation | NÍZKÁ | Není v repozitáři |
| Ansible | Infrastructure | NÍZKÁ | `ansible/` adresář zmíněn v docs, neexistuje |
| Terraform | IaC | NÍZKÁ | Není v repozitáři |
| OpenWebUI | AI Frontend | PLÁNOVANÝ | Není v docker-compose |
| Whisper | Speech-to-Text | PLÁNOVANÝ | Není v repozitáři |
| Piper | Text-to-Speech | PLÁNOVANÝ | Není v repozitáři |
| ComfyUI | Image Generation | PLÁNOVANÝ | Není v repozitáři |
| Grafana/Prometheus | Monitoring | PLÁNOVANÝ | Zmíněn v COMPUTE_REGISTRY |

---

## POZNÁMKA KE ROOT ADRESÁŘŮM

```yaml
# Tyto adresáře VYPADAJÍ jako tool implementace, ale jsou Termux stubs:
tools/:            # tools/access, tools/context, tools/control_center ... — bez .py souborů nebo Termux stubs
runtime/:          # runtime/android/ = 100+ Termux adresářů
distributed/:      # 9 .py souborů, všechny ~/STARCORE path
autonomous/:       # 9 .py souborů, všechny ~/STARCORE path

# Pravidlo: žádný nástroj z těchto adresářů není v TOOL_ROUTER — jsou nepoužitelné mimo Termux
```
