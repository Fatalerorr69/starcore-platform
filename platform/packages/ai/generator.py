"""
AI Blueprint Generator

Selects the configured AI provider and delegates blueprint generation to it.
The public API (generate_blueprint_yaml / BlueprintGenerationError) is unchanged.
"""

from __future__ import annotations

import logging

from core.config import Settings, get_settings
from provider_sdk.retry import RetryConfig

# Re-export BlueprintGenerationError and _strip_code_fences so all existing
# importers of `from ai.generator import ...` continue to work unchanged.
from ai.base import AIProvider, BlueprintGenerationError, _strip_code_fences  # noqa: F401

__all__ = ["BlueprintGenerationError", "_strip_code_fences", "generate_blueprint_yaml"]

logger = logging.getLogger(__name__)


def _build_retry_config(settings: Settings) -> RetryConfig:
    """Build a RetryConfig from the AI retry settings."""
    return RetryConfig(max_retries=settings.ai_max_retries)


def _build_provider(settings: Settings) -> AIProvider:
    """Instantiate the AIProvider requested by *settings.ai_provider*."""
    return _build_provider_by_name(settings.ai_provider, settings)


def _build_provider_by_name(provider_name: str, settings: Settings) -> AIProvider:
    """Instantiate an AIProvider by name."""
    retry = _build_retry_config(settings)

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
            max_tokens=settings.ai_max_tokens,
            timeout=settings.ai_timeout,
            retry_config=retry,
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
            max_tokens=settings.ai_max_tokens,
            timeout=settings.ai_timeout,
            retry_config=retry,
        )

    raise BlueprintGenerationError(
        f"Unknown AI provider: {provider_name!r}. "
        "Set STARCORE_AI_PROVIDER to 'anthropic' or 'openai-compatible'."
    )


def _validate_blueprint_yaml(yaml_text: str) -> str | None:
    """Validate AI-generated YAML against the Blueprint model.

    Returns None on success, or an error message on failure.
    """
    try:
        from blueprints.loader import BlueprintLoader

        BlueprintLoader.load_from_string(yaml_text)
        return None
    except Exception as exc:
        return str(exc)


async def generate_blueprint_yaml(description: str) -> str:
    """Generate a blueprint YAML string from a natural language description.

    Raises BlueprintGenerationError if the configured provider is missing
    required credentials, or if the API call fails.
    """
    import time

    from core.events import event_bus

    settings = get_settings()
    provider = _build_provider(settings)
    provider_name = settings.ai_provider
    start = time.monotonic()
    try:
        result = await provider.generate_blueprint_yaml(description)
    except Exception as primary_exc:
        duration = time.monotonic() - start
        await event_bus.emit(
            "ai.request.completed",
            {"provider": provider_name, "status": "error", "duration_seconds": duration},
        )
        if settings.ai_fallback_provider:
            result = await _attempt_fallback(settings, description, primary_exc, event_bus)
        else:
            raise
    else:
        duration = time.monotonic() - start
        event_payload: dict[str, object] = {
            "provider": provider_name,
            "status": "success",
            "duration_seconds": duration,
        }
        usage = provider._last_usage
        if usage:
            if usage.input_tokens is not None:
                event_payload["input_tokens"] = usage.input_tokens
            if usage.output_tokens is not None:
                event_payload["output_tokens"] = usage.output_tokens
        await event_bus.emit("ai.request.completed", event_payload)

    validation_error = _validate_blueprint_yaml(result)
    if validation_error:
        await event_bus.emit(
            "ai.request.completed",
            {
                "provider": provider_name,
                "status": "validation_error",
                "error": validation_error,
            },
        )
        raise BlueprintGenerationError(f"AI-generated YAML failed validation: {validation_error}")

    return result


async def _attempt_fallback(
    settings: Settings,
    description: str,
    primary_exc: Exception,
    event_bus: object,
) -> str:
    """Try the fallback provider after the primary provider failed."""
    import time

    fallback_name = settings.ai_fallback_provider
    assert fallback_name is not None

    logger.warning(
        "Primary AI provider %r failed (%s), trying fallback %r",
        settings.ai_provider,
        primary_exc,
        fallback_name,
    )

    try:
        fallback = _build_provider_by_name(fallback_name, settings)
    except BlueprintGenerationError:
        raise BlueprintGenerationError(
            f"Primary provider {settings.ai_provider!r} failed: {primary_exc}. "
            f"Fallback provider {fallback_name!r} is not configured."
        ) from primary_exc

    start = time.monotonic()
    try:
        result = await fallback.generate_blueprint_yaml(description)
    except Exception as fallback_exc:
        duration = time.monotonic() - start
        await event_bus.emit(  # type: ignore[union-attr]
            "ai.request.completed",
            {
                "provider": fallback_name,
                "status": "error",
                "duration_seconds": duration,
            },
        )
        raise BlueprintGenerationError(
            f"Primary provider {settings.ai_provider!r} failed: {primary_exc}. "
            f"Fallback provider {fallback_name!r} also failed: {fallback_exc}"
        ) from fallback_exc

    duration = time.monotonic() - start
    event_payload: dict[str, object] = {
        "provider": fallback_name,
        "status": "success",
        "duration_seconds": duration,
        "is_fallback": True,
    }
    usage = fallback._last_usage
    if usage:
        if usage.input_tokens is not None:
            event_payload["input_tokens"] = usage.input_tokens
        if usage.output_tokens is not None:
            event_payload["output_tokens"] = usage.output_tokens
    await event_bus.emit("ai.request.completed", event_payload)  # type: ignore[union-attr]
    return result
