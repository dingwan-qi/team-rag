"""Chat routes."""

from __future__ import annotations

from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_chat_service
from app.rag.schemas import ChatRequest, RAGResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=RAGResponse)
def chat(
    payload: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> RAGResponse:
    try:
        return service.answer(
            payload.query,
            rag_mode=payload.rag_mode,
            top_k=payload.top_k,
            metadata_filter=payload.metadata_filter,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/chat/stream")
def chat_stream(
    payload: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> StreamingResponse:
    response = chat(payload, service)

    def generate() -> Iterator[str]:
        yield from response.answer

    return StreamingResponse(generate(), media_type="text/plain; charset=utf-8")
