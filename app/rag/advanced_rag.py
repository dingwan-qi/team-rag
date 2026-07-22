"""Advanced RAG with query rewrite, hybrid retrieval, rerank, and compression."""

from __future__ import annotations

import time

from app.rag.llm import LLMClient
from app.rag.modular_rag import BaseRAG
from app.rag.schemas import AgentStep, RAGResponse, Source
from app.retrieval.base import chunk_to_source
from app.retrieval.context_compressor import ContextCompressor
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.query_rewriter import QueryRewriter
from app.retrieval.reranker import LightweightReranker
from app.retrieval.vector_retriever import VectorRetriever


class AdvancedRAG(BaseRAG):
    def __init__(
        self,
        vector_retriever: VectorRetriever | None = None,
        llm: LLMClient | None = None,
    ):
        self.vector_retriever = vector_retriever or VectorRetriever()
        self.hybrid_retriever = HybridRetriever(self.vector_retriever)
        self.rewriter = QueryRewriter()
        self.reranker = LightweightReranker()
        self.compressor = ContextCompressor()
        self.llm = llm or LLMClient()

    def answer(
        self,
        query: str,
        top_k: int = 4,
        metadata_filter: dict[str, object] | None = None,
    ) -> RAGResponse:
        started = time.perf_counter()
        rewritten = self.rewriter.rewrite(query)
        trace = [
            AgentStep(name="query_rewrite", detail=f"原问题改写为: {rewritten}", tool="QueryRewriter"),
        ]
        candidates = self.hybrid_retriever.search(
            rewritten,
            top_k=max(top_k * 3, top_k),
            metadata_filter=metadata_filter,
        )
        trace.append(
            AgentStep(name="hybrid_retrieval", detail=f"召回 {len(candidates)} 个候选片段", tool="HybridRetriever"),
        )
        reranked = self.reranker.rerank(rewritten, candidates, top_k)
        trace.append(
            AgentStep(name="rerank", detail=f"重排后保留 {len(reranked)} 个片段", tool="LightweightReranker"),
        )
        compressed = self.compressor.compress(reranked)
        trace.append(
            AgentStep(name="context_compression", detail=f"压缩后上下文片段数: {len(compressed)}", tool="ContextCompressor"),
        )
        answer = self.llm.generate(query=query, chunks=compressed)
        sources = [Source(**chunk_to_source(hit.chunk, hit.score)) for hit in compressed]
        return RAGResponse(
            answer=answer,
            sources=sources,
            retrieved_chunks=compressed,
            rag_mode="advanced",
            latency=round(time.perf_counter() - started, 4),
            trace=trace,
            rewritten_query=rewritten,
            metadata={
                "enhancements": [
                    "query_rewrite",
                    "hybrid_retrieval",
                    "lightweight_rerank",
                    "metadata_filter",
                    "context_compression",
                ],
                "retriever_backend": self.vector_retriever.backend_name,
            },
        )

