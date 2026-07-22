from __future__ import annotations

from pathlib import Path

from app.retrieval.vector_retriever import VectorRetriever
from app.services.document_service import DocumentService


def test_document_service_indexes_and_deduplicates(tmp_path: Path) -> None:
    retriever = VectorRetriever(tmp_path / "chroma")
    service = DocumentService(tmp_path / "uploads", retriever=retriever)
    content = "# RAG\nRAG 包含检索、上下文构建和答案生成。".encode()

    first = service.save_and_index("course.md", content)
    second = service.save_and_index("course.md", content)

    assert first.chunks == 1
    assert second.duplicate is True
    assert len(service.list_documents()) == 1

    deleted = service.delete_document(first.document_id)
    assert deleted["deleted_chunks"] == 1
    assert service.list_documents() == []

