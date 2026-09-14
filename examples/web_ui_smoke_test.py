"""
Phase 14 Web UI & API Route Smoke Test Script.
Validates Web UI static asset loading, index route serving, and REST API endpoint integration.
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings
from src.api.app import app


def run_ui_smoke_test():
    print("==================================================")
    print("PHASE 14 WEB UI & API ROUTE SMOKE TEST")
    print("==================================================\n")

    client = TestClient(app)
    client.headers["Authorization"] = f"Bearer {settings.AUTH_TOKEN}"

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

    # 1. UI Root Route GET /
    res_index = client.get("/")
    record("UI Root Route (GET /)", res_index.status_code == 200 and "MRPL Sovereign AI Workbench" in res_index.text)

    # 2. Static CSS Asset GET /static/css/app.css
    res_css = client.get("/static/css/app.css")
    record("Static CSS Asset (GET /static/css/app.css)", res_css.status_code == 200)

    # 3. Static JS Asset GET /static/js/api.js
    res_js = client.get("/static/js/api.js")
    record("Static JS Asset (GET /static/js/api.js)", res_js.status_code == 200)

    # 4. Static SVG Logo GET /static/assets/logo.svg
    res_logo = client.get("/static/assets/logo.svg")
    record("Static SVG Logo (GET /static/assets/logo.svg)", res_logo.status_code == 200)

    # 5. Workbench Health API GET /workbench/health
    res_health = client.get("/workbench/health")
    record("Workbench Health API (GET /workbench/health)", res_health.status_code == 200)

    # 6. Offline Posture API GET /security/offline
    res_off = client.get("/security/offline")
    record("Offline Posture API (GET /security/offline)", res_off.status_code == 200)

    # 7. Offline Validation API POST /security/offline/validate
    res_val = client.post("/security/offline/validate")
    record("Offline Validation API (POST /security/offline/validate)", res_val.status_code == 200)

    # 8. Document Catalog API GET /documents
    res_docs = client.get("/documents")
    record("Document Catalog API (GET /documents)", res_docs.status_code == 200)

    # Browser Automation Availability Check
    try:
        import playwright  # type: ignore
        browser_avail = True
    except ImportError:
        browser_avail = False

    if not browser_avail:
        print("\n[NOTE] Browser automation (Playwright) unavailable — API/UI route validation completed successfully.")

    print("\n--------------------------------------------------")
    print(f"Smoke test checks passed: {passed}")
    print(f"Smoke test checks failed: {failed}")
    print("--------------------------------------------------")

    if failed == 0:
        print("\n=== Phase 14 UI Smoke Test PASSED ===")
        return 0
    else:
        print("\n=== Phase 14 UI Smoke Test FAILED ===")
        return 1


if __name__ == "__main__":
    sys.exit(run_ui_smoke_test())
