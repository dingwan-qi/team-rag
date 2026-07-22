"""Deterministic text splitter used by the ingestion pipeline."""

from __future__ import annotations


def split_text(text: str, chunk_size: int = 700, chunk_overlap: int = 120) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    text = text.strip()
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        candidate = text[start:end]
        if end < len(text):
            split_at = max(candidate.rfind("\n"), candidate.rfind("。"), candidate.rfind("."))
            if split_at > chunk_size // 2:
                end = start + split_at + 1
                candidate = text[start:end]
        chunks.append(candidate.strip())
        if end >= len(text):
            break
        start = max(0, end - chunk_overlap)
    return [chunk for chunk in chunks if chunk]

