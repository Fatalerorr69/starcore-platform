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
                        "kind": "vm",
                    }
                )
            containers = await asyncio.to_thread(self._client.nodes(node["node"]).lxc.get) or []
            for ct in containers:
                resources.append(
                    {
                        "node": node["node"],
                        "vmid": ct["vmid"],
                        "name": ct.get("name"),
                        "status": ct.get("status"),
                        "kind": "lxc",
                    }
                )
        return resources

    async def node_status(self) -> list[dict]:
        """Return raw Proxmox node status (cpu, memory, rootfs) per node."""
        if self._client is None:
            return []
        nodes = await asyncio.to_thread(self._client.nodes.get) or []
        result: list[dict] = []
        for node in nodes:
            node_name = node["node"]
            status = await asyncio.to_thread(self._client.nodes(node_name).status.get) or {}
            result.append({"node": node_name, **status})
        return result

    async def storage_status(self) -> list[dict]:
        """Return raw Proxmox storage status per node."""
        if self._client is None:
            return []
        nodes = await asyncio.to_thread(self._client.nodes.get) or []
        result: list[dict] = []
        for node in nodes:
            node_name = node["node"]
            storages = await asyncio.to_thread(self._client.nodes(node_name).storage.get) or []
            for storage in storages:
                result.append({"node": node_name, **storage})
        return result

    def _resource_endpoint(self, node: str, vmid: int | str, kind: str) -> Any:
        assert self._client is not None
        if kind == "lxc":
            return self._client.nodes(node).lxc(vmid)
        return self._client.nodes(node).qemu(vmid)

    async def execute(self, task) -> None:
        if self._client is None:
            raise RuntimeError("Proxmox provider is not connected")

        action = task.action
        node = task.payload.get("node")
        vmid = task.payload.get("vmid")
        resource_kind = "lxc" if task.kind == "lxc" else "vm"

        if action in ("start", "stop", "shutdown"):
            if not node or not vmid:
                raise ValueError(
                    f"Resource '{task.resource}' requires 'node' and 'vmid' "
                    f"in config for action '{action}'"
                )
            endpoint = self._resource_endpoint(node, vmid, resource_kind)
            await asyncio.to_thread(endpoint.status.post, action)
            logger.info("[Proxmox] {} -> {} {} on node {}", action, resource_kind, vmid, node)
        elif action == "create":
            await self._create_resource(task, resource_kind)
        else:
            raise ValueError(f"Unsupported Proxmox action: '{action}'")

    async def _create_resource(self, task, resource_kind: str) -> None:
        assert self._client is not None
        payload = task.payload

        node = payload.get("node")
        template_vmid = payload.get("template_vmid")
        if not node or not template_vmid:
            raise ValueError(
                f"Resource '{task.resource}' requires 'node' and 'template_vmid' "
                f"in config to clone a {resource_kind}"
            )

        vmid = payload.get("vmid")
        if not vmid:
            next_id = await asyncio.to_thread(self._client.cluster.nextid.get)
            if next_id is None:
                raise RuntimeError("Failed to allocate next ID from Proxmox")
            vmid = int(next_id)
        else:
            vmid = int(vmid)

        clone_kwargs: dict[str, Any] = {
            "newid": vmid,
            "full": 1 if payload.get("full", True) else 0,
        }
        if resource_kind == "lxc":
            clone_kwargs["hostname"] = task.resource
        else:
            clone_kwargs["name"] = task.resource
        if storage := payload.get("storage"):
            clone_kwargs["storage"] = storage
        if target := payload.get("target_node"):
            clone_kwargs["target"] = target

        source_endpoint = self._resource_endpoint(node, template_vmid, resource_kind)
        upid = await asyncio.to_thread(source_endpoint.clone.post, **clone_kwargs)
        if upid is None:
            raise RuntimeError(
                f"Proxmox did not return a task ID for cloning resource '{task.resource}'"
            )

        if payload.get("wait", True):
            await self._wait_for_task(str(node), str(upid))

        config_updates: dict[str, Any] = {}
        if cores := payload.get("cores"):
            config_updates["cores"] = cores
        if memory := payload.get("memory"):
            config_updates["memory"] = memory
        if config_updates:
            target_endpoint = self._resource_endpoint(node, vmid, resource_kind)
            await asyncio.to_thread(target_endpoint.config.post, **config_updates)

        task.result["vmid"] = vmid
        task.result["node"] = node
        task.result["kind"] = resource_kind
        logger.info(
            "[Proxmox] Cloned {} template {} -> vmid {} ('{}') on node {}",
            resource_kind,
            template_vmid,
            vmid,
            task.resource,
            node,
        )

    async def _wait_for_task(
        self, node: str, upid: str, timeout: float = 300.0, interval: float = 2.0
    ) -> None:
        assert self._client is not None
        elapsed = 0.0
        while elapsed < timeout:
            status = await asyncio.to_thread(self._client.nodes(node).tasks(upid).status.get)
            if status is None:
                raise RuntimeError(f"Proxmox returned no status for task {upid}")
            if status.get("status") == "stopped":
                if status.get("exitstatus") != "OK":
                    raise RuntimeError(f"Proxmox task {upid} failed: {status.get('exitstatus')}")
                return
            await asyncio.sleep(interval)
            elapsed += interval
        raise TimeoutError(f"Proxmox task {upid} did not complete within {timeout}s")
