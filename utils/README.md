# Utilities Module (`utils/`)

## Purpose
The `utils/` module provides foundational, reusable utility functions and helpers for the **Sovereign On-Premise Agentic AI Workbench**.

## Sub-Modules
- `logger.py`: Production dual console and rotating timestamped file logging utility.
- `file_utils.py`: Safe directory creation, file extension checking, path sanitization, and size validation helpers.
- `time_utils.py`: Timestamp formatters (ISO-8601, human-readable), execution timer contexts, and benchmark utilities.
- `validation.py`: Input validation, parameter bounds checking, environment verification.
- `model_utils.py`: Ollama endpoint connectivity checker, model tag validator, memory allocation budget calculator.
- `__init__.py`: Package initialization exporting utility functions.
