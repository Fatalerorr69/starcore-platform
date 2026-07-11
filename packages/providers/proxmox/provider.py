"""
Proxmox Provider
"""

from __future__ import annotations

import asyncio
from typing import Any

from core.config import get_settings
from loguru import logger
from provider_sdk.base import BaseProvider
from proxmoxer import ProxmoxAPI


class ProxmoxProvider(BaseProvider):
    name = "proxmox"

    def __init__(self) -> None:
        self._client: ProxmoxAPI | None = None

    async def connect(self) -> bool:
        settings = get_settings()

        if not all(
            [
                settings.proxmox_host,
                settings.proxmox_user,
                settings.proxmox_token_name,
                settings.proxmox_token_value,
            ]
        ):
            logger.error(
                "Proxmox credentials missing. Set STARCORE_PROXMOX_HOST, "
                "STARCORE_PROXMOX_USER, STARCORE_PROXMOX_TOKEN_NAME, "
                "STARCORE_PROXMOX_TOKEN_VALUE (see .env.example)."
            )
            return False

        try:
            self._client = await asyncio.to_thread(
                ProxmoxAPI,
                settings.proxmox_host,
                user=settings.proxmox_user,
                token_name=settings.proxmox_token_name,
                token_value=settings.proxmox_token_value,
                verify_ssl=settings.proxmox_verify_ssl,
            )
            await asyncio.to_thread(self._client.version.get)
            return True
        except Exception as exc:
            logger.error("Proxmox connection failed: {}", exc)
            self._client = None
            return False

    async def disconnect(self) -> None:
        self._client = None

    async def health(self) -> dict[str, Any]:
        if self._client is None:
            return {"status": "disconnected", "provider": self.name}
        try:
            await asyncio.to_thread(self._client.version.get)
            return {"status": "ok", "provider": self.name}
        except Exception as exc:
            return {"status": "error", "provider": self.name, "detail": str(exc)}

    async def list_resources(self) -> list[dict]:
        if self._client is None:
            return []
        nodes = await asyncio.to_thread(self._client.nodes.get) or []
        resources: list[dict] = []
        for node in nodes:
            vms = await asyncio.to_thread(self._client.nodes(node["node"]).qemu.get) or []
            for vm in vms:
                resources.append(
                    {
                        "node": node["node"],
                        "vmid": vm["vmid"],
                        "name": vm.get("name"),
                        "status": vm.get("status"),
                    }
                )
        return resources

    async def execute(self, task) -> None:
        if self._client is None:
            raise RuntimeError("Proxmox provider is not connected")

        action = task.action
        node = task.payload.get("node")
        vmid = task.payload.get("vmid")

        if action in ("start", "stop", "shutdown"):
            if not node or not vmid:
                raise ValueError(
                    f"Resource '{task.resource}' requires 'node' and 'vmid' "
                    f"in config for action '{action}'"
                )
            await asyncio.to_thread(self._client.nodes(node).qemu(vmid).status.post, action)
            logger.info("[Proxmox] {} -> vmid {} on node {}", action, vmid, node)
        elif action == "create":
            raise NotImplementedError(
                "Proxmox VM creation from blueprint (clone/template) is not "
                "implemented yet; provide 'node' and 'vmid' of an existing VM "
                "and use 'start' action instead."
            )
        else:
            raise ValueError(f"Unsupported Proxmox action: '{action}'")
