# PROVIDER ROUTER V2

Standard: SPOS-014 §6 | Aktualizováno: 2026-08-07

Rozšířená dokumentace Provider Routeru pro AAOS. Navazuje na SPOS-011 `PROVIDER_ROUTER.md`.
Přidává: routing intelligence gap analysis, scaffold services, infra provider detaily.

---

## AKTUÁLNÍ STAV

```yaml
router_version: V1 (statický env-based)
aaos_standard: PROVIDER_ROUTER_V2 (tato dokumentace)
routing_model: STATIC
intelligence: ŽÁDNÁ
runtime_routing: CHYBÍ
```

---

## AI PROVIDER SUBSYSTÉM

### Architektura (živě ověřeno)

```python
# platform/packages/ai/base.py
class AIProvider(ABC):
    @abstractmethod
    async def generate_blueprint_yaml(self, description: str) -> str: ...
    @staticmethod
    def _strip_code_fences(text: str) -> str: ...

class BlueprintGenerationError(Exception): ...

# platform/packages/ai/generator.py
def _build_provider(settings: Settings) -> AIProvider:
    if settings.ai_provider == "anthropic":
        return AnthropicProvider(api_key, model)
    elif settings.ai_provider == "openai-compatible":
        return OpenAICompatProvider(base_url, model, api_key)
    raise ValueError(f"Unknown AI provider: {settings.ai_provider}")

async def generate_blueprint_yaml(description: str, settings=...) -> str:
    provider = _build_provider(settings)
    return await provider.generate_blueprint_yaml(description)
```

### AI Provider Registry (aktuální)

| ID | Provider | Třída | SDK | Status |
|---|---|---|---|---|
| AI-P01 | Anthropic | `AnthropicProvider` | `anthropic` (AsyncAnthropic) | AKTIVNÍ (kód + API klíč z env) |
| AI-P02 | OpenAI-compatible | `OpenAICompatProvider` | `httpx` | AKTIVNÍ (kód) / SERVER OFFLINE |

### AI Provider Konfigurace

```yaml
AI-P01_anthropic:
  env_trigger: "STARCORE_AI_PROVIDER=anthropic"
  api_key: "STARCORE_ANTHROPIC_API_KEY"
  model: "STARCORE_ANTHROPIC_MODEL (default: claude-sonnet-5)"
  max_tokens: 2000
  system_prompt: BLUEPRINT_SYSTEM_PROMPT
  capabilities:
    - blueprint_generation
    - long_context: "200k tokens"
    - tool_use: true
    - vision: true
    - offline: false
    - cost: PAID

AI-P02_openai_compat:
  env_trigger: "STARCORE_AI_PROVIDER=openai-compatible"
  base_url: "STARCORE_AI_BASE_URL (required)"
  model: "STARCORE_AI_MODEL (required)"
  api_key: "STARCORE_AI_API_KEY (optional)"
  timeout: "120.0s"
  compatible_backends:
    active: []
    planned: [Ollama, LM Studio, vLLM, LocalAI, OpenRouter, Groq, DeepSeek]
  capabilities:
    - blueprint_generation
    - offline: true (pokud Ollama local)
    - cost: FREE (local) / PAID (cloud)
```

---

## INFRA PROVIDER SUBSYSTÉM (provider_sdk)

### BaseProvider ABC

```python
# platform/packages/provider_sdk/base.py
class BaseProvider(ABC):
    @abstractmethod
    async def connect(self) -> None: ...
    @abstractmethod
    async def disconnect(self) -> None: ...
    @abstractmethod
    async def health(self) -> dict: ...
    @abstractmethod
    async def list_resources(self) -> list[dict]: ...
    @abstractmethod
    async def execute(self, resource_spec: ResourceSpec) -> dict: ...

    @property
    def _connect_lock(self) -> asyncio.Lock:
        # Lazily created — safe pro concurrent connect() calls
        ...
```

### Infra Provider Registry (aktuální)

| ID | Provider | Třída | Status | Endpoint |
|---|---|---|---|---|
| INFRA-P01 | Docker | `DockerProvider` | OFFLINE (daemon neběží) | Unix socket / TCP |
| INFRA-P02 | Proxmox VE | `ProxmoxProvider` | OFFLINE (credentials chybí) | HTTPS API |
| INFRA-P03 | Kubernetes | `KubernetesProvider` | OFFLINE (žádný cluster) | kubeconfig |

### RetryConfig (provider_sdk/retry.py)

```yaml
retry_config:
  max_attempts: konfigurovatelné
  base_delay: konfigurovatelné
  max_delay: konfigurovatelné
  jitter: volitelné
  retryable_exceptions: konfigurovatelné
  raises: RetryableError (při vyčerpání pokusů)
  note: "Implementováno v provider_sdk ale NENÍ napojeno na AI providers (AI-P01/P02)"
```

---

## SCAFFOLD SERVICES (docker-compose.yml)

Potenciální budoucí provider integrace:

```yaml
scaffold_services:
  redis:
    image: "redis:8"
    port: 6379
    profile: scaffold
    status: PLÁNOVANÝ
    aaos_use: "Cache pro AI responses, session state"

  postgres:
    image: "postgres:17"
    port: 5432
    profile: scaffold
    status: PLÁNOVANÝ
    aaos_use: "Produkční DB (aktuálně SQLite)"

  nats:
    image: "nats:2.10"
    port: 4222
    profile: scaffold
    status: PLÁNOVANÝ
    aaos_use: "Agent message bus (multi-agent koordinace)"
```

---

## ROUTING INTELLIGENCE GAP

```yaml
current_routing:
  model: "Static env-var selection"
  decision_point: "_build_provider(settings) — if/else na settings.ai_provider"
  runtime_intelligence: ŽÁDNÁ

planned_routing_dimensions:
  context_size:
    description: "Velký kontext → Anthropic (200k tokens)"
    current: "NEIMLEMENTOVÁNO"
  reasoning_complexity:
    description: "Složité plánování → Anthropic Opus/Sonnet"
    current: "NEIMPLEMENTOVÁNO"
  cost_optimization:
    description: "Batch workloads → Ollama local (zdarma)"
    current: "NEIMPLEMENTOVÁNO"
  offline_requirement:
    description: "Bez internetu → Ollama"
    current: "NEIMPLEMENTOVÁNO"
  fallback:
    description: "Provider nedostupný → automatický fallback"
    current: "NEIMPLEMENTOVÁNO — BlueprintGenerationError propaguje nahoru"

routing_v2_requirements:
  - "IntelligentRouter třída s capability matrix"
  - "Per-provider health check před každým voláním"
  - "Fallback chain: Anthropic → OpenAI-compat → error"
  - "Cost tracking (token count, odhadovaná cena)"
  - "Offline detection (ping nebo cached status)"
  estimated_effort: "MEDIUM (1-2 dny)"
  prerequisite: "Alespoň jeden OpenAI-compat server nasazen"
```

---

## PROVIDER DISCOVERY ENDPOINT

```yaml
discovery_endpoint:
  path: "GET /providers"
  auth: "X-API-Key required"
  returns: "Seznam registrovaných providers (name, type)"
  provider_health: "GET /providers/{name}/health"
  note: "Discovery je read-only, žádná dynamická registrace přes API"

provider_registration:
  method: "ProviderRegistry.register(name, provider_instance)"
  startup: "register_default_providers() v packages/provider_sdk/registry.py"
  plugins: "context.registry.register() v plugin __init__.py"
  runtime_registration: CHYBÍ (žádné hot-plug providers)
```

---

## POROVNÁNÍ: PROVIDER_ROUTER.md (V1) vs PROVIDER_ROUTER_V2.md

| Oblast | V1 (SPOS-011) | V2 (SPOS-014) |
|---|---|---|
| AI Providers | 2 (Anthropic, OpenAI-compat) | 2 + plánované |
| Infra Providers | 3 (všechny offline) | 3 offline + scaffold services |
| Routing model | Static env | Static + routing gap analysis |
| RetryConfig | Zmíněno | Detailně dokumentováno |
| BaseProvider | Stručně | Kompletní API dokumentace |
| AAOS integrace | Žádná | Plně integrováno do AAOS |
