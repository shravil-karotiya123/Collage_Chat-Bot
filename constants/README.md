# Constants Module (`constants/`)

## Purpose
The `constants/` module defines immutable project-wide standards, supported model definitions, file specifications, status codes, and default system prompt templates for the **Sovereign On-Premise Agentic AI Workbench**.

## Modules Overview
- `models.py`: Definitions of supported local Ollama open-weight LLMs, memory budgets, context window constraints, and multimodal capability mappings.
- `file_types.py`: Supported file extensions, MIME types, and document classification mappings (PDF, Excel, Word, Vision Images, Structured Data).
- `prompt_templates.py`: System prompt templates for router, multimodal vision analysis, agent tool calling, code execution, document generation, and RAG retrieval.
- `status_codes.py`: Standardized system enums for task execution, model routing status, tool execution status, and error classification.
- `__init__.py`: Package initialization exporting all constant symbols.
