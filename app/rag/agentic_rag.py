"""Agentic RAG facade."""

from __future__ import annotations

import time

from app.agents.workflow import AgentWorkflow, wrap_agent_response
from app.rag.modular_rag import BaseRAG
from app.rag.schemas import RAGResponse


class AgenticRAG(BaseRAG):
    def __init__(self, workflow: AgentWorkflow | None = None):
        self.workflow = workflow or AgentWorkflow()

    def answer(
        self,
        query: str,
        top_k: int = 4,
        metadata_filter: dict[str, object] | None = None,
    ) -> RAGResponse:
        started = time.perf_counter()
        state = self.workflow.run(query, top_k=top_k, metadata_filter=metadata_filter)
        return wrap_agent_response(state, round(time.perf_counter() - started, 4))

