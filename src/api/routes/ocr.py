"""
OCR REST API Routes for MRPL AI Workbench.
Exposes endpoints for processing scanned documents, images, and checking OCR health.
"""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from src.api.dependencies import get_ocr_service
from src.api.responses.standard_response import StandardResponse, success_response
from src.ocr.ocr_service import OCRService
from src.schemas.ocr import OCRHealthResponse, OCRProcessResponse

router = APIRouter(tags=["OCR & Vision Intelligence"])


@router.post(
    "/ocr/process",
    response_model=StandardResponse[OCRProcessResponse],
    summary="Process Scanned Document or Image with OCR/Vision",
    description="Inspect PDF pages, run OCR/Vision on scanned content, extract text, and produce Phase 5-compatible chunks.",
)
async def process_ocr_document(
    file: UploadFile = File(..., description="Target PDF or image file to process"),
    chunk_size: Optional[int] = Form(None, description="Optional text chunk character limit"),
    chunk_overlap: Optional[int] = Form(None, description="Optional chunk overlap limit"),
    document_id: Optional[str] = Form(None, description="Optional document ID override"),
    ocr_service: OCRService = Depends(get_ocr_service),
) -> StandardResponse[OCRProcessResponse]:
    """
    POST /ocr/process endpoint delegating strictly to OCRService.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file missing valid filename.")

    try:
        content = await file.read()
        res = ocr_service.process_document(
            filename=file.filename,
            content_bytes=content,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            document_id=document_id,
        )

        return success_response(
            data=res,
            message=f"OCR processing completed for '{file.filename}' ({res.total_pages} pages, {len(res.chunks)} chunks).",
        )
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(exc)}")


@router.get(
    "/ocr/health",
    response_model=StandardResponse[OCRHealthResponse],
    summary="OCR & Vision Subsystem Health Check",
    description="Query operational status of OCR engine, vision toggle, and model configuration settings.",
)
async def get_ocr_health(
    ocr_service: Annotated[OCRService, Depends(get_ocr_service)],
) -> StandardResponse[OCRHealthResponse]:
    """
    GET /ocr/health endpoint returning OCR subsystem status.
    """
    health_dict = ocr_service.health()

    health_payload = OCRHealthResponse(
        status=health_dict.get("status", "healthy"),
        ocr_enabled=health_dict.get("ocr_enabled", True),
        ocr_engine=health_dict.get("ocr_engine", "vision_llm"),
        vision_enabled=health_dict.get("vision_enabled", True),
        vision_model=health_dict.get("vision_model", "minicpm-v:8b"),
    )

    return success_response(
        data=health_payload,
        message="OCR subsystem health metrics retrieved successfully",
    )
