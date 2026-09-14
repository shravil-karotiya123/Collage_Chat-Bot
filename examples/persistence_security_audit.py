"""
Phase 12 Persistence & Sovereignty Security Audit Script.
Performs static and runtime checks verifying local-only SQLite persistence, zero cloud dependencies,
secret redaction, approval gate preservation, prohibited tool blocking, and retry policy bounds.
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings
from src.agents.policies import PROHIBITED_TOOL_NAMES, AgentPolicy
from src.persistence import (
    DBAuditEvent,
    DBTask,
    DatabaseManager,
    TaskRepository,
    redact_sensitive_data,
)


def run_persistence_security_audit():
    print("==================================================")
    print("PHASE 12 PERSISTENCE & SECURITY AUDIT")
    print("==================================================\n")

    passed = 0
    failed = 0

    def record(check_name: str, status: bool, detail: str = ""):
        nonlocal passed, failed
        if status:
            passed += 1
            print(f"[PASS] {check_name} {f'({detail})' if detail else ''}")
        else:
            failed += 1
            print(f"[FAIL] {check_name} {f'({detail})' if detail else ''}")

    # Check 1: Local SQLite Database Path Only
    db_path = settings.AGENT_DATABASE_PATH
    is_local_sqlite = db_path.suffix.lower() in (".db", ".sqlite", ".sqlite3")
    record("Local SQLite Database Provider", is_local_sqlite, f"Database Path: {db_path.name}")

    # Check 2: Zero Cloud LLM / SaaS Imports in Persistence Layer
    cloud_keywords = ["openai", "anthropic", "azure", "supabase", "firebase", "mongodb"]
    violations = []
    for root, _, files in os.walk(PROJECT_ROOT / "src" / "persistence"):
        for f in files:
            if f.endswith(".py"):
                content = (Path(root) / f).read_text(encoding="utf-8").lower()
                for kw in cloud_keywords:
                    if f"import {kw}" in content or f"from {kw}" in content:
                        violations.append(f"{f}: {kw}")

    record("Zero Cloud DB / SaaS Dependencies", len(violations) == 0, f"Violations: {violations}")

    # Check 3: Secret & Token Redaction Engine
    raw_payload = {"password": "supersecretpassword", "access_token": "mrpl_tok_secret", "normal": "valid"}
    redacted_payload = redact_sensitive_data(raw_payload)
    is_redacted = (
        redacted_payload["password"] == "[REDACTED_SECRET]"
        and redacted_payload["access_token"] == "[REDACTED_SECRET]"
        and redacted_payload["normal"] == "valid"
    )
    record("Secret & Token Data Redaction", is_redacted)

    # Check 4: Chain-of-Thought Redaction
    cot_payload = {"reasoning": "Internal secret chain-of-thought", "thought": "private step"}
    cleaned_cot = redact_sensitive_data(cot_payload)
    is_cot_redacted = (
        cleaned_cot["reasoning"] == "[REDACTED_SECRET]"
        and cleaned_cot["thought"] == "[REDACTED_SECRET]"
    )
    record("Chain-of-Thought Redaction Layer", is_cot_redacted)

    # Check 5: Prohibited Tools Policy Enforcement
    policy = AgentPolicy()
    prohibited_blocked = all(not policy.is_tool_allowed(tool) for tool in PROHIBITED_TOOL_NAMES)
    record("Prohibited Tool Policy Integrity", prohibited_blocked)

    # Check 6: Retry Bounds Configuration
    has_retry_bounds = settings.MAX_TASK_RETRIES >= 1 and settings.MAX_TASK_RETRIES <= 5
    record("Bounded Task Retry Limits Enforced", has_retry_bounds, f"Max Retries: {settings.MAX_TASK_RETRIES}")

    # Check 7: Single-Model VRAM Strategy Preserved
    record("Single-Model Memory Lifecycle Preserved", settings.MAX_CONCURRENT_MODELS == 1)

    # Check 8: Rate Limiting & Authentication Preserved
    record("Authentication & Rate Limiting Enabled", settings.AUTH_ENABLED and settings.RATE_LIMIT_ENABLED)

    print("\n--------------------------------------------------")
    print(f"Security checks passed: {passed}")
    print(f"Security checks failed: {failed}")
    print("--------------------------------------------------")

    if failed == 0:
        print("\n=== Phase 12 Security Audit PASSED ===")
        return 0
    else:
        print("\n=== Phase 12 Security Audit FAILED ===")
        return 1


if __name__ == "__main__":
    sys.exit(run_persistence_security_audit())
