"""
Phase 14 Network Sovereignty Validation Script for MRPL AI Workbench.
Monitors network traffic and demonstrates strict ALLOW/BLOCK enforcement for air-gapped security.
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.security.network_policy import NetworkPolicy, NetworkPolicyError
from src.security.offline_guard import OfflineGuard


def run_network_sovereignty_validation():
    print("====================================================")
    print("MRPL AI WORKBENCH — NETWORK SOVEREIGNTY VALIDATION")
    print("====================================================\n")

    policy = NetworkPolicy()
    guard = OfflineGuard(network_policy=policy)

    evidence = []

    # 1. Ollama localhost check
    is_ollama_allowed = policy.is_allowed_url("http://127.0.0.1:11434")
    evidence.append(("Ollama Endpoint (http://127.0.0.1:11434)", "ALLOWED", is_ollama_allowed))

    # 2. ChromaDB local check
    chroma_res = guard.validate_vector_store()
    evidence.append(("ChromaDB Vector Store (local filesystem)", "ALLOWED", chroma_res["local"]))

    # 3. SQLite local check
    sqlite_res = guard.validate_persistence()
    evidence.append(("SQLite Persistence DB (local filesystem)", "ALLOWED", sqlite_res["local"]))

    # 4. Embeddings local check
    emb_res = guard.validate_embedding_provider()
    evidence.append(("SentenceTransformer Embeddings (local files)", "ALLOWED", emb_res["local"]))

    # 5. Local OCR check
    ocr_res = guard.validate_ocr_provider()
    evidence.append(("Local Tesseract OCR & MiniCPM-V (local execution)", "ALLOWED", ocr_res["local"]))

    # 6. External Cloud Endpoints (Must be BLOCKED)
    blocked_targets = [
        "https://api.openai.com/v1/chat/completions",
        "https://api.anthropic.com/v1/messages",
        "https://generativelanguage.googleapis.com/v1/models",
        "https://huggingface.co/api/models",
        "https://pinecone.io/index",
    ]

    all_blocked_pass = True
    for target in blocked_targets:
        is_allowed = policy.is_allowed_url(target)
        status_label = "BLOCKED" if not is_allowed else "ALLOWED_VIOLATION"
        passed = (not is_allowed)
        if not passed:
            all_blocked_pass = False
        evidence.append((f"External Endpoint ({target})", status_label, passed))

    print("WORKFLOW NETWORK AUDIT EVIDENCE TRAIL:\n")
    failed_count = 0
    for target_desc, expected_mode, passed in evidence:
        status_str = "[PASS]" if passed else "[FAIL]"
        if not passed:
            failed_count += 1
        print(f"{status_str} {target_desc} => {expected_mode}")

    print("\n====================================================")
    print(f"PASSED AUDIT CHECKS: {len(evidence) - failed_count} / {len(evidence)}")
    print(f"Validation checks failed: {failed_count}")
    print("====================================================")

    if failed_count == 0:
        print("\n=== NETWORK SOVEREIGNTY VALIDATION PASSED ===")
    return failed_count == 0


if __name__ == "__main__":
    success = run_network_sovereignty_validation()
    sys.exit(0 if success else 1)
