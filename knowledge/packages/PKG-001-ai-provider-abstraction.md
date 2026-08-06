# KNOWLEDGE PACKAGE — PKG-001

```yaml
package_id: PKG-001
title: STARCORE AI Provider Abstraction
category: AI / Architecture
sources: [SRC-ANTHROPIC-001, SRC-OLLAMA-001, SRC-STARCORE-INTERNAL-001]
last_update: 2026-08-06
```

## SUMMARY

STARCORE Platform odděluje AI funkcionalitu (blueprint generace z přirozeného jazyka) od konkrétního LLM poskytovatele pomocí `AIProvider` abstraktní třídy (ADR-007). To umožňuje přepínat mezi cloud API (Anthropic Claude) a self-hosted/lokálními modely (Ollama, vLLM, LM Studio, LocalAI) přes jednotné OpenAI-compatible rozhraní, aniž by se měnila zbylá aplikační logika.

## TECHNICAL_DETAILS

- Konfigurace přes `STARCORE_AI_PROVIDER` (`anthropic` | `openai-compatible`)
- Anthropic cesta: `STARCORE_ANTHROPIC_API_KEY`
- OpenAI-compatible cesta: `STARCORE_AI_BASE_URL` + `STARCORE_AI_MODEL`
- Vstup: přirozený jazyk (text)
- Výstup: validovaná blueprint YAML (Pydantic model validace před vrácením)
- Exponováno přes `POST /ai/generate-blueprint` a `starcore ai generate "<description>"`

## IMPLEMENTATION_GUIDE

1. Implementovat `AIProvider` ABC v `platform/packages/ai`
2. Registrovat provider dle env konfigurace při startu aplikace
3. Provider translatuje text → blueprint YAML → validace přes Pydantic model Blueprint Engine
4. Chyby (neplatný YAML, API nedostupné) propagovat jako HTTP 4xx/5xx s jasnou zprávou

## RISKS

- Cloud provider (Anthropic) = závislost na internetu a nákladech
- Self-hosted provider (Ollama) = závislost na dostatečném hardware (RAM/VRAM)
- Generovaný blueprint musí projít stejnou validací jako ručně psaný — nedůvěřovat AI výstupu bez validace

## RELATED_COMPONENTS

- MOD-007 (AI Provider) — MODULE_REGISTRY
- MOD-002 (Blueprint Engine) — konzument generovaného výstupu
- ADR-007 (AI provider abstraction)
- Technology Profiles: `anthropic-claude.md`, `ollama.md`
```
