"""
OpenAI-compatible AI provider — works with any server that implements the
OpenAI Chat Completions API (Ollama, LM Studio, vLLM, LocalAI, OpenAI, etc.).

Uses httpx (already a project dependency) — no additional packages required.
"""

from __future__ import annotations

import httpx

from ai.base import AIProvider, BlueprintGenerationError
from ai.prompts import BLUEPRINT_SYSTEM_PROMPT


class OpenAICompatProvider(AIProvider):
    """Generates blueprints via any OpenAI-compatible /v1/chat/completions endpoint."""

    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        api_key: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._api_key = api_key
        self._timeout = timeout

    async def generate_blueprint_yaml(self, description: str) -> str:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": BLUEPRINT_SYSTEM_PROMPT},
                {"role": "user", "content": description},
            ],
            "max_tokens": 2000,
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise BlueprintGenerationError(
                f"OpenAI-compatible API returned HTTP {exc.response.status_code}: {exc}"
            ) from exc
        except httpx.HTTPError as exc:
            raise BlueprintGenerationError(f"OpenAI-compatible API request failed: {exc}") from exc

        try:
            data = response.json()
            text: str = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as exc:
            raise BlueprintGenerationError(
                f"Unexpected response format from OpenAI-compatible API: {exc}"
            ) from exc

        return self._strip_fences(text)
