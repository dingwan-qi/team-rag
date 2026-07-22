"""Knowledge graph API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_graph_service
from app.rag.schemas import GraphDataResponse, GraphHit
from app.services.graph_service import GraphService

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("", response_model=GraphDataResponse)
def get_graph(
    service: GraphService = Depends(get_graph_service),
) -> GraphDataResponse:
    return service.get_graph()


@router.get("/search", response_model=GraphHit)
def search_graph(
    q: str = Query(..., min_length=1),
    service: GraphService = Depends(get_graph_service),
) -> GraphHit:
    return service.search(q)

