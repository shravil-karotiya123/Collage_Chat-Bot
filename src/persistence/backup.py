"""
Local Database Backup and Archive Manager.
Creates atomic, local SQLite snapshot backups in data/backups/.
"""

from datetime import datetime, timezone
import logging
from pathlib import Path

from typing import Any, Dict, Optional

from config.settings import BASE_DIR, settings
from src.persistence.database import DatabaseManager, get_db_manager
from src.persistence.exceptions import BackupFailedError

logger = logging.getLogger("MRPL.Persistence.Backup")


class PersistenceBackupManager:
    """
    Manages local SQLite database snapshot backup creation.
    """

    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None,
        backup_dir: Optional[Path] = None,
    ) -> None:
        self.db_manager = db_manager or get_db_manager()
        self.backup_dir = Path(backup_dir or (BASE_DIR / "data" / "backups")).resolve()
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_database_backup(self, custom_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a consistent SQLite online snapshot backup file.
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = custom_name or f"mrpl_workbench_backup_{timestamp}.db"
        dest_path = self.backup_dir / filename

        source_conn = self.db_manager.get_raw_connection()

        try:
            import sqlite3
            dest_conn = sqlite3.connect(str(dest_path))
            with dest_conn:
                source_conn.backup(dest_conn)
            dest_conn.close()

            file_size_mb = round(dest_path.stat().st_size / (1024 * 1024), 2)
            logger.info(f"Created SQLite persistence snapshot backup at: {dest_path} ({file_size_mb} MB)")

            return {
                "status": "SUCCESS",
                "filename": filename,
                "backup_path": str(dest_path),
                "file_size_mb": file_size_mb,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:
            logger.error(f"Failed to create database backup: {exc}", exc_info=True)
            raise BackupFailedError(f"Database backup failed: {exc}") from exc
