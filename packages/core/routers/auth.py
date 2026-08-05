"""
Auth router — login, token refresh, and user management.

Endpoints:
  POST /auth/token      — login (username + password) → access + refresh tokens
  POST /auth/refresh    — exchange refresh token → new access token
  POST /auth/users      — create user (admin only)
  GET  /auth/users      — list users (admin only)
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.auth import (
    UserPrincipal,
    UserRole,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    require_role,
    verify_password,
)
from core.config import get_settings
from core.database import get_session
from core.models_db import User

router = APIRouter(prefix="/auth", tags=["auth"])

_AdminPrincipal = Annotated[UserPrincipal, Depends(require_role(UserRole.admin))]


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: UserRole = UserRole.operator


class UserResponse(BaseModel):
    id: str
    username: str
    role: str
    is_active: bool


@router.post("/token", response_model=TokenResponse)
def login(req: LoginRequest) -> TokenResponse:
    """Authenticate with username and password; receive access + refresh tokens."""
    settings = get_settings()
    if not settings.jwt_secret_key:
        raise HTTPException(status_code=503, detail="JWT authentication not configured on server.")
    session = get_session()
    try:
        user = session.query(User).filter_by(username=req.username, is_active=True).first()
        if user is None or not verify_password(req.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials.")
        role = UserRole(user.role)
        return TokenResponse(
            access_token=create_access_token(user.username, role, settings),
            refresh_token=create_refresh_token(user.username, role, settings),
        )
    finally:
        session.close()


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh_token(req: RefreshRequest) -> AccessTokenResponse:
    """Exchange a valid refresh token for a new access token."""
    settings = get_settings()
    payload = decode_token(req.refresh_token, "refresh", settings)
    try:
        role = UserRole(payload["role"])
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid token payload.") from exc
    return AccessTokenResponse(access_token=create_access_token(payload["sub"], role, settings))


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(req: CreateUserRequest, _: _AdminPrincipal) -> UserResponse:
    """Create a new user. Requires admin role."""
    session = get_session()
    try:
        if session.query(User).filter_by(username=req.username).first():
            raise HTTPException(status_code=409, detail=f"User {req.username!r} already exists.")
        user = User(
            username=req.username,
            hashed_password=hash_password(req.password),
            role=req.role.value,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return UserResponse(
            id=user.id,
            username=user.username,
            role=user.role,
            is_active=user.is_active,
        )
    finally:
        session.close()


@router.get("/users", response_model=list[UserResponse])
def list_users(_: _AdminPrincipal) -> list[UserResponse]:
    """List all users. Requires admin role."""
    session = get_session()
    try:
        users = session.query(User).all()
        return [
            UserResponse(id=u.id, username=u.username, role=u.role, is_active=u.is_active)
            for u in users
        ]
    finally:
        session.close()
