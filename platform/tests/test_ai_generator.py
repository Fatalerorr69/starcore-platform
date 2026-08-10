"""
AI Blueprint Generator Tests

Covers the public generate_blueprint_yaml() entry point and the _build_provider()
factory via the updated provider abstraction layer.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from ai.generator import (
    BlueprintGenerationError,
    _build_provider,
    _build_provider_by_name,
    _validate_blueprint_yaml,
    generate_blueprint_yaml,
)
from anthropic.types import TextBlock
from blueprints.loader import BlueprintLoader
from core.config import Settings


def _settings(**overrides: Any) -> Settings:
    defaults: dict[str, Any] = dict(
        anthropic_api_key=None,
        anthropic_model="claude-sonnet-5",
        ai_provider="anthropic",
        ai_base_url=None,
        ai_api_key=None,
        ai_model=None,
    )
    defaults.update(overrides)
    return Settings(**defaults)


# ---------------------------------------------------------------------------
# _build_provider factory
# ---------------------------------------------------------------------------


def test_build_provider_raises_without_anthropic_key():
    with pytest.raises(BlueprintGenerationError, match="STARCORE_ANTHROPIC_API_KEY"):
        _build_provider(_settings(ai_provider="anthropic", anthropic_api_key=None))


def test_build_provider_returns_anthropic_provider():
    from ai.providers.anthropic import AnthropicProvider

    provider = _build_provider(_settings(anthropic_api_key="sk-test-key"))
    assert isinstance(provider, AnthropicProvider)


def test_build_provider_raises_without_base_url():
    with pytest.raises(BlueprintGenerationError, match="STARCORE_AI_BASE_URL"):
        _build_provider(_settings(ai_provider="openai-compatible", ai_base_url=None))


def test_build_provider_raises_without_ai_model():
    with pytest.raises(BlueprintGenerationError, match="STARCORE_AI_MODEL"):
        _build_provider(
            _settings(
                ai_provider="openai-compatible",
                ai_base_url="http://localhost:11434/v1",
                ai_model=None,
            )
        )


def test_build_provider_returns_openai_compat_provider():
    from ai.providers.openai_compat import OpenAICompatProvider

    provider = _build_provider(
        _settings(
            ai_provider="openai-compatible",
            ai_base_url="http://localhost:11434/v1",
            ai_model="llama3",
        )
    )
    assert isinstance(provider, OpenAICompatProvider)
    # RISK finding fix: the openai-compatible provider must use its own
    # configured model, never fall back to the Anthropic model name.
    assert provider._model == "llama3"


def test_build_provider_raises_on_unknown_provider():
    with pytest.raises(BlueprintGenerationError, match="Unknown AI provider"):
        _build_provider(_settings(ai_provider="nonexistent"))


def test_build_provider_passes_configured_max_tokens_and_timeout():
    from ai.providers.anthropic import AnthropicProvider

    provider = _build_provider(
        _settings(anthropic_api_key="sk-test", ai_max_tokens=4096, ai_timeout=60.0)
    )
    assert isinstance(provider, AnthropicProvider)
    assert provider._max_tokens == 4096
    assert provider._timeout == 60.0


def test_build_provider_passes_retry_config_from_settings():
    from ai.providers.anthropic import AnthropicProvider

    provider = _build_provider(_settings(anthropic_api_key="sk-test", ai_max_retries=5))
    assert isinstance(provider, AnthropicProvider)
    assert provider._retry_config.max_retries == 5


# ---------------------------------------------------------------------------
# generate_blueprint_yaml — Anthropic path (patching the provider class)
# ---------------------------------------------------------------------------


async def test_generate_blueprint_yaml_fails_without_api_key():
    with patch("ai.generator.get_settings", return_value=_settings()):
        with pytest.raises(BlueprintGenerationError):
            await generate_blueprint_yaml("a simple web app")


async def test_generate_blueprint_yaml_returns_stripped_text():
    fake_response = MagicMock()
    fake_response.content = [
        MagicMock(spec=TextBlock, text="```yaml\nname: demo\nresources: []\n```")
    ]

    fake_client = MagicMock()
    fake_client.messages.create = AsyncMock(return_value=fake_response)

    settings = _settings(anthropic_api_key="sk-test-key")

    with (
        patch("ai.generator.get_settings", return_value=settings),
        patch("ai.providers.anthropic.AsyncAnthropic", return_value=fake_client),
    ):
        result = await generate_blueprint_yaml("a simple web app")

    assert result == "name: demo\nresources: []"
    fake_client.messages.create.assert_called_once()


async def test_generate_blueprint_yaml_wraps_api_errors():
    fake_client = MagicMock()
    fake_client.messages.create = AsyncMock(side_effect=RuntimeError("network down"))

    settings = _settings(anthropic_api_key="sk-test-key")

    with (
        patch("ai.generator.get_settings", return_value=settings),
        patch("ai.providers.anthropic.AsyncAnthropic", return_value=fake_client),
    ):
        with pytest.raises(BlueprintGenerationError):
            await generate_blueprint_yaml("a simple web app")


async def test_generate_blueprint_yaml_raises_on_empty_response():
    fake_response = MagicMock()
    fake_response.content = []

    fake_client = MagicMock()
    fake_client.messages.create = AsyncMock(return_value=fake_response)

    settings = _settings(anthropic_api_key="sk-test-key")

    with (
        patch("ai.generator.get_settings", return_value=settings),
        patch("ai.providers.anthropic.AsyncAnthropic", return_value=fake_client),
    ):
        with pytest.raises(BlueprintGenerationError):
            await generate_blueprint_yaml("a simple web app")


async def test_generate_blueprint_yaml_raises_on_non_text_block():
    fake_block = MagicMock()  # no spec=TextBlock → isinstance(..., TextBlock) is False
    fake_response = MagicMock()
    fake_response.content = [fake_block]

    fake_client = MagicMock()
    fake_client.messages.create = AsyncMock(return_value=fake_response)

    settings = _settings(anthropic_api_key="sk-test-key")

    with (
        patch("ai.generator.get_settings", return_value=settings),
        patch("ai.providers.anthropic.AsyncAnthropic", return_value=fake_client),
    ):
        with pytest.raises(BlueprintGenerationError, match="non-text response block"):
            await generate_blueprint_yaml("a web app")


# ---------------------------------------------------------------------------
# BlueprintLoader smoke test (unchanged from before)
# ---------------------------------------------------------------------------


async def test_generate_blueprint_yaml_emits_ai_metrics_event_on_success():
    from core.events import event_bus

    fake_response = MagicMock()
    fake_response.content = [MagicMock(spec=TextBlock, text="name: demo\nresources: []")]
    fake_client = MagicMock()
    fake_client.messages.create = AsyncMock(return_value=fake_response)

    settings = _settings(anthropic_api_key="sk-test-key")
    captured: list[dict] = []

    def capture(payload: dict) -> None:
        captured.append(payload)

    event_bus.subscribe("ai.request.completed", capture)
    try:
        with (
            patch("ai.generator.get_settings", return_value=settings),
            patch("ai.providers.anthropic.AsyncAnthropic", return_value=fake_client),
        ):
            await generate_blueprint_yaml("a web app")
    finally:
        event_bus.unsubscribe("ai.request.completed", capture)

    assert len(captured) == 1
    assert captured[0]["provider"] == "anthropic"
    assert captured[0]["status"] == "success"
    assert "duration_seconds" in captured[0]


async def test_generate_blueprint_yaml_emits_ai_metrics_event_on_error():
    from core.events import event_bus

    fake_client = MagicMock()
    fake_client.messages.create = AsyncMock(side_effect=RuntimeError("fail"))

    settings = _settings(anthropic_api_key="sk-test-key")
    captured: list[dict] = []

    def capture(payload: dict) -> None:
        captured.append(payload)

    event_bus.subscribe("ai.request.completed", capture)
    try:
        with (
            patch("ai.generator.get_settings", return_value=settings),
            patch("ai.providers.anthropic.AsyncAnthropic", return_value=fake_client),
        ):
            with pytest.raises(BlueprintGenerationError):
                await generate_blueprint_yaml("a web app")
    finally:
        event_bus.unsubscribe("ai.request.completed", capture)

    assert len(captured) == 1
    assert captured[0]["status"] == "error"


# ---------------------------------------------------------------------------
# Token usage forwarded to AI metrics event
# ---------------------------------------------------------------------------


async def test_generate_blueprint_yaml_includes_token_usage_in_event():
    from core.events import event_bus

    fake_response = MagicMock()
    fake_response.content = [MagicMock(spec=TextBlock, text="name: demo\nresources: []")]
    fake_usage = MagicMock()
    fake_usage.input_tokens = 300
    fake_usage.output_tokens = 120
    fake_response.usage = fake_usage
    fake_client = MagicMock()
    fake_client.messages.create = AsyncMock(return_value=fake_response)

    settings = _settings(anthropic_api_key="sk-test-key")
    captured: list[dict] = []

    def capture(payload: dict) -> None:
        captured.append(payload)

    event_bus.subscribe("ai.request.completed", capture)
    try:
        with (
            patch("ai.generator.get_settings", return_value=settings),
            patch("ai.providers.anthropic.AsyncAnthropic", return_value=fake_client),
        ):
            await generate_blueprint_yaml("a web app")
    finally:
        event_bus.unsubscribe("ai.request.completed", capture)

    assert len(captured) == 1
    assert captured[0]["input_tokens"] == 300
    assert captured[0]["output_tokens"] == 120


async def test_generate_blueprint_yaml_omits_tokens_when_not_available():
    from core.events import event_bus

    fake_response = MagicMock()
    fake_response.content = [MagicMock(spec=TextBlock, text="name: demo\nresources: []")]
    del fake_response.usage
    fake_client = MagicMock()
    fake_client.messages.create = AsyncMock(return_value=fake_response)

    settings = _settings(anthropic_api_key="sk-test-key")
    captured: list[dict] = []

    def capture(payload: dict) -> None:
        captured.append(payload)

    event_bus.subscribe("ai.request.completed", capture)
    try:
        with (
            patch("ai.generator.get_settings", return_value=settings),
            patch("ai.providers.anthropic.AsyncAnthropic", return_value=fake_client),
        ):
            await generate_blueprint_yaml("a web app")
    finally:
        event_bus.unsubscribe("ai.request.completed", capture)

    assert len(captured) == 1
    assert "input_tokens" not in captured[0]
    assert "output_tokens" not in captured[0]


# ---------------------------------------------------------------------------
# BlueprintLoader smoke test (unchanged from before)
# ---------------------------------------------------------------------------


def test_blueprint_loader_load_from_string_parses_valid_yaml():
    yaml_text = (
        "name: demo\n"
        "version: '1.0'\n"
        "resources:\n"
        "  - name: web\n"
        "    provider: docker\n"
        "    kind: container\n"
        "    config:\n"
        "      image: nginx\n"
    )
    blueprint = BlueprintLoader.load_from_string(yaml_text)
    assert blueprint.name == "demo"
    assert blueprint.resources[0].provider == "docker"


# ---------------------------------------------------------------------------
# _build_provider_by_name
# ---------------------------------------------------------------------------


def test_build_provider_by_name_returns_anthropic():
    from ai.providers.anthropic import AnthropicProvider

    s = _settings(anthropic_api_key="sk-test")
    provider = _build_provider_by_name("anthropic", s)
    assert isinstance(provider, AnthropicProvider)


def test_build_provider_by_name_returns_openai_compat():
    from ai.providers.openai_compat import OpenAICompatProvider

    s = _settings(
        ai_provider="openai-compatible",
        ai_base_url="http://localhost:11434/v1",
        ai_model="llama3",
    )
    provider = _build_provider_by_name("openai-compatible", s)
    assert isinstance(provider, OpenAICompatProvider)


def test_build_provider_by_name_raises_on_unknown():
    with pytest.raises(BlueprintGenerationError, match="Unknown AI provider"):
        _build_provider_by_name("nonexistent", _settings())


# ---------------------------------------------------------------------------
# _validate_blueprint_yaml
# ---------------------------------------------------------------------------


def test_validate_blueprint_yaml_returns_none_for_valid():
    yaml_text = (
        "name: demo\nversion: '1.0'\nresources:\n"
        "  - name: web\n    provider: docker\n"
        "    kind: container\n    config:\n      image: nginx\n"
    )
    assert _validate_blueprint_yaml(yaml_text) is None


def test_validate_blueprint_yaml_returns_error_for_invalid():
    result = _validate_blueprint_yaml("not valid yaml: [[[")
    assert result is not None


def test_validate_blueprint_yaml_returns_error_for_missing_name():
    result = _validate_blueprint_yaml("version: '1.0'\n")
    assert result is not None


# ---------------------------------------------------------------------------
# Fallback provider
# ---------------------------------------------------------------------------


async def test_generate_with_fallback_on_primary_failure():
    from core.events import event_bus

    fake_client_fallback = MagicMock()
    fallback_resp = MagicMock()
    fallback_resp.status_code = 200
    fallback_resp.raise_for_status = MagicMock()
    fallback_resp.json = MagicMock(
        return_value={
            "choices": [
                {
                    "message": {
                        "content": (
                            "name: demo\nversion: '1.0'\nresources:\n"
                            "  - name: web\n    provider: docker\n"
                            "    kind: container\n    config:\n      image: nginx\n"
                        )
                    }
                }
            ],
            "usage": {"prompt_tokens": 50, "completion_tokens": 100},
        }
    )
    fake_client_fallback.post = AsyncMock(return_value=fallback_resp)

    fake_anthropic_client = MagicMock()
    fake_anthropic_client.messages.create = AsyncMock(side_effect=RuntimeError("anthropic down"))

    settings = _settings(
        anthropic_api_key="sk-test",
        ai_provider="anthropic",
        ai_fallback_provider="openai-compatible",
        ai_base_url="http://localhost:11434/v1",
        ai_model="llama3",
    )

    captured: list[dict] = []
    event_bus.subscribe("ai.request.completed", lambda p: captured.append(p))

    try:
        with (
            patch("ai.generator.get_settings", return_value=settings),
            patch("ai.providers.anthropic.AsyncAnthropic", return_value=fake_anthropic_client),
            patch(
                "httpx.AsyncClient.__aenter__",
                return_value=MagicMock(post=AsyncMock(return_value=fallback_resp)),
            ),
            patch("httpx.AsyncClient.__aexit__", AsyncMock(return_value=False)),
        ):
            result = await generate_blueprint_yaml("a web app")
    finally:
        event_bus.unsubscribe("ai.request.completed", captured.append)

    assert "name: demo" in result
    assert any(e["status"] == "error" for e in captured)
    fallback_events = [
        e for e in captured if e.get("is_fallback") is True and e["status"] == "success"
    ]
    assert len(fallback_events) == 1
    assert fallback_events[0]["input_tokens"] == 50
    assert fallback_events[0]["output_tokens"] == 100


async def test_generate_fallback_both_fail_raises():
    fake_anthropic = MagicMock()
    fake_anthropic.messages.create = AsyncMock(side_effect=RuntimeError("anthropic down"))

    settings = _settings(
        anthropic_api_key="sk-test",
        ai_provider="anthropic",
        ai_fallback_provider="openai-compatible",
        ai_base_url="http://localhost:11434/v1",
        ai_model="llama3",
    )

    fallback_resp = MagicMock()
    fallback_resp.status_code = 500
    fallback_resp.raise_for_status = MagicMock(side_effect=Exception("server error"))

    with (
        patch("ai.generator.get_settings", return_value=settings),
        patch("ai.providers.anthropic.AsyncAnthropic", return_value=fake_anthropic),
        patch(
            "httpx.AsyncClient.__aenter__",
            return_value=MagicMock(post=AsyncMock(return_value=fallback_resp)),
        ),
        patch("httpx.AsyncClient.__aexit__", AsyncMock(return_value=False)),
    ):
        with pytest.raises(BlueprintGenerationError, match="also failed"):
            await generate_blueprint_yaml("a web app")


async def test_generate_fallback_not_configured_raises_normally():
    fake_anthropic = MagicMock()
    fake_anthropic.messages.create = AsyncMock(side_effect=RuntimeError("anthropic down"))

    settings = _settings(
        anthropic_api_key="sk-test",
        ai_provider="anthropic",
        ai_fallback_provider=None,
    )

    with (
        patch("ai.generator.get_settings", return_value=settings),
        patch("ai.providers.anthropic.AsyncAnthropic", return_value=fake_anthropic),
    ):
        with pytest.raises(BlueprintGenerationError):
            await generate_blueprint_yaml("a web app")


async def test_generate_fallback_provider_misconfigured_raises():
    fake_anthropic = MagicMock()
    fake_anthropic.messages.create = AsyncMock(side_effect=RuntimeError("anthropic down"))

    settings = _settings(
        anthropic_api_key="sk-test",
        ai_provider="anthropic",
        ai_fallback_provider="openai-compatible",
        ai_base_url=None,
        ai_model=None,
    )

    with (
        patch("ai.generator.get_settings", return_value=settings),
        patch("ai.providers.anthropic.AsyncAnthropic", return_value=fake_anthropic),
    ):
        with pytest.raises(BlueprintGenerationError, match="not configured"):
            await generate_blueprint_yaml("a web app")


# ---------------------------------------------------------------------------
# Output validation
# ---------------------------------------------------------------------------


async def test_generate_raises_on_invalid_yaml_output():
    from core.events import event_bus

    fake_response = MagicMock()
    fake_response.content = [MagicMock(spec=TextBlock, text="this is not valid blueprint yaml")]
    fake_client = MagicMock()
    fake_client.messages.create = AsyncMock(return_value=fake_response)

    settings = _settings(anthropic_api_key="sk-test-key")
    captured: list[dict] = []

    event_bus.subscribe("ai.request.completed", lambda p: captured.append(p))
    try:
        with (
            patch("ai.generator.get_settings", return_value=settings),
            patch("ai.providers.anthropic.AsyncAnthropic", return_value=fake_client),
        ):
            with pytest.raises(BlueprintGenerationError, match="validation"):
                await generate_blueprint_yaml("a web app")
    finally:
        event_bus.unsubscribe("ai.request.completed", captured.append)

    assert any(e.get("status") == "validation_error" for e in captured)
