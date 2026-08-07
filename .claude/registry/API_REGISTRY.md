# API REGISTRY

Standard: SPOS-012 §9 | Aktualizováno: 2026-08-07

Registr všech API rozhraní STARCORE. Vychází z přímého čtení FastAPI router souborů.

---

## PLATFORM REST API (platform/packages/core/routers/)

Base URL: `http://localhost:8000` (dev) | Auth: `X-API-Key` header

### AUTH ENDPOINTS

| Endpoint | Method | Auth | Purpose | File |
|---|---|---|---|---|
| `/token` | POST | None (login) | Získání JWT tokenu | `routers/auth.py` |
| `/refresh` | POST | JWT | Refresh přístupového tokenu | `routers/auth.py` |
| `/users` | GET | operator+ | Seznam uživatelů | `routers/auth.py` |
| `/users` | POST | admin | Vytvoření uživatele | `routers/auth.py` |

### DIAGNOSTICS ENDPOINTS

| Endpoint | Method | Auth | Purpose | File |
|---|---|---|---|---|
| `/diagnostics` | GET | operator | Systémové diagnostiky | `routers/diagnostics.py` |
| `/metrics` | GET | operator | Prometheus metriky | `routers/diagnostics.py` |
| `/plugins` | GET | operator | Seznam načtených pluginů | `routers/diagnostics.py` |
| `/health` | GET | None (veřejné) | Health check | `packages/core/main.py` |

### PROVIDER ENDPOINTS

| Endpoint | Method | Auth | Purpose | File |
|---|---|---|---|---|
| `/providers` | GET | operator | Seznam registrovaných providers | `routers/providers.py` |
| `/providers/{name}/health` | GET | operator | Health konkrétního providera | `routers/providers.py` |
| `/proxmox/discover` | GET | operator | Proxmox resource discovery | `routers/providers.py` |

### BLUEPRINT ENDPOINTS

| Endpoint | Method | Auth | Purpose | File |
|---|---|---|---|---|
| `/blueprints/plan` | POST | operator | Blueprint → ExecutionPlan (dry run) | `routers/blueprints.py` |
| `/blueprints/run` | POST | operator | Blueprint → Execution (sync) | `routers/blueprints.py` |
| `/blueprints/run/stream` | POST | operator | Blueprint → Execution (SSE stream) | `routers/blueprints.py` |
| `/blueprints/run/ws` | WebSocket | operator | Blueprint → Execution (WebSocket) | `routers/ws.py` |

### AI ENDPOINTS

| Endpoint | Method | Auth | Purpose | File |
|---|---|---|---|---|
| `/ai/generate-blueprint` | POST | operator | NL → Blueprint YAML + validation | `routers/ai.py` |

### RUN HISTORY ENDPOINTS

| Endpoint | Method | Auth | Purpose | File |
|---|---|---|---|---|
| `/runs` | GET | operator | Historie blueprint runů | `routers/runs.py` |
| `/runs/{run_id}` | GET | operator | Detail konkrétního runu | `routers/runs.py` |

---

## CLI API (platform/apps/cli/main.py)

Rozhraní: Typer CLI | Transport: stdout/stderr, exit codes

| Příkaz | Purpose | Závislosti |
|---|---|---|
| `starcore blueprint plan <file>` | Dry run blueprint | MOD-002 |
| `starcore blueprint run <file>` | Spuštění blueprintu | MOD-002, MOD-003, MOD-005..007 |
| `starcore health` | Platform health | MOD-001 REST |
| `starcore doctor` | Diagnostika prostředí | platform/scripts/doctor.py |
| `starcore diagnose` | Provider health check | MOD-004, MOD-005..007 |
| `starcore audit` | Full QC audit | COMP-013 |
| `starcore snapshot` | State snapshot | MOD-001 |
| `starcore resource list` | Resource listing | MOD-004..007 |
| `starcore proxmox discover` | Proxmox resource discovery | MOD-006 |
| `starcore ai generate <desc>` | AI blueprint generation | MOD-007, MOD-008 |

---

## PROVIDER SDK API (programmatic)

```python
# BaseProvider ABC interface
class BaseProvider(ABC):
    name: str
    version: str
    retry_config: RetryConfig

    async def connect(self, config: dict) -> None: ...
    async def disconnect(self) -> None: ...
    async def health(self) -> HealthStatus: ...
    async def list_resources(self) -> list[Resource]: ...
    async def execute(self, action: str, resource: str, payload: dict) -> dict: ...
```

---

## EXTERNAL APIs (konzumované platformou)

| API | Provider | Auth | Status | Použití |
|---|---|---|---|---|
| Anthropic Messages API | Anthropic | `STARCORE_ANTHROPIC_API_KEY` env | AKTIVNÍ (klíč z env) | Blueprint generation |
| OpenAI Chat Completions | OpenAI-compat server | `STARCORE_OPENAI_API_KEY` env (optional) | SERVER OFFLINE | Blueprint generation (Ollama/vLLM/etc.) |
| Proxmox VE REST API | Proxmox | `STARCORE_PROXMOX_*` env | OFFLINE (chybí credentials) | VM/LXC management |
| Docker Engine API | Docker daemon | Unix socket | OFFLINE (daemon neběží) | Container management |
| GitHub REST API v3 | GitHub | `GITHUB_TOKEN` (CI) | AKTIVNÍ (CI kontext) | GitHub Actions |
| GitHub MCP | GitHub | OAuth (Claude session) | AKTIVNÍ (tato session) | Code review, PR management |

---

## STATISTIKY

```yaml
rest_endpoints_total: 17
websocket_endpoints: 1
cli_commands: 10+
provider_sdk_methods: 5 (abstract)
external_apis_consumed: 6
external_apis_online: 2 (Anthropic klíč z env, GitHub CI)
external_apis_offline: 4 (OpenAI-compat server, Proxmox, Docker daemon)
```
