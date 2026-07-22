"""LangGraph-powered Agentic RAG workflow with a sequential fallback."""

from __future__ import annotations

from app.agents.router import choose_route
from app.agents.state import AgentState
from app.agents.tools import AgentTools
from app.rag.schemas import AgentStep, RAGResponse
from app.retrieval.query_rewriter import QueryRewriter


class AgentWorkflow:
    def __init__(self, tools: AgentTools | None = None):
        self.tools = tools or AgentTools()
        self.rewriter = QueryRewriter()
        self._compiled = self._compile_graph()

    def run(
        self,
        query: str,
        top_k: int = 4,
        metadata_filter: dict[str, object] | None = None,
    ) -> AgentState:
        initial: AgentState = {
            "query": query,
            "top_k": top_k,
            "metadata_filter": metadata_filter,
            "retries": 0,
            "needs_retry": False,
            "response": None,
            "steps": [],
        }
        if self._compiled is None:
            return self._run_sequential(initial)
        return self._compiled.invoke(initial)

    def _compile_graph(self):
        try:
            from langgraph.graph import END, StateGraph
        except Exception:
            return None

        graph = StateGraph(AgentState)
        graph.add_node("analyze_query", self._analyze_query)
        graph.add_node("choose_route", self._choose_route)
        graph.add_node("retrieve", self._retrieve)
        graph.add_node("check_evidence", self._check_evidence)
        graph.add_node("rewrite_and_retry", self._rewrite_and_retry)
        graph.add_node("generate_answer", self._generate_answer)
        graph.set_entry_point("analyze_query")
        graph.add_edge("analyze_query", "choose_route")
        graph.add_edge("choose_route", "retrieve")
        graph.add_edge("retrieve", "check_evidence")
        graph.add_conditional_edges(
            "check_evidence",
            lambda state: "retry" if state.get("needs_retry") else "done",
            {"retry": "rewrite_and_retry", "done": "generate_answer"},
        )
        graph.add_edge("rewrite_and_retry", "generate_answer")
        graph.add_edge("generate_answer", END)
        return graph.compile()

    def _run_sequential(self, state: AgentState) -> AgentState:
        for node in (
            self._analyze_query,
            self._choose_route,
            self._retrieve,
            self._check_evidence,
        ):
            state = node(state)
        if state.get("needs_retry"):
            state = self._rewrite_and_retry(state)
        return self._generate_answer(state)

    def _analyze_query(self, state: AgentState) -> AgentState:
        steps = state.get("steps", [])
        query = state["query"]
        steps.append(
            AgentStep(
                name="analyze_query",
                detail=f"分析问题长度、关系词和复杂度: {len(query)} 字符",
            ),
        )
        state["steps"] = steps
        return state

    def _choose_route(self, state: AgentState) -> AgentState:
        route = choose_route(state["query"])
        state["route"] = route
        state["steps"].append(
            AgentStep(name="choose_route", detail=f"自动选择 {route} RAG", tool="router"),
        )
        return state

    def _retrieve(self, state: AgentState) -> AgentState:
        route = state.get("route", "native")
        response = self.tools.answer_generator(state["query"], route, state.get("top_k", 4))
        state["response"] = response
        tool = {
            "native": "vector_search",
            "advanced": "hybrid_search",
            "graph": "graph_search",
        }.get(route, "vector_search")
        state["steps"].append(
            AgentStep(name="retrieve", detail=f"调用 {tool} 并生成候选答案", tool=tool),
        )
        return state

    def _check_evidence(self, state: AgentState) -> AgentState:
        response = state.get("response")
        count = len(response.retrieved_chunks) if response else 0
        retries = state.get("retries", 0)
        state["needs_retry"] = count < 1 and retries < 1
        state["steps"].append(
            AgentStep(
                name="check_evidence",
                detail=f"检索到 {count} 个片段，重试次数 {retries}",
                tool="evidence_checker",
            ),
        )
        return state

    def _rewrite_and_retry(self, state: AgentState) -> AgentState:
        rewritten = self.rewriter.rewrite(state["query"])
        state["rewritten_query"] = rewritten
        state["retries"] = state.get("retries", 0) + 1
        state["steps"].append(
            AgentStep(name="rewrite_and_retry", detail=f"证据不足，改写为: {rewritten}"),
        )
        state["response"] = self.tools.advanced_rag.answer(rewritten, top_k=state.get("top_k", 4))
        return state

    def _generate_answer(self, state: AgentState) -> AgentState:
        state["steps"].append(
            AgentStep(
                name="generate_answer",
                detail="整理最终答案、引用来源和执行过程",
                tool="answer_generator",
            ),
        )
        return state


def wrap_agent_response(state: AgentState, latency: float) -> RAGResponse:
    response = state.get("response")
    if response is None:
        return RAGResponse(
            answer="Agent 未能生成答案。",
            rag_mode="agentic",
            latency=latency,
            trace=state.get("steps", []),
            agent_steps=state.get("steps", []),
        )
    trace = state.get("steps", []) + response.trace + response.agent_steps
    return RAGResponse(
        answer=response.answer,
        sources=response.sources,
        retrieved_chunks=response.retrieved_chunks,
        rag_mode="agentic",
        latency=latency,
        rewritten_query=state.get("rewritten_query") or response.rewritten_query,
        trace=trace,
        agent_steps=trace,
        graph=response.graph,
        metadata={
            **response.metadata,
            "selected_route": state.get("route", "native"),
            "retries": state.get("retries", 0),
            "langgraph_enabled": True,
        },
    )
