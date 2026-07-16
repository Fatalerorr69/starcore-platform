"""
Rate Limiting Tests

RISK-03 / TD-12 regression tests: no endpoint had any rate limiting before
this fix, allowing unbounded credential-guessing / abuse against the
authenticated endpoints. See docs/changelog/sprint-003.md.
"""

from __future__ import annotations

from core.main import _build_rate_limit_config, app, limiter
from fastapi.testclient import TestClient
from slowapi.util import get_remote_address

client = TestClient(app)


def test_default_deployment_has_rate_limiting_enabled():
    """Regression guard: the deployed default (STARCORE_RATE_LIMIT_PER_MINUTE
    unset -> Settings default of 60) must result in an *enabled* limiter.
    A future change to the default that silently disables protection
    should fail this test.
    """
    assert limiter.enabled is True


def test_exceeding_the_limit_returns_429_with_retry_after():
    """Build a small isolated app using the exact same wiring pattern as
    core/main.py, rather than mutating the shared production `limiter`'s
    internals (which would depend on slowapi implementation details and
    would pollute the counters other tests in this module rely on).
    """
    from fastapi import FastAPI
    from slowapi import Limiter as _Limiter
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded as _RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware as _SlowAPIMiddleware

    default_limits, enabled = _build_rate_limit_config(2)
    probe_app = FastAPI()
    probe_limiter = _Limiter(
        key_func=get_remote_address,
        default_limits=default_limits,
        headers_enabled=True,
        enabled=enabled,
    )
    probe_app.state.limiter = probe_limiter
    probe_app.add_exception_handler(_RateLimitExceeded, _rate_limit_exceeded_handler)
    probe_app.add_middleware(_SlowAPIMiddleware)

    @probe_app.get("/probe")
    def probe():
        return {"ok": True}

    probe_client = TestClient(probe_app)
    assert probe_client.get("/probe").status_code == 200
    assert probe_client.get("/probe").status_code == 200
    response = probe_client.get("/probe")
    assert response.status_code == 429
    assert "retry-after" in {k.lower() for k in response.headers}
    assert response.json()["error"].startswith("Rate limit exceeded")


def test_health_endpoint_is_exempt_from_rate_limiting():
    """/health must remain reachable well beyond the configured default
    limit, since container orchestrators poll it far more often than any
    sane API rate limit would allow. Exercises the real app/limiter to
    prove the @limiter.exempt wiring in core/main.py actually works, not
    just the underlying slowapi mechanism in isolation.
    """
    for _ in range(80):
        assert client.get("/health").status_code == 200


# ---------------------------------------------------------------------------
# Unit tests for the settings -> slowapi-config translation, covering the
# "0 disables rate limiting" branch without needing to reconstruct a full
# FastAPI app / Limiter for each configuration.
# ---------------------------------------------------------------------------


def test_build_rate_limit_config_positive_value_enables_limiting():
    default_limits, enabled = _build_rate_limit_config(60)
    assert enabled is True
    assert default_limits == ["60/minute"]


def test_build_rate_limit_config_zero_disables_limiting():
    default_limits, enabled = _build_rate_limit_config(0)
    assert enabled is False
    assert default_limits == []
