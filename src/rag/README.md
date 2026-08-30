# Local RAG Package (`src/rag/`)

## Purpose
The `src/rag/` package defines the architecture for local document ingestion, embedding generation, and vector retrieval pipelines.

## Principles
- **100% Offline Retrieval**: Performs chunking, embedding, and vector querying locally without cloud services.
- **Vector Storage**: Integrates with local vector database indices stored persistently in `vector_store/`.
- **Industrial PDF & Document Parsing**: Extracts text from technical PDFs and internal manuals for context augmentation.
