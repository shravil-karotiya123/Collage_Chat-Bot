"""
Unit tests for POST /documents/upload REST API endpoint.
"""

from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)


def test_upload_txt_document() -> None:
    file_payload = ("report.txt", b"Refinery inspection log and telemetry data.", "text/plain")
    response = client.post(
        "/documents/upload",
        files={"file": file_payload},
        data={"chunk_size": "500", "chunk_overlap": "50"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    data = payload["data"]
    assert data["status"] == "SUCCESS"
    assert data["metadata"]["file_name"] == "report.txt"
    assert data["metadata"]["file_extension"] == ".txt"
    assert data["metadata"]["total_chunks"] == 1
    assert len(data["chunks"]) == 1
    assert "Refinery inspection" in data["chunks"][0]["content"]


def test_upload_csv_document() -> None:
    csv_bytes = b"ID,Unit,Status\n1,CDU-1,Active\n2,VDU-2,Maintenance"
    file_payload = ("units.csv", csv_bytes, "text/csv")
    response = client.post(
        "/documents/upload",
        files={"file": file_payload},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    data = payload["data"]
    assert data["metadata"]["file_extension"] == ".csv"
    assert "CDU-1" in data["chunks"][0]["content"]


def test_upload_invalid_extension() -> None:
    file_payload = ("malicious.exe", b"binary data", "application/octet-stream")
    response = client.post(
        "/documents/upload",
        files={"file": file_payload},
    )
    assert response.status_code == 400
    payload = response.json()
    assert payload["success"] is False
    assert "Unsupported file format" in payload["error"]["detail"]
