"""
Resource Actions Tests
"""

from __future__ import annotations

import pytest
from core.resource_actions import execute_resource_action
from orchestrator.task import TaskStatus
from provider_sdk.base import BaseProvider
from provider_sdk.registry import registry


class FakeProvider(BaseProvider):
    name = "fake"

    def __init__(self, connect_result: bool = True, should_fail: bool = False) -> None:
        self._connect_result = connect_result
        self._should_fail = should_fail
        self.executed: list[str] = []

    async def connect(self) -> bool:
        return self._connect_result

    async def disconnect(self) -> None:
        return None

    async def health(self) -> dict:
        return {"status": "ok", "provider": self.name}

    async def list_resources(self) -> list[dict]:
        return []

    async def execute(self, task) -> None:
        if self._should_fail:
            raise RuntimeError("boom")
        self.executed.append(task.action)


@pytest.fixture(autouse=True)
def clean_registry():
    registry._providers.clear()
    yield
    registry._providers.clear()


async def test_execute_resource_action_succeeds():
    fake = FakeProvider()
    registry.register(fake)

    task = await execute_resource_action("fake", "stop", "thing")

    assert task.status == TaskStatus.SUCCESS
    assert fake.executed == ["stop"]


async def test_execute_resource_action_skips_unknown_provider():
    task = await execute_resource_action("ghost", "stop", "thing")
    assert task.status == TaskStatus.SKIPPED


async def test_execute_resource_action_fails_on_connect_failure():
    registry.register(FakeProvider(connect_result=False))
    task = await execute_resource_action("fake", "stop", "thing")
    assert task.status == TaskStatus.FAILED


async def test_execute_resource_action_fails_and_captures_error():
    registry.register(FakeProvider(should_fail=True))
    task = await execute_resource_action("fake", "stop", "thing")
    assert task.status == TaskStatus.FAILED
    assert "boom" in task.result["error"]


async def test_proxmox_destroy_action_calls_delete_endpoint():
    from unittest.mock import MagicMock

    from orchestrator.task import Task
    from providers.proxmox.provider import ProxmoxProvider

    fake_client = MagicMock()
    fake_client.nodes.return_value.qemu.return_value.delete.return_value = "UPID:test"
    fake_client.nodes.return_value.tasks.return_value.status.get.return_value = {
        "status": "stopped",
        "exitstatus": "OK",
    }

    provider = ProxmoxProvider()
    provider._client = fake_client

    task = Task(
        id="1",
        provider="proxmox",
        action="destroy",
        resource="old-vm",
        payload={"node": "fatalab", "vmid": 105},
    )

    await provider.execute(task)

    fake_client.nodes.return_value.qemu.return_value.delete.assert_called_once()
    assert task.result["vmid"] == 105


async def test_proxmox_destroy_requires_node_and_vmid():
    from orchestrator.task import Task
    from providers.proxmox.provider import ProxmoxProvider

    provider = ProxmoxProvider()
    provider._client = object()

    task = Task(id="1", provider="proxmox", action="destroy", resource="old-vm")

    with pytest.raises(ValueError):
        await provider.execute(task)
