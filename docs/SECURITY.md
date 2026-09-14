# MRPL AI Workbench — Security & Authorization Architecture

## Security Overview

The security model of the MRPL AI Workbench enforces **defense-in-depth**, zero cloud reliance, and strict least-privilege data access across all operational stages.

---

## 1. Authentication & RBAC Hierarchy

User access is controlled via authenticated session contexts associated with explicit RBAC roles:

| Role | Access Scope | Workspace Permissions | Document Classification Ceiling |
|---|---|---|---|
| `ADMIN` | System configuration, audit export, full workspace access | Full read/write/admin | Level 5 (RESTRICTED) |
| `ENGINEER` | Technical inspection, script analysis, schema modification | Workspace read/write | Level 4 (CONFIDENTIAL) |
| `OPERATOR` | Active refinery operations, task execution, document uploads | Workspace read/write | Level 3 (OPERATIONAL) |
| `ANALYST` | Technical investigation, historical telemetry queries | Workspace read-only | Level 2 (INTERNAL) |
| `VIEWER` | SOP query & standard grounded Q&A | Assigned workspace read-only | Level 1 (PUBLIC) |

---

## 2. Authorization-Before-Retrieval Gate

A core security principle of the architecture is that **retrieval filtering happens BEFORE vector similarity search results reach model context**.

```text
User Request + Identity
       ↓
RBAC Authorization Gate (Role + Workspace ID + Classification Ceiling)
       ↓
Metadata Filter (document_id, workspace_id, role, classification)
       ↓
ChromaDB Vector Similarity Query
       ↓
Filtered Approved Context -> Local LLM Prompt
```

This prevents unauthorized document chunks from ever entering prompt memory or being exposed to model context.

---

## 3. Sandboxing & File System Controls

- All local file ingestion occurs inside designated workspace boundaries (`data/workspaces/<workspace_id>`).
- [`PathSecurity`](file:///c:/Users/shrav/OneDrive/Desktop/MRPL_AI_Workbench/src/core/security/path_security.py) prevents path traversal attacks (`../`, symlinks, absolute path escapes).
- File uploads are validated by MIME type, size limit, extension whitelist (`.pdf`, `.docx`, `.txt`, `.csv`, `.xlsx`, `.png`, `.jpg`), and SHA-256 hash duplication checks.
- Uploaded files are processed in read-only mode and are **never executed as code**.
