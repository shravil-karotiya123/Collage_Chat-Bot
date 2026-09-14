"""
System Restoration & Recovery Manager.
"""

import json
import zipfile
from pathlib import Path
from typing import Any, Dict

from config.settings import settings, BASE_DIR
from src.deployment.backup import BackupManager


class RecoveryManager:
    """
    Handles safe system state restoration from verified backup archives.
    Does not overwrite existing settings or secrets blindly.
    """

    def __init__(self) -> None:
        self.backup_mgr = BackupManager()

    def restore_backup(self, archive_path: Path) -> Dict[str, Any]:
        """
        Restore system state from verified backup archive.
        """
        valid, msg = self.backup_mgr.validate_backup(archive_path)
        if not valid:
            raise ValueError(f"Cannot restore backup: {msg}")

        restored_components = []

        with zipfile.ZipFile(archive_path, "r") as zipf:
            manifest_data = json.loads(zipf.read("manifest.json").decode("utf-8"))
            backup_id = manifest_data.get("backup_id", "unknown")

            # Extract vector store if included
            for member in zipf.namelist():
                if member.startswith("vector_store/"):
                    zipf.extract(member, BASE_DIR)
                    if "vector_store" not in restored_components:
                        restored_components.append("vector_store")

        return {
            "backup_id": backup_id,
            "timestamp": manifest_data.get("timestamp", ""),
            "status": "SUCCESS",
            "components_restored": restored_components,
            "details": f"System state restored successfully from '{archive_path.name}'.",
        }
