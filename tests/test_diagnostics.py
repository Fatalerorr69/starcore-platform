"""
Diagnostics Tests
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from core.config import get_settings
from core.database import get_session
from core.diagnostics import CheckResult, run_diagnostics
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


async def test_check_database_creates_missing_sqlite_directory(tmp_path, monkeypatch):
    nested_path = tmp_path / "fresh_clone" / "data" / "starcore.db"
    monkeypatch.setenv("STARCORE_DATABASE_URL", f"sqlite:///{nested_path}")
    get_settings.cache_clear()
    try:
        report = await run_diagnostics()
        db_check = next(c for c in report["checks"] if c["name"] == "config.database")
        assert db_check["status"] == "ok"
        assert nested_path.parent.exists()
    finally:
        get_settings.cache_clear()


def test_check_database_connectivity_returns_error_when_engine_fails():
    """Lines 60-61: check_database_connectivity() error path when DB is unreachable."""
    from core.diagnostics import check_database_connectivity

    with patch("core.diagnostics.create_engine", side_effect=Exception("cannot reach database")):
        result = check_database_connectivity()
    assert result.status == "error"
    assert "Cannot connect" in result.detail


def test_check_api_key_returns_warning_without_api_key(monkeypatch):
    """Line 38: _check_api_key() warning path when no key is configured."""
    from core.diagnostics import _check_api_key

    monkeypatch.delenv("STARCORE_API_KEY", raising=False)
    get_settings.cache_clear()
    try:
        result = _check_api_key()
        assert result.status == "warning"
    finally:
        get_settings.cache_clear()


def test_check_migrations_returns_ok_when_db_is_at_head(tmp_path, monkeypatch):
    """Line 73: _check_migrations() "ok" path when DB revision matches head.

    _isolated_database autouse fixture already created and stamped this DB at
    head, so pointing settings at the same URL should yield status "ok".
    """
    from core.diagnostics import _check_migrations

    db_url = f"sqlite:///{tmp_path / 'test.db'}"
    monkeypatch.setenv("STARCORE_DATABASE_URL", db_url)
    get_settings.cache_clear()
    try:
        result = _check_migrations()
        assert result.status == "ok"
    finally:
        get_settings.cache_clear()


def test_check_migrations_returns_error_on_exception():
    """Lines 80-81: _check_migrations() error path when an exception is raised."""
    from core.diagnostics import _check_migrations

    with patch("core.diagnostics.get_migration_head", side_effect=RuntimeError("cfg missing")):
        result = _check_migrations()
    assert result.status == "error"
    assert "Could not verify migrations" in result.detail


def test_check_proxmox_config_returns_ok_when_all_credentials_set(monkeypatch):
    """Line 94: _check_proxmox_config() "ok" path when all four vars are present."""
    from core.diagnostics import _check_proxmox_config

    monkeypatch.setenv("STARCORE_PROXMOX_HOST", "192.168.1.100")
    monkeypatch.setenv("STARCORE_PROXMOX_USER", "root@pam")
    monkeypatch.setenv("STARCORE_PROXMOX_TOKEN_NAME", "my-token")
    monkeypatch.setenv("STARCORE_PROXMOX_TOKEN_VALUE", "secret-value")
    get_settings.cache_clear()
    try:
        result = _check_proxmox_config()
        assert result.status == "ok"
    finally:
        get_settings.cache_clear()


async def test_diagnose_proxmox_returns_error_when_not_in_registry():
    """Line 120: early return when proxmox provider is absent from registry."""
    from core.diagnostics import _diagnose_proxmox

    with patch("core.diagnostics.register_default_providers"):
        check, _ = await _diagnose_proxmox()
    assert check.status == "error"
    assert "not registered" in check.detail


async def test_diagnose_proxmox_returns_error_on_exception_in_inspection():
    """Lines 186-187: exception raised inside the inspection try block is caught."""
    from core.diagnostics import _diagnose_proxmox

    class _RaisingProxmox(BaseProvider):
        name = "proxmox"

        async def connect(self) -> bool:
            return True

        async def disconnect(self) -> None:
            pass

        async def health(self) -> dict:
            return {}

        async def list_resources(self) -> list[dict]:
            raise RuntimeError("proxmox API error")

        async def execute(self, task) -> None:
            pass

    registry.register(_RaisingProxmox())
    check, _ = await _diagnose_proxmox()
    assert check.status == "error"
    assert "Diagnostics failed" in check.detail


async def test_diagnose_docker_returns_error_when_not_in_registry():
    """Line 200: early return when docker provider is absent from registry."""
    from core.diagnostics import _diagnose_docker

    with patch("core.diagnostics.register_default_providers"):
        check, _ = await _diagnose_docker()
    assert check.status == "error"
    assert "not registered" in check.detail


async def test_diagnose_docker_happy_path():
    """Lines 213-223, 229-230: successful connect + list_resources returns ok."""
    from core.diagnostics import _diagnose_docker

    class _FakeDocker(BaseProvider):
        name = "docker"

        async def connect(self) -> bool:
            return True

        async def disconnect(self) -> None:
            pass

        async def health(self) -> dict:
            return {"status": "ok"}

        async def list_resources(self) -> list[dict]:
            return [
                {"id": "a1", "name": "web", "status": "running"},
                {"id": "b2", "name": "db", "status": "stopped"},
            ]

        async def execute(self, task) -> None:
            pass

    registry.register(_FakeDocker())
    check, details = await _diagnose_docker()
    assert check.status == "ok"
    assert "2 container(s)" in check.detail
    assert details["containers"]["running"] == 1
    assert details["containers"]["stopped"] == 1


async def test_diagnose_docker_returns_error_on_exception_in_inspection():
    """Lines 224-228: exception raised inside the inspection try block is caught."""
    from core.diagnostics import _diagnose_docker

    class _RaisingDocker(BaseProvider):
        name = "docker"

        async def connect(self) -> bool:
            return True

        async def disconnect(self) -> None:
            pass

        async def health(self) -> dict:
            return {}

        async def list_resources(self) -> list[dict]:
            raise RuntimeError("docker daemon error")

        async def execute(self, task) -> None:
            pass

    registry.register(_RaisingDocker())
    check, _ = await _diagnose_docker()
    assert check.status == "error"
    assert "Diagnostics failed" in check.detail


async def test_run_diagnostics_overall_status_is_warning():
    """Lines 249-250: overall = "warning" when some checks warn but none error."""
    ok = CheckResult("x", "ok", "fine")
    warn = CheckResult("y", "warning", "heads up")

    with (
        patch("core.diagnostics._check_api_key", return_value=ok),
        patch("core.diagnostics.check_database_connectivity", return_value=ok),
        patch("core.diagnostics._check_migrations", return_value=warn),
        patch("core.diagnostics._check_proxmox_config", return_value=ok),
        patch("core.diagnostics._diagnose_proxmox", new=AsyncMock(return_value=(ok, {}))),
        patch("core.diagnostics._diagnose_docker", new=AsyncMock(return_value=(ok, {}))),
    ):
        report = await run_diagnostics()
    assert report["overall_status"] == "warning"


async def test_run_diagnostics_overall_status_is_ok():
    """Lines 251-252: overall = "ok" when every check passes."""
    ok = CheckResult("x", "ok", "fine")

    with (
        patch("core.diagnostics._check_api_key", return_value=ok),
        patch("core.diagnostics.check_database_connectivity", return_value=ok),
        patch("core.diagnostics._check_migrations", return_value=ok),
        patch("core.diagnostics._check_proxmox_config", return_value=ok),
        patch("core.diagnostics._diagnose_proxmox", new=AsyncMock(return_value=(ok, {}))),
        patch("core.diagnostics._diagnose_docker", new=AsyncMock(return_value=(ok, {}))),
    ):
        report = await run_diagnostics()
    assert report["overall_status"] == "ok"
