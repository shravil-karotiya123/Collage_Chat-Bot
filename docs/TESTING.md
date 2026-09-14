# MRPL AI Workbench — Test Suite Architecture & Verification Guide

## Test Suite Overview

The test suite covers unit, integration, security, RAG, OCR, model management, analytics, and multi-agent workflow verification.

All tests run **100% offline** without external internet access or third-party cloud API dependencies.

---

## Directory Layout

```text
tests/
├── api/                  # FastAPI REST endpoint integration tests
├── routing/              # Intent classification and model router unit tests
├── models/               # Model manager lifecycle & VRAM eviction unit tests (Qwen, Coder, Vision)
├── ocr/                  # PaddleOCR engine & text/table extraction tests
├── document_processing/  # PDF/DOCX/CSV parsing & chunking unit tests
├── embeddings/           # SentenceTransformers embedding engine unit tests
├── retrieval/            # Pre-retrieval authorization filter unit tests
├── rag/                  # End-to-end RAG service tests
├── agents/               # Tool execution & agent policy unit tests
├── orchestration/        # LangGraph workflow state transition tests
├── verification/         # Hallucination firewall & causal leap guard tests
├── audit/                # SHA-256 hash-chaining unit tests
├── attestation/          # Ed25519 signature & .clora-proof tests
└── security/             # Airgap policy, path security & rate limit tests
```

---

## Running Tests

Execute the complete offline test suite using Windows Python Launcher (`py -3`):

```powershell
py -3 -m pytest
```

Execute fast core unit tests excluding slow model integration tests:

```powershell
py -3 -m pytest tests/agents tests/routing tests/models tests/ocr tests/document_processing tests/rag tests/security tests/auth tests/persistence
```

---

## Baseline Verification Standard

- **Total Test Items**: 252 items
- **Passing Rate**: 100% of runnable tests (**251 passed**, **1 skipped**, **0 failed**).
- **Offline Environment**: Executed with `OFFLINE_MODE=True` and `ALLOW_EXTERNAL_NETWORK=False`.
