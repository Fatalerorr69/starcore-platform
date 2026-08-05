from __future__ import annotations

from pydantic import BaseModel


class TaskResult(BaseModel):
    id: str
    provider: str
    resource: str
    status: str
    result: dict


class RunRecordResponse(BaseModel):
    id: str
    blueprint_name: str
    version: str
    parallel: bool
    tasks: list[TaskResult]
