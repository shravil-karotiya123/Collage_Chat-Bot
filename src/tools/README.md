# Tools & Extensions Package (`src/tools/`)

## Purpose
The `src/tools/` package provides base tool registry patterns and execution contracts used by agents during task execution.

## Architecture
- **Tool Standard Interface**: Establishes input validation, execution wrappers, and output schemas for agent tools.
- **Safety First**: Enforces local path restrictions and parameter checks prior to invoking file system or code tools.
