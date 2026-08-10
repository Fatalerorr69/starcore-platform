from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Annotated

from ai.generator import BlueprintGenerationError, generate_blueprint_yaml
from blueprints.loader import BlueprintLoader
from blueprints.models import Blueprint
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from core.ai_audit import ai_usage_summary, list_ai_requests
from core.auth import UserRole, require_role
from core.database import get_session
from core.models_api import AIRequestLogResponse, AIUsageSummaryResponse

router = APIRouter(dependencies=[Depends(require_role(UserRole.operator))])


class GenerateBlueprintRequest(BaseModel):
    description: str


class GenerateBlueprintResponse(BaseModel):
    yaml: str
    blueprint: Blueprint | None = None
    validation_error: str | None = None


@router.post("/ai/generate-blueprint", response_model=GenerateBlueprintResponse)
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


@router.get("/ai/usage", response_model=AIUsageSummaryResponse)
async def get_ai_usage(
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    provider: Annotated[str | None, Query()] = None,
    status: Annotated[str | None, Query()] = None,
    since: Annotated[datetime | None, Query()] = None,
    until: Annotated[datetime | None, Query()] = None,
):
    def _query() -> AIUsageSummaryResponse:
        session = get_session()
        try:
            summary = ai_usage_summary(session, provider=provider, since=since, until=until)
            logs = list_ai_requests(
                session,
                limit=limit,
                offset=offset,
                provider=provider,
                status=status,
                since=since,
                until=until,
            )
            return AIUsageSummaryResponse(
                total_requests=summary["total_requests"],
                total_input_tokens=summary["total_input_tokens"],
                total_output_tokens=summary["total_output_tokens"],
                logs=[
                    AIRequestLogResponse(
                        id=log.id,
                        provider=log.provider,
                        status=log.status,
                        duration_seconds=log.duration_seconds,
                        input_tokens=log.input_tokens,
                        output_tokens=log.output_tokens,
                        is_fallback=log.is_fallback,
                        error=log.error,
                        created_at=log.created_at,
                    )
                    for log in logs
                ],
            )
        finally:
            session.close()

    return await asyncio.to_thread(_query)
