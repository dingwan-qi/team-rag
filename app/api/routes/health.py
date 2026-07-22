"""Health check route."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "TeamRAG",
        "chroma_dir": str(settings.chroma_dir),
        "upload_dir": str(settings.upload_dir),
    }

