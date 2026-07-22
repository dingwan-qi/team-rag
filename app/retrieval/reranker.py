"""Lightweight reranker that can later be replaced by a model reranker."""

from __future__ import annotations

from app.rag.schemas import RetrievedChunk
from app.retrieval.base import tokenize


class LightweightReranker:
    def rerank(self, query: str, hits: list[RetrievedChunk], top_k: int) -> list[RetrievedChunk]:
        query_tokens = set(tokenize(query))
        reranked: list[RetrievedChunk] = []
        for hit in hits:
            chunk_tokens = set(tokenize(hit.chunk.text))
            overlap = len(query_tokens & chunk_tokens) / max(len(query_tokens), 1)
            section_bonus = 0.05 if hit.chunk.metadata.get("section") else 0.0
            score = hit.score * 0.7 + overlap * 0.25 + section_bonus
            reranked.append(RetrievedChunk(chunk=hit.chunk, score=score))
        reranked.sort(key=lambda item: item.score, reverse=True)
        return reranked[:top_k]

