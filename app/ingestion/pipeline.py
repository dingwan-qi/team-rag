"""End-to-end document ingestion and chunk preparation."""

from __future__ import annotations

from pathlib import Path

from app.core.config import settings
from app.core.exceptions import EmptyDocumentError
from app.ingestion.cleaner import clean_text
from app.ingestion.loaders import load_document
from app.ingestion.metadata import build_chunk, document_id_from_bytes
from app.ingestion.splitter import split_text
from app.rag.schemas import DocumentChunk


class IngestionPipeline:
    def __init__(self, chunk_size: int | None = None, chunk_overlap: int | None = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

    def prepare_file(self, path: Path, display_name: str | None = None) -> tuple[str, list[DocumentChunk]]:
        content = path.read_bytes()
        document_id = document_id_from_bytes(content)
        pages = load_document(path)
        metadata_path = Path(display_name) if display_name else path

        chunks: list[DocumentChunk] = []
        chunk_index = 0
        for page in pages:
            cleaned = clean_text(page.text)
            for piece in split_text(cleaned, self.chunk_size, self.chunk_overlap):
                chunks.append(
                    build_chunk(
                        document_id=document_id,
                        path=metadata_path,
                        page=page,
                        text=piece,
                        chunk_index=chunk_index,
                    ),
                )
                chunk_index += 1

        if not chunks:
            raise EmptyDocumentError("文档清洗和分块后没有可索引内容")
        return document_id, chunks
