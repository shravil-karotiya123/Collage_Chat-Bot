# MRPL AI Workbench — Sovereign RAG Architecture

## RAG Overview

The Retrieval-Augmented Generation (RAG) subsystem enables factual, grounded Q&A over local refinery manuals, technical standards, inspection reports, and P&ID documentation.

---

## 1. Document Ingestion Pipeline

```text
Raw Document (PDF/DOCX/CSV/Image)
       ↓
Validator (MIME, Extension, Size)
       ↓
Parser / OCR Pipeline (PaddleOCR Text/Table Extraction & Vision Fallback)
       ↓
Chunker (Configurable Character Limits & Overlap)
       ↓
Metadata Attachment (document_id, workspace_id, role, classification, page_number)
       ↓
Offline SentenceTransformers Embedding (all-MiniLM-L6-v2)
       ↓
Local Persistent ChromaDB Store (data/chroma/)
```

---

## 2. Local Embeddings

- **Provider**: Offline `SentenceTransformers` model (`all-MiniLM-L6-v2` by default).
- **RAM Footprint**: ~80 MB memory footprint.
- **Execution Mode**: 100% offline CPU/GPU execution without remote API dependencies.

---

## 3. Metadata Authorization Filtering

ChromaDB search operations enforce strict pre-retrieval filtering:

```python
where_filter = {
    "$and": [
        {"workspace_id": {"$eq": target_workspace_id}},
        {"classification": {"$lte": max_allowed_classification_level}},
    ]
}
```

Only chunks satisfying both vector similarity and metadata authorization criteria are returned for prompt context assembly.
