"""
Provider Tests
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest
from core.config import Settings
from docker.errors import DockerException, NotFound
from provider_sdk.base import BaseProvider
from providers.docker.provider import DockerProvider
from providers.proxmox.provider import ProxmoxProvider
from proxmoxer import ProxmoxAPI


def _settings(**overrides: Any) -> Settings:
    defaults: dict[str, Any] = dict(
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


async def test_proxmox_wait_for_task_accepts_warnings_exitstatus():
    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_client.cluster.nextid.get.return_value = "101"
    fake_client.nodes.return_value.lxc.return_value.clone.post.return_value = "UPID:starcore:clone"
    fake_client.nodes.return_value.tasks.return_value.status.get.return_value = {
        "status": "stopped",
        "exitstatus": "WARNINGS: 1",
    }
    provider = ProxmoxProvider()
    provider._client = fake_client
    task = Task(
        id="1",
        provider="proxmox",
        action="create",
        kind="lxc",
        resource="test-ct",
        payload={"node": "starcore", "template_vmid": 100, "cores": 1, "memory": 512},
    )
    await provider.execute(task)
    assert task.result["vmid"] == 101


async def test_proxmox_create_lxc_uses_put_for_config_update():
    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_client.cluster.nextid.get.return_value = "103"
    fake_client.nodes.return_value.lxc.return_value.clone.post.return_value = "UPID:starcore:clone"
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
        kind="lxc",
        resource="test-ct",
        payload={"node": "starcore", "template_vmid": 100, "cores": 1, "memory": 512},
    )
    await provider.execute(task)
    fake_client.nodes.return_value.lxc.return_value.config.put.assert_called_once_with(
        cores=1, memory=512
    )
    fake_client.nodes.return_value.lxc.return_value.config.post.assert_not_called()


async def test_proxmox_create_vm_still_uses_post_for_config_update():
    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_client.cluster.nextid.get.return_value = "104"
    fake_client.nodes.return_value.qemu.return_value.clone.post.return_value = "UPID:starcore:clone"
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
        payload={"node": "starcore", "template_vmid": 9000, "cores": 2, "memory": 2048},
    )
    await provider.execute(task)
    fake_client.nodes.return_value.qemu.return_value.config.post.assert_called_once_with(
        cores=2, memory=2048
    )
    fake_client.nodes.return_value.qemu.return_value.config.put.assert_not_called()


async def test_proxmox_wait_for_task_raises_on_real_error_exitstatus():
    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_client.cluster.nextid.get.return_value = "102"
    fake_client.nodes.return_value.lxc.return_value.clone.post.return_value = "UPID:starcore:clone"
    fake_client.nodes.return_value.tasks.return_value.status.get.return_value = {
        "status": "stopped",
        "exitstatus": "unable to allocate storage",
    }
    provider = ProxmoxProvider()
    provider._client = fake_client
    task = Task(
        id="1",
        provider="proxmox",
        action="create",
        kind="lxc",
        resource="test-ct",
        payload={"node": "starcore", "template_vmid": 100},
    )
    try:
        await provider.execute(task)
        raise AssertionError("expected RuntimeError")
    except RuntimeError as exc:
        assert "unable to allocate storage" in str(exc)


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
    fake_client.nodes.return_value.lxc.return_value.config.put.assert_called_once_with(
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


async def test_proxmox_node_status_returns_node_metrics():
    fake_client = MagicMock()
    fake_client.nodes.get.return_value = [{"node": "fatalab"}]
    fake_client.nodes.return_value.status.get.return_value = {
        "cpu": 0.42,
        "memory": {"used": 4_000_000_000, "total": 16_000_000_000},
        "rootfs": {"used": 20_000_000_000, "total": 100_000_000_000},
    }

    provider = ProxmoxProvider()
    provider._client = fake_client

    result = await provider.node_status()

    assert result[0]["node"] == "fatalab"
    assert result[0]["cpu"] == 0.42


async def test_proxmox_storage_status_returns_storage_list():
    fake_client = MagicMock()
    fake_client.nodes.get.return_value = [{"node": "fatalab"}]
    fake_client.nodes.return_value.storage.get.return_value = [
        {"storage": "local-zfs", "type": "zfspool", "used": 1000, "total": 5000}
    ]

    provider = ProxmoxProvider()
    provider._client = fake_client

    result = await provider.storage_status()

    assert result[0]["storage"] == "local-zfs"
    assert result[0]["node"] == "fatalab"


async def test_proxmox_snapshot_create_calls_snapshot_endpoint():
    from unittest.mock import MagicMock

    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_client.nodes.return_value.qemu.return_value.snapshot.post.return_value = "UPID:test"
    fake_client.nodes.return_value.tasks.return_value.status.get.return_value = {
        "status": "stopped",
        "exitstatus": "OK",
    }

    provider = ProxmoxProvider()
    provider._client = fake_client

    task = Task(
        id="1",
        provider="proxmox",
        action="snapshot-create",
        resource="web-vm",
        payload={"node": "fatalab", "vmid": 105, "snapshot_name": "before-upgrade"},
    )

    await provider.execute(task)

    fake_client.nodes.return_value.qemu.return_value.snapshot.post.assert_called_once_with(
        snapname="before-upgrade"
    )
    assert task.result["snapshot_name"] == "before-upgrade"


async def test_proxmox_snapshot_create_requires_snapshot_name():
    from orchestrator.task import Task

    provider = ProxmoxProvider()
    provider._client = cast(ProxmoxAPI, object())

    task = Task(
        id="1",
        provider="proxmox",
        action="snapshot-create",
        resource="web-vm",
        payload={"node": "fatalab", "vmid": 105},
    )

    with pytest.raises(ValueError):
        await provider.execute(task)


async def test_proxmox_snapshot_list_filters_out_current():
    from unittest.mock import MagicMock

    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_client.nodes.return_value.qemu.return_value.snapshot.get.return_value = [
        {"name": "before-upgrade", "snaptime": 1000},
        {"name": "current"},
    ]

    provider = ProxmoxProvider()
    provider._client = fake_client

    task = Task(
        id="1",
        provider="proxmox",
        action="snapshot-list",
        resource="web-vm",
        payload={"node": "fatalab", "vmid": 105},
    )

    await provider.execute(task)

    assert len(task.result["snapshots"]) == 1
    assert task.result["snapshots"][0]["name"] == "before-upgrade"


async def test_proxmox_snapshot_delete_calls_correct_endpoint():
    from unittest.mock import MagicMock

    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_client.nodes.return_value.qemu.return_value.snapshot.return_value.delete
    fake_client.nodes.return_value.qemu.return_value.snapshot.return_value.delete.return_value = (
        None
    )

    provider = ProxmoxProvider()
    provider._client = fake_client

    task = Task(
        id="1",
        provider="proxmox",
        action="snapshot-delete",
        resource="web-vm",
        payload={"node": "fatalab", "vmid": 105, "snapshot_name": "old-snap"},
    )

    await provider.execute(task)

    fake_client.nodes.return_value.qemu.return_value.snapshot.assert_called_with("old-snap")
    assert task.result["snapshot_name"] == "old-snap"


async def test_proxmox_snapshot_rollback_calls_rollback_endpoint():
    from unittest.mock import MagicMock

    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_rollback = MagicMock()
    fake_rollback.post.return_value = "UPID:test"
    fake_client.nodes.return_value.qemu.return_value.snapshot.return_value.rollback = fake_rollback
    fake_client.nodes.return_value.tasks.return_value.status.get.return_value = {
        "status": "stopped",
        "exitstatus": "OK",
    }

    provider = ProxmoxProvider()
    provider._client = fake_client

    task = Task(
        id="1",
        provider="proxmox",
        action="snapshot-rollback",
        resource="web-vm",
        payload={"node": "fatalab", "vmid": 105, "snapshot_name": "old-snap"},
    )

    await provider.execute(task)

    fake_rollback.post.assert_called_once()
    assert task.result["snapshot_name"] == "old-snap"


# ---------------------------------------------------------------------------
# RISK-01 / TD-02 regression tests: provider connect() must be safe under
# concurrent invocation from multiple orchestration tasks in the same
# scheduler wave (see orchestrator/scheduler.py, Scheduler.execute).
# ---------------------------------------------------------------------------


async def test_base_provider_connect_lock_is_memoized_and_instance_scoped():
    """The lock is created once per instance and never shared across instances."""

    class _MinimalProvider(BaseProvider):
        name = "minimal"

        async def connect(self) -> bool:
            return True

        async def disconnect(self) -> None:
            return None

        async def health(self) -> dict:
            return {"status": "ok", "provider": self.name}

        async def list_resources(self) -> list[dict]:
            return []

        async def execute(self, task) -> None:
            return None

    provider_a = _MinimalProvider()
    provider_b = _MinimalProvider()

    # Same instance -> same lock object across repeated access.
    assert provider_a._connect_lock is provider_a._connect_lock
    # Different instances -> independent locks.
    assert provider_a._connect_lock is not provider_b._connect_lock
    assert isinstance(provider_a._connect_lock, asyncio.Lock)


async def test_proxmox_connect_is_safe_under_concurrent_calls():
    """Concurrent connect() calls on one shared ProxmoxProvider instance
    must perform the actual (slow) connection handshake exactly once.
    """
    call_count = 0

    def _slow_constructor(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        time.sleep(0.05)  # simulates the blocking handshake done in a thread
        client = MagicMock()
        client.version.get.return_value = {"version": "8.0"}
        return client

    settings = _settings(
        proxmox_host="fatalab.local",
        proxmox_user="root@pam",
        proxmox_token_name="starcore",
        proxmox_token_value="secret",
    )

    with (
        patch("providers.proxmox.provider.get_settings", return_value=settings),
        patch("providers.proxmox.provider.ProxmoxAPI", side_effect=_slow_constructor),
    ):
        provider = ProxmoxProvider()
        results = await asyncio.gather(provider.connect(), provider.connect(), provider.connect())

    assert results == [True, True, True]
    assert call_count == 1
    assert provider._client is not None


async def test_proxmox_connect_failure_is_visible_to_all_concurrent_callers():
    """If the (single) real connection attempt fails, every concurrent
    caller must observe the failure -- not just the one that happened to
    perform the actual work.
    """
    settings = _settings()  # no credentials configured -> connect() fails fast

    with patch("providers.proxmox.provider.get_settings", return_value=settings):
        provider = ProxmoxProvider()
        results = await asyncio.gather(provider.connect(), provider.connect())

    assert results == [False, False]
    assert provider._client is None


async def test_docker_connect_is_safe_under_concurrent_calls():
    """Concurrent connect() calls on one shared DockerProvider instance
    must construct the underlying Docker client exactly once.
    """
    call_count = 0

    def _slow_from_env(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        time.sleep(0.05)  # simulates the blocking daemon handshake
        client = MagicMock()
        client.ping.return_value = True
        return client

    with patch("providers.docker.provider.docker.from_env", side_effect=_slow_from_env):
        provider = DockerProvider()
        results = await asyncio.gather(provider.connect(), provider.connect(), provider.connect())

    assert results == [True, True, True]
    assert call_count == 1
    assert provider._client is not None


async def test_docker_disconnect_is_idempotent_under_concurrent_calls():
    fake_client = MagicMock()

    provider = DockerProvider()
    provider._client = fake_client

    await asyncio.gather(provider.disconnect(), provider.disconnect())

    fake_client.close.assert_called_once()
    assert provider._client is None


# ---------------------------------------------------------------------------
# DockerProvider — connect() edge cases
# ---------------------------------------------------------------------------


async def test_docker_connect_fails_when_daemon_unavailable():
    with patch(
        "providers.docker.provider.docker.from_env",
        side_effect=DockerException("daemon not running"),
    ):
        provider = DockerProvider()
        result = await provider.connect()

    assert result is False
    assert provider._client is None


async def test_docker_connect_already_connected_skips_construction():
    """connect() is a no-op when _client is already set."""
    fake_client = MagicMock()
    provider = DockerProvider()
    provider._client = fake_client

    call_count = 0

    def _from_env():
        nonlocal call_count
        call_count += 1
        return MagicMock()

    with patch("providers.docker.provider.docker.from_env", side_effect=_from_env):
        result = await provider.connect()

    assert result is True
    assert call_count == 0
    assert provider._client is fake_client


# ---------------------------------------------------------------------------
# DockerProvider — health()
# ---------------------------------------------------------------------------


async def test_docker_health_disconnected():
    provider = DockerProvider()
    result = await provider.health()

    assert result["status"] == "disconnected"
    assert result["provider"] == "docker"


async def test_docker_health_ok_when_connected():
    fake_client = MagicMock()
    fake_client.ping.return_value = True

    provider = DockerProvider()
    provider._client = fake_client

    result = await provider.health()

    assert result["status"] == "ok"
    assert result["provider"] == "docker"


async def test_docker_health_error_when_ping_raises():
    fake_client = MagicMock()
    fake_client.ping.side_effect = DockerException("connection refused")

    provider = DockerProvider()
    provider._client = fake_client

    result = await provider.health()

    assert result["status"] == "error"
    assert result["provider"] == "docker"
    assert "connection refused" in result["detail"]


# ---------------------------------------------------------------------------
# DockerProvider — list_resources()
# ---------------------------------------------------------------------------


async def test_docker_list_resources_returns_empty_when_disconnected():
    provider = DockerProvider()
    result = await provider.list_resources()

    assert result == []


async def test_docker_list_resources_returns_container_list():
    fake_client = MagicMock()
    fake_image = MagicMock()
    fake_image.tags = ["nginx:latest"]
    fake_image.id = "sha256:aaa"
    fake_container = MagicMock()
    fake_container.id = "abc123"
    fake_container.name = "my-app"
    fake_container.status = "running"
    fake_container.image = fake_image
    fake_client.containers.list.return_value = [fake_container]

    provider = DockerProvider()
    provider._client = fake_client

    result = await provider.list_resources()

    assert len(result) == 1
    assert result[0] == {
        "id": "abc123",
        "name": "my-app",
        "status": "running",
        "image": "nginx:latest",
    }
    fake_client.containers.list.assert_called_once_with(all=True)


async def test_docker_list_resources_falls_back_to_image_id_when_no_tags():
    fake_client = MagicMock()
    fake_image = MagicMock()
    fake_image.tags = []
    fake_image.id = "sha256:bbb"
    fake_container = MagicMock()
    fake_container.id = "def456"
    fake_container.name = "tagless"
    fake_container.status = "stopped"
    fake_container.image = fake_image
    fake_client.containers.list.return_value = [fake_container]

    provider = DockerProvider()
    provider._client = fake_client

    result = await provider.list_resources()

    assert result[0]["image"] == "sha256:bbb"


async def test_docker_list_resources_handles_none_image():
    fake_client = MagicMock()
    fake_container = MagicMock()
    fake_container.id = "ghi789"
    fake_container.name = "no-image"
    fake_container.status = "created"
    fake_container.image = None
    fake_client.containers.list.return_value = [fake_container]

    provider = DockerProvider()
    provider._client = fake_client

    result = await provider.list_resources()

    assert result[0]["image"] is None


# ---------------------------------------------------------------------------
# DockerProvider — execute() dispatch
# ---------------------------------------------------------------------------


async def test_docker_execute_raises_when_not_connected():
    from orchestrator.task import Task

    provider = DockerProvider()
    task = Task(id="1", provider="docker", action="create", resource="web")

    with pytest.raises(RuntimeError, match="not connected"):
        await provider.execute(task)


async def test_docker_execute_create_new_container():
    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_client.containers.get.side_effect = NotFound("not found")

    provider = DockerProvider()
    provider._client = fake_client

    task = Task(
        id="1",
        provider="docker",
        action="create",
        resource="my-app",
        payload={"image": "nginx:latest"},
    )
    await provider.execute(task)

    fake_client.containers.run.assert_called_once_with(
        "nginx:latest", name="my-app", volumes=None, detach=True
    )


async def test_docker_execute_create_skips_existing_container():
    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_client.containers.get.return_value = MagicMock()

    provider = DockerProvider()
    provider._client = fake_client

    task = Task(
        id="1",
        provider="docker",
        action="create",
        resource="already-running",
        payload={"image": "nginx:latest"},
    )
    await provider.execute(task)

    fake_client.containers.run.assert_not_called()


async def test_docker_execute_create_raises_without_image():
    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_client.containers.get.side_effect = NotFound("not found")

    provider = DockerProvider()
    provider._client = fake_client

    task = Task(id="1", provider="docker", action="create", resource="my-app", payload={})

    with pytest.raises(ValueError, match="image"):
        await provider.execute(task)


async def test_docker_execute_create_with_volume():
    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_client.containers.get.side_effect = NotFound("not found")

    provider = DockerProvider()
    provider._client = fake_client

    task = Task(
        id="1",
        provider="docker",
        action="create",
        resource="app",
        payload={"image": "redis:7", "volume": "app-data"},
    )
    await provider.execute(task)

    _, kwargs = fake_client.containers.run.call_args
    assert kwargs["volumes"] == {"app-data": {"bind": "/data/app-data", "mode": "rw"}}


async def test_docker_execute_start():
    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_container = MagicMock()
    fake_client.containers.get.return_value = fake_container

    provider = DockerProvider()
    provider._client = fake_client

    task = Task(id="1", provider="docker", action="start", resource="my-app")
    await provider.execute(task)

    fake_client.containers.get.assert_called_with("my-app")
    fake_container.start.assert_called_once_with()


async def test_docker_execute_stop():
    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_container = MagicMock()
    fake_client.containers.get.return_value = fake_container

    provider = DockerProvider()
    provider._client = fake_client

    task = Task(id="1", provider="docker", action="stop", resource="my-app")
    await provider.execute(task)

    fake_container.stop.assert_called_once_with()


async def test_docker_execute_remove():
    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_container = MagicMock()
    fake_client.containers.get.return_value = fake_container

    provider = DockerProvider()
    provider._client = fake_client

    task = Task(id="1", provider="docker", action="remove", resource="my-app")
    await provider.execute(task)

    fake_container.remove.assert_called_once_with(force=True)


async def test_docker_execute_unsupported_action_raises():
    from orchestrator.task import Task

    fake_client = MagicMock()
    provider = DockerProvider()
    provider._client = fake_client

    task = Task(id="1", provider="docker", action="destroy", resource="my-app")

    with pytest.raises(ValueError, match="Unsupported Docker action"):
        await provider.execute(task)


# ---------------------------------------------------------------------------
# ProxmoxProvider — additional coverage
# ---------------------------------------------------------------------------


async def test_proxmox_connect_fails_when_version_check_raises():
    """Lines 69-72: ProxmoxAPI constructs fine but version.get raises."""
    fake_client = MagicMock()
    fake_client.version.get.side_effect = Exception("connection refused")

    settings = _settings(
        proxmox_host="fatalab.local",
        proxmox_user="root@pam",
        proxmox_token_name="starcore",
        proxmox_token_value="secret",
    )

    with (
        patch("providers.proxmox.provider.get_settings", return_value=settings),
        patch("providers.proxmox.provider.ProxmoxAPI", return_value=fake_client),
    ):
        provider = ProxmoxProvider()
        result = await provider.connect()

    assert result is False
    assert provider._client is None


async def test_proxmox_disconnect_clears_client():
    """Lines 77-78: disconnect() sets _client to None."""
    provider = ProxmoxProvider()
    provider._client = MagicMock()
    await provider.disconnect()
    assert provider._client is None


async def test_proxmox_health_disconnected():
    """Line 81-82: health() returns disconnected when _client is None."""
    provider = ProxmoxProvider()
    result = await provider.health()
    assert result["status"] == "disconnected"
    assert result["provider"] == "proxmox"


async def test_proxmox_health_ok_when_connected():
    """Lines 83-85: health() returns ok when version.get succeeds."""
    fake_client = MagicMock()
    fake_client.version.get.return_value = {"version": "8.0"}
    provider = ProxmoxProvider()
    provider._client = fake_client
    result = await provider.health()
    assert result["status"] == "ok"
    assert result["provider"] == "proxmox"


async def test_proxmox_health_error_when_version_check_raises():
    """Lines 86-87: health() returns error when version.get raises."""
    fake_client = MagicMock()
    fake_client.version.get.side_effect = Exception("timeout")
    provider = ProxmoxProvider()
    provider._client = fake_client
    result = await provider.health()
    assert result["status"] == "error"
    assert "timeout" in result["detail"]


async def test_proxmox_list_resources_returns_empty_when_disconnected():
    """Lines 90-91: list_resources() returns [] when _client is None."""
    provider = ProxmoxProvider()
    result = await provider.list_resources()
    assert result == []


async def test_proxmox_list_resources_returns_vms_and_containers():
    """Lines 92-117: list_resources() returns VMs and LXC containers."""
    fake_client = MagicMock()
    fake_client.nodes.get.return_value = [{"node": "pve"}]
    fake_client.nodes.return_value.qemu.get.return_value = [
        {"vmid": 100, "name": "web-vm", "status": "running"}
    ]
    fake_client.nodes.return_value.lxc.get.return_value = [
        {"vmid": 200, "name": "db-ct", "status": "stopped"}
    ]

    provider = ProxmoxProvider()
    provider._client = fake_client

    result = await provider.list_resources()

    assert len(result) == 2
    vm = next(r for r in result if r["kind"] == "vm")
    ct = next(r for r in result if r["kind"] == "lxc")
    assert vm["vmid"] == 100
    assert ct["vmid"] == 200
    assert ct["node"] == "pve"


async def test_proxmox_list_templates_returns_empty_when_disconnected():
    """Line 121: list_templates() returns [] when _client is None."""
    provider = ProxmoxProvider()
    result = await provider.list_templates()
    assert result == []


async def test_proxmox_list_templates_returns_vm_and_lxc_templates():
    """Lines 122-148: list_templates() returns VMs and LXC containers marked template=1."""
    fake_client = MagicMock()
    fake_client.nodes.get.return_value = [{"node": "pve"}]
    fake_client.nodes.return_value.qemu.get.return_value = [
        {"vmid": 9000, "name": "ubuntu-22.04", "template": 1},
        {"vmid": 101, "name": "running-vm", "template": 0},
    ]
    fake_client.nodes.return_value.lxc.get.return_value = [
        {"vmid": 8000, "name": "debian-ct", "template": 1},
    ]

    provider = ProxmoxProvider()
    provider._client = fake_client

    result = await provider.list_templates()

    assert len(result) == 2
    vmids = {t["vmid"] for t in result}
    assert vmids == {9000, 8000}
    kinds = {t["kind"] for t in result}
    assert kinds == {"vm", "lxc"}


async def test_proxmox_list_networks_returns_empty_when_disconnected():
    """Line 152: list_networks() returns [] when _client is None."""
    provider = ProxmoxProvider()
    result = await provider.list_networks()
    assert result == []


async def test_proxmox_list_networks_returns_bridge_interfaces():
    """Lines 153-167: list_networks() returns only bridge-type interfaces."""
    fake_client = MagicMock()
    fake_client.nodes.get.return_value = [{"node": "pve"}]
    fake_client.nodes.return_value.network.get.return_value = [
        {"iface": "vmbr0", "type": "bridge", "active": 1},
        {"iface": "eth0", "type": "eth", "active": 1},
    ]

    provider = ProxmoxProvider()
    provider._client = fake_client

    result = await provider.list_networks()

    assert len(result) == 1
    assert result[0]["bridge"] == "vmbr0"
    assert result[0]["active"] is True
    assert result[0]["node"] == "pve"


async def test_proxmox_node_status_returns_empty_when_disconnected():
    """Line 171: node_status() returns [] when _client is None."""
    provider = ProxmoxProvider()
    result = await provider.node_status()
    assert result == []


async def test_proxmox_storage_status_returns_empty_when_disconnected():
    """Line 182: storage_status() returns [] when _client is None."""
    provider = ProxmoxProvider()
    result = await provider.storage_status()
    assert result == []


async def test_proxmox_execute_start_requires_node_and_vmid():
    """Line 209: execute() raises ValueError when node/vmid missing for start."""
    from orchestrator.task import Task

    provider = ProxmoxProvider()
    provider._client = MagicMock()

    task = Task(id="1", provider="proxmox", action="start", resource="web-vm", payload={})

    with pytest.raises(ValueError, match="node.*vmid"):
        await provider.execute(task)


async def test_proxmox_execute_raises_for_unsupported_action():
    """Line 229: execute() raises ValueError for unknown action."""
    from orchestrator.task import Task

    provider = ProxmoxProvider()
    provider._client = MagicMock()

    task = Task(id="1", provider="proxmox", action="teleport", resource="web-vm")

    with pytest.raises(ValueError, match="Unsupported Proxmox action"):
        await provider.execute(task)


async def test_proxmox_create_raises_when_nextid_returns_none():
    """Line 247: _create_resource() raises when cluster.nextid.get returns None."""
    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_client.cluster.nextid.get.return_value = None

    provider = ProxmoxProvider()
    provider._client = fake_client

    task = Task(
        id="1",
        provider="proxmox",
        action="create",
        resource="web-vm",
        payload={"node": "pve", "template_vmid": 9000},
    )

    with pytest.raises(RuntimeError, match="Failed to allocate next ID"):
        await provider.execute(task)


async def test_proxmox_create_uses_explicit_vmid_when_provided():
    """Line 250: _create_resource() uses payload vmid without calling nextid."""
    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_client.nodes.return_value.qemu.return_value.clone.post.return_value = "UPID:pve:clone"
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
        payload={"node": "pve", "template_vmid": 9000, "vmid": 150},
    )

    await provider.execute(task)

    assert task.result["vmid"] == 150
    fake_client.cluster.nextid.get.assert_not_called()


async def test_proxmox_create_passes_storage_and_target_node():
    """Lines 261, 263: _create_resource() forwards storage and target_node to clone."""
    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_client.cluster.nextid.get.return_value = "110"
    fake_client.nodes.return_value.qemu.return_value.clone.post.return_value = "UPID:pve:clone"
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
            "node": "pve",
            "template_vmid": 9000,
            "storage": "local-zfs",
            "target_node": "pve2",
        },
    )

    await provider.execute(task)

    kwargs = fake_client.nodes.return_value.qemu.return_value.clone.post.call_args.kwargs
    assert kwargs["storage"] == "local-zfs"
    assert kwargs["target"] == "pve2"


async def test_proxmox_create_raises_when_clone_returns_none_upid():
    """Line 268: _create_resource() raises when clone returns no task ID."""
    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_client.cluster.nextid.get.return_value = "111"
    fake_client.nodes.return_value.qemu.return_value.clone.post.return_value = None

    provider = ProxmoxProvider()
    provider._client = fake_client

    task = Task(
        id="1",
        provider="proxmox",
        action="create",
        resource="web-vm",
        payload={"node": "pve", "template_vmid": 9000},
    )

    with pytest.raises(RuntimeError, match="did not return a task ID"):
        await provider.execute(task)


async def test_proxmox_destroy_requires_node_and_vmid():
    """Line 309: _destroy_resource() raises ValueError when node/vmid missing."""
    from orchestrator.task import Task

    provider = ProxmoxProvider()
    provider._client = MagicMock()

    task = Task(
        id="1",
        provider="proxmox",
        action="destroy",
        resource="web-vm",
        payload={},
    )

    with pytest.raises(ValueError, match="node.*vmid"):
        await provider.execute(task)


async def test_proxmox_destroy_waits_for_task_when_upid_returned():
    """Line 324: _destroy_resource() calls _wait_for_task when delete returns upid."""
    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_client.nodes.return_value.qemu.return_value.delete.return_value = "UPID:pve:del"
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
        resource="web-vm",
        payload={"node": "pve", "vmid": 150},
    )

    await provider.execute(task)

    fake_client.nodes.return_value.tasks.return_value.status.get.assert_called()
    assert task.result["vmid"] == 150


async def test_proxmox_destroy_passes_purge_and_force_flags():
    """Lines 316, 318: _destroy_resource() includes purge/force in delete call."""
    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_client.nodes.return_value.qemu.return_value.delete.return_value = None

    provider = ProxmoxProvider()
    provider._client = fake_client

    task = Task(
        id="1",
        provider="proxmox",
        action="destroy",
        resource="web-vm",
        payload={"node": "pve", "vmid": 150, "purge": True, "force": True},
    )

    await provider.execute(task)

    fake_client.nodes.return_value.qemu.return_value.delete.assert_called_once_with(
        purge=1, force=1
    )


async def test_proxmox_snapshot_create_requires_node_and_vmid():
    """Line 336: _require_snapshot_fields() raises when node/vmid missing."""
    from orchestrator.task import Task

    provider = ProxmoxProvider()
    provider._client = MagicMock()

    task = Task(
        id="1",
        provider="proxmox",
        action="snapshot-create",
        resource="web-vm",
        payload={"snapshot_name": "snap1"},
    )

    with pytest.raises(ValueError, match="node.*vmid"):
        await provider.execute(task)


async def test_proxmox_snapshot_create_passes_description():
    """Line 356: _snapshot_create() includes description in post kwargs."""
    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_client.nodes.return_value.qemu.return_value.snapshot.post.return_value = None

    provider = ProxmoxProvider()
    provider._client = fake_client

    task = Task(
        id="1",
        provider="proxmox",
        action="snapshot-create",
        resource="web-vm",
        payload={
            "node": "pve",
            "vmid": 105,
            "snapshot_name": "before-upgrade",
            "description": "pre-upgrade backup",
        },
    )

    await provider.execute(task)

    fake_client.nodes.return_value.qemu.return_value.snapshot.post.assert_called_once_with(
        snapname="before-upgrade", description="pre-upgrade backup"
    )


async def test_proxmox_snapshot_delete_waits_for_task_when_upid_returned():
    """Line 392: _snapshot_delete() calls _wait_for_task when upid is returned."""
    from orchestrator.task import Task

    fake_client = MagicMock()
    fake_client.nodes.return_value.qemu.return_value.snapshot.return_value.delete.return_value = (
        "UPID:pve:del"
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
        action="snapshot-delete",
        resource="web-vm",
        payload={"node": "pve", "vmid": 105, "snapshot_name": "old-snap"},
    )

    await provider.execute(task)

    fake_client.nodes.return_value.tasks.return_value.status.get.assert_called()
    assert task.result["snapshot_name"] == "old-snap"


async def test_proxmox_wait_for_task_raises_when_status_is_none():
    """Line 432: _wait_for_task() raises RuntimeError when status.get returns None."""
    fake_client = MagicMock()
    fake_client.nodes.return_value.tasks.return_value.status.get.return_value = None

    provider = ProxmoxProvider()
    provider._client = fake_client

    with pytest.raises(RuntimeError, match="no status"):
        await provider._wait_for_task("pve", "UPID:pve:test")


async def test_proxmox_wait_for_task_raises_timeout_when_task_never_stops():
    """Lines 442-444: _wait_for_task() raises TimeoutError after timeout elapses."""
    from unittest.mock import AsyncMock as _AsyncMock

    fake_client = MagicMock()
    fake_client.nodes.return_value.tasks.return_value.status.get.return_value = {
        "status": "running"
    }

    provider = ProxmoxProvider()
    provider._client = fake_client

    with patch("asyncio.sleep", new=_AsyncMock()):
        with pytest.raises(TimeoutError, match="did not complete"):
            await provider._wait_for_task("pve", "UPID:pve:test", timeout=0.001, interval=1.0)
