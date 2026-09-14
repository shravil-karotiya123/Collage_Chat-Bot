"""
MRPL AI Workbench — Environment Setup Script
Initializes sovereign processing directory structure and sets up SQLite WAL mode.
"""

import os
import sqlite3
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

TARGET_DATA_DIRS = [
    BASE_DIR / "data" / "documents",
    BASE_DIR / "data" / "workspaces",
    BASE_DIR / "data" / "chroma",
    BASE_DIR / "data" / "sqlite",
    BASE_DIR / "data" / "duckdb",
    BASE_DIR / "data" / "audit",
]


def setup_directories() -> None:
    """Create all required data directories."""
    print("[1/2] Initializing sovereign processing directories...")
    for d in TARGET_DATA_DIRS:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  [OK] Verified: {d.relative_to(BASE_DIR)}")


def setup_sqlite_wal() -> None:
    """Configure SQLite database in WAL mode."""
    print("[2/2] Configuring SQLite WAL mode...")
    db_path = BASE_DIR / "data" / "sqlite" / "mrpl_workbench.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        mode = cursor.fetchone()[0]
        conn.close()
        print(f"  [OK] SQLite database configured ({db_path.relative_to(BASE_DIR)}): journal_mode={mode.upper()}")
    except Exception as exc:
        print(f"  [WARN] SQLite WAL setup warning: {exc}")


def main() -> None:
    print("=" * 60)
    print("MRPL AI Workbench Environment Setup")
    print("=" * 60)
    setup_directories()
    setup_sqlite_wal()
    print("=" * 60)
    print("Environment setup completed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()
