"""Metadata helpers for document chunks."""

from __future__ import annotations

import hashlib
from pathlib import Path

from app.rag.schemas import DocumentChunk, DocumentPage


def document_id_from_bytes(content: bytes) -> str:
    return hashlib.sha1(content).hexdigest()[:16]


def chunk_id(document_id: str, page_number: int, chunk_index: int) -> str:
    raw = f"{document_id}:{page_number}:{chunk_index}".encode()
    return hashlib.sha1(raw).hexdigest()[:20]


def build_chunk(
    *,
    document_id: str,
    path: Path,
    page: DocumentPage,
    text: str,
    chunk_index: int,
) -> DocumentChunk:
    metadata = {
        "filename": path.name,
        "file_type": path.suffix.lower().lstrip("."),
        "page_number": page.page_number,
        "section": page.section,
        "chunk_index": chunk_index,
    }
    return DocumentChunk(
        id=chunk_id(document_id, page.page_number, chunk_index),
        document_id=document_id,
        text=text,
        metadata=metadata,
    )

