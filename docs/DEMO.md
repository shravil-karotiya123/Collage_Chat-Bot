# MRPL AI WORKBENCH — INDUSTRIAL DEMONSTRATION GUIDE

**Project**: MRPL Sovereign On-Premise Agentic AI Workbench  
**Sovereignty**: 100% Air-Gapped & Local Execution Enforced  

---

## 1. Overview

The **MRPL AI Workbench** is a sovereign, air-gapped enterprise AI platform designed for refineries, PSUs, and defense-linked engineering organizations handling confidential knowledge.

This guide details the three primary industrial demonstrations provided by the platform:

1. **Primary Industrial Inspection Demonstration** (`POST /workbench/demo/inspection`)
2. **Secure Coding Sandbox Demonstration** (`POST /workbench/demo/coding`)
3. **Multimodal Engineering Vision Demonstration** (`POST /workbench/demo/vision`)

---

## 2. Demonstration Workflows

### 2.1 Primary Industrial Demonstration
**Scenario**: "Scanned Inspection Report → OCR → Findings → RAG → Approval Note → Word File (.DOCX)"

```text
User Upload (scanned_inspection_report.pdf)
  ↓
PaddleOCR Engine (Text & Table Extraction)
  ↓
Document Chunking & Local Embeddings (SentenceTransformers)
  ↓
Local Vector Indexing (ChromaDB)
  ↓
Agent Analysis (Qwen 2.5 7B Instruct)
  ↓
RAG Knowledge Retrieval
  ↓
Approval Gate Evaluation (Human-in-the-Loop Governance)
  ↓
Official Approval Note Deliverable (.DOCX Artifact)
```

**Executing via API**:
```bash
curl -X POST "http://127.0.0.1:8000/workbench/demo/inspection" \
     -F "file=@examples/data/scanned_inspection_report.pdf" \
     -F "auto_index=true" \
     -F "generate_approval_note=true"
```

---

### 2.2 Secure Coding Sandbox Demonstration
**Scenario**: "Write Python email validator → generate tests → execute in sandbox → fix if needed → return verified code"

```text
User Request
  ↓
Intelligent Router (Intent: CODING)
  ↓
CoderManager (Qwen 2.5 Coder 7B Instruct)
  ↓
CodingTool & Local Sandbox Container
  ↓
Unit Test Execution & Verification
  ↓
Verified Code Deliverable (.py Artifact)
```

**Executing via API**:
```bash
curl -X POST "http://127.0.0.1:8000/workbench/demo/coding" \
     -F "prompt=Write a Python function that validates MRPL email addresses"
```

---

### 2.3 Multimodal Engineering Vision Demonstration
**Scenario**: "Technical Diagram / Schematic → Visual Analysis → Findings"

```text
Technical Image Upload (engineering_diagram.png)
  ↓
VisionManager (Qwen 2.5 VL 3B Instruct)
  ↓
Visual Observations & Image Analysis
  ↓
Structured Findings Payload
```

**Executing via API**:
```bash
curl -X POST "http://127.0.0.1:8000/workbench/demo/vision" \
     -F "file=@examples/data/engineering_diagram.png"
```

---

## 3. Automated Demonstration Scripts

You can execute all end-to-end demonstrations via automated CLI scripts:

```powershell
# 1. Full Production Demonstration Suite
py examples/industrial_workbench_demo.py

# 2. Network Sovereignty Proof
py examples/network_sovereignty_validation.py

# 3. Security Audit (20 / 20 Checks)
py examples/final_security_sovereignty_audit.py

# 4. Live Model Verification (when Ollama is active)
py examples/real_model_inference_validation.py
```
