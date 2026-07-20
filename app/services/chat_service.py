"""Chat orchestration service."""

from __future__ import annotations

from app.agents.tools import AgentTools
from app.agents.workflow import AgentWorkflow
from app.rag.advanced_rag import AdvancedRAG
from app.rag.agentic_rag import AgenticRAG
from app.rag.graph_rag import GraphRAG
from app.rag.native_rag import NativeRAG
from app.rag.schemas import RAGMode, RAGResponse
from app.retrieval.vector_retriever import VectorRetriever


class ChatService:
    def __init__(self, retriever: VectorRetriever | None = None):
        self.retriever = retriever or VectorRetriever()
        self.native = NativeRAG(self.retriever)
        self.advanced = AdvancedRAG(self.retriever)
        self.graph = GraphRAG(self.retriever)
        self.agentic = AgenticRAG(AgentWorkflow(AgentTools(self.retriever)))

    def answer(
        self,
        query: str,
        rag_mode: RAGMode = "native",
        top_k: int = 4,
        metadata_filter: dict[str, object] | None = None,
    ) -> RAGResponse:
        if not query.strip():
            raise ValueError("问题不能为空")
        if rag_mode == "advanced":
            return self.advanced.answer(query, top_k=top_k, metadata_filter=metadata_filter)
        if rag_mode == "graph":
            return self.graph.answer(query, top_k=top_k, metadata_filter=metadata_filter)
        if rag_mode == "agentic":
            return self.agentic.answer(query, top_k=top_k, metadata_filter=metadata_filter)
        return self.native.answer(query, top_k=top_k, metadata_filter=metadata_filter)
