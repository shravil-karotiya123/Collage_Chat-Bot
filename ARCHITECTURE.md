# Enterprise Architecture Specification

> **Sovereign On-Premise Agentic AI Workbench**  
> Technical Architecture Blueprint & Design Principles

---

## 1. Clean Architecture & Separation of Concerns

The architecture strictly adheres to **Clean Architecture** principles, maintaining clear dependency boundaries across system layers.

```
+-----------------------------------------------------------------------+
|                         Presentation Layer                            |
|                 (FastAPI REST API / Workbench API)                    |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                    Unified Orchestration Service                      |
|            (src/services/workbench_service.py: WorkbenchService)     |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                 OCR, Vision & Document Processing Subsystems          |
|      (src/ocr: PDFDetector, TextOCR | src/document_processing)       |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                         Local RAG Subsystem                           |
| (src/rag: Embeddings | VectorStore | Indexer | Retriever | RAGService)  |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                    Persistence & Crash Recovery Layer                  |
| (src/persistence: DatabaseManager, TaskRepo, ExecRepo, AuditRepo)    |
| (src/agents: TaskStateMachine, RecoveryManager, SQLiteStateStore)     |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                          Routing Layer                                |
|    (src/routing: BaseRouter | IntentClassifier | ModelRouter)         |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                    Domain Abstraction Layer                           |
|       (src/models: BaseModel Interface | src/schemas: Pydantic DTOs)    |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                     Inference Adapter Layer                           |
|     (Ollama Adapter / vLLM Adapter / llama.cpp / LM Studio Adapter)   |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                         Hardware & Models                             |
|       (Local Models: qwen2.5:7b, deepseek-coder:6.7b, minicpm-v:8b)   |
+-----------------------------------+-----------------------------------+
```

---

## 2. End-to-End Architectural Workflows

### Unified Document Ingestion Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant API as FastAPI REST Endpoint
    participant Svc as WorkbenchService
    participant Det as PDFDetector
    participant OCR as OCRService
    participant Pipe as DocumentPipeline
    participant RAG as RAGService
    participant Vec as VectorStore

    User->>API: POST /workbench/documents (file)
    API->>Svc: process_document(filename, bytes)
    Svc->>Det: inspect_page_types(bytes)
    alt Scanned PDF or Image
        Svc->>OCR: process_document(filename, bytes)
        OCR-->>Svc: OCRDocumentResult (chunks)
    else Machine-Readable Document
        Svc->>Pipe: process_document(file_name, bytes)
        Pipe-->>Svc: DocumentUploadResponse (chunks)
    end
    Svc->>RAG: index_document(chunks)
    RAG->>Vec: add_chunks(embeddings)
    RAG-->>Svc: Indexed confirmation
    Svc-->>API: WorkbenchDocumentUploadResponse
    API-->>User: 200 OK Response
```

### Grounded RAG Chat & Intent Routing Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant API as FastAPI REST Endpoint
    participant Svc as WorkbenchService
    participant Router as ModelRouter
    participant RAG as RAGService
    participant Model as QwenManager / DeepSeekManager

    User->>API: POST /workbench/chat (query)
    API->>Svc: ask_question(query)
    Svc->>Router: route(query)
    Router-->>Svc: RoutingResult (intent, manager)
    alt Context Required (DOCUMENT / SUMMARIZATION)
        Svc->>RAG: query(query)
        RAG->>Model: generate(grounded_prompt)
        Model-->>RAG: Grounded answer + sources
        RAG-->>Svc: RAGQueryResult
    else General / Coding Query
        Svc->>Model: generate(prompt)
        Model-->>Svc: Generated answer
    end
    Svc-->>API: WorkbenchChatResponse
    API-->>User: 200 OK Response
```

---

## 3. Hardware Resource & Memory Management Lifecycle

The workstation hardware configuration (16 GB system RAM, NVIDIA RTX 5050 GPU ~8 GB VRAM) enforces a strict **Single-Model Memory Strategy**:

```mermaid
stateDiagram-v2
    [*] --> Idle: VRAM Unloaded
    Idle --> Loading_Qwen: Intent GENERAL_CHAT / RAG
    Loading_Qwen --> Active_Qwen: qwen2.5:7b in VRAM
    Active_Qwen --> Evicting_Qwen: Intent switched to CODING
    Evicting_Qwen --> Loading_DeepSeek: VRAM Cleared
    Loading_DeepSeek --> Active_DeepSeek: deepseek-coder:6.7b in VRAM
    Active_DeepSeek --> Evicting_DeepSeek: Intent switched to IMAGE
    Evicting_DeepSeek --> Loading_Vision: VRAM Cleared
    Loading_Vision --> Active_Vision: minicpm-v:8b in VRAM
```

---

## 4. Complete REST API Endpoint Registry

| HTTP Method | Path | Subsystem / Workflow | Response Schema |
| :--- | :--- | :--- | :--- |
| **GET** | `/health` | System Health | `StandardResponse[Dict]` |
| **GET** | `/models` | Local Model Catalog | `StandardResponse[Dict]` |
| **GET** | `/router` | Model Router Telemetry | `StandardResponse[Dict]` |
| **POST** | `/chat` | Intent-based Chat Routing | `StandardResponse[ChatResponse]` |
| **POST** | `/documents/upload` | Document Parsing | `StandardResponse[DocumentUploadResponse]` |
| **POST** | `/documents/index` | RAG Chunk Indexing | `StandardResponse[RAGIndexResponse]` |
| **POST** | `/documents/query` | Grounded RAG Query | `StandardResponse[RAGQueryResponse]` |
| **DELETE** | `/documents/{id}` | Vector Chunk Eviction | `StandardResponse[Dict]` |
| **GET** | `/documents/rag/health` | RAG Telemetry | `StandardResponse[RAGHealthResponse]` |
| **POST** | `/ocr/process` | OCR & Page Analysis | `StandardResponse[OCRProcessResponse]` |
| **GET** | `/ocr/health` | OCR Telemetry | `StandardResponse[OCRHealthResponse]` |
| **POST** | `/workbench/chat` | Unified Grounded Chat | `StandardResponse[WorkbenchChatResponse]` |
| **POST** | `/workbench/documents` | Unified Ingestion | `StandardResponse[WorkbenchDocumentUploadResponse]` |
| **POST** | `/workbench/images` | Unified Vision Analysis | `StandardResponse[WorkbenchImageResponse]` |
| **GET** | `/workbench/health` | Unified Telemetry | `StandardResponse[WorkbenchHealthResponse]` |
| **POST** | `/agent/run` | Create & Execute Agent Task | `StandardResponse[AgentRunResponse]` |
| **POST** | `/agent/approve/{id}` | Approve Waiting Task | `StandardResponse[AgentApprovalResponse]` |
| **POST** | `/agent/reject/{id}` | Reject Waiting Task | `StandardResponse[AgentRejectionResponse]` |
| **GET** | `/agent/status/{id}` | Get Task Execution Status | `StandardResponse[AgentStatusResponse]` |
| **GET** | `/agent/plan/{id}` | Get Operational Plan | `StandardResponse[AgentPlanResponse]` |
| **POST** | `/agent/cancel/{id}` | Cancel Task Execution | `StandardResponse[AgentStatusResponse]` |
| **GET** | `/agent/tools` | List Registered Agent Tools | `StandardResponse[List[AgentToolSchema]]` |
| **GET** | `/agent/health` | Agent Subsystem Health | `StandardResponse[AgentHealthResponse]` |
| **POST** | `/auth/login` | Bearer Token Authentication | `StandardResponse[TokenResponse]` |
| **GET** | `/auth/me` | Active Identity Profile | `StandardResponse[UserResponse]` |
| **POST** | `/auth/logout` | Token Session Revocation | `StandardResponse[Dict]` |
| **GET** | `/operator/dashboard` | Server-Rendered Dashboard | `HTMLResponse` |
| **GET** | `/operator/system` | Operator Platform Telemetry | `StandardResponse[OperatorSystemResponse]` |
| **GET** | `/operator/models` | Model Catalog Status | `StandardResponse[OperatorModelResponse]` |
| **GET** | `/operator/memory` | RAM & VRAM Diagnostics | `StandardResponse[OperatorMemoryResponse]` |
| **GET** | `/operator/tasks` | Active Task Summaries | `StandardResponse[List[OperatorTaskResponse]]` |
| **GET** | `/operator/audit` | Structured Audit Event Log | `StandardResponse[List[AuditEventResponse]]` |
| **GET** | `/metrics` | In-Process Telemetry Map | `StandardResponse[MetricsResponse]` |
| **GET** | `/security/status` | Security Posture Summary | `StandardResponse[SecurityStatusResponse]` |
| **GET** | `/security/policy` | Tool Boundary & Policy | `StandardResponse[SecurityPolicyResponse]` |
| **GET** | `/security/events` | Recorded Security Violations | `StandardResponse[List[SecurityEventResponse]]` |
| **GET** | `/live` | Process Liveness Probe | `StandardResponse[Dict]` |
| **GET** | `/` | Web UI Operator Console Shell | `FileResponse (index.html)` |
| **GET** | `/static/*` | Local Static Assets (CSS, JS, SVG) | `StaticFiles` |
| **GET** | `/documents` | Indexed Document Metadata Catalog | `StandardResponse[List]` |
| **GET** | `/security/offline` | Air-Gapped Posture Status | `StandardResponse[OfflineStatusResponse]` |
| **POST** | `/security/offline/validate` | Air-Gapped Posture Validation Check | `StandardResponse[OfflineValidationResponse]` |

---

## 5. Offline-First Sovereign Design

- **Zero External Egress**: Engineered to run in 100% air-gapped industrial environments.
- **Local Weight Storage**: All open-weight LLMs (`qwen2.5:7b`, `deepseek-coder:6.7b`, `minicpm-v:8b`) execute locally on host workstation GPU hardware.
- **Data Sovereignty**: Industrial telemetry, schematics, and confidential documents remain exclusively on-premise.

---

## 6. Phase 14 Web UI Operator Console Architecture

```mermaid
graph TD
    User([Operator User]) -->|Browser HTTP| UI[Web UI SPA index.html]
    
    subgraph Frontend [Local Browser Layer]
        UI --> API_JS[api.js Client]
        API_JS --> Router_JS[router.js SPA Navigation]
        API_JS --> Modules[dashboard.js, chat.js, documents.js, rag.js, ocr.js, agents.js, approvals.js, audit.js]
    end

    subgraph Backend [FastAPI Sovereign Server]
        API_JS -->|Same-Origin Fetch| FastAPI[FastAPI App App.py]
        FastAPI -->|GET /| UI_Route[ui.py Router]
        FastAPI -->|/static/*| StaticFiles[StaticFiles Directory]
        FastAPI -->|REST Endpoints| Services[WorkbenchService / RAGService / OCRService / AgentOrchestrator]
    end

    subgraph Security [Air-Gapped Governance]
        Services --> OfflineGuard[OfflineGuard]
        OfflineGuard --> NetworkPolicy[LOCAL_ONLY NetworkPolicy]
    end

    subgraph Execution [Local Infrastructure]
        Services --> ModelRouter[ModelRouter]
        ModelRouter --> Ollama[Local Ollama Runtime]
        Ollama --> Qwen[Qwen 2.5 7B]
        Ollama --> DeepSeek[DeepSeek Coder 6.7B]
        Ollama --> MiniCPM[MiniCPM-V 8B]
        Services --> ChromaDB[(Local ChromaDB)]
        Services --> SQLite[(Local SQLite WAL)]
    end
```
