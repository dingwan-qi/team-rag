"""Hybrid vector and keyword retrieval."""

from __future__ import annotations

from collections import defaultdict

from app.rag.schemas import RetrievedChunk
from app.retrieval.keyword_retriever import KeywordRetriever
from app.retrieval.vector_retriever import VectorRetriever


class HybridRetriever:
    def __init__(self, vector_retriever: VectorRetriever | None = None):
        self.vector_retriever = vector_retriever or VectorRetriever()
        self.keyword_retriever = KeywordRetriever(self.vector_retriever)

    def search(
        self,
        query: str,
        top_k: int = 4,
        metadata_filter: dict[str, object] | None = None,
    ) -> list[RetrievedChunk]:
        vector_hits = self.vector_retriever.search(query, top_k * 2, metadata_filter)
        keyword_hits = self.keyword_retriever.search(query, top_k * 2, metadata_filter)

        merged: dict[str, RetrievedChunk] = {}
        scores: dict[str, float] = defaultdict(float)
        for hit in vector_hits:
            merged[hit.chunk.id] = hit
            scores[hit.chunk.id] += hit.score * 0.65
        for hit in keyword_hits:
            merged[hit.chunk.id] = hit
            scores[hit.chunk.id] += hit.score * 0.35

        results = [
            RetrievedChunk(chunk=hit.chunk, score=scores[chunk_id])
            for chunk_id, hit in merged.items()
        ]
        results.sort(key=lambda item: item.score, reverse=True)
        return results[:top_k]

