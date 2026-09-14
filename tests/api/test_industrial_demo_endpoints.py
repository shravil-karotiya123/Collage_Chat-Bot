"""
API Unit and Integration Tests for Phase 14 Demonstration & Telemetry Endpoints.
"""

from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)


def test_phase14_demo_inspection_endpoint():
    response = client.post("/workbench/demo/inspection")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    data = json_data["data"]
    assert data["workflow"] == "inspection_to_approval_note"
    assert data["status"] == "COMPLETED"
    assert data["selected_model"] == "qwen2.5:7b"
    assert data["artifact"] is not None
    assert data["artifact"]["type"] == "docx"


def test_phase14_demo_coding_endpoint():
    response = client.post("/workbench/demo/coding")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    data = json_data["data"]
    assert data["workflow"] == "secure_coding_sandbox"
    assert data["selected_model"] == "deepseek-coder:6.7b"
    assert data["tests_passed"] > 0
    assert data["artifact"] is not None
    assert data["artifact"]["type"] == "code"


def test_phase14_demo_vision_endpoint():
    response = client.post("/workbench/demo/vision")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    data = json_data["data"]
    assert data["workflow"] == "multimodal_vision_inspection"
    assert data["selected_model"] == "minicpm-v:8b"


def test_phase14_performance_endpoint():
    response = client.get("/workbench/performance")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    data = json_data["data"]
    assert "benchmarks" in data


def test_phase14_security_posture_endpoint():
    response = client.get("/workbench/security/posture")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    data = json_data["data"]
    assert data["network_sovereignty"] == "LOCAL_ONLY_ENFORCED"
