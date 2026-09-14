"""
Documents API Endpoint for MRPL AI Workbench.
Handles file uploads and document processing pipeline execution.
"""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from src.api.dependencies import get_document_pipeline
from src.api.responses.standard_response import StandardResponse, success_response
from src.document_processing.pipeline import DocumentProcessingPipeline
from src.schemas.document import DocumentUploadResponse

router = APIRouter(tags=["Documents"])


@router.post(
    "/documents/upload",
    response_model=StandardResponse[DocumentUploadResponse],
    summary="Upload & Process Document for RAG Indexing",
    description="Validate, load, parse, chunk, and extract metadata from uploaded PDF, DOCX, TXT, MD, CSV, or XLSX document.",
)
async def upload_document(
    file: UploadFile = File(..., description="Target document file to process"),
    chunk_size: Optional[int] = Form(None, description="Optional text chunk character limit"),
    chunk_overlap: Optional[int] = Form(None, description="Optional chunk overlap limit"),
    pipeline: DocumentProcessingPipeline = Depends(get_document_pipeline),
) -> StandardResponse[DocumentUploadResponse]:
    """
    POST /documents/upload endpoint orchestrating document validation, parsing, chunking, and metadata extraction.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file missing valid filename.")

    try:
        content = await file.read()
        result = pipeline.process_document(
            file_name=file.filename,
            content=content,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        return success_response(
            data=result,
            message=f"Document '{file.filename}' processed successfully into {result.metadata.total_chunks} chunks.",
        )

    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(exc)}")


@router.get(
    "/documents",
    response_model=StandardResponse[list],
    summary="List Tracked & Indexed Document Catalog",
    description="Retrieve list of document metadata catalog entries stored in local vector store.",
)
async def list_documents(
    rag_service = Depends(get_document_pipeline),
) -> StandardResponse[list]:
    """
    GET /documents endpoint returning document catalog.
    """
    from src.api.dependencies import get_rag_service
    rag_svc = get_rag_service()
    
    # Extract distinct document metadata entries from collection
    coll_items = []
    try:
        if hasattr(rag_svc.vector_store, "_get_collection"):
            coll = rag_svc.vector_store._get_collection(rag_svc.collection_name)
            if hasattr(coll, "get"):
                raw_data = coll.get(include=["metadatas"])
                metas = raw_data.get("metadatas", []) or []
                docs_map = {}
                for m in metas:
                    if not m:
                        continue
                    doc_id = m.get("document_id") or m.get("doc_id") or "doc_unknown"
                    if doc_id not in docs_map:
                        docs_map[doc_id] = {
                            "document_id": doc_id,
                            "filename": m.get("filename") or m.get("file_name") or "document.txt",
                            "total_chunks": 1,
                            "created_at": m.get("timestamp") or "2026-08-31T00:00:00Z"
                        }
                    else:
                        docs_map[doc_id]["total_chunks"] += 1
                coll_items = list(docs_map.values())
    except Exception:
        coll_items = []

    return success_response(
        data=coll_items,
        message=f"Retrieved {len(coll_items)} indexed document metadata items",
    )
