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

    async def list_templates(self) -> list[dict]:
        if self._client is None:
            return []
        nodes = await asyncio.to_thread(self._client.nodes.get) or []
        templates: list[dict] = []
        for node in nodes:
            node_name = node["node"]
            vms = await asyncio.to_thread(self._client.nodes(node_name).qemu.get) or []
            for vm in vms:
                if vm.get("template") == 1:
                    templates.append(
                        {
                            "node": node_name,
                            "vmid": vm["vmid"],
                            "name": vm.get("name"),
                            "kind": "vm",
                        }
                    )
            containers = await asyncio.to_thread(self._client.nodes(node_name).lxc.get) or []
            for ct in containers:
                if ct.get("template") == 1:
                    templates.append(
                        {
                            "node": node_name,
                            "vmid": ct["vmid"],
                            "name": ct.get("name"),
                            "kind": "lxc",
                        }
                    )
        return templates

    async def list_networks(self) -> list[dict]:
        if self._client is None:
            return []
        nodes = await asyncio.to_thread(self._client.nodes.get) or []
        networks: list[dict] = []
        for node in nodes:
            node_name = node["node"]
            ifaces = await asyncio.to_thread(self._client.nodes(node_name).network.get) or []
            for iface in ifaces:
                if iface.get("type") == "bridge":
                    networks.append(
                        {
                            "node": node_name,
                            "bridge": iface.get("iface"),
                            "active": bool(iface.get("active", 0)),
                        }
                    )
        return networks

    async def node_status(self) -> list[dict]:
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
        elif action == "destroy":
            await self._destroy_resource(task, resource_kind)
        elif action == "snapshot-create":
            await self._snapshot_create(task, resource_kind)
        elif action == "snapshot-list":
            await self._snapshot_list(task, resource_kind)
        elif action == "snapshot-delete":
            await self._snapshot_delete(task, resource_kind)
        elif action == "snapshot-rollback":
            await self._snapshot_rollback(task, resource_kind)
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

    async def _destroy_resource(self, task, resource_kind: str) -> None:
        assert self._client is not None
        payload = task.payload

        node = payload.get("node")
        vmid = payload.get("vmid")
        if not node or not vmid:
            raise ValueError(
                f"Resource '{task.resource}' requires 'node' and 'vmid' "
                "in config for action 'destroy'"
            )

        delete_kwargs: dict[str, Any] = {}
        if payload.get("purge"):
            delete_kwargs["purge"] = 1
        if payload.get("force"):
            delete_kwargs["force"] = 1

        endpoint = self._resource_endpoint(node, vmid, resource_kind)
        upid = await asyncio.to_thread(endpoint.delete, **delete_kwargs)

        if upid and payload.get("wait", True):
            await self._wait_for_task(str(node), str(upid))

        task.result["vmid"] = vmid
        task.result["node"] = node
        task.result["kind"] = resource_kind
        logger.info("[Proxmox] Destroyed {} vmid {} on node {}", resource_kind, vmid, node)

    def _require_snapshot_fields(self, task, need_name: bool) -> tuple[str, int]:
        payload = task.payload
        node = payload.get("node")
        vmid = payload.get("vmid")
        if not node or not vmid:
            raise ValueError(
                f"Resource '{task.resource}' requires 'node' and 'vmid' "
                f"in config for action '{task.action}'"
            )
        if need_name and not payload.get("snapshot_name"):
            raise ValueError(
                f"Resource '{task.resource}' requires 'snapshot_name' in config "
                f"for action '{task.action}'"
            )
        return node, vmid

    async def _snapshot_create(self, task, resource_kind: str) -> None:
        assert self._client is not None
        node, vmid = self._require_snapshot_fields(task, need_name=True)
        payload = task.payload
        snapshot_name = payload["snapshot_name"]

        endpoint = self._resource_endpoint(node, vmid, resource_kind)
        post_kwargs: dict[str, Any] = {"snapname": snapshot_name}
        if description := payload.get("description"):
            post_kwargs["description"] = description

        upid = await asyncio.to_thread(endpoint.snapshot.post, **post_kwargs)
        if upid and payload.get("wait", True):
            await self._wait_for_task(str(node), str(upid))

        task.result["snapshot_name"] = snapshot_name
        task.result["vmid"] = vmid
        task.result["node"] = node
        logger.info(
            "[Proxmox] Created snapshot '{}' on {} vmid {}",
            snapshot_name,
            resource_kind,
            vmid,
        )

    async def _snapshot_list(self, task, resource_kind: str) -> None:
        assert self._client is not None
        node, vmid = self._require_snapshot_fields(task, need_name=False)

        endpoint = self._resource_endpoint(node, vmid, resource_kind)
        raw = await asyncio.to_thread(endpoint.snapshot.get) or []
        snapshots = [s for s in raw if s.get("name") != "current"]

        task.result["snapshots"] = snapshots
        task.result["vmid"] = vmid
        task.result["node"] = node

    async def _snapshot_delete(self, task, resource_kind: str) -> None:
        assert self._client is not None
        node, vmid = self._require_snapshot_fields(task, need_name=True)
        snapshot_name = task.payload["snapshot_name"]

        endpoint = self._resource_endpoint(node, vmid, resource_kind)
        upid = await asyncio.to_thread(endpoint.snapshot(snapshot_name).delete)
        if upid and task.payload.get("wait", True):
            await self._wait_for_task(str(node), str(upid))

        task.result["snapshot_name"] = snapshot_name
        task.result["vmid"] = vmid
        task.result["node"] = node
        logger.info(
            "[Proxmox] Deleted snapshot '{}' on {} vmid {}",
            snapshot_name,
            resource_kind,
            vmid,
        )

    async def _snapshot_rollback(self, task, resource_kind: str) -> None:
        assert self._client is not None
        node, vmid = self._require_snapshot_fields(task, need_name=True)
        snapshot_name = task.payload["snapshot_name"]

        endpoint = self._resource_endpoint(node, vmid, resource_kind)
        upid = await asyncio.to_thread(endpoint.snapshot(snapshot_name).rollback.post)
        if upid and task.payload.get("wait", True):
            await self._wait_for_task(str(node), str(upid))

        task.result["snapshot_name"] = snapshot_name
        task.result["vmid"] = vmid
        task.result["node"] = node
        logger.info(
            "[Proxmox] Rolled back {} vmid {} to snapshot '{}'",
            resource_kind,
            vmid,
            snapshot_name,
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
