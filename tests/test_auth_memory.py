from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.api.dependencies import get_chat_service, get_user_service
from app.api.main import app
from app.retrieval.vector_retriever import VectorRetriever
from app.services.chat_service import ChatService
from app.services.user_service import UserService


def test_user_registration_login_and_memory(tmp_path: Path) -> None:
    service = UserService(tmp_path / "users.sqlite3")

    registered = service.register("member5", "password123")
    assert registered.user.username == "member5"
    assert service.get_user_by_token(registered.token) is not None

    service.add_memory(registered.user.id, "user", "我正在学习 RAG", "native")
    service.add_memory(registered.user.id, "assistant", "已记录你的学习主题", "native")
    memory = service.list_memory(registered.user.id)
    assert [message["role"] for message in memory] == ["user", "assistant"]
    assert service.memory_context(registered.user.id)

    service.clear_memory(registered.user.id)
    assert service.list_memory(registered.user.id) == []

    logged_in = service.login("member5", "password123")
    assert service.get_user_by_token(logged_in.token).username == "member5"


def test_auth_api_records_chat_memory(tmp_path: Path) -> None:
    user_service = UserService(tmp_path / "users.sqlite3")
    chat_service = ChatService(VectorRetriever(tmp_path / "chroma"))
    app.dependency_overrides[get_user_service] = lambda: user_service
    app.dependency_overrides[get_chat_service] = lambda: chat_service

    client = TestClient(app)
    register = client.post(
        "/api/auth/register",
        json={"username": "apiuser", "password": "password123"},
    )
    assert register.status_code == 200
    token = register.json()["token"]

    chat = client.post(
        "/api/chat",
        json={"query": "记住我在学习 GraphRAG", "rag_mode": "native"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert chat.status_code == 200
    assert chat.json()["metadata"]["memory_saved"] is True

    memory = client.get("/api/memory", headers={"Authorization": f"Bearer {token}"})
    assert memory.status_code == 200
    messages = memory.json()["messages"]
    assert len(messages) == 2
    assert messages[0]["role"] == "user"

    clear = client.delete("/api/memory", headers={"Authorization": f"Bearer {token}"})
    assert clear.status_code == 200
    assert client.get("/api/memory", headers={"Authorization": f"Bearer {token}"}).json()[
        "messages"
    ] == []

    app.dependency_overrides.clear()
