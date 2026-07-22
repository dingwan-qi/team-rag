from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.api.dependencies import get_chat_service, get_document_service, get_evaluation_service
from app.api.main import app
from app.retrieval.vector_retriever import VectorRetriever
from app.services.chat_service import ChatService
from app.services.document_service import DocumentService
from app.services.evaluation_service import EvaluationService

WEB_START = Path(__file__).resolve().parents[1] / "app" / "web" / "start.html"


def test_api_upload_list_chat_and_health(tmp_path: Path) -> None:
    retriever = VectorRetriever(tmp_path / "chroma")
    document_service = DocumentService(tmp_path / "uploads", retriever=retriever)
    chat_service = ChatService(retriever)
    evaluation_service = EvaluationService(chat_service)
    app.dependency_overrides[get_document_service] = lambda: document_service
    app.dependency_overrides[get_chat_service] = lambda: chat_service
    app.dependency_overrides[get_evaluation_service] = lambda: evaluation_service

    client = TestClient(app)
    health = client.get("/health")
    assert health.status_code == 200

    home = client.get("/", follow_redirects=False)
    assert home.status_code in {307, 308}
    assert home.headers["location"] == "/web/start.html"

    if WEB_START.exists():
        web = client.get("/web/start.html")
        assert web.status_code == 200
        assert "课程资料智能问答" in web.text

    upload = client.post(
        "/api/documents/upload",
        files={"file": ("course.txt", b"RAG uses retrieval and generation.", "text/plain")},
    )
    assert upload.status_code == 200
    assert upload.json()["chunks"] >= 1

    documents = client.get("/api/documents")
    assert documents.status_code == 200
    assert len(documents.json()) == 1

    chat = client.post("/api/chat", json={"query": "What does RAG use?", "rag_mode": "native"})
    assert chat.status_code == 200
    assert chat.json()["rag_mode"] == "native"
    assert chat.json()["trace"]

    graph = client.get("/api/graph")
    assert graph.status_code == 200
    assert "nodes" in graph.json()

    evaluation = client.post("/api/evaluate", json={"questions": ["What is RAG?"]})
    assert evaluation.status_code == 200
    assert evaluation.json()["rows"]

    app.dependency_overrides.clear()
