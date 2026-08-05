"""
STARCORE Platform
Core API
"""

from __future__ import annotations

import re
import time
import uuid
from collections.abc import Callable
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

import core.logger  # noqa: F401 -- side effect: configures the process-wide loguru sink
from core.config import get_settings
from core.database import create_initial_admin
from core.diagnostics import check_database_connectivity
from core.metrics import HTTP_REQUEST_DURATION_SECONDS, HTTP_REQUESTS_TOTAL
from core.routers import ai, auth, blueprints, diagnostics, providers, runs
from core.tracing import configure_tracing

app = FastAPI(
    title="STARCORE Platform",
    version="0.1.0-dev",
)


@app.on_event("startup")
def _on_startup() -> None:
    create_initial_admin()


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


configure_tracing(get_settings().otlp_endpoint)

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


@app.middleware("http")
async def _metrics_middleware(request: Request, call_next):
    """Record HTTP request count and latency for all HTTP routes.

    Uses the matched route's path template (e.g. "/runs/{run_id}") rather
    than the raw request path, so per-resource IDs don't blow up metric
    cardinality. Starlette sets `request.scope["route"]` once routing has
    resolved, which has already happened by the time `call_next` returns;
    falls back to the raw path if routing didn't match (e.g. a 404).
    """
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    route = request.scope.get("route")
    path = route.path if route is not None else request.url.path
    HTTP_REQUESTS_TOTAL.labels(
        method=request.method, path=path, status=str(response.status_code)
    ).inc()
    HTTP_REQUEST_DURATION_SECONDS.labels(method=request.method, path=path).observe(duration)
    return response


_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


def _resolve_request_id(incoming: str | None) -> str:
    """Accept a caller-supplied X-Request-ID if it looks like a reasonable
    opaque token, otherwise generate one.

    A malformed or missing header is not an error worth failing the
    request over -- it just means correlation falls back to a fresh ID,
    same as if the caller hadn't sent one at all.
    """
    if incoming and _REQUEST_ID_PATTERN.fullmatch(incoming):
        return incoming
    return str(uuid.uuid4())


@app.middleware("http")
async def _request_id_middleware(request: Request, call_next):
    """Bind a correlation ID to every log line emitted while handling this
    request, and echo it back in the response header.

    `logger.contextualize()` is backed by the same `contextvars` machinery
    `asyncio` itself uses for context propagation, so the bound
    `request_id` is automatically visible to any coroutine awaited from
    within this request -- including a `Scheduler.execute()` wave spawned
    by `POST /blueprints/run?parallel=true` -- with no extra plumbing.
    """
    request_id = _resolve_request_id(request.headers.get("x-request-id"))
    with logger.contextualize(request_id=request_id):
        response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# ── Static UI ──────────────────────────────────────────────────────────────
_STATIC_DIR = Path(__file__).parent / "static"

app.mount("/ui/assets", StaticFiles(directory=str(_STATIC_DIR)), name="ui-assets")


@app.get("/ui")
def dashboard():
    return FileResponse(str(_STATIC_DIR / "index.html"))


# ── Infrastructure routes (unauthenticated) ────────────────────────────────
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


# ── Domain routers ─────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(providers.router)
app.include_router(blueprints.router)
app.include_router(runs.router)
app.include_router(ai.router)
app.include_router(diagnostics.router)
