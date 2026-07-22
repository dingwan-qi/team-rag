"""Document management routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.dependencies import get_document_service
from app.core.exceptions import TeamRAGError
from app.rag.schemas import DocumentSummary, UploadResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    service: DocumentService = Depends(get_document_service),
) -> UploadResponse:
    try:
        content = await file.read()
        return service.save_and_index(file.filename or "uploaded.txt", content)
    except (TeamRAGError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[DocumentSummary])
def list_documents(
    service: DocumentService = Depends(get_document_service),
) -> list[DocumentSummary]:
    return service.list_documents()


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service),
) -> dict[str, int | str]:
    result = service.delete_document(document_id)
    if result["deleted_chunks"] == 0 and result["deleted_files"] == 0:
        raise HTTPException(status_code=404, detail="文档不存在")
    return result

