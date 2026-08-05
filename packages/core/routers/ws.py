"""WebSocket endpoint for real-time blueprint execution streaming (REC-002)."""

from __future__ import annotations

import asyncio
import hmac
import json
from collections.abc import Callable
from typing import Annotated

from blueprints.executor import BlueprintExecutor
from blueprints.models import Blueprint
from blueprints.planner import ExecutionPlanner
from blueprints.template_resolver import TemplateResolutionError, resolve_templates
from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from orchestrator.scheduler import Scheduler
from orchestrator.task import Task
from pydantic import ValidationError

from core.auth import UserPrincipal, UserRole, decode_token
from core.config import get_settings
from core.database import get_session
from core.events import event_bus
from core.repository import save_run

router = APIRouter()

_ROLE_WEIGHT: dict[UserRole, int] = {
    UserRole.reader: 0,
    UserRole.operator: 1,
    UserRole.admin: 2,
}


@router.websocket("/blueprints/run/ws")
async def ws_run_blueprint(
    websocket: WebSocket,
    token: Annotated[str | None, Query()] = None,
    api_key: Annotated[str | None, Query()] = None,
    parallel: Annotated[bool, Query()] = False,
) -> None:
    """WebSocket endpoint for real-time blueprint execution progress.

    Authenticate via query parameters (HTTP headers are not forwarded on
    WebSocket handshakes):

    - ``?token=<jwt>`` — Bearer JWT access token
    - ``?api_key=<key>`` — Legacy X-API-Key

    **Protocol**

    After connecting, send the blueprint JSON as a single text frame.  The
    server streams JSON text frames as tasks execute::

        {"event": "task.started", "resource": "web", "provider": "docker"}
        {"event": "task.completed", "resource": "web", "provider": "docker", "status": "completed"}
        {"event": "run.completed", "blueprint_name": "my-bp"}
        {"event": "run.persisted", "run_id": "<uuid>"}

    The server closes the connection with code **1000** after ``run.persisted``.

    **Application close codes**

    =========  ====================================================
    Code       Meaning
    =========  ====================================================
    4401       Authentication failed (bad/expired token, wrong key, no credentials)
    4403       Forbidden — JWT not configured on server, or insufficient role
    4422       Invalid blueprint JSON or template resolution error
    =========  ====================================================
    """
    await websocket.accept()

    settings = get_settings()
    principal: UserPrincipal | None = None

    if token is not None:
        try:
            payload = decode_token(token, "access", settings)
            role = UserRole(payload["role"])
            principal = UserPrincipal(username=payload["sub"], role=role)
        except HTTPException as exc:
            code = 4403 if exc.status_code == 403 else 4401
            await websocket.close(code=code, reason=exc.detail)
            return
        except (KeyError, ValueError):
            await websocket.close(code=4401, reason="Invalid token payload.")
            return
    elif api_key is not None:
        if not settings.api_key:
            await websocket.close(code=4401, reason="API key not configured on server.")
            return
        if not hmac.compare_digest(api_key, settings.api_key):
            await websocket.close(code=4401, reason="Invalid API key.")
            return
        principal = UserPrincipal(username="api-key", role=UserRole.admin)
    else:
        await websocket.close(code=4401, reason="No credentials provided.")
        return

    if _ROLE_WEIGHT[principal.role] < _ROLE_WEIGHT[UserRole.operator]:
        await websocket.close(code=4403, reason="Requires 'operator' role or higher.")
        return

    await _ws_run_blueprint(websocket, parallel)


async def _ws_run_blueprint(websocket: WebSocket, parallel: bool) -> None:
    """Receive a blueprint text frame, execute it, and stream event frames."""
    try:
        raw = await websocket.receive_text()
    except WebSocketDisconnect:
        return

    try:
        blueprint = Blueprint.model_validate_json(raw)
    except ValidationError as exc:
        await websocket.send_text(json.dumps({"event": "error", "detail": str(exc)}))
        await websocket.close(code=4422, reason="Invalid blueprint")
        return

    try:
        blueprint = await resolve_templates(blueprint)
    except TemplateResolutionError as exc:
        await websocket.send_text(json.dumps({"event": "error", "detail": str(exc)}))
        await websocket.close(code=4422, reason="Template resolution failed")
        return

    queue: asyncio.Queue[tuple[str, dict]] = asyncio.Queue()
    completed_tasks: list[Task] = []

    def _make_handler(event_name: str) -> Callable[[dict], None]:
        def _handler(payload: dict) -> None:
            queue.put_nowait((event_name, payload))

        return _handler

    subscribed = {
        name: _make_handler(name)
        for name in ("task.started", "task.completed", "run.completed")
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

    exec_task = asyncio.create_task(_run())
    try:
        while True:
            event_name, payload = await queue.get()
            await websocket.send_text(json.dumps({"event": event_name, **payload}))
            if event_name == "run.completed":
                break
        await exec_task
        run_id = await asyncio.to_thread(
            lambda: _persist_run(blueprint, parallel, completed_tasks)
        )
        await websocket.send_text(json.dumps({"event": "run.persisted", "run_id": run_id}))
        await websocket.close()
    except WebSocketDisconnect:
        pass
    finally:
        for name, handler in subscribed.items():
            event_bus.unsubscribe(name, handler)
        if not exec_task.done():
            exec_task.cancel()
            try:
                await exec_task
            except asyncio.CancelledError:
                pass


def _persist_run(blueprint: Blueprint, parallel: bool, tasks: list[Task]) -> str:
    session = get_session()
    try:
        record = save_run(session, blueprint.name, blueprint.version, parallel, tasks)
        return record.id
    finally:
        session.close()
