# TECHNOLOGY PROFILE — Ollama

```yaml
name: Ollama
purpose: Lokální LLM inference server — cílová AI komponenta pro Docker AI Stack
category: AI / LLM Inference
version: latest
official_source: SRC-OLLAMA-001
status: PLÁNOVÁNO (dosud nenasazeno)
```

## DEPENDENCIES
Docker (nebo bare-metal binary), GPU driver (volitelné, pro akceleraci), dostatek RAM/VRAM dle modelu.

## COMPATIBILITY
Poskytuje OpenAI-compatible `/v1/chat/completions` endpoint — přímo kompatibilní se STARCORE `AIProvider` abstrakcí (`STARCORE_AI_PROVIDER=openai-compatible`).

## INSTALLATION
Plánováno jako Docker kontejner v `docker/ai-stack/docker-compose.yml` (image `ollama/ollama`).

## CONFIGURATION
`STARCORE_AI_BASE_URL` směřuje na Ollama endpoint (výchozí port 11434), `STARCORE_AI_MODEL` volí konkrétní model.

## SECURITY
Ollama endpoint by neměl být exponován mimo interní síť bez autentizace (Ollama sám o sobě nemá built-in auth).

## AUTOMATION
Model pull přes `ollama pull <model>`; lze automatizovat v Ansible playbooku nebo docker-compose init kontejneru.

## INTEGRATION
STARCORE AI Provider abstrakce (`platform/packages/ai`, ADR-007) — Ollama je jedna z podporovaných OpenAI-compatible backendů vedle vLLM, LM Studio, LocalAI.

## STARCORE_USAGE
Plánováno pro: AI Blueprint Generation bez závislosti na cloud API (offline/homelab scénář), embedding pro Qdrant RAG (nomic-embed-text).

## RISKS
- Vyžaduje significant RAM/VRAM na AI Core VM
- Bez GPU passthrough na Proxmox bude inference pomalá (CPU-only)

## UPDATE_POLICY
Review při přidání do `docker/ai-stack/` (MOD-100/MOD-101, viz MODULE_REGISTRY).
```
