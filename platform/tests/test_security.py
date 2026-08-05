"""
Secret Redaction Tests

Covers core.security directly, plus a broad regression sweep proving that
no unauthenticated endpoint ever echoes back a configured secret -- see the
STARCORE-Claude-Code-Complete-Optimization-Runbook's P0 security section.
"""

from __future__ import annotations

from core.config import get_settings
from core.main import app
from core.security import redact_database_url, scrub_configured_secrets
from fastapi.testclient import TestClient

# Deliberately unauthenticated: no X-API-Key header. Every endpoint hit in
# this file must be reachable without one, by design (/, /health, /ui).
anonymous_client = TestClient(app)


# ---------------------------------------------------------------------------
# core.security unit tests
# ---------------------------------------------------------------------------


def test_redact_database_url_masks_password():
    safe = redact_database_url("postgresql://dbuser:s3cret-password@db.example.com/starcore")
    assert "s3cret-password" not in safe
    assert "dbuser" in safe


def test_redact_database_url_is_noop_for_default_sqlite_url():
    assert redact_database_url("sqlite:///./data/starcore.db") == "sqlite:///./data/starcore.db"


def test_redact_database_url_falls_back_on_unparseable_url():
    assert redact_database_url("not-a-valid-url") == "<unparseable database URL>"


def test_scrub_configured_secrets_replaces_configured_api_key(monkeypatch):
    monkeypatch.setenv("STARCORE_API_KEY", "top-secret-key")
    get_settings.cache_clear()
    try:
        text = "request failed, key=top-secret-key was rejected"
        scrubbed = scrub_configured_secrets(text)
        assert "top-secret-key" not in scrubbed
        assert "***REDACTED***" in scrubbed
    finally:
        get_settings.cache_clear()


def test_scrub_configured_secrets_replaces_proxmox_token(monkeypatch):
    monkeypatch.setenv("STARCORE_PROXMOX_TOKEN_VALUE", "pve-token-abc123")
    get_settings.cache_clear()
    try:
        text = "auth header carried pve-token-abc123 to the API"
        scrubbed = scrub_configured_secrets(text)
        assert "pve-token-abc123" not in scrubbed
    finally:
        get_settings.cache_clear()


def test_scrub_configured_secrets_ignores_unset_secrets(monkeypatch):
    """An empty/unset secret must never cause every character to be
    'replaced' with the placeholder -- str.replace('', X) would otherwise
    corrupt any text."""
    monkeypatch.delenv("STARCORE_API_KEY", raising=False)
    monkeypatch.delenv("STARCORE_PROXMOX_TOKEN_VALUE", raising=False)
    monkeypatch.delenv("STARCORE_ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("STARCORE_AI_API_KEY", raising=False)
    get_settings.cache_clear()
    try:
        text = "nothing sensitive here"
        assert scrub_configured_secrets(text) == text
    finally:
        get_settings.cache_clear()


def test_scrub_configured_secrets_leaves_unrelated_text_untouched(monkeypatch):
    monkeypatch.setenv("STARCORE_API_KEY", "abc123")
    get_settings.cache_clear()
    try:
        assert scrub_configured_secrets("connection refused") == "connection refused"
    finally:
        get_settings.cache_clear()


# ---------------------------------------------------------------------------
# Endpoint-level regression sweep: no unauthenticated response leaks secrets
# ---------------------------------------------------------------------------

_SYNTHETIC_PASSWORD = "sw33t-and-s3cret-p4ssw0rd"
_SYNTHETIC_DSN = f"postgresql://prod_user:{_SYNTHETIC_PASSWORD}@db.internal.example/starcore"


def _configure_synthetic_secrets(monkeypatch) -> None:
    monkeypatch.setenv("STARCORE_DATABASE_URL", _SYNTHETIC_DSN)
    monkeypatch.setenv("STARCORE_API_KEY", "test-api-key")
    get_settings.cache_clear()


def test_root_endpoint_never_leaks_configured_database_password(monkeypatch):
    _configure_synthetic_secrets(monkeypatch)
    try:
        response = anonymous_client.get("/")
        assert _SYNTHETIC_PASSWORD not in response.text
    finally:
        get_settings.cache_clear()


def test_health_endpoint_never_leaks_configured_database_password(monkeypatch):
    _configure_synthetic_secrets(monkeypatch)
    try:
        response = anonymous_client.get("/health")
        assert _SYNTHETIC_PASSWORD not in response.text
        # The engine can't actually connect to this fake host, so this
        # exercises check_database_connectivity()'s *error* detail path --
        # the one most likely to accidentally echo something raw.
        assert response.status_code == 503
    finally:
        get_settings.cache_clear()


def test_ui_dashboard_never_leaks_configured_database_password(monkeypatch):
    _configure_synthetic_secrets(monkeypatch)
    try:
        response = anonymous_client.get("/ui")
        assert _SYNTHETIC_PASSWORD not in response.text
    finally:
        get_settings.cache_clear()


def test_unauthenticated_request_to_protected_endpoint_never_leaks_password(monkeypatch):
    """A 401/503 rejection body itself must not leak the configured DSN --
    verify_api_key() never even looks at settings.database_url, but this
    proves it as a standing invariant rather than an inference."""
    _configure_synthetic_secrets(monkeypatch)
    try:
        response = anonymous_client.get("/diagnostics")
        assert response.status_code in (401, 503)
        assert _SYNTHETIC_PASSWORD not in response.text
    finally:
        get_settings.cache_clear()
