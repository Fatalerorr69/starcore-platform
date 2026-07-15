"""
STARCORE Platform
Core API
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from ai.generator import BlueprintGenerationError, generate_blueprint_yaml
from blueprints.executor import BlueprintExecutor
from blueprints.loader import BlueprintLoader
from blueprints.models import Blueprint
from blueprints.planner import ExecutionPlanner
from blueprints.template_resolver import TemplateResolutionError, resolve_templates
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from orchestrator.scheduler import Scheduler
from provider_sdk.registry import register_default_providers, registry
from pydantic import BaseModel

from core.config import get_settings
from core.database import get_session
from core.diagnostics import run_diagnostics
from core.discovery import discover_proxmox_environment
from core.plugin_manager import plugin_manager
from core.repository import get_run, list_runs, save_run
from core.resource_actions import execute_resource_action

app = FastAPI(
    title="STARCORE Platform",
    version="0.1.0-dev",
)


def verify_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    settings = get_settings()
    if not settings.api_key:
        raise HTTPException(
            status_code=503,
            detail="API key not configured on server. Set STARCORE_API_KEY in .env.",
        )
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid API key. Provide it via the X-API-Key header.",
        )


_STATIC_DIR = Path(__file__).parent / "static"

app.mount("/ui/assets", StaticFiles(directory=str(_STATIC_DIR)), name="ui-assets")


@app.get("/ui")
def dashboard():
    return FileResponse(str(_STATIC_DIR / "index.html"))


@app.get("/")
def root():
    return {"project": "STARCORE Platform", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/providers", dependencies=[Depends(verify_api_key)])
async def list_providers():
    register_default_providers()
    return {"providers": [{"name": provider.name} for provider in registry.all()]}


@app.get("/providers/{name}/health", dependencies=[Depends(verify_api_key)])
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


@app.get("/diagnostics", dependencies=[Depends(verify_api_key)])
async def get_diagnostics():
    return await run_diagnostics()


@app.get("/proxmox/discover", dependencies=[Depends(verify_api_key)])
async def discover_proxmox():
    return await discover_proxmox_environment()


class ResourceActionRequest(BaseModel):
    provider: str
    action: str
    resource: str
    kind: str = ""
    node: str | None = None
    vmid: int | None = None


class ResourceActionResponse(BaseModel):
    resource: str
    provider: str
    status: str
    result: dict


@app.post(
    "/resources/action",
    response_model=ResourceActionResponse,
    dependencies=[Depends(verify_api_key)],
)
async def resource_action_endpoint(request: ResourceActionRequest):
    payload: dict = {}
    if request.node:
        payload["node"] = request.node
    if request.vmid is not None:
        payload["vmid"] = request.vmid

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


@app.get("/plugins", dependencies=[Depends(verify_api_key)])
async def list_plugins():
    discovered = plugin_manager.discover()
    loaded = await asyncio.to_thread(plugin_manager.load_all)
    return {"discovered": discovered, "loaded": loaded}


class GenerateBlueprintRequest(BaseModel):
    description: str


class GenerateBlueprintResponse(BaseModel):
    yaml: str
    blueprint: Blueprint | None = None
    validation_error: str | None = None


@app.post(
    "/ai/generate-blueprint",
    response_model=GenerateBlueprintResponse,
    dependencies=[Depends(verify_api_key)],
)
async def generate_blueprint_endpoint(request: GenerateBlueprintRequest):
    try:
        yaml_text = await generate_blueprint_yaml(request.description)
    except BlueprintGenerationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    try:
        blueprint = BlueprintLoader.load_from_string(yaml_text)
        return GenerateBlueprintResponse(yaml=yaml_text, blueprint=blueprint)
    except Exception as exc:
        return GenerateBlueprintResponse(yaml=yaml_text, validation_error=str(exc))


class PlanResponse(BaseModel):
    name: str
    version: str
    steps: list[dict]


@app.post("/blueprints/plan", response_model=PlanResponse, dependencies=[Depends(verify_api_key)])
async def plan_blueprint(blueprint: Blueprint):
    try:
        blueprint = await resolve_templates(blueprint)
    except TemplateResolutionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    plan = ExecutionPlanner().create_plan(blueprint)
    return PlanResponse(name=blueprint.name, version=blueprint.version, steps=plan)


class TaskResult(BaseModel):
    id: str
    provider: str
    resource: str
    status: str
    result: dict


class RunResponse(BaseModel):
    name: str
    version: str
    run_id: str
    tasks: list[TaskResult]


class RunRecordResponse(BaseModel):
    id: str
    blueprint_name: str
    version: str
    parallel: bool
    tasks: list[TaskResult]


@app.post("/blueprints/run", response_model=RunResponse, dependencies=[Depends(verify_api_key)])
async def run_blueprint(blueprint: Blueprint, parallel: bool = False):
    try:
        blueprint = await resolve_templates(blueprint)
    except TemplateResolutionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if parallel:
        graph = ExecutionPlanner().create_graph(blueprint)
        tasks = await Scheduler().execute(graph)
    else:
        tasks = await BlueprintExecutor().execute(blueprint)

    def _persist() -> str:
        session = get_session()
        try:
            record = save_run(session, blueprint.name, blueprint.version, parallel, tasks)
            return record.id
        finally:
            session.close()

    run_id = await asyncio.to_thread(_persist)

    return RunResponse(
        name=blueprint.name,
        version=blueprint.version,
        run_id=run_id,
        tasks=[
            TaskResult(
                id=task.id,
                provider=task.provider,
                resource=task.resource,
                status=task.status.value,
                result=task.result,
            )
            for task in tasks
        ],
    )


@app.get("/runs", response_model=list[RunRecordResponse], dependencies=[Depends(verify_api_key)])
async def get_runs():
    def _list() -> list[RunRecordResponse]:
        session = get_session()
        try:
            records = list_runs(session)
            return [
                RunRecordResponse(
                    id=r.id,
                    blueprint_name=r.blueprint_name,
                    version=r.version,
                    parallel=r.parallel,
                    tasks=[
                        TaskResult(
                            id=t.task_id,
                            provider=t.provider,
                            resource=t.resource,
                            status=t.status,
                            result=t.result,
                        )
                        for t in r.tasks
                    ],
                )
                for r in records
            ]
        finally:
            session.close()

    return await asyncio.to_thread(_list)


@app.get(
    "/runs/{run_id}",
    response_model=RunRecordResponse,
    dependencies=[Depends(verify_api_key)],
)
async def get_run_detail(run_id: str):
    def _get() -> RunRecordResponse | None:
        session = get_session()
        try:
            record = get_run(session, run_id)
            if record is None:
                return None
            return RunRecordResponse(
                id=record.id,
                blueprint_name=record.blueprint_name,
                version=record.version,
                parallel=record.parallel,
                tasks=[
                    TaskResult(
                        id=t.task_id,
                        provider=t.provider,
                        resource=t.resource,
                        status=t.status,
                        result=t.result,
                    )
                    for t in record.tasks
                ],
            )
        finally:
            session.close()

    result = await asyncio.to_thread(_get)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return result
