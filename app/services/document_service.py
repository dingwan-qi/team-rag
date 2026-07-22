"""Document upload, indexing, listing, and deletion service."""

from __future__ import annotations

import re
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import DuplicateDocumentError
from app.ingestion.loaders import supported_file
from app.ingestion.metadata import document_id_from_bytes
from app.ingestion.pipeline import IngestionPipeline
from app.rag.schemas import DocumentSummary, IndexResponse, UploadResponse
from app.retrieval.vector_retriever import VectorRetriever


class DocumentService:
    def __init__(
        self,
        upload_dir: Path | None = None,
        pipeline: IngestionPipeline | None = None,
        retriever: VectorRetriever | None = None,
    ):
        self.upload_dir = upload_dir or settings.upload_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.pipeline = pipeline or IngestionPipeline()
        self.retriever = retriever or VectorRetriever()

    def save_and_index(self, filename: str, content: bytes) -> UploadResponse:
        if not content:
            raise ValueError("上传文件为空")
        if not supported_file(filename):
            raise ValueError("仅支持 PDF、DOCX、TXT 和 Markdown 文件")

        document_id = document_id_from_bytes(content)
        if any(doc.document_id == document_id for doc in self.retriever.list_documents()):
            existing = next(doc for doc in self.retriever.list_documents() if doc.document_id == document_id)
            return UploadResponse(
                document_id=document_id,
                filename=existing.filename,
                chunks=existing.chunk_count,
                duplicate=True,
                message="重复文件，已复用现有索引",
            )

        safe_name = _safe_filename(filename)
        target = self.upload_dir / f"{document_id}_{safe_name}"
        target.write_bytes(content)
        try:
            _, chunks = self.pipeline.prepare_file(target, display_name=filename)
        except Exception:
            target.unlink(missing_ok=True)
            raise
        self.retriever.add_chunks(chunks)
        return UploadResponse(
            document_id=document_id,
            filename=filename,
            chunks=len(chunks),
            duplicate=False,
            message="文件已上传并完成索引",
        )

    def index_uploaded_files(self) -> IndexResponse:
        indexed_documents = 0
        indexed_chunks = 0
        for path in self.upload_dir.iterdir():
            if not path.is_file() or not supported_file(path.name):
                continue
            try:
                _, chunks = self.pipeline.prepare_file(path, display_name=_display_name(path))
                self.retriever.add_chunks(chunks)
            except DuplicateDocumentError:
                continue
            indexed_documents += 1
            indexed_chunks += len(chunks)
        return IndexResponse(
            indexed_documents=indexed_documents,
            indexed_chunks=indexed_chunks,
            backend=self.retriever.backend_name,
            message="索引构建完成",
        )

    def list_documents(self) -> list[DocumentSummary]:
        return self.retriever.list_documents()

    def delete_document(self, document_id: str) -> dict[str, int | str]:
        deleted_chunks = self.retriever.delete_document(document_id)
        deleted_files = 0
        for path in self.upload_dir.glob(f"{document_id}_*"):
            path.unlink(missing_ok=True)
            deleted_files += 1
        return {
            "document_id": document_id,
            "deleted_chunks": deleted_chunks,
            "deleted_files": deleted_files,
        }


def _safe_filename(filename: str) -> str:
    name = Path(filename).name
    return re.sub(r"[^A-Za-z0-9_.\-\u4e00-\u9fff]+", "_", name)


def _display_name(path: Path) -> str:
    parts = path.name.split("_", 1)
    return parts[1] if len(parts) == 2 else path.name

