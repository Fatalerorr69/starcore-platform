"""
JWT Authentication and RBAC Tests (REC-001).

Covers:
  - Bearer JWT happy path (login, access, refresh)
  - Expired and invalid tokens
  - Role enforcement (reader / operator / admin)
  - User management endpoints
  - Initial admin bootstrap
  - JWT not configured (fallback to legacy X-API-Key)
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
import pytest
from core.auth import (
    UserRole,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    require_role,
    verify_password,
)
from core.config import Settings, get_settings
from core.database import create_initial_admin, get_session
from core.main import app
from core.models_db import User
from fastapi.testclient import TestClient

_JWT_SECRET = "test-jwt-secret-for-unit-tests-only"
_ALGORITHM = "HS256"

client = TestClient(app)


# ── helpers ───────────────────────────────────────────────────────────────────


def _settings_with_jwt(monkeypatch) -> None:
    monkeypatch.setenv("STARCORE_JWT_SECRET_KEY", _JWT_SECRET)
    get_settings.cache_clear()


def _create_user(username: str, password: str, role: UserRole = UserRole.operator) -> User:
    session = get_session()
    try:
        user = User(
            username=username,
            hashed_password=hash_password(password),
            role=role.value,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    finally:
        session.close()


def _make_token(
    username: str,
    role: UserRole,
    token_type: str = "access",
    expired: bool = False,
) -> str:
    exp = datetime.now(UTC) + (
        timedelta(seconds=-1) if expired else timedelta(minutes=30)
    )
    payload = {
        "sub": username,
        "role": role.value,
        "type": token_type,
        "iat": datetime.now(UTC),
        "exp": exp,
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm=_ALGORITHM)


# ── Password utilities ────────────────────────────────────────────────────────


def test_hash_password_returns_valid_bcrypt_hash():
    h = hash_password("secret")
    assert h.startswith("$2b$")


def test_verify_password_correct():
    h = hash_password("mypassword")
    assert verify_password("mypassword", h) is True


def test_verify_password_wrong():
    h = hash_password("mypassword")
    assert verify_password("wrong", h) is False


# ── Token creation ────────────────────────────────────────────────────────────


def test_create_access_token_encodes_role_and_type(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        settings = get_settings()
        token = create_access_token("alice", UserRole.operator, settings)
        payload = jwt.decode(token, _JWT_SECRET, algorithms=[_ALGORITHM])
        assert payload["sub"] == "alice"
        assert payload["role"] == "operator"
        assert payload["type"] == "access"
    finally:
        get_settings.cache_clear()


def test_create_refresh_token_encodes_refresh_type(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        settings = get_settings()
        token = create_refresh_token("bob", UserRole.reader, settings)
        payload = jwt.decode(token, _JWT_SECRET, algorithms=[_ALGORITHM])
        assert payload["type"] == "refresh"
    finally:
        get_settings.cache_clear()


# ── decode_token ──────────────────────────────────────────────────────────────


def test_decode_token_raises_403_when_jwt_not_configured():
    settings = Settings(jwt_secret_key=None, api_key="k")
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        decode_token("anything", "access", settings)
    assert exc_info.value.status_code == 403


def test_decode_token_raises_401_for_expired_token(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        settings = get_settings()
        token = _make_token("alice", UserRole.reader, expired=True)
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            decode_token(token, "access", settings)
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()
    finally:
        get_settings.cache_clear()


def test_decode_token_raises_401_for_invalid_signature(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        settings = get_settings()
        token = jwt.encode({"sub": "x", "type": "access"}, "wrong-secret", algorithm="HS256")
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            decode_token(token, "access", settings)
        assert exc_info.value.status_code == 401
    finally:
        get_settings.cache_clear()


def test_decode_token_raises_401_for_wrong_type(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        settings = get_settings()
        token = _make_token("alice", UserRole.reader, token_type="refresh")
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            decode_token(token, "access", settings)
        assert exc_info.value.status_code == 401
        assert "access" in exc_info.value.detail
    finally:
        get_settings.cache_clear()


# ── Login endpoint ────────────────────────────────────────────────────────────


def test_login_returns_tokens_for_valid_credentials(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        _create_user("alice", "secret", UserRole.operator)
        resp = client.post("/auth/token", json={"username": "alice", "password": "secret"})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    finally:
        get_settings.cache_clear()


def test_login_rejects_wrong_password(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        _create_user("carol", "goodpass", UserRole.reader)
        resp = client.post("/auth/token", json={"username": "carol", "password": "badpass"})
        assert resp.status_code == 401
    finally:
        get_settings.cache_clear()


def test_login_rejects_unknown_user(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        resp = client.post("/auth/token", json={"username": "nobody", "password": "pass"})
        assert resp.status_code == 401
    finally:
        get_settings.cache_clear()


def test_login_returns_503_when_jwt_not_configured():
    resp = client.post("/auth/token", json={"username": "x", "password": "y"})
    assert resp.status_code == 503


# ── Refresh endpoint ──────────────────────────────────────────────────────────


def test_refresh_returns_new_access_token(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        _create_user("dave", "pw", UserRole.operator)
        login = client.post("/auth/token", json={"username": "dave", "password": "pw"})
        refresh_tok = login.json()["refresh_token"]
        resp = client.post("/auth/refresh", json={"refresh_token": refresh_tok})
        assert resp.status_code == 200
        assert "access_token" in resp.json()
    finally:
        get_settings.cache_clear()


def test_refresh_rejects_access_token_as_refresh(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        _create_user("eve", "pw", UserRole.reader)
        login = client.post("/auth/token", json={"username": "eve", "password": "pw"})
        access_tok = login.json()["access_token"]
        resp = client.post("/auth/refresh", json={"refresh_token": access_tok})
        assert resp.status_code == 401
    finally:
        get_settings.cache_clear()


def test_refresh_rejects_invalid_token(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        resp = client.post("/auth/refresh", json={"refresh_token": "garbage"})
        assert resp.status_code == 401
    finally:
        get_settings.cache_clear()


def test_refresh_rejects_expired_refresh_token(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        token = _make_token("alice", UserRole.reader, token_type="refresh", expired=True)
        resp = client.post("/auth/refresh", json={"refresh_token": token})
        assert resp.status_code == 401
    finally:
        get_settings.cache_clear()


# ── Bearer token access to endpoints ─────────────────────────────────────────


def test_bearer_token_grants_access_to_protected_endpoint(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        token = _make_token("alice", UserRole.reader)
        resp = client.get("/providers", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
    finally:
        get_settings.cache_clear()


def test_expired_bearer_token_is_rejected(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        token = _make_token("alice", UserRole.reader, expired=True)
        resp = client.get("/providers", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401
    finally:
        get_settings.cache_clear()


def test_invalid_bearer_token_is_rejected(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        resp = client.get("/providers", headers={"Authorization": "Bearer not.a.valid.token"})
        assert resp.status_code == 401
    finally:
        get_settings.cache_clear()


def test_bearer_with_invalid_payload_role_is_rejected(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        payload = {
            "sub": "alice",
            "role": "superuser",  # not a valid UserRole
            "type": "access",
            "exp": datetime.now(UTC) + timedelta(minutes=30),
            "iat": datetime.now(UTC),
        }
        token = jwt.encode(payload, _JWT_SECRET, algorithm=_ALGORITHM)
        resp = client.get("/providers", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401
    finally:
        get_settings.cache_clear()


def test_bearer_without_configured_secret_is_rejected(monkeypatch):
    """When JWT_SECRET_KEY is not set, Bearer tokens get 403."""
    # JWT secret is not set (conftest only sets API_KEY)
    token = _make_token("alice", UserRole.admin)
    resp = client.get("/providers", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


# ── Role enforcement ──────────────────────────────────────────────────────────


def test_reader_can_access_reader_endpoints(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        token = _make_token("reader_user", UserRole.reader)
        resp = client.get("/runs", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
    finally:
        get_settings.cache_clear()


def test_reader_cannot_access_operator_endpoints(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        token = _make_token("reader_user", UserRole.reader)
        resp = client.get("/diagnostics", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403
    finally:
        get_settings.cache_clear()


def test_operator_can_access_operator_endpoints(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        token = _make_token("op_user", UserRole.operator)
        resp = client.get("/diagnostics", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
    finally:
        get_settings.cache_clear()


def test_operator_cannot_access_admin_endpoints(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        token = _make_token("op_user", UserRole.operator)
        resp = client.get("/auth/users", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403
    finally:
        get_settings.cache_clear()


def test_admin_can_access_admin_endpoints(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        token = _make_token("admin_user", UserRole.admin)
        resp = client.get("/auth/users", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
    finally:
        get_settings.cache_clear()


def test_reader_cannot_run_resources_action(monkeypatch):
    """POST /resources/action requires operator even though the router is reader-base."""
    _settings_with_jwt(monkeypatch)
    try:
        token = _make_token("reader_user", UserRole.reader)
        resp = client.post(
            "/resources/action",
            json={"provider": "docker", "action": "start", "resource": "web"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403
    finally:
        get_settings.cache_clear()


def test_reader_cannot_discover_proxmox(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        token = _make_token("reader_user", UserRole.reader)
        resp = client.get("/proxmox/discover", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403
    finally:
        get_settings.cache_clear()


# ── User management ───────────────────────────────────────────────────────────


def test_create_user_as_admin(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        admin_token = _make_token("admin", UserRole.admin)
        resp = client.post(
            "/auth/users",
            json={"username": "newop", "password": "securepass", "role": "operator"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "newop"
        assert data["role"] == "operator"
        assert data["is_active"] is True
    finally:
        get_settings.cache_clear()


def test_create_user_default_role_is_operator(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        admin_token = _make_token("admin", UserRole.admin)
        resp = client.post(
            "/auth/users",
            json={"username": "defaultrole", "password": "pw"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 201
        assert resp.json()["role"] == "operator"
    finally:
        get_settings.cache_clear()


def test_create_duplicate_user_returns_409(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        admin_token = _make_token("admin", UserRole.admin)
        _create_user("existing", "pw", UserRole.reader)
        resp = client.post(
            "/auth/users",
            json={"username": "existing", "password": "pw"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 409
    finally:
        get_settings.cache_clear()


def test_list_users_returns_created_users(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        _create_user("user1", "pw1", UserRole.reader)
        _create_user("user2", "pw2", UserRole.operator)
        admin_token = _make_token("admin", UserRole.admin)
        resp = client.get("/auth/users", headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        usernames = {u["username"] for u in resp.json()}
        assert "user1" in usernames
        assert "user2" in usernames
    finally:
        get_settings.cache_clear()


def test_non_admin_cannot_create_user(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        op_token = _make_token("op", UserRole.operator)
        resp = client.post(
            "/auth/users",
            json={"username": "newuser", "password": "pw"},
            headers={"Authorization": f"Bearer {op_token}"},
        )
        assert resp.status_code == 403
    finally:
        get_settings.cache_clear()


def test_non_admin_cannot_list_users(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        reader_token = _make_token("reader", UserRole.reader)
        resp = client.get("/auth/users", headers={"Authorization": f"Bearer {reader_token}"})
        assert resp.status_code == 403
    finally:
        get_settings.cache_clear()


# ── Legacy X-API-Key + JWT coexistence ───────────────────────────────────────


def test_legacy_api_key_still_grants_access_when_jwt_configured(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:
        resp = client.get("/providers", headers={"X-API-Key": "test-api-key"})
        assert resp.status_code == 200
    finally:
        get_settings.cache_clear()


def test_legacy_api_key_grants_admin_access(monkeypatch):
    """X-API-Key maps to admin; user management endpoints must accept it."""
    _settings_with_jwt(monkeypatch)
    try:
        resp = client.get("/auth/users", headers={"X-API-Key": "test-api-key"})
        assert resp.status_code == 200
    finally:
        get_settings.cache_clear()


def test_no_auth_header_returns_401():
    resp = client.get("/providers")
    assert resp.status_code == 401


# ── Initial admin bootstrap ───────────────────────────────────────────────────


def test_create_initial_admin_creates_admin_user(monkeypatch):
    monkeypatch.setenv("STARCORE_INITIAL_ADMIN_PASSWORD", "bootstrap-pw")
    get_settings.cache_clear()
    try:
        created = create_initial_admin()
        assert created is True
        session = get_session()
        try:
            user = session.query(User).filter_by(username="admin").first()
            assert user is not None
            assert user.role == "admin"
        finally:
            session.close()
    finally:
        get_settings.cache_clear()


def test_create_initial_admin_is_idempotent(monkeypatch):
    monkeypatch.setenv("STARCORE_INITIAL_ADMIN_PASSWORD", "bootstrap-pw")
    get_settings.cache_clear()
    try:
        first = create_initial_admin()
        second = create_initial_admin()
        assert first is True
        assert second is False
    finally:
        get_settings.cache_clear()


def test_create_initial_admin_noop_when_password_not_configured():
    created = create_initial_admin()
    assert created is False


def test_create_initial_admin_skips_if_admin_exists(monkeypatch):
    monkeypatch.setenv("STARCORE_INITIAL_ADMIN_PASSWORD", "pw")
    get_settings.cache_clear()
    try:
        _create_user("admin", "existing-pw", UserRole.admin)
        created = create_initial_admin()
        assert created is False
    finally:
        get_settings.cache_clear()


# ── require_role unit tests ───────────────────────────────────────────────────


@pytest.mark.anyio
async def test_require_role_allows_sufficient_role(monkeypatch):
    _settings_with_jwt(monkeypatch)
    try:

        from core.auth import UserPrincipal, UserRole

        principal = UserPrincipal(username="alice", role=UserRole.operator)
        check_fn = require_role(UserRole.reader)

        class _FakeDep:
            async def __call__(self) -> UserPrincipal:
                return principal

        result = await check_fn(principal)
        assert result == principal
    finally:
        get_settings.cache_clear()


@pytest.mark.anyio
async def test_require_role_rejects_insufficient_role():
    from core.auth import UserPrincipal, UserRole
    from fastapi import HTTPException

    principal = UserPrincipal(username="reader", role=UserRole.reader)
    check_fn = require_role(UserRole.operator)
    with pytest.raises(HTTPException) as exc_info:
        await check_fn(principal)
    assert exc_info.value.status_code == 403


# ── Startup event ─────────────────────────────────────────────────────────────


def test_startup_event_calls_create_initial_admin():
    """The ASGI startup handler must invoke create_initial_admin()."""
    from unittest.mock import patch

    with patch("core.main.create_initial_admin") as mock_fn:
        mock_fn.return_value = False
        with TestClient(app):
            pass
    mock_fn.assert_called_once()


# ── Refresh token with invalid role payload ───────────────────────────────────


def test_refresh_rejects_token_with_invalid_role(monkeypatch):
    """A refresh token that decodes fine but carries an unrecognised role → 401."""
    _settings_with_jwt(monkeypatch)
    try:
        payload = {
            "sub": "alice",
            "role": "superadmin",
            "type": "refresh",
            "exp": datetime.now(UTC) + timedelta(minutes=30),
            "iat": datetime.now(UTC),
        }
        token = jwt.encode(payload, _JWT_SECRET, algorithm=_ALGORITHM)
        resp = client.post("/auth/refresh", json={"refresh_token": token})
        assert resp.status_code == 401
    finally:
        get_settings.cache_clear()
