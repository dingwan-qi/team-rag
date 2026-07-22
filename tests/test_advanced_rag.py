from __future__ import annotations

from app.rag.advanced_rag import AdvancedRAG
from app.retrieval.vector_retriever import VectorRetriever


def test_advanced_rag_uses_rewrite_and_enhancements(indexed_retriever: VectorRetriever) -> None:
    response = AdvancedRAG(indexed_retriever).answer("这个怎么用？", top_k=2)

    assert response.rag_mode == "advanced"
    assert response.rewritten_query
    assert "hybrid_retrieval" in response.metadata["enhancements"]
    assert any(step.name == "context_compression" for step in response.trace)
