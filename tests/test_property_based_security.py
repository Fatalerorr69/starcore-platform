"""
Property-Based Tests — core.security

Verifies structural invariants for redact_database_url and
scrub_configured_secrets that must hold for all valid inputs.
"""

from __future__ import annotations

from core.config import Settings
from core.security import redact_database_url, scrub_configured_secrets
from hypothesis import given
from hypothesis import strategies as st

# ── Strategies ─────────────────────────────────────────────────────────────────

_ANY_STRING = st.text(min_size=0, max_size=200)

# Restricted to chars absent from REDACTED_PLACEHOLDER ("***REDACTED***") and free
# of URL metacharacters, so postgres DSNs constructed from these always parse correctly.
_SAFE_SECRET = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=40
)
_HOSTNAME = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=3, max_size=20
)


# ── redact_database_url invariants ─────────────────────────────────────────────


@given(url=_ANY_STRING)
def test_redact_database_url_never_raises(url: str) -> None:
    """redact_database_url never raises for any string input."""
    redact_database_url(url)  # must not raise


@given(password=_SAFE_SECRET, hostname=_HOSTNAME)
def test_redact_database_url_masks_postgres_password(password: str, hostname: str) -> None:
    """For any postgres DSN, the :<password>@ pattern never appears in the result."""
    url = f"postgresql://user:{password}@{hostname}/db"
    result = redact_database_url(url)
    assert f":{password}@" not in result


@given(db_name=_SAFE_SECRET)
def test_redact_database_url_sqlite_passthrough(db_name: str) -> None:
    """SQLite URLs carry no credentials; the rendered form starts with 'sqlite'."""
    url = f"sqlite:///{db_name}.db"
    result = redact_database_url(url)
    assert result.startswith("sqlite")


# ── scrub_configured_secrets invariants ────────────────────────────────────────


@given(text=_ANY_STRING, secret=_SAFE_SECRET)
def test_scrub_configured_secrets_never_returns_configured_secret(
    text: str, secret: str
) -> None:
    """scrub_configured_secrets never returns text containing the configured secret."""
    s = Settings.model_construct(
        api_key=secret, proxmox_token_value=None, anthropic_api_key=None, ai_api_key=None
    )
    result = scrub_configured_secrets(text, settings=s)
    assert secret not in result


@given(text=_ANY_STRING, secret=_SAFE_SECRET)
def test_scrub_configured_secrets_is_idempotent(text: str, secret: str) -> None:
    """Calling scrub_configured_secrets twice gives the same result as once."""
    s = Settings.model_construct(
        api_key=secret, proxmox_token_value=None, anthropic_api_key=None, ai_api_key=None
    )
    once = scrub_configured_secrets(text, settings=s)
    twice = scrub_configured_secrets(once, settings=s)
    assert once == twice


@given(text=_ANY_STRING)
def test_scrub_configured_secrets_with_no_secrets_is_noop(text: str) -> None:
    """When no secrets are configured, scrub_configured_secrets returns text unchanged."""
    s = Settings.model_construct(
        api_key=None, proxmox_token_value=None, anthropic_api_key=None, ai_api_key=None
    )
    result = scrub_configured_secrets(text, settings=s)
    assert result == text
