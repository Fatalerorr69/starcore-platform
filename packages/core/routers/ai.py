from __future__ import annotations

from ai.generator import BlueprintGenerationError, generate_blueprint_yaml
from blueprints.loader import BlueprintLoader
from blueprints.models import Blueprint
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.auth import UserRole, require_role

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
