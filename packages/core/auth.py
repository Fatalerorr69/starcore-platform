"""
Authentication and RBAC (REC-001).

Two authentication paths are supported simultaneously:

1. Bearer JWT  — ``Authorization: Bearer <token>``
   Requires ``STARCORE_JWT_SECRET_KEY`` to be configured.  The token payload
   carries ``sub`` (username) and ``role`` (reader/operator/admin).

2. Legacy X-API-Key — ``X-API-Key: <key>``
   Requires ``STARCORE_API_KEY`` to be configured.  Always grants admin role
   for full backward compatibility with existing deployments.

Use ``require_role(minimum_role)`` as a FastAPI dependency to gate endpoints.
"""

from __future__ import annotations

import hmac
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Annotated, Any, NamedTuple

import bcrypt
import jwt
from fastapi import Depends, Header, HTTPException

from core.config import Settings, get_settings

_ALGORITHM = "HS256"


class UserRole(StrEnum):
    reader = "reader"
    operator = "operator"
    admin = "admin"


_ROLE_WEIGHT: dict[UserRole, int] = {
    UserRole.reader: 0,
    UserRole.operator: 1,
    UserRole.admin: 2,
}


class UserPrincipal(NamedTuple):
    username: str
    role: UserRole


# ── Password utilities ────────────────────────────────────────────────────────


def hash_password(password: str) -> str:
    """Return a bcrypt hash of *password*."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Return True when *plain* matches the stored *hashed* bcrypt value."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ── JWT utilities ─────────────────────────────────────────────────────────────


def create_access_token(username: str, role: UserRole, settings: Settings) -> str:
    """Encode a short-lived access JWT for *username* / *role*."""
    payload = {
        "sub": username,
        "role": role.value,
        "type": "access",
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=_ALGORITHM)


def create_refresh_token(username: str, role: UserRole, settings: Settings) -> str:
    """Encode a long-lived refresh JWT for *username* / *role*."""
    payload = {
        "sub": username,
        "role": role.value,
        "type": "refresh",
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=_ALGORITHM)


def decode_token(token: str, expected_type: str, settings: Settings) -> dict[str, Any]:
    """Decode and validate a JWT; raise HTTPException on any failure."""
    if not settings.jwt_secret_key:
        raise HTTPException(status_code=403, detail="JWT authentication not configured on server.")
    try:
        payload: dict[str, Any] = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.") from None
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.") from None
    if payload.get("type") != expected_type:
        raise HTTPException(
            status_code=401, detail=f"Expected {expected_type!r} token type."
        )
    return payload


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def get_current_user(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> UserPrincipal:
    """Resolve the calling principal from either Bearer JWT or X-API-Key.

    Bearer JWT is attempted first; X-API-Key (legacy) is the fallback.
    Returns a :class:`UserPrincipal` with ``username`` and ``role``.
    """
    settings = get_settings()

    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ")
        payload = decode_token(token, "access", settings)
        try:
            role = UserRole(payload["role"])
        except (KeyError, ValueError) as exc:
            raise HTTPException(status_code=401, detail="Invalid token payload.") from exc
        return UserPrincipal(username=payload["sub"], role=role)

    if x_api_key is not None:
        if not settings.api_key:
            raise HTTPException(
                status_code=503,
                detail="API key not configured on server. Set STARCORE_API_KEY in .env.",
            )
        if not hmac.compare_digest(x_api_key, settings.api_key):
            raise HTTPException(
                status_code=401,
                detail="Missing or invalid API key. Provide it via the X-API-Key header.",
            )
        return UserPrincipal(username="api-key", role=UserRole.admin)

    raise HTTPException(
        status_code=401,
        detail="Authorization required. Use 'Authorization: Bearer <token>' or 'X-API-Key' header.",
    )


def require_role(minimum_role: UserRole) -> Callable[..., Any]:
    """Return a FastAPI dependency that enforces *minimum_role* or higher.

    Usage::

        router = APIRouter(dependencies=[Depends(require_role(UserRole.operator))])
    """

    async def _check(
        principal: Annotated[UserPrincipal, Depends(get_current_user)],
    ) -> UserPrincipal:
        if _ROLE_WEIGHT[principal.role] < _ROLE_WEIGHT[minimum_role]:
            raise HTTPException(
                status_code=403,
                detail=f"Requires '{minimum_role.value}' role or higher.",
            )
        return principal

    return _check
