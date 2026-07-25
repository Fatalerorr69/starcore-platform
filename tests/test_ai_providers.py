"""
AI Provider Tests

Covers AIProvider base class utilities, AnthropicProvider, and
OpenAICompatProvider.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from ai.base import AIProvider, BlueprintGenerationError
from ai.providers.anthropic import AnthropicProvider
from ai.providers.openai_compat import OpenAICompatProvider
from anthropic.types import TextBlock

# ---------------------------------------------------------------------------
# AIProvider base — _strip_fences
# ---------------------------------------------------------------------------


def test_strip_fences_removes_yaml_fences():
    text = "```yaml\nname: demo\n```"
    assert AIProvider._strip_fences(text) == "name: demo"


def test_strip_fences_removes_plain_code_fences():
    text = "```\nname: demo\n```"
    assert AIProvider._strip_fences(text) == "name: demo"


def test_strip_fences_removes_yml_fences():
    text = "```yml\nname: demo\n```"
    assert AIProvider._strip_fences(text) == "name: demo"


def test_strip_fences_noop_on_plain_text():
    text = "name: demo\nresources: []"
    assert AIProvider._strip_fences(text) == text


def test_blueprint_generation_error_is_exception():
    err = BlueprintGenerationError("test message")
    assert isinstance(err, Exception)
    assert str(err) == "test message"


# ---------------------------------------------------------------------------
# AnthropicProvider
# ---------------------------------------------------------------------------


async def test_anthropic_provider_returns_stripped_blueprint():
    fake_response = MagicMock()
    fake_response.content = [
        MagicMock(spec=TextBlock, text="```yaml\nname: demo\nresources: []\n```")
    ]
    fake_client = MagicMock()
    fake_client.messages.create = AsyncMock(return_value=fake_response)

    with patch("ai.providers.anthropic.AsyncAnthropic", return_value=fake_client):
        provider = AnthropicProvider(api_key="sk-test-key", model="claude-sonnet-5")
        result = await provider.generate_blueprint_yaml("a web app")

    assert result == "name: demo\nresources: []"


async def test_anthropic_provider_raises_on_api_error():
    fake_client = MagicMock()
    fake_client.messages.create = AsyncMock(side_effect=RuntimeError("timeout"))

    with patch("ai.providers.anthropic.AsyncAnthropic", return_value=fake_client):
        provider = AnthropicProvider(api_key="sk-test-key", model="claude-sonnet-5")
        with pytest.raises(BlueprintGenerationError, match="Anthropic API request failed"):
            await provider.generate_blueprint_yaml("a web app")


async def test_anthropic_provider_raises_on_empty_response():
    fake_response = MagicMock()
    fake_response.content = []
    fake_client = MagicMock()
    fake_client.messages.create = AsyncMock(return_value=fake_response)

    with patch("ai.providers.anthropic.AsyncAnthropic", return_value=fake_client):
        provider = AnthropicProvider(api_key="sk-test-key", model="claude-sonnet-5")
        with pytest.raises(BlueprintGenerationError, match="empty response"):
            await provider.generate_blueprint_yaml("a web app")


async def test_anthropic_provider_raises_on_non_text_block():
    fake_block = MagicMock()  # no spec=TextBlock → isinstance(..., TextBlock) is False
    fake_response = MagicMock()
    fake_response.content = [fake_block]
    fake_client = MagicMock()
    fake_client.messages.create = AsyncMock(return_value=fake_response)

    with patch("ai.providers.anthropic.AsyncAnthropic", return_value=fake_client):
        provider = AnthropicProvider(api_key="sk-test-key", model="claude-sonnet-5")
        with pytest.raises(BlueprintGenerationError, match="non-text response block"):
            await provider.generate_blueprint_yaml("a web app")


# ---------------------------------------------------------------------------
# OpenAICompatProvider
# ---------------------------------------------------------------------------


def _ok_response(content: str = "name: demo\nresources: []") -> MagicMock:
    """Build a fake successful httpx Response with OpenAI-compat JSON body."""
    resp = MagicMock(spec=httpx.Response)
    resp.raise_for_status = MagicMock()
    resp.json = MagicMock(return_value={"choices": [{"message": {"content": content}}]})
    return resp


async def test_openai_compat_provider_returns_blueprint():
    fake_resp = _ok_response()
    mock_post = AsyncMock(return_value=fake_resp)

    with patch("ai.providers.openai_compat.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=MagicMock(post=mock_post))
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        provider = OpenAICompatProvider(
            base_url="http://localhost:11434/v1",
            model="llama3.2",
        )
        result = await provider.generate_blueprint_yaml("a web app")

    assert result == "name: demo\nresources: []"
    mock_post.assert_called_once()


async def test_openai_compat_provider_sets_auth_header_when_api_key_given():
    fake_resp = _ok_response()
    mock_post = AsyncMock(return_value=fake_resp)

    with patch("ai.providers.openai_compat.httpx.AsyncClient") as mock_cls:
        mock_client = MagicMock(post=mock_post)
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        provider = OpenAICompatProvider(
            base_url="http://localhost:11434/v1",
            model="llama3.2",
            api_key="my-secret",
        )
        await provider.generate_blueprint_yaml("a web app")

    _, kwargs = mock_post.call_args
    assert kwargs["headers"]["Authorization"] == "Bearer my-secret"


async def test_openai_compat_provider_no_auth_header_without_api_key():
    fake_resp = _ok_response()
    mock_post = AsyncMock(return_value=fake_resp)

    with patch("ai.providers.openai_compat.httpx.AsyncClient") as mock_cls:
        mock_client = MagicMock(post=mock_post)
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        provider = OpenAICompatProvider(
            base_url="http://localhost:11434/v1",
            model="llama3.2",
        )
        await provider.generate_blueprint_yaml("a web app")

    _, kwargs = mock_post.call_args
    assert "Authorization" not in kwargs["headers"]


async def test_openai_compat_provider_raises_on_http_status_error():
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 500
    exc = httpx.HTTPStatusError("server error", request=MagicMock(), response=mock_response)

    mock_post = AsyncMock(side_effect=exc)

    with patch("ai.providers.openai_compat.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=MagicMock(post=mock_post))
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        provider = OpenAICompatProvider(
            base_url="http://localhost:11434/v1",
            model="llama3.2",
        )
        with pytest.raises(BlueprintGenerationError, match="HTTP 500"):
            await provider.generate_blueprint_yaml("a web app")


async def test_openai_compat_provider_raises_on_connection_error():
    exc = httpx.ConnectError("connection refused")
    mock_post = AsyncMock(side_effect=exc)

    with patch("ai.providers.openai_compat.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=MagicMock(post=mock_post))
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        provider = OpenAICompatProvider(
            base_url="http://localhost:11434/v1",
            model="llama3.2",
        )
        with pytest.raises(BlueprintGenerationError, match="request failed"):
            await provider.generate_blueprint_yaml("a web app")


async def test_openai_compat_provider_raises_on_unexpected_response_format():
    resp = MagicMock(spec=httpx.Response)
    resp.raise_for_status = MagicMock()
    resp.json = MagicMock(return_value={"no_choices_key": True})
    mock_post = AsyncMock(return_value=resp)

    with patch("ai.providers.openai_compat.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=MagicMock(post=mock_post))
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        provider = OpenAICompatProvider(
            base_url="http://localhost:11434/v1",
            model="llama3.2",
        )
        with pytest.raises(BlueprintGenerationError, match="Unexpected response format"):
            await provider.generate_blueprint_yaml("a web app")


async def test_openai_compat_provider_strips_fences_from_response():
    fenced_content = "```yaml\nname: demo\nresources: []\n```"
    fake_resp = _ok_response(content=fenced_content)
    mock_post = AsyncMock(return_value=fake_resp)

    with patch("ai.providers.openai_compat.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=MagicMock(post=mock_post))
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        provider = OpenAICompatProvider(
            base_url="http://localhost:11434/v1",
            model="llama3.2",
        )
        result = await provider.generate_blueprint_yaml("a web app")

    assert result == "name: demo\nresources: []"


async def test_openai_compat_provider_trims_trailing_slash_from_base_url():
    """Provider must POST to /v1/chat/completions, not /v1//chat/completions."""
    fake_resp = _ok_response()
    mock_post = AsyncMock(return_value=fake_resp)

    with patch("ai.providers.openai_compat.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=MagicMock(post=mock_post))
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        provider = OpenAICompatProvider(
            base_url="http://localhost:11434/v1/",  # trailing slash
            model="llama3.2",
        )
        await provider.generate_blueprint_yaml("a web app")

    url_arg = mock_post.call_args[0][0]
    assert "//" not in url_arg.split("://", 1)[1]
