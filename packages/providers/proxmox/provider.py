"""
Proxmox Provider
"""

from __future__ import annotations

import asyncio
import os
from typing import Any

from loguru import logger
from provider_sdk.base import BaseProvider
from proxmoxer import ProxmoxAPI


class ProxmoxProvider(BaseProvider):
    name = "proxmox"

    def __init__(self) -> None:
        self._client: ProxmoxAPI | None = None

    async def connect(self) -> bool:
        host = os.environ.get("PROXMOX_HOST")
        user = os.environ.get("PROXMOX_USER")
        token_name = os.environ.get("PROXMOX_TOKEN_NAME")
        token_value = os.environ.get("PROXMOX_TOKEN_VALUE")
        verify_ssl = os.environ.get("PROXMOX_VERIFY_SSL", "true").lower() == "true"

        if not all([host, user, token_name, token_value]):
            logger.error(
                "Proxmox credentials missing. Set PROXMOX_HOST, PROXMOX_USER, "
                "PROXMOX_TOKEN_NAME, PROXMOX_TOKEN_VALUE."
            )
            return False

        try:
            self._client = await asyncio.to_thread(
                ProxmoxAPI,
                host,
                user=user,
                token_name=token_name,
                token_value=token_value,
                verify_ssl=verify_ssl,
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
