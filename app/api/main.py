"""FastAPI application for TeamRAG."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, documents, evaluation, graph, health, knowledge_base
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(
    title="TeamRAG API",
    description="多源课程资料智能问答平台后端接口",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(documents.router)
app.include_router(knowledge_base.router)
app.include_router(graph.router)
app.include_router(chat.router)
app.include_router(evaluation.router)
