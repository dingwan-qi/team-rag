"""Chat routes."""

from __future__ import annotations

from collections.abc import Iterator

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_chat_service, get_user_service
from app.api.routes.auth import get_optional_user
from app.rag.schemas import ChatRequest, RAGResponse
from app.services.chat_service import ChatService
from app.services.user_service import UserService

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=RAGResponse)
def chat(
    payload: ChatRequest,
    authorization: str | None = Header(default=None),
    service: ChatService = Depends(get_chat_service),
    user_service: UserService = Depends(get_user_service),
) -> RAGResponse:
    user = get_optional_user(authorization, user_service)
    memory_context = user_service.memory_context(user.id) if user else []
    try:
        response = service.answer(
            payload.query,
            rag_mode=payload.rag_mode,
            top_k=payload.top_k,
            metadata_filter=payload.metadata_filter,
            memory_context=memory_context,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if user:
        user_service.add_memory(user.id, "user", payload.query, payload.rag_mode)
        user_service.add_memory(user.id, "assistant", response.answer, response.rag_mode)
        response.metadata["memory_saved"] = True
    return response


@router.post("/chat/stream")
def chat_stream(
    payload: ChatRequest,
    authorization: str | None = Header(default=None),
    service: ChatService = Depends(get_chat_service),
    user_service: UserService = Depends(get_user_service),
) -> StreamingResponse:
    response = chat(payload, authorization, service, user_service)

    def generate() -> Iterator[str]:
        yield from response.answer

    return StreamingResponse(generate(), media_type="text/plain; charset=utf-8")
