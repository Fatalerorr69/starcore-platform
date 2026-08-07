# PROVIDER ROUTER

Standard: SPOS-011 §6 | Aktualizováno: 2026-08-07

Dokumentace existujícího AI provider routing modelu STARCORE. Vychází z auditu `platform/packages/ai/`.

---

## AKTUÁLNÍ MODEL (env-based, statický)

```python
# platform/packages/ai/generator.py — provider selection
# Provider vybrán dle env proměnné STARCORE_AI_PROVIDER
# Aktuálně: statická volba, ne runtime routing
```

```yaml
current_routing_model: STATIC (env var)
env_var: STARCORE_AI_PROVIDER
values:
  - "anthropic" → AnthropicProvider
  - "openai_compat" → OpenAICompatProvider
decision_logic: if/else na env var, žádná runtime intelligence
```

---

## REGISTROVANÉ AI PROVIDERS

### PROVIDER-001 — Anthropic

```yaml
id: PROVIDER-001
name: "Anthropic"
provider_class: "AnthropicProvider (packages/ai/providers/anthropic.py)"
sdk: "anthropic (AsyncAnthropic)"
models:
  - "claude-sonnet-4-6 (aktuální)"
  - "claude-opus-5, claude-sonnet-5, claude-haiku-4-5 (dostupné)"
capabilities:
  - AI blueprint generation
  - Long context (200k tokens)
  - Tool use
  - Vision
status: AKTIVNÍ (kód + API klíč z env)
config:
  api_key: "STARCORE_ANTHROPIC_API_KEY (env)"
  model: "STARCORE_ANTHROPIC_MODEL (env)"
routing_affinity:
  - reasoning: HIGH
  - coding: HIGH
  - planning: HIGH
  - vision: YES
  - offline: NO
  - cost: PAID
```

### PROVIDER-002 — OpenAI-compatible

```yaml
id: PROVIDER-002
name: "OpenAI-compatible"
provider_class: "OpenAICompatProvider (packages/ai/providers/openai_compat.py)"
sdk: "httpx (žádné extra závislosti)"
compatible_backends:
  - "Ollama (local LLM, plánováno v ai-core VM)"
  - "LM Studio"
  - "vLLM"
  - "LocalAI"
  - "OpenRouter"
  - "Groq"
  - "DeepSeek"
  - "Mistral API"
  - "Together AI"
  - "LiteLLM proxy"
  - "OpenAI"
status: AKTIVNÍ (kód) / NEOVĚŘITELNÝ (žádný kompatibilní server neběží)
config:
  base_url: "STARCORE_OPENAI_BASE_URL (env)"
  model: "STARCORE_OPENAI_MODEL (env)"
  api_key: "STARCORE_OPENAI_API_KEY (env, optional)"
  timeout: "120.0s (default)"
routing_affinity:
  - reasoning: MEDIUM
  - coding: MEDIUM
  - offline: YES (Ollama)
  - cost: FREE (local) / PAID (cloud)
```

---

## INFRASTRUCTURE PROVIDERS (provider_sdk)

| Provider | Třída | Status | Poznámka |
|---|---|---|---|
| Docker | `DockerProvider` | OFFLINE (daemon neběží zde) | `providers/docker/provider.py` |
| Proxmox | `ProxmoxProvider` | OFFLINE (chybí credentials) | `providers/proxmox/provider.py` |
| Kubernetes | `KubernetesProvider` | OFFLINE (žádný cluster) | `providers/kubernetes/provider.py` |

---

## PLÁNOVANÝ ROUTING MODEL (SPOS-011 §6)

```yaml
planned_intelligence:
  routing_dimensions:
    - context_size: "Velký kontext → Anthropic (200k)"
    - reasoning: "Složité plánování → Anthropic Opus/Sonnet"
    - coding: "Kód → Sonnet / Claude nebo Qwen-coder (Ollama)"
    - vision: "Obrázky → pouze Anthropic nebo OpenAI"
    - speed: "Real-time → Haiku nebo Groq"
    - cost: "Batch → Ollama local (zdarma)"
    - offline: "Bez internetu → Ollama"
    - tool_support: "Tool use → Anthropic nebo OpenAI"

  implementation_gap:
    "Runtime routing logic neexistuje. Aktuálně: statická env-var volba.
     Pro implementaci by bylo potřeba: router třídu, capability matrix per model,
     fallback logiku při selhání providera."

  estimated_effort: "MEDIUM — 1-2 dny, žádný nový framework"
  prerequisite: "Ollama/vLLM musí být nasazen (ai-core VM, plánováno)"
```

---

## SCAFFOLD SERVICES (docker-compose.yml, neaktivní)

```yaml
# Spustitelné přes: docker compose --profile scaffold up
redis:
  image: redis:8
  port: 6379
  status: PLÁNOVANÝ (profile scaffold)

postgres:
  image: postgres:17
  port: 5432
  status: PLÁNOVANÝ (profile scaffold)

nats:
  image: nats:2.10
  port: 4222
  status: PLÁNOVANÝ (profile scaffold)

# Nezmiňované v docker-compose.yml (dle SPOS-011 specifikace, ale neexistují):
qdrant: NEEXISTUJE (jen zmíněn ve specifikaci)
ollama: NEEXISTUJE v docker-compose (plánován v ai-core VM)
open_webui: NEEXISTUJE
comfyui: NEEXISTUJE
whisper: NEEXISTUJE
piper: NEEXISTUJE
```
