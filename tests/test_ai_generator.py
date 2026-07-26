"""
AI Blueprint Generator Tests

Covers the public generate_blueprint_yaml() entry point and the _build_provider()
factory via the updated provider abstraction layer.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from ai.generator import BlueprintGenerationError, _build_provider, generate_blueprint_yaml
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


def test_build_provider_returns_openai_compat_provider():
    from ai.providers.openai_compat import OpenAICompatProvider

    provider = _build_provider(
        _settings(ai_provider="openai-compatible", ai_base_url="http://localhost:11434/v1")
    )
    assert isinstance(provider, OpenAICompatProvider)


def test_build_provider_raises_on_unknown_provider():
    with pytest.raises(BlueprintGenerationError, match="Unknown AI provider"):
        _build_provider(_settings(ai_provider="nonexistent"))


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
