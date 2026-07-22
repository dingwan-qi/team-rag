from __future__ import annotations

import os
import re
import uuid
from pathlib import Path

import pytest

os.environ.setdefault("EMBEDDING_BACKEND", "hashing")
os.environ.setdefault("VECTOR_BACKEND", "json")
os.environ["LLM_API_KEY"] = ""
os.environ["LLM_BASE_URL"] = ""
os.environ["LLM_MODEL"] = ""

from app.rag.schemas import DocumentChunk
from app.retrieval.vector_retriever import VectorRetriever

TEST_TEMP_ROOT = Path(__file__).resolve().parents[1] / ".test_tmp_work"


@pytest.fixture()
def tmp_path(request: pytest.FixtureRequest) -> Path:
    """Use a project-local temp path to avoid locked Windows pytest temp roots."""
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", request.node.nodeid)
    path = TEST_TEMP_ROOT / f"{safe_name}_{uuid.uuid4().hex[:8]}"
    path.mkdir(parents=True, exist_ok=False)
    return path


@pytest.fixture()
def sample_text() -> str:
    return (
        "RAG 是检索增强生成。Native RAG 使用向量检索和大语言模型回答问题。\n"
        "Advanced RAG 包括问题改写、混合检索、重排和上下文压缩。\n"
        "GraphRAG 使用知识图谱描述实体关系。Agentic RAG 会自动选择工具。"
    )


@pytest.fixture()
def indexed_retriever(tmp_path: Path, sample_text: str) -> VectorRetriever:
    retriever = VectorRetriever(tmp_path / "chroma")
    chunks = [
        DocumentChunk(
            id="c1",
            document_id="doc1",
            text=sample_text,
            metadata={
                "filename": "course.md",
                "file_type": "md",
                "page_number": 1,
                "section": "RAG",
                "chunk_index": 0,
            },
        ),
        DocumentChunk(
            id="c2",
            document_id="doc1",
            text="知识图谱包含实体、边和关系路径，适合解释概念之间的联系。",
            metadata={
                "filename": "course.md",
                "file_type": "md",
                "page_number": 1,
                "section": "GraphRAG",
                "chunk_index": 1,
            },
        ),
    ]
    retriever.add_chunks(chunks)
    return retriever
