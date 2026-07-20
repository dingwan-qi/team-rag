"""Evaluation API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_evaluation_service
from app.rag.schemas import EvaluationRequest, EvaluationResponse
from app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/api", tags=["evaluation"])


@router.post("/evaluate", response_model=EvaluationResponse)
def evaluate(
    payload: EvaluationRequest,
    service: EvaluationService = Depends(get_evaluation_service),
) -> EvaluationResponse:
    return service.evaluate(payload.questions, top_k=payload.top_k)

