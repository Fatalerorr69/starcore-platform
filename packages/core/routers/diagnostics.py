from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST

from core.auth import UserRole, require_role
from core.diagnostics import run_diagnostics
from core.environment import classify_client_platform
from core.metrics import render_metrics

router = APIRouter(dependencies=[Depends(require_role(UserRole.operator))])


@router.get("/diagnostics")
async def get_diagnostics(request: Request):
    report = await run_diagnostics()
    user_agent = request.headers.get("user-agent")
    report["client"] = {
        "user_agent": user_agent,
        "platform": classify_client_platform(user_agent),
    }
    return report


@router.get("/metrics")
def get_metrics():
    """Prometheus scrape endpoint.

    Authenticated like every other non-/health endpoint (see verify_api_key):
    metrics can reveal deployment shape (which providers are configured, run
    volume), so they're not exposed without a credential. Configure your
    Prometheus scrape job with the X-API-Key header via `authorization`
    (bearer token config won't match this header-based scheme).
    """
    return Response(content=render_metrics(), media_type=CONTENT_TYPE_LATEST)
