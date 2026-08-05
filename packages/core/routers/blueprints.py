from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import AsyncGenerator, Callable

from blueprints.executor import BlueprintExecutor
from blueprints.models import Blueprint
from blueprints.planner import ExecutionPlanner
from blueprints.template_resolver import TemplateResolutionError, resolve_templates
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from orchestrator.scheduler import Scheduler
from orchestrator.task import Task
from pydantic import BaseModel

from core.auth import UserRole, require_role
from core.database import get_session
from core.events import _STREAM_CTX, event_bus
from core.models_api import TaskResult
from core.repository import save_run

router = APIRouter(dependencies=[Depends(require_role(UserRole.operator))])


class PlanResponse(BaseModel):
    name: str
    version: str
    steps: list[dict]


class RunResponse(BaseModel):
    name: str
    version: str
    run_id: str
    tasks: list[TaskResult]


@router.post("/blueprints/plan", response_model=PlanResponse)
async def plan_blueprint(blueprint: Blueprint):
    try:
        blueprint = await resolve_templates(blueprint)
    except TemplateResolutionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    plan = ExecutionPlanner().create_plan(blueprint)
    return PlanResponse(name=blueprint.name, version=blueprint.version, steps=plan)


@router.post("/blueprints/run", response_model=RunResponse)
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

    run_id = await asyncio.to_thread(lambda: _persist_run(blueprint, parallel, tasks))

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


@router.post("/blueprints/run/stream")
async def stream_blueprint(blueprint: Blueprint, parallel: bool = False):
    """Execute a blueprint and stream SSE events for real-time progress.

    Emits `task.started`, `task.completed`, and `run.completed` events as
    they occur, followed by a `run.persisted` event once the run record has
    been saved to the database.

    Each event is a JSON object on a `data:` SSE line::

        data: {"event": "task.started", "resource": "web", "provider": "docker"}
        data: {"event": "run.persisted", "run_id": "<uuid>"}
    """
    try:
        blueprint = await resolve_templates(blueprint)
    except TemplateResolutionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return StreamingResponse(
        _sse_generator(blueprint, parallel),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def _sse_generator(blueprint: Blueprint, parallel: bool) -> AsyncGenerator[str, None]:
    queue: asyncio.Queue[tuple[str, dict]] = asyncio.Queue()
    completed_tasks: list[Task] = []
    run_nonce = str(uuid.uuid4())

    def _make_handler(name: str) -> Callable[[dict], None]:
        def _handler(payload: dict) -> None:
            if isinstance(payload, dict) and payload.get("_stream_id") == run_nonce:
                clean = {k: v for k, v in payload.items() if k != "_stream_id"}
                queue.put_nowait((name, clean))

        return _handler

    subscribed = {
        name: _make_handler(name) for name in ("task.started", "task.completed", "run.completed")
    }
    for name, handler in subscribed.items():
        event_bus.subscribe(name, handler)

    async def _run() -> None:
        if parallel:
            graph = ExecutionPlanner().create_graph(blueprint)
            tasks = await Scheduler().execute(graph)
        else:
            tasks = await BlueprintExecutor().execute(blueprint)
        completed_tasks.extend(tasks)

    # Set the stream context so exec_task inherits run_nonce via context copy.
    token = _STREAM_CTX.set(run_nonce)
    exec_task = asyncio.create_task(_run())
    _STREAM_CTX.reset(token)

    queue_getter: asyncio.Task[tuple[str, dict]] = asyncio.create_task(queue.get())
    try:
        while True:
            done, _ = await asyncio.wait(
                {exec_task, queue_getter},
                return_when=asyncio.FIRST_COMPLETED,
            )

            if queue_getter in done:
                event_name, payload = queue_getter.result()
                yield f"data: {json.dumps({'event': event_name, **payload})}\n\n"
                if event_name == "run.completed":
                    queue_getter.cancel()
                    break
                queue_getter = asyncio.create_task(queue.get())

            if exec_task in done and not exec_task.cancelled():
                exc = exec_task.exception()
                if exc is not None:
                    queue_getter.cancel()
                    yield f"data: {json.dumps({'event': 'error', 'detail': str(exc)})}\n\n"
                    return

        await exec_task

        run_id = await asyncio.to_thread(lambda: _persist_run(blueprint, parallel, completed_tasks))
        yield f"data: {json.dumps({'event': 'run.persisted', 'run_id': run_id})}\n\n"
    finally:
        for name, handler in subscribed.items():
            event_bus.unsubscribe(name, handler)
        if not exec_task.done():
            exec_task.cancel()
            try:
                await exec_task
            except asyncio.CancelledError:
                pass
        queue_getter.cancel()


def _persist_run(blueprint: Blueprint, parallel: bool, tasks: list[Task]) -> str:
    session = get_session()
    try:
        record = save_run(session, blueprint.name, blueprint.version, parallel, tasks)
        return record.id
    finally:
        session.close()
