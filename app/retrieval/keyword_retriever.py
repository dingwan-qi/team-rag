"""Keyword retrieval over indexed chunks."""

from __future__ import annotations

from app.rag.schemas import RetrievedChunk
from app.retrieval.base import metadata_matches, tokenize
from app.retrieval.vector_retriever import VectorRetriever


class KeywordRetriever:
    def __init__(self, vector_retriever: VectorRetriever | None = None):
        self.vector_retriever = vector_retriever or VectorRetriever()

    def search(
        self,
        query: str,
        top_k: int = 4,
        metadata_filter: dict[str, object] | None = None,
    ) -> list[RetrievedChunk]:
        query_tokens = set(tokenize(query))
        if not query_tokens:
            return []

        hits: list[RetrievedChunk] = []
        for chunk in self.vector_retriever.all_chunks():
            if not metadata_matches(chunk.metadata, metadata_filter):
                continue
            chunk_tokens = tokenize(chunk.text)
            if not chunk_tokens:
                continue
            overlap = sum(1 for token in chunk_tokens if token in query_tokens)
            if overlap == 0:
                continue
            coverage = len(set(chunk_tokens) & query_tokens) / max(len(query_tokens), 1)
            density = overlap / max(len(chunk_tokens), 1)
            hits.append(RetrievedChunk(chunk=chunk, score=coverage * 0.8 + density * 0.2))

        hits.sort(key=lambda item: item.score, reverse=True)
        return hits[:top_k]

