"""
Unit tests for PersistenceBackupManager.
"""

from pathlib import Path
from src.persistence.backup import PersistenceBackupManager
from src.persistence.database import DatabaseManager


def test_persistence_backup_manager(tmp_path):
    db_mgr = DatabaseManager(db_path=tmp_path / "main.db")
    backup_dir = tmp_path / "backups"

    backup_mgr = PersistenceBackupManager(db_manager=db_mgr, backup_dir=backup_dir)
    res = backup_mgr.create_database_backup(custom_name="test_snap.db")

    assert res["status"] == "SUCCESS"
    assert Path(res["backup_path"]).exists()
    assert res["filename"] == "test_snap.db"
