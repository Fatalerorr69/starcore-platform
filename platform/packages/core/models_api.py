from __future__ import annotations

from datetime import datetime

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


class AIRequestLogResponse(BaseModel):
    id: str
    provider: str
    status: str
    duration_seconds: float | None
    input_tokens: int | None
    output_tokens: int | None
    is_fallback: bool
    error: str | None
    created_at: datetime


class AIUsageSummaryResponse(BaseModel):
    total_requests: int
    total_input_tokens: int
    total_output_tokens: int
    logs: list[AIRequestLogResponse]
