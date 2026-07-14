"""
Diagnostics

Performs a deep health/status check of the STARCORE deployment itself
and of the configured infrastructure providers (Docker, Proxmox).
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from provider_sdk.registry import register_default_providers, registry
from sqlalchemy import create_engine

from core.config import get_settings
from core.database import get_session
from core.repository import list_known_provider_vmids


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str


def _check_api_key() -> CheckResult:
    settings = get_settings()
    if settings.api_key:
        return CheckResult("config.api_key", "ok", "API key is configured")
    return CheckResult(
        "config.api_key",
        "warning",
        "STARCORE_API_KEY is not set; protected endpoints will return 503",
    )


def _check_database() -> CheckResult:
    settings = get_settings()
    try:
        engine = create_engine(settings.database_url)
        with engine.connect():
            pass
        return CheckResult("config.database", "ok", f"Connected to {settings.database_url}")
    except Exception as exc:
        return CheckResult("config.database", "error", f"Cannot connect to database: {exc}")


def _check_migrations() -> CheckResult:
    settings = get_settings()
    try:
        cfg = Config("alembic.ini")
        cfg.set_main_option("sqlalchemy.url", settings.database_url)
        script = ScriptDirectory.from_config(cfg)
        head = script.get_current_head()

        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            context = MigrationContext.configure(conn)
            current = context.get_current_revision()

        if current == head:
            return CheckResult("config.migrations", "ok", f"Database schema is at head ({head})")
        return CheckResult(
            "config.migrations",
            "warning",
            f"Database at revision {current!r}, expected head {head!r}. "
            "Run 'alembic upgrade head'.",
        )
    except Exception as exc:
        return CheckResult("config.migrations", "error", f"Could not verify migrations: {exc}")


def _check_proxmox_config() -> CheckResult:
    settings = get_settings()
    if all(
        [
            settings.proxmox_host,
            settings.proxmox_user,
            settings.proxmox_token_name,
            settings.proxmox_token_value,
        ]
    ):
        return CheckResult("config.proxmox", "ok", "Proxmox credentials are configured")
    return CheckResult(
        "config.proxmox",
        "warning",
        "Proxmox credentials are not fully set (see .env.example)",
    )


def _known_vmids_sync(provider_name: str) -> set[int]:
    session = get_session()
    try:
        return list_known_provider_vmids(session, provider_name)
    finally:
        session.close()


async def _diagnose_proxmox() -> tuple[CheckResult, dict[str, Any]]:
    register_default_providers()
    details: dict[str, Any] = {
        "nodes": [],
        "storage": [],
        "resources": {},
        "orphaned_resources": [],
    }

    if "proxmox" not in registry.names():
        return (
            CheckResult("provider.proxmox", "error", "Proxmox provider is not registered"),
            details,
        )

    provider = registry.get("proxmox")
    connected = await provider.connect()
    if not connected:
        return (
            CheckResult("provider.proxmox", "error", "Failed to connect to Proxmox API"),
            details,
        )

    try:
        node_status_fn = getattr(provider, "node_status", None)
        storage_status_fn = getattr(provider, "storage_status", None)

        raw_nodes = await node_status_fn() if node_status_fn else []
        for node in raw_nodes:
            mem = node.get("memory", {}) or {}
            disk = node.get("rootfs", {}) or {}
            details["nodes"].append(
                {
                    "node": node.get("node"),
                    "cpu_percent": round(float(node.get("cpu", 0) or 0) * 100, 1),
                    "memory_used_gb": round(mem.get("used", 0) / 1e9, 2),
                    "memory_total_gb": round(mem.get("total", 0) / 1e9, 2),
                    "disk_used_gb": round(disk.get("used", 0) / 1e9, 2),
                    "disk_total_gb": round(disk.get("total", 0) / 1e9, 2),
                }
            )

        raw_storage = await storage_status_fn() if storage_status_fn else []
        for storage in raw_storage:
            details["storage"].append(
                {
                    "node": storage.get("node"),
                    "storage": storage.get("storage"),
                    "type": storage.get("type"),
                    "used_gb": round(storage.get("used", 0) / 1e9, 2),
                    "total_gb": round(storage.get("total", 0) / 1e9, 2),
                }
            )

        resources = await provider.list_resources()
        counts: dict[str, dict[str, int]] = {}
        for res in resources:
            kind = res.get("kind", "unknown")
            status_name = res.get("status", "unknown")
            counts.setdefault(kind, {})
            counts[kind][status_name] = counts[kind].get(status_name, 0) + 1
        details["resources"] = counts

        known_vmids = await asyncio.to_thread(_known_vmids_sync, "proxmox")
        orphaned = [
            res
            for res in resources
            if res.get("vmid") is not None and int(res["vmid"]) not in known_vmids
        ]
        details["orphaned_resources"] = orphaned

        detail_msg = (
            f"{len(details['nodes'])} node(s), {len(resources)} resource(s), "
            f"{len(orphaned)} orphaned"
        )
        return CheckResult("provider.proxmox", "ok", detail_msg), details
    except Exception as exc:
        return (
            CheckResult("provider.proxmox", "error", f"Diagnostics failed: {exc}"),
            details,
        )
    finally:
        await provider.disconnect()


async def _diagnose_docker() -> tuple[CheckResult, dict[str, Any]]:
    register_default_providers()
    details: dict[str, Any] = {"containers": {}}

    if "docker" not in registry.names():
        return (
            CheckResult("provider.docker", "error", "Docker provider is not registered"),
            details,
        )

    provider = registry.get("docker")
    connected = await provider.connect()
    if not connected:
        return (
            CheckResult("provider.docker", "error", "Failed to connect to Docker daemon"),
            details,
        )

    try:
        resources = await provider.list_resources()
        counts: dict[str, int] = {}
        for res in resources:
            status_name = res.get("status", "unknown")
            counts[status_name] = counts.get(status_name, 0) + 1
        details["containers"] = counts
        return (
            CheckResult("provider.docker", "ok", f"{len(resources)} container(s)"),
            details,
        )
    except Exception as exc:
        return (
            CheckResult("provider.docker", "error", f"Diagnostics failed: {exc}"),
            details,
        )
    finally:
        await provider.disconnect()


async def run_diagnostics() -> dict[str, Any]:
    checks: list[CheckResult] = [
        _check_api_key(),
        _check_database(),
        _check_migrations(),
        _check_proxmox_config(),
    ]

    proxmox_check, proxmox_details = await _diagnose_proxmox()
    checks.append(proxmox_check)

    docker_check, docker_details = await _diagnose_docker()
    checks.append(docker_check)

    if any(c.status == "error" for c in checks):
        overall = "error"
    elif any(c.status == "warning" for c in checks):
        overall = "warning"
    else:
        overall = "ok"

    return {
        "overall_status": overall,
        "checks": [{"name": c.name, "status": c.status, "detail": c.detail} for c in checks],
        "proxmox": proxmox_details,
        "docker": docker_details,
    }
