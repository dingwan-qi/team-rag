"""Small API client used when the UI is configured to call FastAPI."""

from __future__ import annotations

import json
import urllib.request
from typing import Any


class APIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")

    def health(self) -> dict[str, Any]:
        return self._get("/health")

    def chat(
        self,
        query: str,
        rag_mode: str,
        top_k: int,
        token: str | None = None,
    ) -> dict[str, Any]:
        return self._post(
            "/api/chat",
            {"query": query, "rag_mode": rag_mode, "top_k": top_k},
            token=token,
        )

    def register(self, username: str, password: str) -> dict[str, Any]:
        return self._post("/api/auth/register", {"username": username, "password": password})

    def login(self, username: str, password: str) -> dict[str, Any]:
        return self._post("/api/auth/login", {"username": username, "password": password})

    def memory(self, token: str) -> dict[str, Any]:
        return self._get("/api/memory", token=token)

    def list_documents(self) -> list[dict[str, Any]]:
        return self._get("/api/documents")

    def graph(self) -> dict[str, Any]:
        return self._get("/api/graph")

    def _get(self, path: str, token: str | None = None) -> Any:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        request = urllib.request.Request(f"{self.base_url}{path}", headers=headers, method="GET")
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))

    def _post(self, path: str, payload: dict[str, Any], token: str | None = None) -> Any:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
