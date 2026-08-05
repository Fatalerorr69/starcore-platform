"""
Secret redaction

Centralized utilities for keeping configured secrets (database credentials,
API keys, provider tokens) out of anything that might reach a response
body, a log line, or a CLI output -- whether that surface is authenticated
or not. Endpoint- or provider-specific string replacement is exactly what
this module exists to avoid: every call site that might echo back
user-configured secret material should redact through here, once, rather
than reimplementing masking logic locally.
"""

from __future__ import annotations

from sqlalchemy.engine import make_url

from core.config import Settings, get_settings

REDACTED_PLACEHOLDER = "***REDACTED***"


def redact_database_url(database_url: str) -> str:
    """Render *database_url* with any embedded credentials masked.

    A `STARCORE_DATABASE_URL` pointing at Postgres/MySQL/etc. commonly
    embeds `user:password@host`; the default SQLite URL carries no
    credentials, so this is a no-op for it. Falls back to a fixed
    placeholder, never the raw input, if the URL cannot be parsed --
    an unparseable string must never reach a response body unmodified
    on the theory that "at least it's not a valid DSN".
    """
    try:
        return make_url(database_url).render_as_string(hide_password=True)
    except Exception:
        return "<unparseable database URL>"


def scrub_configured_secrets(text: str, settings: Settings | None = None) -> str:
    """Replace any currently-configured secret value found verbatim in *text*.

    Defense in depth for free-text strings this process doesn't fully
    control the shape of -- most importantly exception messages surfaced
    from third-party provider SDKs (proxmoxer, docker-py), which could in
    principle echo back connection details. Every `STARCORE_*` setting that
    holds a bearer credential (API keys, the Proxmox API token, AI provider
    keys) is checked; each occurrence is replaced with a fixed placeholder.
    Empty/unset secrets are skipped so an empty string never causes
    every character boundary in *text* to be "replaced" with the
    placeholder.
    """
    settings = settings or get_settings()
    secret_values = (
        settings.api_key,
        settings.proxmox_token_value,
        settings.anthropic_api_key,
        settings.ai_api_key,
    )
    result = text
    for value in secret_values:
        if value:
            result = result.replace(value, REDACTED_PLACEHOLDER)
    return result
