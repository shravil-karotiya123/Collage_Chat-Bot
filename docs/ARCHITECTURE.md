# MRPL AI Workbench — Architecture Specification

## Executive Overview

The **MRPL Sovereign On-Premises AI Workbench** is a local-first, air-gap-capable operational intelligence platform engineered for refinery and industrial technology (OT) environments. 

The system operates strictly within local workstation boundaries under three architectural mandates:
1. **Data Sovereignty** — Zero external API calls, cloud telemetry, or remote vector storage.
2. **Least-Privilege Retrieval** — RBAC roles (`ADMIN`, `ENGINEER`, `OPERATOR`, `ANALYST`, `VIEWER`) and document classification filters are enforced *before* vector search context reaches model memory.
3. **Defensible Outputs** — Engineering answers undergo multi-tier evidence verification, SHA-256 tamper-evident hash chaining, and Ed25519 cryptographic signing.

---

## 6-Tier Sovereign Processing Plane

```mermaid
flowchart TB
    subgraph DataPlane["Six-Tier Local Sovereign Data Plane"]
        T1["Tier 1: Local Ollama LLMs & OCR\n(qwen2.5:7b-instruct, qwen2.5-coder:7b-instruct, qwen2.5-vl:3b-instruct, paddleocr)"]
        T2["Tier 2: Offline Embeddings\n(SentenceTransformers / PyTorch CPU/GPU)"]
        T3["Tier 3: Permission-Tagged ChromaDB\n(data/chroma/ Vector Store)"]
        T4["Tier 4: DuckDB Telemetry Engine\n(data/duckdb/ In-Memory Analytics & Validation)"]
        T5["Tier 5: SQLite WAL Storage\n(data/sqlite/ mrpl_workbench.db)"]
        T6["Tier 6: Sandboxed File Storage\n(data/documents/ & data/workspaces/)"]
    end

    T6 --> T2 --> T3
    T5 --- T3
    T4 --- T1
    T3 --- T1
```

---

## High-Level Execution Topology

```mermaid
flowchart TB
    User["Refinery User / Identity"] --> API["FastAPI Application Boundary"]
    
    subgraph SecurityBoundary["Sovereignty & Security Boundary"]
        AirGap["AirGapEnforcer & Network Policy"]
        Sentinel["AirGapSentinel Socket Auditor"]
        API --> AirGap --> Sentinel
    end

    subgraph LangGraphEngine["Deterministic LangGraph Pipeline"]
        Router["1. Planner / Router"]
        AuthGate["2. Authorization Gate"]
        RAG["3. RAG Retrieval Agent"]
        Investigate["4. Investigation Agent"]
        Synthesize["5. Industrial Synthesizer"]
        Verify["6. Hallucination Firewall"]
        Format["7. Guardrail Formatter"]
        Attest["8. Ed25519 Evidence Attestor"]

        Router --> AuthGate --> RAG --> Investigate --> Synthesize --> Verify --> Format --> Attest
    end

    API --> Router
    Attest --> Ledger["SHA-256 Chained Audit Ledger"]
    Format --> Response["Guarded Engineering Response"]
```

---

## Component Responsibilities

| Layer | Component | Core Function |
|---|---|---|
| API & Auth | `src/api/` | FastAPI REST endpoints, Bearer auth, RBAC context propagation |
| Sovereignty | `src/core/network/` | Enforces `STRICT_AIRGAP` policy and socket audit logging |
| Security Gate | `src/core/security/` | Path traversal protection, input sanitization, classification filters |
| Model Managers | `src/models/` | `QwenManager`, `CoderManager`, `VisionManager` Ollama execution |
| OCR Subsystem | `src/ocr/` | `PaddleOCR` primary text/table extraction with `VisionAnalyzer` fallback |
| Routing | `src/routing/` | `ModelRouter` and `IntentClassifier` for model selection |
| RAG & Vector | `src/rag/`, `src/retrieval/` | Permission-filtered similarity search in ChromaDB |
| Analytics | `src/analytics/` | DuckDB analytical queries with SQL safety validator |
| Verification | `src/verification/` | Claim extraction, NLI cross-checking, causal leap guard |
| Audit & Proof | `src/audit/`, `src/attestation/` | Hash-chained JSONL logging & Ed25519 digital signature export |
