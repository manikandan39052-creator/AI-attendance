"""
FaceAttend AI Pro - Database Backup & Restore Manager
Manages automated and manual SQLite backups.
"""

import shutil
import os
from datetime import datetime
from pathlib import Path
import config
from core.logger import log_info, log_error

class BackupManager:
    def __init__(self, backups_dir: Path = config.BACKUPS_DIR, db_path: Path = config.DATABASE_PATH):
        self.backups_dir = backups_dir
        self.db_path = db_path
        os.makedirs(self.backups_dir, exist_ok=True)

    def create_backup(self, tag: str = "manual") -> str:
        """Create a timestamped database backup."""
        if not self.db_path.exists():
            log_error("Database file does not exist to back up.")
            return ""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"students_backup_{tag}_{timestamp}.db"
        backup_file = self.backups_dir / backup_filename

        try:
            shutil.copy2(self.db_path, backup_file)
            log_info(f"Database backup created: {backup_filename}")
            return str(backup_file)
        except Exception as e:
            log_error(f"Failed to create backup: {e}")
            return ""

    def list_backups(self) -> list[dict]:
        """List available backups ordered by date."""
        backups = []
        if not self.backups_dir.exists():
            return backups

        for f in self.backups_dir.glob("*.db"):
            stat = f.stat()
            backups.append({
                "filename": f.name,
                "path": str(f),
                "size_kb": round(stat.st_size / 1024, 2),
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            })

        return sorted(backups, key=lambda x: x["modified"], reverse=True)

    def restore_backup(self, backup_filepath: str) -> bool:
        """Restore database from a specific backup file."""
        if not os.path.exists(backup_filepath):
            log_error(f"Backup file not found: {backup_filepath}")
            return False

        try:
            # First create emergency pre-restore snapshot
            self.create_backup(tag="prerestore")
            shutil.copy2(backup_filepath, self.db_path)
            log_info(f"Database successfully restored from {backup_filepath}")
            return True
        except Exception as e:
            log_error(f"Error restoring backup: {e}")
            return False
