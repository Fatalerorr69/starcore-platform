"""
Environment Discovery

Catalogs what's available on the configured Proxmox host (templates,
storage, networks, node capacity) so deployments can be tailored to
the actual environment instead of guessed at. Unlike diagnostics.py
(is everything healthy?), this answers "what can I deploy into?".
"""

from __future__ import annotations

from typing import Any

from provider_sdk.registry import register_default_providers, registry


def _format_node(node: dict) -> dict:
    mem = node.get("memory", {}) or {}
    disk = node.get("rootfs", {}) or {}
    return {
        "node": node.get("node"),
        "cpu_percent": round(float(node.get("cpu", 0) or 0) * 100, 1),
        "memory_used_gb": round(mem.get("used", 0) / 1e9, 2),
        "memory_total_gb": round(mem.get("total", 0) / 1e9, 2),
        "disk_used_gb": round(disk.get("used", 0) / 1e9, 2),
        "disk_total_gb": round(disk.get("total", 0) / 1e9, 2),
    }


def _format_storage(storage: dict) -> dict:
    return {
        "node": storage.get("node"),
        "storage": storage.get("storage"),
        "type": storage.get("type"),
        "used_gb": round(storage.get("used", 0) / 1e9, 2),
        "total_gb": round(storage.get("total", 0) / 1e9, 2),
    }


async def discover_proxmox_environment() -> dict[str, Any]:
    register_default_providers()

    if "proxmox" not in registry.names():
        return {"connected": False, "error": "Proxmox provider is not registered"}

    provider = registry.get("proxmox")
    connected = await provider.connect()
    if not connected:
        return {"connected": False, "error": "Failed to connect to Proxmox API"}

    try:
        node_status_fn = getattr(provider, "node_status", None)
        storage_status_fn = getattr(provider, "storage_status", None)
        list_templates_fn = getattr(provider, "list_templates", None)
        list_networks_fn = getattr(provider, "list_networks", None)

        raw_nodes = await node_status_fn() if node_status_fn else []
        raw_storage = await storage_status_fn() if storage_status_fn else []
        templates = await list_templates_fn() if list_templates_fn else []
        networks = await list_networks_fn() if list_networks_fn else []
        resources = await provider.list_resources()

        return {
            "connected": True,
            "nodes": [_format_node(n) for n in raw_nodes],
            "storage": [_format_storage(s) for s in raw_storage],
            "templates": templates,
            "networks": networks,
            "existing_resources": resources,
        }
    finally:
        await provider.disconnect()
