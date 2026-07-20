"""State schema used by the LangGraph workflow."""

from __future__ import annotations

from typing import Any, TypedDict

from app.rag.schemas import AgentStep, RAGResponse


class AgentState(TypedDict, total=False):
    query: str
    top_k: int
    metadata_filter: dict[str, Any] | None
    route: str
    rewritten_query: str
    retries: int
    needs_retry: bool
    response: RAGResponse | None
    steps: list[AgentStep]

