# Sovereign On-Premise Agentic AI Workbench using Open-Weight Multimodal LLMs for Confidential Industrial Work

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![License](https://img.shields.io/badge/license-Proprietary%20%2F%20MRPL-red.svg)]()
[![Platform](https://img.shields.io/badge/platform-Windows%20%2F%20Offline-lightgrey.svg)]()

> **Smart India Hackathon (SIH) Project Architecture Blueprint**  
> Developed for **Mangalore Refinery and Petrochemicals Limited (MRPL)**.

---

## 1. Project Overview

The **Sovereign On-Premise Agentic AI Workbench** is a 100% offline, self-contained AI architecture designed specifically for confidential industrial operations at MRPL. 

Industrial facilities require strict data sovereignty: proprietary technical manuals, refinery sensor logs, financial spreadsheets, structural inspection images, and operational reports must **never** leave the local network boundary or be transmitted to external cloud APIs.

### Key Capabilities Supported by Architecture
- **Multiple Local LLMs**: Dynamic model switching using Ollama local inference.
- **Automatic Model Routing**: Intelligent task routing based on intent (Code, Vision, RAG, General).
- **Agentic Workflow**: Modular multi-step agent planning and tool calling contracts.
- **OCR & Vision Understanding**: Multimodal inspection of engineering drawings, diagrams, and scanned documents.
- **Local RAG (Retrieval-Augmented Generation)**: Vector search over confidential local documents.
- **Isolated Code Execution**: Secure local execution sandbox for Python scripts.
- **Automated Report Generation**: Generation of Word (`.docx`) reports and Excel (`.xlsx`) spreadsheets.

---

## 2. Hardware & Resource Constraints

The architecture is explicitly tailored for workstation deployment:
- **GPU**: NVIDIA RTX 5050 GPU (~8 GB VRAM)
- **System Memory**: 16 GB RAM
- **Storage**: Limited local SSD storage

### Single-Model Memory Strategy
To guarantee stability without out-of-memory (OOM) crashes on 16 GB RAM / 8 GB VRAM hardware:
1. **Only ONE model resides in memory at any given time**.
2. When switching tasks (e.g., from general reasoning to vision analysis), the router unloads the active model before loading the target model.
3. Future models can be integrated into `constants/models.py` without modifying the core system architecture.

---

## 3. Architecture Overview

```
                                  +-----------------------+
                                  |   User Input Query    |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  | Automatic LLM Router  |
                                  | (qwen2.5-coder:7b)    |
                                  +-----------+-----------+
                                              |
                  +---------------------------+---------------------------+
                  |                           |                           |
                  v                           v                           v
        +-------------------+       +-------------------+       +-------------------+
        |   Vision Task     |       |   Local RAG Task  |       |   Code Exec Task  |
        |    (llava:7b)     |       |    (llama3:8b)    |       | (qwen2.5-coder:7b)|
        +---------+---------+       +---------+---------+       +---------+---------+
                  |                           |                           |
                  +---------------------------+---------------------------+
                                              |
                                              v
                                  +-----------------------+
                                  | Document Generators   |
                                  |  (Word .docx / Excel) |
                                  +-----------------------+
```

---

## 4. Folder Explanation

Every directory in this project follows Clean Architecture principles:

| Directory | Purpose & Explanation |
| :--- | :--- |
| [`config/`](file:///c:/Users/shrav/OneDrive/Desktop/MRPL_AI_Workbench/config) | Configuration management using `pydantic-settings`. Loads environment variables from `.env`. |
| [`constants/`](file:///c:/Users/shrav/OneDrive/Desktop/MRPL_AI_Workbench/constants) | System constants: supported models, file extensions, status codes, and default prompt templates. |
| [`logs/`](file:///c:/Users/shrav/OneDrive/Desktop/MRPL_AI_Workbench/logs) | Stores timestamped application log files (`workbench.log`) with automatic file rotation. |
| [`utils/`](file:///c:/Users/shrav/OneDrive/Desktop/MRPL_AI_Workbench/utils) | Reusable utilities for file management, timing benchmarks, logger setup, and environment validation. |
| [`src/`](file:///c:/Users/shrav/OneDrive/Desktop/MRPL_AI_Workbench/src) | Core application code separated into modular domain sub-packages. |
| [`src/agents/`](file:///c:/Users/shrav/OneDrive/Desktop/MRPL_AI_Workbench/src/agents) | Base interfaces and state contracts for autonomous agent workflows. |
| [`src/routing/`](file:///c:/Users/shrav/OneDrive/Desktop/MRPL_AI_Workbench/src/routing) | Automatic model router specifications enforcing single-model VRAM loading. |
| [`src/rag/`](file:///c:/Users/shrav/OneDrive/Desktop/MRPL_AI_Workbench/src/rag) | Local vector store embedding and offline retrieval interfaces. |
| [`src/tools/`](file:///c:/Users/shrav/OneDrive/Desktop/MRPL_AI_Workbench/src/tools) | Tool registry and tool-calling abstraction definitions. |
| [`src/execution/`](file:///c:/Users/shrav/OneDrive/Desktop/MRPL_AI_Workbench/src/execution) | Isolated local Python code execution sandbox interfaces. |
| [`src/generators/`](file:///c:/Users/shrav/OneDrive/Desktop/MRPL_AI_Workbench/src/generators) | Automated Word (`.docx`) and Excel (`.xlsx`) document generator interfaces. |
| [`documents/`](file:///c:/Users/shrav/OneDrive/Desktop/MRPL_AI_Workbench/documents) | Ingestion directory for raw input PDFs, spreadsheets, and inspection images. |
| [`outputs/`](file:///c:/Users/shrav/OneDrive/Desktop/MRPL_AI_Workbench/outputs) | Export directory for generated reports, tables, and execution artifacts. |
| [`database/`](file:///c:/Users/shrav/OneDrive/Desktop/MRPL_AI_Workbench/database) | Local relational SQLite database for persistent task state tracking. |
| [`vector_store/`](file:///c:/Users/shrav/OneDrive/Desktop/MRPL_AI_Workbench/vector_store) | Local offline vector storage indices for document RAG. |
| [`cache/`](file:///c:/Users/shrav/OneDrive/Desktop/MRPL_AI_Workbench/cache) | Transient computational cache and temporary data buffers. |
| [`downloads/`](file:///c:/Users/shrav/OneDrive/Desktop/MRPL_AI_Workbench/downloads) | Temporary staging for local model weights and offline package wheels. |

---

## 5. Installation Steps

### Prerequisites
- Operating System: Windows 10/11
- Python: **Python 3.11**
- Local Inference Engine: **Ollama** installed on local workstation (`http://127.0.0.1:11434`)

### Setup Instructions

1. **Clone or Navigate to the Workspace Directory**:
   ```cmd
   cd c:\Users\shrav\OneDrive\Desktop\MRPL_AI_Workbench
   ```

2. **Create Python 3.11 Virtual Environment**:
   ```cmd
   python -m venv venv
   call venv\Scripts\activate
   ```

3. **Install Base Dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

4. **Environment Configuration**:
   Copy `.env.example` to `.env`:
   ```cmd
   copy .env.example .env
   ```

---

## 6. How to Run & Verify

To verify that the configuration, logger, utilities, and package imports operate cleanly:

```cmd
python -c "from config import settings; from utils import logger, validate_environment; validate_environment(); logger.info(f'Loaded settings for: {settings.PROJECT_NAME}')"
```

---

## 7. Compliance & Rules

- **Zero Cloud APIs**: OpenAI, Gemini, and Claude are strictly excluded.
- **Zero Framework Bloat**: No FastAPI, Streamlit, LangGraph, or ChromaDB dependencies.
- **Clean Foundation**: Foundation architecture contains zero mock business logic.
