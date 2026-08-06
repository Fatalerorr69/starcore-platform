# TECHNOLOGY PROFILE — Anthropic Claude

```yaml
name: Anthropic Claude
purpose: Cloud LLM provider — AI Blueprint Generation + AI Engineering Agent operátor (toto prostředí)
category: AI / LLM Provider
version: "claude-sonnet-4-6 / claude-sonnet-5 (aktuální session)"
official_source: SRC-ANTHROPIC-001
status: AKTIVNÍ
```

## DEPENDENCIES
`anthropic` Python SDK (`>=0.116.0`), platný API klíč (`STARCORE_ANTHROPIC_API_KEY`).

## COMPATIBILITY
Nativní STARCORE AI Provider implementace (ne přes OpenAI-compatible vrstvu) — `platform/packages/ai`.

## INSTALLATION
`uv sync` instaluje `anthropic` SDK jako součást `platform/pyproject.toml` dependencies.

## CONFIGURATION
`.env`: `STARCORE_ANTHROPIC_API_KEY`. Volitelné — pokud chybí, AI blueprint generation endpoint vrací chybu, zbytek platformy funguje beze změny.

## SECURITY
API klíč NIKDY necommitovat (viz SES-000 P007, SES-001 §15). `.gitignore` vylučuje `.env`.

## AUTOMATION
`starcore ai generate "<description>"` CLI příkaz, `POST /ai/generate-blueprint` API endpoint.

## INTEGRATION
- `platform/packages/ai` — AIProvider ABC implementace (ADR-007)
- Toto Claude Code prostředí — Claude Sonnet jako AI Engineering Agent operátor projektu (viz AI_REGISTRY)

## STARCORE_USAGE
1. Runtime AI Provider pro blueprint generaci z přirozeného jazyka
2. Meta-úroveň: Claude Code jako hlavní AI architekt vykonávající SES/SAKB/SPOS framework

## RISKS
- Cloud dependency — vyžaduje internetové připojení a platný API klíč
- Náklady na API volání (token-based pricing)

## UPDATE_POLICY
Sledovat nové Claude modely (Sonnet 5, Opus 5) — aktualizovat `STARCORE_AI_MODEL` doporučení a AI_REGISTRY při release.
```
