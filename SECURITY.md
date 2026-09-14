# Enterprise Security & Sovereignty Policy Specification

**Project Name**: MRPL_AI_Workbench  
**Classification**: Sovereign On-Premise Industrial AI Platform  
**Compliance Standard**: 100% Offline, Air-Gapped Data Sovereignty  

---

## 1. Security Architecture & Threat Model

The **MRPL AI Workbench** is designed for deployment in confidential oil & gas industrial facilities. All operational data, technical schematics, sensor logs, and operational reports remain exclusively within the local network perimeter.

```
                    ┌──────────────────────────────┐
                    │      FastAPI REST API        │
                    │ /auth /operator /agent /chat │
                    └───────────────┬──────────────┘
                                    │
                    ┌───────────────▼──────────────┐
                    │ Bearer Auth & RBAC Middleware│
                    │ (ADMIN, OPERATOR, ANALYST)   │
                    └───────────────┬──────────────┘
                                    │
                    ┌───────────────▼──────────────┐
                    │  Rate Limiting & Sanitizer   │
                    │ (Sliding Window, Injection)  │
                    └───────────────┬──────────────┘
                                    │
                    ┌───────────────▼──────────────┐
                    │  Agent Policy & Approval     │
                    │ (Allowlist & Human Gate)     │
                    └───────────────┬──────────────┘
                                    │
                    ┌───────────────▼──────────────┐
                    │ Local Ollama Open-Weight LLMs│
                    └──────────────────────────────┘
```

---

## 2. Authentication & Role-Based Access Control (RBAC)

Authentication is enforced via local Bearer access tokens (`src/auth/`). Password hashes are generated using SHA-256 with constant-time token comparison (`hmac.compare_digest`) to prevent timing attacks.

### Role Hierarchy & Permissions
| Role | Permissions | Description |
| :--- | :--- | :--- |
| **ADMIN** | All Permissions | System configuration, full operational access |
| **OPERATOR** | `chat`, `document_upload`, `rag_query`, `vision`, `agent_run`, `agent_approve`, `agent_reject`, `agent_cancel`, `operator_read`, `audit_read` | Operational monitoring, agent task approval gate management |
| **ANALYST** | `chat`, `document_upload`, `rag_query`, `vision`, `agent_run`, `audit_read` | Analytics, agent execution, document ingestion |
| **USER** | `chat`, `document_upload`, `rag_query`, `vision` | Basic interactive chat and retrieval |

---

## 3. Defense-in-Depth Controls

1. **Prohibited Execution Vectors**: Shell, Python `eval()`, subprocess, arbitrary network calls, and browser tools are hard-blocked by `AgentPolicy`.
2. **Path Traversal Defenses**: Document upload filenames are sanitized (`os.path.basename`), rejecting relative tokens (`..`), UNC paths, and unpermitted extensions.
3. **Prompt Injection Defense**: Retrieved RAG document context is wrapped in isolation boundaries (`<<<UNTRUSTED_DOC_DATA>>>`) to prevent untrusted content from overriding system instructions.
4. **Audit Trajectory Logging**: Operations are logged without exposing raw secrets, Bearer tokens, or private model reasoning (chain-of-thought).
5. **Rate Limiting**: Sliding window rate limiter returning `HTTP 429` on request threshold breaches.
