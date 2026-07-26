# Sprint 012 — CLAUDE.md/README Catch-Up & ADR-007 AI Provider Abstraction

**Date:** 2026-07-25
**Branch:** `claude/new-session-p84x62` → merged as PR #81
**Mode:** MODE 5 — CONTROLLED AUTONOMY

## Changes

### A01 — CLAUDE.md brought current with actual CI and architecture
- Ruff rule set updated: `E, F, I, UP` → `E, F, I, UP, B, PERF, N, FAST`
  (rules added in sprint-007 but never reflected here).
- CI Gates section expanded to list Bandit SAST, gitleaks, `alembic check`,
  and `--cov-fail-under=100` (previously only 5 basic gates).
- `packages/ai` description rewritten for the pluggable `AIProvider`
  abstraction introduced in PR #79, instead of "Calls the Anthropic API".
- Config section: added `STARCORE_AI_PROVIDER` / `AI_BASE_URL` / `AI_API_KEY`
  / `LOG_JSON` to the key variables list.
- Commands section: added `starcore doctor`/`audit`, noted `--json`/`--quiet`
  scripting flags added in PR #78.

### B01 — README.md
- Test count corrected: 361 → 407.
- New Security row documenting Bandit + gitleaks + pip-audit.
- AI Blueprint Generation row rewritten for pluggable provider support.

### C01 — docs/adr/ADR-007-ai-provider-abstraction.md
Documents the `AIProvider` abstract base + Anthropic/OpenAI-compatible
provider split introduced in PR #79 — context, decision, trade-offs, and
alternatives considered (LangChain/LiteLLM, Anthropic-only). `mkdocs.yml`
nav updated to include it.

## Test counts
| Before | After |
|--------|-------|
| 407 passed | 407 passed |
| 0 warnings | 0 warnings |
| 100% coverage | 100% coverage |
