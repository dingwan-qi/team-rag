"""Native RAG implementation."""

from __future__ import annotations

import time

from app.rag.llm import LLMClient
from app.rag.modular_rag import BaseRAG
from app.rag.schemas import AgentStep, RAGResponse, Source
from app.retrieval.base import chunk_to_source
from app.retrieval.vector_retriever import VectorRetriever


class NativeRAG(BaseRAG):
    def __init__(
        self,
        retriever: VectorRetriever | None = None,
        llm: LLMClient | None = None,
    ):
        self.retriever = retriever or VectorRetriever()
        self.llm = llm or LLMClient()

    def answer(
        self,
        query: str,
        top_k: int = 4,
        metadata_filter: dict[str, object] | None = None,
    ) -> RAGResponse:
        started = time.perf_counter()
        hits = self.retriever.search(query, top_k=top_k, metadata_filter=metadata_filter)
        answer = self.llm.generate(query=query, chunks=hits)
        sources = [Source(**chunk_to_source(hit.chunk, hit.score)) for hit in hits]
        trace = [
            AgentStep(name="vector_search", detail=f"向量检索返回 {len(hits)} 个片段", tool="VectorRetriever"),
            AgentStep(name="answer_generator", detail="基于检索上下文生成答案", tool="LLMClient"),
        ]
        return RAGResponse(
            answer=answer,
            sources=sources,
            retrieved_chunks=hits,
            rag_mode="native",
            latency=round(time.perf_counter() - started, 4),
            trace=trace,
            metadata={"retriever_backend": self.retriever.backend_name},
        )
