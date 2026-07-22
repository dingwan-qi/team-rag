"""FastAPI dependency factories."""

from __future__ import annotations

from functools import lru_cache

from app.services.chat_service import ChatService
from app.services.document_service import DocumentService
from app.services.evaluation_service import EvaluationService
from app.services.graph_service import GraphService
from app.services.user_service import UserService


@lru_cache(maxsize=1)
def get_document_service() -> DocumentService:
    return DocumentService()


@lru_cache(maxsize=1)
def get_chat_service() -> ChatService:
    return ChatService()


@lru_cache(maxsize=1)
def get_evaluation_service() -> EvaluationService:
    return EvaluationService(get_chat_service())


@lru_cache(maxsize=1)
def get_graph_service() -> GraphService:
    return GraphService(get_document_service())


@lru_cache(maxsize=1)
def get_user_service() -> UserService:
    return UserService()
