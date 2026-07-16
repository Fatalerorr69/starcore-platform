"""
STARCORE Platform
Core API
"""

from __future__ import annotations

import asyncio
import hmac
from collections.abc import Callable
from pathlib import Path

from ai.generator import BlueprintGenerationError, generate_blueprint_yaml
from blueprints.executor import BlueprintExecutor
from blueprints.loader import BlueprintLoader
from blueprints.models import Blueprint
from blueprints.planner import ExecutionPlanner
from blueprints.template_resolver import TemplateResolutionError, resolve_templates
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from orchestrator.scheduler import Scheduler
from provider_sdk.registry import register_default_providers, registry
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from core.config import get_settings
from core.database import get_session
from core.diagnostics import check_database_connectivity, run_diagnostics
from core.discovery import discover_proxmox_environment
from core.plugin_manager import plugin_manager
from core.repository import get_run, list_runs, save_run
from core.resource_actions import execute_resource_action

app = FastAPI(
    title="STARCORE Platform",
    version="0.1.0-dev",
)


# Rate limiting (RISK-03 / TD-12): a single, process-wide, in-memory limiter
# applied to every route via SlowAPIMiddleware's default_limits, except
# /health (see its @limiter.exempt below -- container orchestrators must be
# able to probe it without being throttled by their own polling interval).
#
# The limit is read once at process startup, not per-request: like `app`
# itself, the limiter is part of process wiring rather than a value that is
# expected to change while the process is running. Set
# STARCORE_RATE_LIMIT_PER_MINUTE=0 to disable entirely (e.g. for local
# development or a deployment an operator has already decided to expose
# only on a trusted network).
def _build_rate_limit_config(
    rate_limit_per_minute: int,
) -> tuple[list[str | Callable[..., str]], bool]:
    """Translate the configured per-minute limit into slowapi's inputs.

    Extracted as a standalone, settings-free function so the "0 disables
    rate limiting" branch is unit-testable without constructing a FastAPI
    app or a real Limiter (see tests/test_rate_limiting.py).

    Return type is widened to `str | Callable[..., str]` (rather than just
    `str`) to match slowapi's `Limiter.__init__` parameter type exactly --
    `list` is invariant, so a plain `list[str]` is not assignable where
    `list[str | Callable[..., str]]` is expected, even though every element
    here is always a `str`.
    """
    enabled = rate_limit_per_minute > 0
    default_limits: list[str | Callable[..., str]] = (
        [f"{rate_limit_per_minute}/minute"] if enabled else []
    )
    return default_limits, enabled


def _handle_rate_limit_exceeded(request: Request, exc: Exception) -> Response:
    """Typed adapter for FastAPI's `add_exception_handler`.

    FastAPI's `ExceptionHandler` type expects a handler taking `Exception`,
    but slowapi's `_rate_limit_exceeded_handler` is typed to take the more
    specific `RateLimitExceeded` -- correct at runtime (this handler is only
    ever invoked for `RateLimitExceeded`, per the registration below), but
    not directly assignable under static typing without this adapter.
    """
    assert isinstance(exc, RateLimitExceeded)
    return _rate_limit_exceeded_handler(request, exc)


_rate_limit_settings = get_settings()
_default_limits, _rate_limit_enabled = _build_rate_limit_config(
    _rate_limit_settings.rate_limit_per_minute
)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=_default_limits,
    headers_enabled=True,
    enabled=_rate_limit_enabled,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _handle_rate_limit_exceeded)
app.add_middleware(SlowAPIMiddleware)


def verify_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    settings = get_settings()
    if not settings.api_key:
        raise HTTPException(
            status_code=503,
            detail="API key not configured on server. Set STARCORE_API_KEY in .env.",
        )
    # Constant-time comparison: a plain `!=` here would leak the number of
    # matching leading characters via response-timing differences to a
    # network-positioned attacker. compare_digest() is safe for this even
    # though `x_api_key` is attacker-controlled, because it always compares
    # the full length of both inputs regardless of where they first differ.
    if x_api_key is None or not hmac.compare_digest(x_api_key, settings.api_key):
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
@limiter.exempt
def health():
    """Liveness/readiness check for container orchestration.

    Intentionally checks only local, fast dependencies (currently: the
    database). It deliberately does NOT call out to external providers
    (Docker daemon, Proxmox API) the way `/diagnostics` does: this endpoint
    is public and unauthenticated by design (so orchestrators can probe it
    without a credential), and triggering slow, attacker-triggerable
    outbound network calls to infrastructure providers from an
    unauthenticated endpoint would itself be a denial-of-service and
    provider-abuse surface. Use the authenticated `/diagnostics` endpoint
    for a full deployment/provider health check.
    """
    db_check = check_database_connectivity()
    status = "healthy" if db_check.status == "ok" else "unhealthy"
    body = {"status": status, "database": db_check.detail}
    if db_check.status != "ok":
        return JSONResponse(status_code=503, content=body)
    return body


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
    snapshot_name: str | None = None
    description: str | None = None


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
async def get_runs(
    limit: int = Query(default=50, ge=1, le=200, description="Max number of runs to return."),
    offset: int = Query(default=0, ge=0, description="Number of most-recent runs to skip."),
):
    def _list() -> list[RunRecordResponse]:
        session = get_session()
        try:
            records = list_runs(session, limit=limit, offset=offset)
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
