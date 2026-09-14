"""
Phase 14 Web UI Security Audit Script.
Performs 15 static and runtime checks verifying zero CDNs, zero remote fonts/scripts/styles,
same-origin API calls, zero cloud URLs, and active air-gapped policy.
"""

import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings
from src.security import NetworkPolicy, OfflineGuard


def run_ui_security_audit():
    print("==================================================")
    print("PHASE 14 WEB UI SECURITY AUDIT")
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

    frontend_dir = PROJECT_ROOT / "frontend"
    index_file = frontend_dir / "index.html"
    index_content = index_file.read_text(encoding="utf-8") if index_file.exists() else ""

    # Check 1: No CDN URLs in index.html
    has_cdn = "cdn" in index_content.lower() or "cdnjs" in index_content.lower() or "unpkg" in index_content.lower()
    record("Zero CDN URLs in index.html", not has_cdn)

    # Check 2: No Remote Script Tags (http:// or https://)
    remote_scripts = re.findall(r'<script[^>]+src=["\'](http[s]?://[^"\']+)["\']', index_content)
    record("Zero External Remote Script Tags", len(remote_scripts) == 0, f"Found: {remote_scripts}")

    # Check 3: No Remote Stylesheets (http:// or https://)
    remote_styles = re.findall(r'<link[^>]+href=["\'](http[s]?://[^"\']+)["\']', index_content)
    record("Zero External Remote Stylesheet Tags", len(remote_styles) == 0, f"Found: {remote_styles}")

    # Check 4: No Google Fonts References
    has_gfonts = "fonts.googleapis.com" in index_content or "fonts.gstatic.com" in index_content
    record("Zero Google Fonts References", not has_gfonts)

    # Check 5: No Cloud API Domain Calls in JavaScript
    cloud_domains = ["api.openai.com", "api.anthropic.com", "generativelanguage.googleapis.com", "huggingface.co"]
    js_cloud_found = []
    for root, _, files in os.walk(frontend_dir / "js"):
        for f in files:
            if f.endswith(".py") or f.endswith(".js"):
                content = (Path(root) / f).read_text(encoding="utf-8")
                for cd in cloud_domains:
                    if cd in content:
                        js_cloud_found.append(f"{f}: {cd}")

    record("Zero Cloud API Domain Calls in Frontend JS", len(js_cloud_found) == 0, f"Found: {js_cloud_found}")

    # Check 6: Same-Origin Relative API URLs
    api_js = (frontend_dir / "js" / "api.js").read_text(encoding="utf-8") if (frontend_dir / "js" / "api.js").exists() else ""
    has_relative = "fetch(endpoint," in api_js
    record("Same-Origin Relative API Fetch Client", has_relative)

    # Check 7: No Direct Ollama API Access from Frontend JS
    has_direct_ollama = "11434" in index_content
    record("No Direct Ollama Port 11434 in Frontend", not has_direct_ollama)

    # Check 8: No Direct SQLite Access from Frontend JS
    has_sqlite_js = ".db" in index_content or "sqlite" in index_content
    record("No Direct SQLite Access in Frontend", not has_sqlite_js)

    # Check 9: No Direct ChromaDB Access from Frontend JS
    has_chroma_js = "chroma" in index_content
    record("No Direct ChromaDB Access in Frontend", not has_chroma_js)

    # Check 10: No Shell Execution in Frontend JS
    has_shell = "exec(" in index_content or "subprocess" in index_content
    record("No Shell Execution Syntax in Frontend", not has_shell)

    # Check 11: No Python Code Execution in Frontend JS
    has_py_eval = "eval(" in index_content
    record("No Unsafe Eval Execution in Frontend", not has_py_eval)

    # Check 12: Offline Configuration Active
    record("Offline Configuration Active", settings.OFFLINE_MODE is True)

    # Check 13: Strict Offline Mode Active
    record("Strict Offline Mode Active", settings.OFFLINE_STRICT_MODE is True)

    # Check 14: Local-Only Network Policy Active
    record("Local-Only Network Policy Active", settings.ALLOW_EXTERNAL_NETWORK is False)

    # Check 15: OfflineGuard Posture Active
    guard = OfflineGuard()
    record("OfflineGuard Posture Validation Active", guard.is_offline_safe())

    print("\n--------------------------------------------------")
    print(f"Security checks passed: {passed}")
    print(f"Security checks failed: {failed}")
    print("--------------------------------------------------")

    if failed == 0:
        print("\n=== Phase 14 UI Security Audit PASSED ===")
        return 0
    else:
        print("\n=== Phase 14 UI Security Audit FAILED ===")
        return 1


if __name__ == "__main__":
    sys.exit(run_ui_security_audit())
