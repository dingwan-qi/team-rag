"""Context de-duplication and length compression."""

from __future__ import annotations

from app.rag.schemas import RetrievedChunk


class ContextCompressor:
    def __init__(self, max_chars_per_chunk: int = 900):
        self.max_chars_per_chunk = max_chars_per_chunk

    def compress(self, hits: list[RetrievedChunk]) -> list[RetrievedChunk]:
        compressed: list[RetrievedChunk] = []
        seen: set[str] = set()
        for hit in hits:
            normalized = " ".join(hit.chunk.text.split())
            fingerprint = normalized[:180]
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            if len(normalized) > self.max_chars_per_chunk:
                hit.chunk.text = f"{normalized[: self.max_chars_per_chunk]}..."
            else:
                hit.chunk.text = normalized
            compressed.append(hit)
        return compressed

