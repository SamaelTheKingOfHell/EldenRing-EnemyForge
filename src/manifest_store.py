"""
Manifest store for PhantomForge.
Persists and retrieves injection records to enable clean 1-click uninstallation.
Adheres to [CS-MODULAR] and [CS-GRANULARITY].
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from src.models import PhantomForgeManifest
from src.logger import system_logger


class ManifestStore:
    """Manages reading and writing phantomforge_manifest.json."""

    def __init__(self, manifest_file: Path):
        self.manifest_file = Path(manifest_file).resolve()

    def load(self) -> PhantomForgeManifest:
        if not self.manifest_file.exists():
            return PhantomForgeManifest()

        try:
            with open(self.manifest_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            return PhantomForgeManifest(
                version=data.get("version", "1.0.0"),
                timestamp=data.get("timestamp", ""),
                regulation_backup_file=data.get("regulation_backup_file", ""),
                forged_phantoms=data.get("forged_phantoms", []),
                injected_npc_ids=data.get("injected_npc_ids", []),
                injected_chr_asm_ids=data.get("injected_chr_asm_ids", []),
                injected_face_param_ids=data.get("injected_face_param_ids", []),
                injected_item_lot_ids=data.get("injected_item_lot_ids", [])
            )
        except Exception as ex:
            system_logger.error(f"Failed to read manifest file: {ex}", source="ManifestStore")
            return PhantomForgeManifest()

    def save(
        self,
        backup_file: str,
        phantoms_spec: List[Dict[str, Any]]
    ) -> None:
        """Saves current forging manifest with all injected IDs."""
        npc_ids = [p["npc_param_id"] for p in phantoms_spec]
        chr_asm_ids = [p["chr_asm_id"] for p in phantoms_spec]
        face_ids = [p["face_param_id"] for p in phantoms_spec]
        item_lot_ids = [p["item_lot_id"] for p in phantoms_spec]

        data = {
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "regulation_backup_file": backup_file,
            "forged_phantoms": phantoms_spec,
            "injected_npc_ids": npc_ids,
            "injected_chr_asm_ids": chr_asm_ids,
            "injected_face_param_ids": face_ids,
            "injected_item_lot_ids": item_lot_ids
        }

        with open(self.manifest_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        system_logger.info(f"Saved manifest tracking {len(phantoms_spec)} phantoms to {self.manifest_file.name}", source="ManifestStore")

    def clear(self) -> None:
        """Clears the manifest file."""
        if self.manifest_file.exists():
            self.manifest_file.unlink()
            system_logger.info("Cleared phantomforge_manifest.json.", source="ManifestStore")
