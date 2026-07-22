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
        memory_context: list[str] | None = None,
    ) -> RAGResponse:
        if not query.strip():
            raise ValueError("问题不能为空")
        effective_query = self._with_memory_context(query, memory_context or [])
        if rag_mode == "advanced":
            response = self.advanced.answer(
                effective_query,
                top_k=top_k,
                metadata_filter=metadata_filter,
            )
            response.metadata["original_query"] = query
            response.metadata["memory_used"] = bool(memory_context)
            return response
        if rag_mode == "graph":
            response = self.graph.answer(effective_query, top_k=top_k, metadata_filter=metadata_filter)
            response.metadata["original_query"] = query
            response.metadata["memory_used"] = bool(memory_context)
            return response
        if rag_mode == "agentic":
            response = self.agentic.answer(effective_query, top_k=top_k, metadata_filter=metadata_filter)
            response.metadata["original_query"] = query
            response.metadata["memory_used"] = bool(memory_context)
            return response
        response = self.native.answer(effective_query, top_k=top_k, metadata_filter=metadata_filter)
        response.metadata["original_query"] = query
        response.metadata["memory_used"] = bool(memory_context)
        return response

    def _with_memory_context(self, query: str, memory_context: list[str]) -> str:
        if not memory_context:
            return query
        memory = "\n".join(memory_context[-8:])
        return (
            "以下是当前登录用户的历史对话记忆，用于理解指代和上下文，"
            "不要把它当作课程资料证据：\n"
            f"{memory}\n\n当前问题：{query}"
        )
