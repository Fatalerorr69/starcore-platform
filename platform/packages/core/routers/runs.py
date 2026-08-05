from __future__ import annotations

import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from core.auth import UserRole, require_role
from core.database import get_session
from core.models_api import RunRecordResponse, TaskResult
from core.repository import get_run, list_runs

router = APIRouter(dependencies=[Depends(require_role(UserRole.reader))])


@router.get("/runs", response_model=list[RunRecordResponse])
async def get_runs(
    limit: Annotated[int, Query(ge=1, le=200, description="Max number of runs to return.")] = 50,
    offset: Annotated[int, Query(ge=0, description="Number of most-recent runs to skip.")] = 0,
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


@router.get("/runs/{run_id}", response_model=RunRecordResponse)
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
