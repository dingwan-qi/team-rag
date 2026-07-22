"""Unified RAG interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.rag.schemas import RAGResponse


class BaseRAG(ABC):
    @abstractmethod
    def answer(
        self,
        query: str,
        top_k: int = 4,
        metadata_filter: dict[str, object] | None = None,
    ) -> RAGResponse:
        """Return a unified RAG response."""

