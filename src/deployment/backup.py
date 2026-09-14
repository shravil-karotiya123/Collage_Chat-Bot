"""
Local System Backup Manager.
"""

import json
import os
import shutil
import time
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from config.settings import settings


class BackupManager:
    """
    Manages local offline backups of vector database indexes and configuration metadata.
    Excludes raw secrets, passwords, and temporary files.
    """

    def __init__(self, backup_dir: Optional[Path] = None) -> None:
        self.backup_dir = backup_dir or settings.BACKUP_PATH
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, custom_destination: Optional[Path] = None) -> Dict[str, Any]:
        """
        Create a zip backup archive containing vector store and system metadata.
        """
        timestamp_str = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        backup_id = f"backup_{timestamp_str}"
        target_dir = custom_destination or self.backup_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        zip_path = target_dir / f"{backup_id}.zip"

        components = []

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # 1. Archive Vector Store index if present
            if settings.VECTOR_STORE_PATH.exists():
                for root, _, files in os.walk(settings.VECTOR_STORE_PATH):
                    for file in files:
                        full_p = Path(root) / file
                        rel_p = Path("vector_store") / full_p.relative_to(settings.VECTOR_STORE_PATH)
                        zipf.write(full_p, rel_p)
                components.append("vector_store")

            # 2. Archive System Metadata manifest (excluding secrets)
            meta = {
                "backup_id": backup_id,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "version": settings.WORKBENCH_VERSION,
                "environment": settings.ENVIRONMENT,
                "components": components,
            }
            zipf.writestr("manifest.json", json.dumps(meta, indent=2))

        size_bytes = zip_path.stat().st_size

        return {
            "backup_id": backup_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "destination_path": str(zip_path.resolve()),
            "size_bytes": size_bytes,
            "components_included": components,
            "status": "SUCCESS",
        }

    def validate_backup(self, archive_path: Path) -> Tuple[bool, str]:
        """Verify backup archive structure and manifest integrity."""
        if not archive_path.exists() or not zipfile.is_zipfile(archive_path):
            return False, "Invalid or non-existent zip archive file."

        try:
            with zipfile.ZipFile(archive_path, "r") as zipf:
                files = zipf.namelist()
                if "manifest.json" not in files:
                    return False, "Missing manifest.json inside backup archive."
                manifest_data = json.loads(zipf.read("manifest.json").decode("utf-8"))
                if "backup_id" not in manifest_data:
                    return False, "Invalid manifest structure."
            return True, "Backup archive is valid."
        except Exception as exc:
            return False, f"Backup validation error: {str(exc)}"
