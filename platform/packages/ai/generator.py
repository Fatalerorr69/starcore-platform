"""
AI Blueprint Generator

Selects the configured AI provider and delegates blueprint generation to it.
The public API (generate_blueprint_yaml / BlueprintGenerationError) is unchanged.
"""

from __future__ import annotations

from core.config import Settings, get_settings

# Re-export BlueprintGenerationError and _strip_code_fences so all existing
# importers of `from ai.generator import ...` continue to work unchanged.
from ai.base import AIProvider, BlueprintGenerationError, _strip_code_fences  # noqa: F401

__all__ = ["BlueprintGenerationError", "_strip_code_fences", "generate_blueprint_yaml"]


def _build_provider(settings: Settings) -> AIProvider:
    """Instantiate the AIProvider requested by *settings.ai_provider*."""
    provider_name = settings.ai_provider

    if provider_name == "anthropic":
        from ai.providers.anthropic import AnthropicProvider

        if not settings.anthropic_api_key:
            raise BlueprintGenerationError(
                "AI blueprint generation requires an Anthropic API key. "
                "Set STARCORE_ANTHROPIC_API_KEY in .env (see .env.example)."
            )
        return AnthropicProvider(
            api_key=settings.anthropic_api_key,
            model=settings.anthropic_model,
        )

    if provider_name == "openai-compatible":
        from ai.providers.openai_compat import OpenAICompatProvider

        if not settings.ai_base_url:
            raise BlueprintGenerationError(
                "STARCORE_AI_BASE_URL must be set when using the openai-compatible provider "
                "(e.g. http://localhost:11434/v1 for Ollama)."
            )
        if not settings.ai_model:
            raise BlueprintGenerationError(
                "STARCORE_AI_MODEL must be set when using the openai-compatible provider "
                "(e.g. 'llama3' for Ollama, 'gpt-4o-mini' for OpenAI). There is no default: "
                "falling back to an Anthropic model name would silently send a nonexistent "
                "model to your configured server."
            )
        return OpenAICompatProvider(
            base_url=settings.ai_base_url,
            model=settings.ai_model,
            api_key=settings.ai_api_key,
        )

    raise BlueprintGenerationError(
        f"Unknown AI provider: {settings.ai_provider!r}. "
        "Set STARCORE_AI_PROVIDER to 'anthropic' or 'openai-compatible'."
    )


async def generate_blueprint_yaml(description: str) -> str:
    """Generate a blueprint YAML string from a natural language description.

    Raises BlueprintGenerationError if the configured provider is missing
    required credentials, or if the API call fails.
    """
    settings = get_settings()
    provider = _build_provider(settings)
    return await provider.generate_blueprint_yaml(description)
