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


async def test_proxmox_create_vm_clones_template_and_sets_result():
    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_client.cluster.nextid.get.return_value = "105"
    fake_client.nodes.return_value.qemu.return_value.clone.post.return_value = "UPID:fatalab:clone"
    fake_client.nodes.return_value.tasks.return_value.status.get.return_value = {
        "status": "stopped",
        "exitstatus": "OK",
    }

    provider = ProxmoxProvider()
    provider._client = fake_client

    task = Task(
        id="1",
        provider="proxmox",
        action="create",
        resource="web-vm",
        payload={
            "node": "fatalab",
            "template_vmid": 9000,
            "cores": 2,
            "memory": 2048,
        },
    )

    await provider.execute(task)

    assert task.result["vmid"] == 105
    assert task.result["node"] == "fatalab"
    fake_client.nodes.return_value.qemu.return_value.clone.post.assert_called_once()
    fake_client.nodes.return_value.qemu.return_value.config.post.assert_called_once_with(
        cores=2, memory=2048
    )


async def test_proxmox_create_vm_requires_node_and_template_vmid():
    from orchestrator.task import Task

    provider = ProxmoxProvider()
    provider._client = MagicMock()

    task = Task(
        id="1",
        provider="proxmox",
        action="create",
        resource="web-vm",
        payload={},
    )

    try:
        await provider.execute(task)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


async def test_proxmox_create_lxc_clones_template_and_sets_result():
    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_client.cluster.nextid.get.return_value = "205"
    fake_client.nodes.return_value.lxc.return_value.clone.post.return_value = (
        "UPID:fatalab:lxcclone"
    )
    fake_client.nodes.return_value.tasks.return_value.status.get.return_value = {
        "status": "stopped",
        "exitstatus": "OK",
    }

    provider = ProxmoxProvider()
    provider._client = fake_client

    task = Task(
        id="1",
        provider="proxmox",
        action="create",
        resource="web-lxc",
        kind="lxc",
        payload={
            "node": "fatalab",
            "template_vmid": 8000,
            "cores": 1,
            "memory": 512,
        },
    )

    await provider.execute(task)

    assert task.result["vmid"] == 205
    assert task.result["kind"] == "lxc"
    fake_client.nodes.return_value.lxc.return_value.clone.post.assert_called_once()
    call_kwargs = fake_client.nodes.return_value.lxc.return_value.clone.post.call_args.kwargs
    assert call_kwargs["hostname"] == "web-lxc"
    fake_client.nodes.return_value.lxc.return_value.config.post.assert_called_once_with(
        cores=1, memory=512
    )


async def test_proxmox_start_lxc_uses_lxc_endpoint_not_qemu():
    from orchestrator.task import Task

    fake_client = MagicMock()
    provider = ProxmoxProvider()
    provider._client = fake_client

    task = Task(
        id="1",
        provider="proxmox",
        action="start",
        resource="web-lxc",
        kind="lxc",
        payload={"node": "fatalab", "vmid": 205},
    )

    await provider.execute(task)

    fake_client.nodes.return_value.lxc.return_value.status.post.assert_called_once_with("start")
    fake_client.nodes.return_value.qemu.return_value.status.post.assert_not_called()
