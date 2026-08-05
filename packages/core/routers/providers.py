from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, HTTPException
from provider_sdk.registry import register_default_providers, registry
from pydantic import BaseModel

from core.auth import UserRole, require_role
from core.discovery import discover_proxmox_environment
from core.plugin_manager import plugin_manager
from core.resource_actions import execute_resource_action

router = APIRouter(dependencies=[Depends(require_role(UserRole.reader))])


@router.get("/providers")
async def list_providers():
    register_default_providers()
    return {"providers": [{"name": provider.name} for provider in registry.all()]}


@router.get("/providers/{name}/health")
async def provider_health(name: str):
    register_default_providers()
    if name not in registry.names():
        raise HTTPException(status_code=404, detail=f"Provider '{name}' not found")

    provider = registry.get(name)
    connected = await provider.connect()
    try:
        return await provider.health()
    finally:
        if connected:
            await provider.disconnect()


@router.get("/proxmox/discover", dependencies=[Depends(require_role(UserRole.operator))])
async def discover_proxmox():
    return await discover_proxmox_environment()


class ResourceActionRequest(BaseModel):
    provider: str
    action: str
    resource: str
    kind: str = ""
    node: str | None = None
    vmid: int | None = None
    snapshot_name: str | None = None
    description: str | None = None


class ResourceActionResponse(BaseModel):
    resource: str
    provider: str
    status: str
    result: dict


@router.post(
    "/resources/action",
    response_model=ResourceActionResponse,
    dependencies=[Depends(require_role(UserRole.operator))],
)
async def resource_action_endpoint(request: ResourceActionRequest):
    payload: dict = {}
    if request.node:
        payload["node"] = request.node
    if request.vmid is not None:
        payload["vmid"] = request.vmid
    if request.snapshot_name:
        payload["snapshot_name"] = request.snapshot_name
    if request.description:
        payload["description"] = request.description

    task = await execute_resource_action(
        request.provider,
        request.action,
        request.resource,
        kind=request.kind,
        payload=payload,
    )
    return ResourceActionResponse(
        resource=task.resource,
        provider=task.provider,
        status=task.status.value,
        result=task.result,
    )


@router.get("/plugins")
async def list_plugins():
    discovered = plugin_manager.discover()
    loaded = await asyncio.to_thread(plugin_manager.load_all)
    return {"discovered": discovered, "loaded": loaded}
