# Agentic Workflows Package (`src/agents/`)

## Purpose
The `src/agents/` package defines abstract interfaces, state management contracts, and base lifecycle structures for agentic workflows in the **Sovereign On-Premise Agentic AI Workbench**.

## Principles
- **Clean Architecture**: Decouples agent planning logic from model inference implementations.
- **Offline Sovereignty**: Ensures agent loops process locally without cloud telemetries or external API dependencies.
- **Single Model Constraint**: Interfaces with the model router to request single-model RAM loading prior to planning or tool execution turns.
