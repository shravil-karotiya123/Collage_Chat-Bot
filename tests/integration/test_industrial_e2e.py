"""
Phase 14 End-to-End Integration Test Suite.
Validates complete industrial workflow: Scanned report -> OCR -> RAG -> Planning -> Approval -> DOCX deliverable.
"""

from pathlib import Path
import pytest
from src.services.workbench_service import WorkbenchService
from src.artifacts.manager import artifact_manager
from src.artifacts.models import ArtifactType


def test_phase14_end_to_end_inspection_to_docx():
    service = WorkbenchService()
    sample_text = Path("examples/data/inspection_report.txt").read_bytes()

    res = service.run_inspection_demo(
        content_bytes=sample_text,
        filename="inspection_report.txt",
        auto_index=True,
        generate_approval_note=True,
    )

    # 1. Workflow status
    assert res["success"] is True
    assert res["workflow"] == "inspection_to_approval_note"
    assert res["status"] == "COMPLETED"
    assert res["selected_model"] == "qwen2.5:7b"

    # 2. Findings & Sources
    assert len(res["findings"]) > 0
    assert res["approval_status"] == "APPROVED"

    # 3. Deliverable artifact
    art = res["artifact"]
    assert art is not None
    assert art["type"] == "docx"
    assert Path(art["filepath"]).exists()


def test_phase14_end_to_end_coding_sandbox():
    service = WorkbenchService()
    res = service.run_coding_demo(prompt="Write email validator")

    assert res["success"] is True
    assert res["workflow"] == "secure_coding_sandbox"
    assert res["selected_model"] == "deepseek-coder:6.7b"
    assert res["tests_passed"] == 3
    assert res["artifact"]["type"] == "code"
    assert Path(res["artifact"]["filepath"]).exists()


def test_phase14_end_to_end_multimodal_vision():
    service = WorkbenchService()
    res = service.run_vision_demo(prompt="Analyze engineering schematic")

    assert res["success"] is True
    assert res["workflow"] == "multimodal_vision_inspection"
    assert res["selected_model"] == "minicpm-v:8b"
    assert len(res["visual_observations"]) > 0
