"""
Backup and snapshot manager for PhantomForge.
Guarantees safe rollbacks with SHA-256 verification.
Adheres to [CS-MODULAR] and [CS-GRANULARITY].
"""

import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from src.logger import system_logger


class BackupManager:
    """Manages timestamped regulation.bin snapshots and rollbacks."""

    def __init__(self, backups_dir: Path):
        self.backups_dir = Path(backups_dir).resolve()
        self.backups_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def calculate_sha256(file_path: Path) -> str:
        """Computes SHA-256 hash of a file for integrity verification."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(65536), b""):
                sha256.update(block)
        return sha256.hexdigest()

    def create_snapshot(self, target_reg: Path) -> Optional[Path]:
        """Creates a timestamped pre-write backup of target regulation.bin."""
        target_path = Path(target_reg).resolve()
        if not target_path.exists():
            system_logger.warning(f"Cannot snapshot non-existent regulation: {target_path}", source="BackupManager")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"regulation.bin.bak_{timestamp}"
        backup_path = self.backups_dir / backup_filename

        shutil.copy2(target_path, backup_path)
        checksum = self.calculate_sha256(backup_path)

        system_logger.info(
            f"Created safety backup: {backup_filename} (SHA-256: {checksum[:12]}...)",
            source="BackupManager"
        )
        return backup_path

    def get_latest_backup(self) -> Optional[Path]:
        """Returns the most recent backup in the backups directory."""
        backups = sorted(self.backups_dir.glob("regulation.bin.bak_*"), key=lambda p: p.stat().st_mtime, reverse=True)
        return backups[0] if backups else None

    def list_backups(self) -> List[Path]:
        """Returns all available backups sorted from newest to oldest."""
        return sorted(self.backups_dir.glob("regulation.bin.bak_*"), key=lambda p: p.stat().st_mtime, reverse=True)

    def restore_backup(self, target_reg: Path, backup_path: Optional[Path] = None) -> bool:
        """Restores a backup over target regulation.bin."""
        target = Path(target_reg).resolve()
        src = backup_path or self.get_latest_backup()

        if not src or not src.exists():
            system_logger.error("No backup found to restore.", source="BackupManager")
            return False

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        system_logger.info(f"Successfully restored regulation from '{src.name}' -> '{target}'", source="BackupManager")
        return True
