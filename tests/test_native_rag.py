from __future__ import annotations

from app.rag.native_rag import NativeRAG
from app.retrieval.vector_retriever import VectorRetriever


def test_native_rag_response_shape(indexed_retriever: VectorRetriever) -> None:
    response = NativeRAG(indexed_retriever).answer("RAG 的流程是什么？", top_k=2)

    assert response.rag_mode == "native"
    assert response.answer
    assert response.sources
    assert response.retrieved_chunks
    assert response.trace
