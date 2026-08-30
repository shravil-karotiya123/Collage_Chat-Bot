# Automatic Model Routing Package (`src/routing/`)

## Purpose
The `src/routing/` package provides the architecture for automatic model selection and VRAM/RAM lifecycle management.

## Key Responsibilities
- **Task Intent Classification**: Analyzes queries and inputs (Vision, Code, RAG, General) to map to appropriate local open-weight models.
- **Single Model Loading Enforcer**: Manages model unload/load cycles in Ollama so that only one model resides in GPU VRAM / System RAM at any given moment.
- **VRAM Budget Compliance**: Verifies model parameter requirements against the RTX 5050 hardware limits before triggering model swaps.
