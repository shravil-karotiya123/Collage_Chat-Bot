# Configuration Module (`config/`)

## Purpose
The `config/` module centralizes all system configurations, hardware constraints, and environment settings for the **Sovereign On-Premise Agentic AI Workbench**.

## Architecture & Principles
- **Pydantic BaseSettings**: Implements strongly-typed settings powered by `pydantic-settings`.
- **Environment Driven**: Reads configurations directly from environment variables and `.env` files.
- **Hardware Enforced**: Maintains GPU VRAM and RAM allocation limits tailored for the RTX 5050 (16 GB system RAM) workstation setup.
- **Single Model Constraint**: Enforces `MAX_CONCURRENT_MODELS = 1` to strictly manage memory switching during local model execution.

## Files
- `settings.py`: Core `Settings` class inheriting from `BaseSettings`.
- `__init__.py`: Package initialization exporting the singleton `settings` instance.
