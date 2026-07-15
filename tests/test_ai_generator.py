"""
AI Blueprint Generator Tests
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from ai.generator import BlueprintGenerationError, generate_blueprint_yaml
from anthropic.types import TextBlock
from blueprints.loader import BlueprintLoader
from core.config import Settings


def _settings(**overrides) -> Settings:
    defaults = dict(anthropic_api_key=None, anthropic_model="claude-sonnet-5")
    defaults.update(overrides)
    return Settings(**defaults)


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
        patch("ai.generator.AsyncAnthropic", return_value=fake_client),
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
        patch("ai.generator.AsyncAnthropic", return_value=fake_client),
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
        patch("ai.generator.AsyncAnthropic", return_value=fake_client),
    ):
        with pytest.raises(BlueprintGenerationError):
            await generate_blueprint_yaml("a simple web app")


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
