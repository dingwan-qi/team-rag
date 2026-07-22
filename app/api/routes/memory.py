"""Persistent user memory routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field

from app.api.dependencies import get_user_service
from app.api.routes.auth import _require_user
from app.services.user_service import UserService

router = APIRouter(prefix="/api/memory", tags=["memory"])


class MemoryMessage(BaseModel):
    id: str
    role: str
    content: str
    rag_mode: str | None = None
    created_at: str


class MemoryResponse(BaseModel):
    messages: list[MemoryMessage] = Field(default_factory=list)


class MessageResponse(BaseModel):
    message: str


@router.get("", response_model=MemoryResponse)
def list_memory(
    authorization: str | None = Header(default=None),
    service: UserService = Depends(get_user_service),
) -> MemoryResponse:
    user = _require_user(authorization, service)
    return MemoryResponse(messages=service.list_memory(user.id))


@router.delete("", response_model=MessageResponse)
def clear_memory(
    authorization: str | None = Header(default=None),
    service: UserService = Depends(get_user_service),
) -> MessageResponse:
    user = _require_user(authorization, service)
    service.clear_memory(user.id)
    return MessageResponse(message="聊天记忆已清空")
