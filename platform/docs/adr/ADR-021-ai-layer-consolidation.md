# ADR-021 — AI Layer Consolidation

- **Status:** Accepted
- **Date:** 2026-08-06
- **Implements:** GADR-005 (STARCORE Architecture Governance Report)
- **Relates to:** ADR-007 (Pluggable AI Provider Abstraction)

## Context

The discovery audit found AI-related code duplicated across the
repository: `platform/packages/ai/` is a tested, ADR-007-governed
`AIProvider` abstraction supporting both an Anthropic backend and any
OpenAI-compatible endpoint (which already covers Ollama, LM Studio, vLLM,
and LocalAI). In parallel, the legacy root layer contains `ai_core/`,
`ai_runtime/`, and connector stubs such as
`autonomous/connectors/ollama_connector.py` — each a small script whose
entire function is writing a static "status: ready" JSON file, with no
inference logic, no tests, and no relationship to `packages/ai/`.

Without a consolidation decision, a future session could reasonably (but
incorrectly) treat the root `ai_core/`/`ai_runtime/` trees as a second,
lower-level AI system to build on, duplicating ADR-007's work.

## Options

1. **Maintain both** — treat root AI modules as a distinct concern from
   `packages/ai/`.
2. **Consolidate on `packages/ai/`** — declare it the sole AI integration
   point; root AI modules are legacy (covered by ADR-020's freeze) with no
   migration path, since they contain no functionality to migrate.
3. **Merge root AI modules into `packages/ai/`** as new provider
   implementations.

## Decision

**Option 2.** `platform/packages/ai/`'s `AIProvider` abstraction (ADR-007)
is the sole AI integration point for STARCORE. `ai_core/`, `ai_runtime/`,
and root-level AI/LLM connector stubs are legacy content under ADR-020's
freeze; they are not migrated because inspection confirmed they contain no
functional logic to preserve (each file's entire body is a fixed-value JSON
write).

## Consequences

- Any future AI capability (a new provider, RAG support, multi-step agent
  orchestration) is added as a new implementation of `AIProvider` inside
  `packages/ai/`, per ADR-019's extension policy — not as a new root
  module.
- Local-inference use cases (the apparent motivation behind
  `ollama_connector.py`) are already served today via
  `STARCORE_AI_PROVIDER=openai-compatible` pointed at an Ollama endpoint —
  no new code is required to close that gap.
- No data or behavior migration occurs, because there is nothing functional
  in the root AI modules to carry forward.

## Alternatives rejected

**Option 1** was rejected because maintaining two parallel "AI layers" —
one real, one cosmetic — is precisely the confusion ADR-018 exists to
eliminate.

**Option 3** was rejected because there is no logic in the root AI modules
worth merging; they do not call any inference API, model, or SDK. Treating
them as source material for new provider implementations would mean
writing that implementation from scratch under a "merge" label — which is
just Option 2 with extra ceremony.
