"""
Diagnostics Tests
"""

from __future__ import annotations

import pytest
from core.database import get_session
from core.diagnostics import run_diagnostics
from core.repository import save_run
from orchestrator.task import Task, TaskStatus
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
        return [
            {"node": "fatalab", "vmid": 105, "name": "web-vm", "status": "running", "kind": "vm"},
            {"node": "fatalab", "vmid": 999, "name": "ghost-vm", "status": "stopped", "kind": "vm"},
        ]

    async def execute(self, task) -> None:
        return None

    async def node_status(self) -> list[dict]:
        return [
            {
                "node": "fatalab",
                "cpu": 0.15,
                "memory": {"used": 8_000_000_000, "total": 24_000_000_000},
                "rootfs": {"used": 50_000_000_000, "total": 200_000_000_000},
            }
        ]

    async def storage_status(self) -> list[dict]:
        return [
            {
                "node": "fatalab",
                "storage": "local-zfs",
                "type": "zfspool",
                "used": 100_000_000_000,
                "total": 500_000_000_000,
            }
        ]


@pytest.fixture(autouse=True)
def clean_registry():
    registry._providers.clear()
    yield
    registry._providers.clear()


async def test_run_diagnostics_reports_proxmox_node_and_storage_stats():
    registry.register(FakeProxmoxProvider())

    report = await run_diagnostics()

    assert report["proxmox"]["nodes"][0]["node"] == "fatalab"
    assert report["proxmox"]["nodes"][0]["cpu_percent"] == 15.0
    assert report["proxmox"]["storage"][0]["storage"] == "local-zfs"


async def test_run_diagnostics_flags_orphaned_resources_not_in_run_history():
    registry.register(FakeProxmoxProvider())

    session = get_session()
    try:
        task = Task(id="t1", provider="proxmox", action="create", resource="web-vm")
        task.status = TaskStatus.SUCCESS
        task.result = {"vmid": 105, "node": "fatalab"}
        save_run(session, "demo", "1.0", False, [task])
    finally:
        session.close()

    report = await run_diagnostics()
    orphaned_vmids = {r["vmid"] for r in report["proxmox"]["orphaned_resources"]}

    assert 999 in orphaned_vmids
    assert 105 not in orphaned_vmids


async def test_run_diagnostics_includes_config_checks():
    report = await run_diagnostics()
    check_names = {c["name"] for c in report["checks"]}

    assert "config.api_key" in check_names
    assert "config.database" in check_names
    assert "config.migrations" in check_names
    assert "config.proxmox" in check_names


async def test_run_diagnostics_overall_status_reflects_docker_unavailable():
    report = await run_diagnostics()
    assert report["overall_status"] in ("warning", "error")
