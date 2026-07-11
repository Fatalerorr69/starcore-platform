"""
Provider Tests
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from core.config import Settings
from providers.proxmox.provider import ProxmoxProvider


def _settings(**overrides) -> Settings:
    defaults = dict(
        proxmox_host=None,
        proxmox_user=None,
        proxmox_token_name=None,
        proxmox_token_value=None,
        proxmox_verify_ssl=True,
    )
    defaults.update(overrides)
    return Settings(**defaults)


async def test_proxmox_connect_fails_without_credentials():
    with patch(
        "providers.proxmox.provider.get_settings",
        return_value=_settings(),
    ):
        provider = ProxmoxProvider()
        connected = await provider.connect()

    assert connected is False


async def test_proxmox_connect_succeeds_with_credentials():
    fake_client = MagicMock()
    fake_client.version.get.return_value = {"version": "8.0"}

    settings = _settings(
        proxmox_host="fatalab.local",
        proxmox_user="root@pam",
        proxmox_token_name="starcore",
        proxmox_token_value="secret",
    )

    with (
        patch("providers.proxmox.provider.get_settings", return_value=settings),
        patch(
            "providers.proxmox.provider.ProxmoxAPI",
            return_value=fake_client,
        ),
    ):
        provider = ProxmoxProvider()
        connected = await provider.connect()

    assert connected is True
    assert provider._client is fake_client


async def test_proxmox_execute_raises_without_connection():
    from orchestrator.task import Task

    provider = ProxmoxProvider()
    task = Task(id="1", provider="proxmox", action="start", resource="web-vm")

    try:
        await provider.execute(task)
        raise AssertionError("expected RuntimeError")
    except RuntimeError:
        pass
