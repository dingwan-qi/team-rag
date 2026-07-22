"""Agent tools wrapping retrievers and answer generators."""

from __future__ import annotations

from app.graph.graph_retriever import GraphRetriever
from app.rag.advanced_rag import AdvancedRAG
from app.rag.graph_rag import GraphRAG
from app.rag.native_rag import NativeRAG
from app.rag.schemas import GraphHit, RAGResponse, RetrievedChunk
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.vector_retriever import VectorRetriever


class AgentTools:
    def __init__(self, vector_retriever: VectorRetriever | None = None):
        self.vector_retriever = vector_retriever or VectorRetriever()
        self.hybrid_retriever = HybridRetriever(self.vector_retriever)
        self.graph_retriever = GraphRetriever()
        self.native_rag = NativeRAG(self.vector_retriever)
        self.advanced_rag = AdvancedRAG(self.vector_retriever)
        self.graph_rag = GraphRAG(self.vector_retriever, self.graph_retriever)

    def vector_search(self, query: str, top_k: int) -> list[RetrievedChunk]:
        return self.vector_retriever.search(query, top_k)

    def hybrid_search(self, query: str, top_k: int) -> list[RetrievedChunk]:
        return self.hybrid_retriever.search(query, top_k)

    def graph_search(self, query: str) -> GraphHit:
        return self.graph_retriever.search(query)

    def document_filter(
        self,
        query: str,
        top_k: int,
        metadata_filter: dict[str, object] | None,
    ) -> list[RetrievedChunk]:
        return self.vector_retriever.search(query, top_k, metadata_filter)

    def answer_generator(self, query: str, route: str, top_k: int) -> RAGResponse:
        if route == "graph":
            return self.graph_rag.answer(query, top_k=top_k)
        if route == "advanced":
            return self.advanced_rag.answer(query, top_k=top_k)
        return self.native_rag.answer(query, top_k=top_k)

