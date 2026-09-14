"""
MRPL AI Workbench — Environment Verification Script
Verifies system hardware, Python runtime, local directories, and mandatory dependencies.
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

REQUIRED_MODULES = [
    ("fastapi", "FastAPI Web Engine"),
    ("uvicorn", "Uvicorn ASGI Server"),
    ("pydantic", "Pydantic Settings & Schemas"),
    ("ollama", "Local Ollama LLM Client"),
    ("chromadb", "Local Vector Store"),
    ("sentence_transformers", "Offline Embedding Provider"),
    ("torch", "PyTorch Core Engine"),
    ("duckdb", "Local Telemetry Investigation Engine"),
    ("cryptography", "Ed25519 Cryptographic Signatures"),
]


def check_python_version() -> bool:
    print(f"[1/4] Checking Python Runtime: {sys.version.split()[0]}...")
    if sys.version_info >= (3, 10):
        print("  [OK] Compatible Python version detected.")
        return True
    print("  [FAIL] Python 3.10+ required.")
    return False


def check_directories() -> bool:
    print("[2/4] Checking 6-Tier Sovereign Data Directories...")
    dirs = [
        BASE_DIR / "data" / "documents",
        BASE_DIR / "data" / "workspaces",
        BASE_DIR / "data" / "chroma",
        BASE_DIR / "data" / "sqlite",
        BASE_DIR / "data" / "duckdb",
        BASE_DIR / "data" / "audit",
    ]
    all_ok = True
    for d in dirs:
        if d.exists():
            print(f"  [OK] Found: {d.relative_to(BASE_DIR)}")
        else:
            print(f"  [FAIL] Missing directory: {d.relative_to(BASE_DIR)}")
            all_ok = False
    return all_ok


def check_dependencies() -> bool:
    print("[3/4] Checking Core Dependencies...")
    all_ok = True
    for module_name, label in REQUIRED_MODULES:
        try:
            __import__(module_name)
            print(f"  [OK] {label} ({module_name}): Installed")
        except ImportError:
            print(f"  [WARN] {label} ({module_name}): NOT INSTALLED")
            all_ok = False
    return all_ok


def check_ollama_local_status() -> bool:
    print("[4/4] Checking Local Ollama Endpoint (127.0.0.1:11434)...")
    try:
        import urllib.request
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags")
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200:
                print("  [OK] Ollama local daemon active and responding.")
                return True
    except Exception:
        print("  [INFO] Ollama local daemon not detected on 127.0.0.1:11434 (offline fallback active).")
    return True


def main() -> None:
    print("=" * 60)
    print("MRPL AI Workbench Environment Verification")
    print("=" * 60)
    v_ok = check_python_version()
    d_ok = check_directories()
    m_ok = check_dependencies()
    o_ok = check_ollama_local_status()
    print("=" * 60)
    if v_ok and d_ok and m_ok and o_ok:
        print("Environment status: READY FOR SOVEREIGN EXECUTION")
    else:
        print("Environment status: ACTION REQUIRED — Missing dependencies or directories.")
    print("=" * 60)


if __name__ == "__main__":
    main()
