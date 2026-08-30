# Vector Store Directory (`vector_store/`)

## Purpose
The `vector_store/` directory houses local persistent vector store indices and embedding caches for local offline RAG retrieval.

## Offline Guarantee
- Embeddings are generated locally using open-weight embedding models (e.g. `nomic-embed-text` via Ollama).
- Vector databases are stored completely on disk in this directory.
