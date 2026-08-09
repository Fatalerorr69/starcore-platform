"""
Anthropic AI provider — wraps the Anthropic Messages API.
"""

from __future__ import annotations

import httpx
from anthropic import AsyncAnthropic
from anthropic.types import TextBlock
from provider_sdk.retry import RetryableError, RetryConfig, attempt_with_retry

from ai.base import AIProvider, BlueprintGenerationError, TokenUsage
from ai.prompts import BLUEPRINT_SYSTEM_PROMPT


class AnthropicProvider(AIProvider):
    """Generates blueprints via the Anthropic Messages API (claude-*)."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        max_tokens: int = 2000,
        timeout: float = 120.0,
        retry_config: RetryConfig | None = None,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._max_tokens = max_tokens
        self._timeout = timeout
        self._retry_config = retry_config or RetryConfig(
            retryable_exceptions=(ConnectionError, TimeoutError, OSError, httpx.ConnectError),
        )

    async def generate_blueprint_yaml(self, description: str) -> str:
        client = AsyncAnthropic(api_key=self._api_key, timeout=self._timeout)

        async def _call() -> object:
            return await client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                system=BLUEPRINT_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": description}],
            )

        try:
            response = await attempt_with_retry(
                _call,
                config=self._retry_config,
                operation_name="anthropic_generate",
            )
        except RetryableError as exc:
            raise BlueprintGenerationError(
                f"Anthropic API request failed after retries: {exc.last_exception}"
            ) from exc
        except Exception as exc:
            raise BlueprintGenerationError(f"Anthropic API request failed: {exc}") from exc

        if not response.content:  # type: ignore[union-attr]
            raise BlueprintGenerationError("Anthropic API returned an empty response.")

        usage = getattr(response, "usage", None)
        if usage:
            self._last_usage = TokenUsage(
                input_tokens=getattr(usage, "input_tokens", None),
                output_tokens=getattr(usage, "output_tokens", None),
            )

        first_block = response.content[0]  # type: ignore[union-attr]
        if not isinstance(first_block, TextBlock):
            raise BlueprintGenerationError("Anthropic API returned a non-text response block.")

        return self._strip_fences(first_block.text)
