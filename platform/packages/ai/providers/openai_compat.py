"""
OpenAI-compatible AI provider — works with any server that implements the
OpenAI Chat Completions API (Ollama, LM Studio, vLLM, LocalAI, OpenAI, etc.).

Uses httpx (already a project dependency) — no additional packages required.
"""

from __future__ import annotations

import httpx
from provider_sdk.retry import RetryableError, RetryConfig, attempt_with_retry

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
        max_tokens: int = 2000,
        retry_config: RetryConfig | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._api_key = api_key
        self._timeout = timeout
        self._max_tokens = max_tokens
        self._retry_config = retry_config or RetryConfig(
            retryable_exceptions=(
                ConnectionError,
                TimeoutError,
                OSError,
                httpx.ConnectError,
                httpx.ReadTimeout,
            ),
        )

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
            "max_tokens": self._max_tokens,
        }

        async def _call() -> httpx.Response:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                resp.raise_for_status()
                return resp

        try:
            response = await attempt_with_retry(
                _call,
                config=self._retry_config,
                operation_name="openai_compat_generate",
            )
        except RetryableError as exc:
            raise BlueprintGenerationError(
                f"OpenAI-compatible API request failed after retries: {exc.last_exception}"
            ) from exc
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
