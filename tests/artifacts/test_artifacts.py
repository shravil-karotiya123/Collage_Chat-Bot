"""
Unit tests for Artifact Generation Subsystem.
"""

from pathlib import Path
import pytest
from src.artifacts.manager import ArtifactManager, artifact_manager
from src.artifacts.models import ArtifactType


def test_artifact_manager_creation(tmp_path: Path):
    manager = ArtifactManager(output_dir=tmp_path)
    
    # 1. Test DOCX Creation
    docx_meta = manager.create_docx_approval_note(
        task_id="task-test-001",
        title="TEST APPROVAL NOTE",
        reference_number="MRPL-AI-DEMO-001",
        findings=["Finding 1", "Finding 2"],
    )
    assert docx_meta.artifact_type == ArtifactType.DOCX
    assert docx_meta.task_id == "task-test-001"
    assert Path(docx_meta.filepath).exists()

    # 2. Test XLSX Creation
    xlsx_meta = manager.create_xlsx_deliverable(
        task_id="task-test-001",
        title="TEST TABULAR DELIVERABLE",
    )
    assert xlsx_meta.artifact_type == ArtifactType.XLSX
    assert Path(xlsx_meta.filepath).exists()

    # 3. Test PPTX Creation
    pptx_meta = manager.create_pptx_summary(
        task_id="task-test-001",
        title="TEST PRESENTATION",
    )
    assert pptx_meta.artifact_type == ArtifactType.PPTX
    assert Path(pptx_meta.filepath).exists()

    # 4. Test CODE Creation
    code_meta = manager.create_code_deliverable(
        task_id="task-test-001",
        code_content="def test_func(): return True\n",
        language="python",
    )
    assert code_meta.artifact_type == ArtifactType.CODE
    assert Path(code_meta.filepath).exists()

    # 5. Test Retrieval
    task_artifacts = manager.list_artifacts_for_task("task-test-001")
    assert len(task_artifacts) == 4
