from __future__ import annotations

from pathlib import Path

from app.graph.graph_builder import GraphBuilder
from app.graph.graph_retriever import GraphRetriever
from app.graph.graph_store import GraphStore
from app.rag.graph_rag import GraphRAG
from app.retrieval.vector_retriever import VectorRetriever


def test_graph_rag_returns_graph_hit(tmp_path: Path, indexed_retriever: VectorRetriever) -> None:
    store = GraphStore(tmp_path / "graph")
    graph = GraphBuilder().build(indexed_retriever.all_chunks())
    store.save(graph)

    response = GraphRAG(
        indexed_retriever,
        GraphRetriever(store),
    ).answer("GraphRAG 和知识图谱的关系是什么？", top_k=2)

    assert response.rag_mode == "graph"
    assert response.graph is not None
    assert response.answer
    assert response.trace
