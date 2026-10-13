"""
Manifest store for PhantomForge.
Persists and retrieves injection records to enable clean 1-click uninstallation.
Adheres to [CS-MODULAR] and [CS-GRANULARITY].
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from src.models import EnemyForgeManifest, PhantomForgeManifest
from src.logger import system_logger


class ManifestStore:
    """Manages reading and writing enemyforge_manifest.json."""

    def __init__(self, manifest_file: Path):
        self.manifest_file = Path(manifest_file).resolve()
        # Fallback to legacy phantomforge_manifest.json if target doesn't exist
        self.legacy_file = self.manifest_file.parent / "phantomforge_manifest.json"

    def load(self) -> EnemyForgeManifest:
        target = self.manifest_file if self.manifest_file.exists() else self.legacy_file
        if not target.exists():
            return EnemyForgeManifest()

        try:
            with open(target, "r", encoding="utf-8") as f:
                data = json.load(f)

            enemies = data.get("forged_enemies") or data.get("forged_phantoms", [])
            return EnemyForgeManifest(
                version=data.get("version", "1.0.0"),
                timestamp=data.get("timestamp", ""),
                regulation_backup_file=data.get("regulation_backup_file", ""),
                forged_enemies=enemies,
                injected_npc_ids=data.get("injected_npc_ids", []),
                injected_chr_asm_ids=data.get("injected_chr_asm_ids", []),
                injected_face_param_ids=data.get("injected_face_param_ids", []),
                injected_item_lot_ids=data.get("injected_item_lot_ids", [])
            )
        except Exception as ex:
            system_logger.error(f"Failed to read manifest file: {ex}", source="ManifestStore")
            return EnemyForgeManifest()

    def save(
        self,
        backup_file: str,
        enemies_spec: List[Dict[str, Any]]
    ) -> None:
        """Saves current forging manifest with all injected IDs."""
        npc_ids = [p["npc_param_id"] for p in enemies_spec]
        chr_asm_ids = [p["chr_asm_id"] for p in enemies_spec]
        face_ids = [p["face_param_id"] for p in enemies_spec]
        item_lot_ids = [p["item_lot_id"] for p in enemies_spec]

        data = {
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "regulation_backup_file": backup_file,
            "forged_enemies": enemies_spec,
            "forged_phantoms": enemies_spec,  # backward compatibility
            "injected_npc_ids": npc_ids,
            "injected_chr_asm_ids": chr_asm_ids,
            "injected_face_param_ids": face_ids,
            "injected_item_lot_ids": item_lot_ids
        }

        with open(self.manifest_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        system_logger.info(f"Saved manifest tracking {len(enemies_spec)} enemies to {self.manifest_file.name}", source="ManifestStore")

    def clear(self) -> None:
        """Clears the manifest file."""
        if self.manifest_file.exists():
            self.manifest_file.unlink()
        if self.legacy_file.exists():
            self.legacy_file.unlink()
        system_logger.info("Cleared manifest store.", source="ManifestStore")
