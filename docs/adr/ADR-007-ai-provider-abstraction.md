# ADR-007 — Pluggable AI Provider Abstraction

**Date:** 2026-07-25
**Status:** Accepted
**Deciders:** Core team

---

## Context

`starcore ai generate` / `POST /ai/generate-blueprint` originally called the
Anthropic Messages API directly from `packages/ai/generator.py`. This tied
blueprint generation to a single vendor and required a paid, internet-reachable
API key even for homelab users who already run a local LLM (Ollama, LM Studio,
vLLM, LocalAI) and would rather not send infrastructure descriptions to a
third-party service.

## Decision

Introduce an abstract base class, `AIProvider` (`packages/ai/base.py`), with a
single async method:

```python
class AIProvider(ABC):
    @abstractmethod
    async def generate_blueprint_yaml(self, description: str) -> str: ...
```

Two concrete implementations live in `packages/ai/providers/`:

- **`AnthropicProvider`** — wraps the Anthropic Messages API. Requires
  `STARCORE_ANTHROPIC_API_KEY`.
- **`OpenAICompatProvider`** — POSTs to any `/v1/chat/completions` endpoint
  using `httpx` (already a project dependency, no new package required).
  Configured via `STARCORE_AI_BASE_URL` (e.g. `http://localhost:11434/v1` for
  Ollama) and an optional `STARCORE_AI_API_KEY`.

`STARCORE_AI_PROVIDER` (`anthropic` default, or `openai-compatible`) selects
which implementation `packages/ai/generator.py`'s `_build_provider()` factory
instantiates. The public API — `generate_blueprint_yaml(description)` and
`BlueprintGenerationError` — is unchanged, so every existing caller (CLI,
FastAPI endpoint, tests) required no changes beyond the new settings fields.

Shared behavior — markdown code-fence stripping that models sometimes emit
despite instructions — lives once in `AIProvider._strip_fences` rather than
being duplicated per provider.

## Consequences

**Positive**
- Homelab users can point at a local model with zero external API cost and
  no data leaving their network.
- Adding a third provider (e.g. Google Gemini) means one new file implementing
  `AIProvider`, plus a branch in `_build_provider()` — no changes to the CLI,
  the API endpoint, or existing tests.
- `generate_blueprint_yaml` callers remain provider-agnostic by construction;
  there is no code path that imports a concrete provider directly.

**Negative / Trade-offs**
- Two code paths to keep behaviorally consistent (error message wording,
  timeout handling, response parsing) instead of one.
- `STARCORE_AI_PROVIDER` is a plain string field validated only at first use
  (inside `_build_provider`), not at settings-load time — an invalid value is
  caught only when generation is actually attempted.

## Alternatives considered

- **LangChain / LiteLLM as a provider-abstraction layer**: would have handled
  multi-provider dispatch for us, but pulls in a large dependency tree for a
  single call (`generate_blueprint_yaml`) with a narrow, stable contract.
  Rejected as disproportionate to the actual integration surface.
- **Keep Anthropic-only, document a workaround**: rejected — local-LLM support
  is a frequently requested homelab use case and the abstraction cost was low
  given the narrow existing interface.
