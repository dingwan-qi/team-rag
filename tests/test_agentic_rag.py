from __future__ import annotations

from app.agents.router import choose_route
from app.agents.tools import AgentTools
from app.agents.workflow import AgentWorkflow
from app.rag.agentic_rag import AgenticRAG
from app.retrieval.vector_retriever import VectorRetriever


def test_agent_router_selects_graph_for_relation_query() -> None:
    assert choose_route("实体之间有什么关系？") == "graph"


def test_agentic_rag_response(indexed_retriever: VectorRetriever) -> None:
    workflow = AgentWorkflow(AgentTools(indexed_retriever))
    response = AgenticRAG(workflow).answer("Advanced RAG 如何改进检索？", top_k=2)

    assert response.rag_mode == "agentic"
    assert response.metadata["selected_route"] in {"native", "advanced", "graph"}
    assert response.agent_steps

