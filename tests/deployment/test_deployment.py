"""
Unit tests for Deployment Readiness, Backup, and Recovery Subsystems.
"""

from pathlib import Path
import pytest

from config.settings import settings
from src.deployment.backup import BackupManager
from src.deployment.readiness import ReadinessChecker
from src.deployment.recovery import RecoveryManager


def test_readiness_checker():
    checker = ReadinessChecker()
    assessment = checker.readiness_check()

    assert "ready" in assessment
    assert "checks" in assessment
    assert assessment["checks"]["vector_store_directory"] is True


def test_backup_and_recovery_flow(tmp_path):
    backup_mgr = BackupManager(backup_dir=tmp_path)
    recovery_mgr = RecoveryManager()

    # 1. Create Backup
    backup_res = backup_mgr.create_backup(custom_destination=tmp_path)
    assert backup_res["status"] == "SUCCESS"
    archive_path = Path(backup_res["destination_path"])
    assert archive_path.exists()

    # 2. Validate Backup Archive
    is_valid, msg = backup_mgr.validate_backup(archive_path)
    assert is_valid is True

    # 3. Invalid backup handling
    invalid_path = tmp_path / "corrupted.zip"
    invalid_path.write_bytes(b"not a zip file")
    is_valid_inv, _ = backup_mgr.validate_backup(invalid_path)
    assert is_valid_inv is False

    with pytest.raises(ValueError, match="Cannot restore backup"):
        recovery_mgr.restore_backup(invalid_path)

    # 4. Restore valid backup
    restore_res = recovery_mgr.restore_backup(archive_path)
    assert restore_res["status"] == "SUCCESS"
