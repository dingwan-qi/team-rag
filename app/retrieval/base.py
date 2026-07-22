"""Retriever protocol and helper functions."""

from __future__ import annotations

import math
import re
from typing import Protocol

from app.rag.schemas import DocumentChunk, RetrievedChunk

TOKEN_RE = re.compile(r"[\u4e00-\u9fff]|[A-Za-z0-9_]+")


class BaseRetriever(Protocol):
    def search(
        self,
        query: str,
        top_k: int = 4,
        metadata_filter: dict[str, object] | None = None,
    ) -> list[RetrievedChunk]:
        ...


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def metadata_matches(
    metadata: dict[str, object],
    metadata_filter: dict[str, object] | None,
) -> bool:
    if not metadata_filter:
        return True
    for key, expected in metadata_filter.items():
        if expected in (None, "", []):
            continue
        if metadata.get(key) != expected:
            return False
    return True


def chunk_to_source(chunk: DocumentChunk, score: float | None = None) -> dict[str, object]:
    return {
        "document_id": chunk.document_id,
        "filename": str(chunk.metadata.get("filename", "")),
        "chunk_id": chunk.id,
        "page_number": chunk.metadata.get("page_number"),
        "score": score,
    }

