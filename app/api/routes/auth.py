"""Authentication routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from app.api.dependencies import get_user_service
from app.services.user_service import UserRecord, UserService

router = APIRouter(prefix="/api/auth", tags=["auth"])


class AuthPayload(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=6)


class UserProfile(BaseModel):
    id: str
    username: str
    created_at: str


class AuthResponse(BaseModel):
    token: str
    user: UserProfile


class MessageResponse(BaseModel):
    message: str


@router.post("/register", response_model=AuthResponse)
def register(
    payload: AuthPayload,
    service: UserService = Depends(get_user_service),
) -> AuthResponse:
    try:
        result = service.register(payload.username, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return AuthResponse(token=result.token, user=_profile(result.user))


@router.post("/login", response_model=AuthResponse)
def login(
    payload: AuthPayload,
    service: UserService = Depends(get_user_service),
) -> AuthResponse:
    try:
        result = service.login(payload.username, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return AuthResponse(token=result.token, user=_profile(result.user))


@router.get("/me", response_model=UserProfile)
def me(
    authorization: str | None = Header(default=None),
    service: UserService = Depends(get_user_service),
) -> UserProfile:
    return _profile(_require_user(authorization, service))


@router.post("/logout", response_model=MessageResponse)
def logout(
    authorization: str | None = Header(default=None),
    service: UserService = Depends(get_user_service),
) -> MessageResponse:
    token = _extract_bearer_token(authorization)
    if token:
        service.logout(token)
    return MessageResponse(message="已退出登录")


def get_optional_user(
    authorization: str | None,
    service: UserService,
) -> UserRecord | None:
    token = _extract_bearer_token(authorization)
    if token is None:
        return None
    user = service.get_user_by_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="登录状态无效或已过期")
    return user


def _require_user(authorization: str | None, service: UserService) -> UserRecord:
    user = get_optional_user(authorization, service)
    if user is None:
        raise HTTPException(status_code=401, detail="请先登录")
    return user


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(status_code=401, detail="Authorization 需要使用 Bearer token")
    return token.strip()


def _profile(user: UserRecord) -> UserProfile:
    return UserProfile(id=user.id, username=user.username, created_at=user.created_at)
