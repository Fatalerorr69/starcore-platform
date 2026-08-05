"""
Anthropic AI provider — wraps the Anthropic Messages API.
"""

from __future__ import annotations

from anthropic import AsyncAnthropic
from anthropic.types import TextBlock

from ai.base import AIProvider, BlueprintGenerationError
from ai.prompts import BLUEPRINT_SYSTEM_PROMPT


class AnthropicProvider(AIProvider):
    """Generates blueprints via the Anthropic Messages API (claude-*)."""

    def __init__(self, *, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    async def generate_blueprint_yaml(self, description: str) -> str:
        client = AsyncAnthropic(api_key=self._api_key)
        try:
            response = await client.messages.create(
                model=self._model,
                max_tokens=2000,
                system=BLUEPRINT_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": description}],
            )
        except Exception as exc:
            raise BlueprintGenerationError(f"Anthropic API request failed: {exc}") from exc

        if not response.content:
            raise BlueprintGenerationError("Anthropic API returned an empty response.")

        first_block = response.content[0]
        if not isinstance(first_block, TextBlock):
            raise BlueprintGenerationError("Anthropic API returned a non-text response block.")

        return self._strip_fences(first_block.text)
