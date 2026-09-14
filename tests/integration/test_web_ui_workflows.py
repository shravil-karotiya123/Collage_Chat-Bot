"""
Integration test suite for Phase 14 Web UI REST API workflows.
"""

import pytest
from fastapi.testclient import TestClient

from config.settings import settings
from src.api.app import app


@pytest.fixture
def client():
    from src.security.request_security import get_security_service
    get_security_service().rate_limiter.reset()
    c = TestClient(app)
    c.headers["Authorization"] = f"Bearer {settings.AUTH_TOKEN}"
    return c


from unittest.mock import patch


@patch("src.models.runtime.ollama_runtime.OllamaRuntime.generate", return_value="MRPL Refinery CDU Unit operates at standard temperature and pressure.")
def test_ui_workflows_e2e(mock_gen, client):
    # 1. Health Telemetry
    res_health = client.get("/workbench/health")
    assert res_health.status_code == 200
    assert res_health.json()["success"] is True

    # 2. Offline Security Posture
    res_sec = client.get("/security/offline")
    assert res_sec.status_code == 200
    assert res_sec.json()["data"]["offline_mode"] is True

    # 3. Document Ingestion & Chunking
    files = {"file": ("test_ui_doc.txt", b"MRPL Crude Distillation Unit (CDU-1) Operating Pressure: 2.4 bar.", "text/plain")}
    res_doc = client.post("/workbench/documents", files=files)
    assert res_doc.status_code == 200
    doc_id = res_doc.json()["data"]["document_id"]

    # 4. Document Indexing
    chunks_payload = [{
        "chunk_id": 0,
        "text": "MRPL Crude Distillation Unit (CDU-1) Operating Pressure: 2.4 bar.",
        "content": "MRPL Crude Distillation Unit (CDU-1) Operating Pressure: 2.4 bar.",
        "start_char": 0,
        "end_char": 64,
        "word_count": 9,
        "page_number": 1
    }]
    res_idx = client.post("/documents/index", json={
        "document_id": doc_id,
        "filename": "test_ui_doc.txt",
        "file_hash": "dummyhash123",
        "chunks": chunks_payload
    })
    assert res_idx.status_code == 200

    # 5. Document List Retrieval
    res_list = client.get("/documents")
    assert res_list.status_code == 200
    assert isinstance(res_list.json()["data"], list)

    # 6. Knowledge Base Query
    res_rag = client.post("/documents/query", json={"query": "CDU-1 pressure", "top_k": 2})
    assert res_rag.status_code == 200

    # 7. Grounded Chat Query
    res_chat = client.post("/workbench/chat", json={"query": "What is CDU-1 pressure?", "force_rag": True})
    assert res_chat.status_code == 200

    # 8. OCR Processing
    import io
    from PIL import Image
    img = Image.new("RGB", (50, 50), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    ocr_files = {"file": ("test_diagram.png", buf.getvalue(), "image/png")}
    res_ocr = client.post("/ocr/process", files=ocr_files)
    assert res_ocr.status_code == 200

    # 9. Agent Task Creation
    res_agent = client.post("/agent/tasks", json={"query": "Draft approval note for refinery expansion"})
    assert res_agent.status_code == 200
    task_id = res_agent.json()["data"]["task_id"]

    # 10. Audit Trajectory Log Retrieval
    res_audit = client.get(f"/agent/tasks/{task_id}/audit")
    assert res_audit.status_code == 200

    # 11. Persistence Backup & Status
    res_pstat = client.get("/operator/persistence/status")
    assert res_pstat.status_code == 200
