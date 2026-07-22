"""FastAPI application for TeamRAG."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import auth, chat, documents, evaluation, graph, health, knowledge_base, memory
from app.core.logging import configure_logging

configure_logging()

WEB_DIR = Path(__file__).resolve().parents[1] / "web"

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
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(knowledge_base.router)
app.include_router(graph.router)
app.include_router(chat.router)
app.include_router(evaluation.router)
app.include_router(memory.router)


@app.get("/", include_in_schema=False)
def web_home() -> RedirectResponse:
    return RedirectResponse(url="/web/start.html")


app.mount("/web", StaticFiles(directory=WEB_DIR, check_dir=False), name="web")
