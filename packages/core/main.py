"""
STARCORE Platform
Core API
"""

from __future__ import annotations

from blueprints.executor import BlueprintExecutor
from blueprints.models import Blueprint
from blueprints.planner import ExecutionPlanner
from fastapi import FastAPI, HTTPException
from provider_sdk.registry import register_default_providers, registry
from pydantic import BaseModel

app = FastAPI(
    title="STARCORE Platform",
    version="0.1.0-dev",
)


@app.get("/")
def root():
    return {"project": "STARCORE Platform", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/providers")
async def list_providers():
    register_default_providers()
    return {"providers": [{"name": provider.name} for provider in registry.all()]}


@app.get("/providers/{name}/health")
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


class PlanResponse(BaseModel):
    name: str
    version: str
    steps: list[dict]


@app.post("/blueprints/plan", response_model=PlanResponse)
def plan_blueprint(blueprint: Blueprint):
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
    tasks: list[TaskResult]


@app.post("/blueprints/run", response_model=RunResponse)
async def run_blueprint(blueprint: Blueprint):
    tasks = await BlueprintExecutor().execute(blueprint)
    return RunResponse(
        name=blueprint.name,
        version=blueprint.version,
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
