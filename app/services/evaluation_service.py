"""Simple side-by-side evaluation service for classroom demos."""

from __future__ import annotations

from app.rag.schemas import EvaluationResponse, EvaluationRow, RAGMode
from app.services.chat_service import ChatService

DEFAULT_QUESTIONS = [
    "课程资料中 RAG 的核心流程是什么？",
    "向量索引和关键词检索有什么区别？",
    "知识图谱中的实体关系如何辅助问答？",
]


class EvaluationService:
    def __init__(self, chat_service: ChatService | None = None):
        self.chat_service = chat_service or ChatService()

    def evaluate(self, questions: list[str] | None = None, top_k: int = 4) -> EvaluationResponse:
        rows: list[EvaluationRow] = []
        modes: list[RAGMode] = ["native", "advanced", "graph", "agentic"]
        for question in questions or DEFAULT_QUESTIONS:
            for mode in modes:
                response = self.chat_service.answer(question, mode, top_k=top_k)
                rows.append(
                    EvaluationRow(
                        question=question,
                        rag_mode=mode,
                        answer=response.answer,
                        retrieval_count=len(response.retrieved_chunks),
                        citation_count=len(response.sources),
                        latency=response.latency,
                    ),
                )
        return EvaluationResponse(rows=rows)

