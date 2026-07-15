"""
Proxmox Environment Discovery Tests
"""

from __future__ import annotations

import pytest
from core.discovery import discover_proxmox_environment
from provider_sdk.base import BaseProvider
from provider_sdk.registry import registry


class FakeProxmoxProvider(BaseProvider):
    name = "proxmox"

    async def connect(self) -> bool:
        return True

    async def disconnect(self) -> None:
        return None

    async def health(self) -> dict:
        return {"status": "ok", "provider": self.name}

    async def list_resources(self) -> list[dict]:
        return [{"node": "fatalab", "vmid": 105, "name": "web", "status": "running", "kind": "vm"}]

    async def execute(self, task) -> None:
        return None

    async def node_status(self) -> list[dict]:
        return [
            {
                "node": "fatalab",
                "cpu": 0.2,
                "memory": {"used": 8_000_000_000, "total": 32_000_000_000},
                "rootfs": {"used": 50_000_000_000, "total": 200_000_000_000},
            }
        ]

    async def storage_status(self) -> list[dict]:
        return [
            {
                "node": "fatalab",
                "storage": "local-zfs",
                "type": "zfspool",
                "used": 1e9,
                "total": 5e9,
            }
        ]

    async def list_templates(self) -> list[dict]:
        return [
            {"node": "fatalab", "vmid": 9000, "name": "ubuntu-24.04", "kind": "vm"},
            {"node": "fatalab", "vmid": 8000, "name": "debian-12", "kind": "lxc"},
        ]

    async def list_networks(self) -> list[dict]:
        return [{"node": "fatalab", "bridge": "vmbr0", "active": True}]


class DisconnectedProxmoxProvider(BaseProvider):
    name = "proxmox"

    async def connect(self) -> bool:
        return False

    async def disconnect(self) -> None:
        return None

    async def health(self) -> dict:
        return {"status": "disconnected", "provider": self.name}

    async def list_resources(self) -> list[dict]:
        return []

    async def execute(self, task) -> None:
        return None


@pytest.fixture(autouse=True)
def clean_registry():
    registry._providers.clear()
    yield
    registry._providers.clear()


async def test_discover_returns_error_when_provider_not_registered():
    from unittest.mock import patch

    with patch("core.discovery.register_default_providers"):
        report = await discover_proxmox_environment()

    assert report["connected"] is False
    assert "not registered" in report["error"]


async def test_discover_returns_error_when_connect_fails():
    registry.register(DisconnectedProxmoxProvider())
    report = await discover_proxmox_environment()
    assert report["connected"] is False
    assert "Failed to connect" in report["error"]


async def test_discover_returns_full_environment_report():
    registry.register(FakeProxmoxProvider())
    report = await discover_proxmox_environment()

    assert report["connected"] is True
    assert report["nodes"][0]["node"] == "fatalab"
    assert report["nodes"][0]["cpu_percent"] == 20.0
    assert report["storage"][0]["storage"] == "local-zfs"
    assert len(report["templates"]) == 2
    assert report["templates"][0]["name"] == "ubuntu-24.04"
    assert report["networks"][0]["bridge"] == "vmbr0"
    assert len(report["existing_resources"]) == 1


async def test_proxmox_list_templates_filters_by_template_flag():
    from unittest.mock import MagicMock

    from providers.proxmox.provider import ProxmoxProvider

    fake_client = MagicMock()
    fake_client.nodes.get.return_value = [{"node": "fatalab"}]
    fake_client.nodes.return_value.qemu.get.return_value = [
        {"vmid": 9000, "name": "ubuntu-tpl", "template": 1},
        {"vmid": 101, "name": "web-vm", "template": 0},
    ]
    fake_client.nodes.return_value.lxc.get.return_value = [
        {"vmid": 8000, "name": "debian-tpl", "template": 1},
    ]

    provider = ProxmoxProvider()
    provider._client = fake_client

    templates = await provider.list_templates()

    assert len(templates) == 2
    assert {t["vmid"] for t in templates} == {9000, 8000}


async def test_proxmox_list_networks_filters_bridges_only():
    from unittest.mock import MagicMock

    from providers.proxmox.provider import ProxmoxProvider

    fake_client = MagicMock()
    fake_client.nodes.get.return_value = [{"node": "fatalab"}]
    fake_client.nodes.return_value.network.get.return_value = [
        {"iface": "vmbr0", "type": "bridge", "active": 1},
        {"iface": "eth0", "type": "eth", "active": 1},
    ]

    provider = ProxmoxProvider()
    provider._client = fake_client

    networks = await provider.list_networks()

    assert len(networks) == 1
    assert networks[0]["bridge"] == "vmbr0"
