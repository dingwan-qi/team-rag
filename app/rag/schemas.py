"""Shared schemas for document chunks, retrieval, RAG, and API payloads."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

RAGMode = Literal["native", "advanced", "graph", "agentic"]


class DocumentPage(BaseModel):
    text: str
    page_number: int = 1
    section: str = ""


class DocumentChunk(BaseModel):
    id: str
    document_id: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class Source(BaseModel):
    document_id: str
    filename: str
    chunk_id: str
    page_number: int | None = None
    score: float | None = None


class RetrievedChunk(BaseModel):
    chunk: DocumentChunk
    score: float = 0.0


class AgentStep(BaseModel):
    name: str
    detail: str
    tool: str | None = None


class GraphHit(BaseModel):
    matched_entities: list[str] = Field(default_factory=list)
    nodes: list[str] = Field(default_factory=list)
    edges: list[dict[str, str]] = Field(default_factory=list)
    facts: list[str] = Field(default_factory=list)


class RAGResponse(BaseModel):
    answer: str
    sources: list[Source] = Field(default_factory=list)
    retrieved_chunks: list[RetrievedChunk] = Field(default_factory=list)
    rag_mode: RAGMode
    latency: float
    trace: list[AgentStep] = Field(default_factory=list)
    rewritten_query: str | None = None
    agent_steps: list[AgentStep] = Field(default_factory=list)
    graph: GraphHit | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentSummary(BaseModel):
    document_id: str
    filename: str
    file_type: str
    chunk_count: int
    status: str = "indexed"


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    chunks: int
    duplicate: bool = False
    message: str


class IndexResponse(BaseModel):
    indexed_documents: int
    indexed_chunks: int
    backend: str
    message: str


class GraphBuildResponse(BaseModel):
    nodes: int
    edges: int
    message: str


class GraphDataResponse(BaseModel):
    nodes: list[dict[str, str]] = Field(default_factory=list)
    edges: list[dict[str, str]] = Field(default_factory=list)


class ChatRequest(BaseModel):
    query: str
    rag_mode: RAGMode = "native"
    top_k: int = 4
    metadata_filter: dict[str, Any] | None = None


class EvaluationRequest(BaseModel):
    questions: list[str] = Field(default_factory=list)
    top_k: int = 4


class EvaluationRow(BaseModel):
    question: str
    rag_mode: RAGMode
    answer: str
    retrieval_count: int
    citation_count: int
    latency: float
    human_score: int | None = None


class EvaluationResponse(BaseModel):
    rows: list[EvaluationRow]
