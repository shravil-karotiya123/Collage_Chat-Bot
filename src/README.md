# Core Source Package (`src/`)

## Purpose
The `src/` directory contains the core domain packages and architectural abstractions for the **Sovereign On-Premise Agentic AI Workbench**.

## Module Architecture & Structure
- `agents/`: Base interfaces and orchestration contracts for autonomous AI agents.
- `routing/`: Dynamic model router specifications enforcing single-model VRAM loading policies.
- `rag/`: Local vector retrieval and offline RAG context pipeline contracts.
- `tools/`: Tool registry and tool-calling abstraction definitions.
- `execution/`: Local isolated Python code execution sandbox interfaces.
- `generators/`: Automated Word (`.docx`) and Excel (`.xlsx`) document generator interfaces.
