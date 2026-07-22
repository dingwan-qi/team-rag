"""Knowledge base and graph index routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_document_service, get_graph_service
from app.rag.schemas import GraphBuildResponse, IndexResponse
from app.services.document_service import DocumentService
from app.services.graph_service import GraphService

router = APIRouter(prefix="/api/knowledge-base", tags=["knowledge-base"])


@router.post("/index", response_model=IndexResponse)
def build_index(
    service: DocumentService = Depends(get_document_service),
) -> IndexResponse:
    return service.index_uploaded_files()


@router.post("/graph", response_model=GraphBuildResponse)
def build_graph(
    service: GraphService = Depends(get_graph_service),
) -> GraphBuildResponse:
    return service.build_graph()
