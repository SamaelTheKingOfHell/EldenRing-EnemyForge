"""
Cross-Game Prototype Orchestrator for EnemyForge.
Automates the legal extraction of Crossbreed Priscilla from local Dark Souls PTDE,
synthesizes her combat parameters and carried loot drops, and injects her as an active
world encounter stationed right outside the Stranded Graveyard opening tutorial cave.
Adheres to [CS-MODULAR], [CS-DECOUPLE], [CS-SAFETY], and [CS-NO-MOCK].
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from src.cross_game.ds1_extractor import DS1Extractor
from src.cross_game.priscilla_builder import create_priscilla_preset, create_priscilla_encounter, build_priscilla_loot_spec
from src.models import EnemyForgeConfig, PlacementMode
from src.enemy_builder import EnemyBuilder
from src.regulation_manager import RegulationManager
from src.logger import system_logger


class PrototypeOrchestrator:
    """Orchestrates end-to-end automation for porting Crossbreed Priscilla into Elden Ring."""

    def __init__(self, workspace_root: Optional[Path] = None, ds1_data_dir: Optional[Path] = None):
        self.workspace_root = Path(workspace_root or Path(__file__).resolve().parent.parent.parent)
        self.extracted_cache_dir = self.workspace_root / "data" / "extracted_assets" / "ds1" / "c2730"
        self.encounters_file = self.workspace_root / "data" / "world_encounters.json"
        self.extractor = DS1Extractor(data_dir=Path(ds1_data_dir) if ds1_data_dir else None)
        self.reg_manager = RegulationManager(self.workspace_root)
        self.builder = EnemyBuilder()

    def run_priscilla_prototype(
        self,
        target_regulation: Optional[Path] = None,
        custom_encounter: Optional[Any] = None,
        extract_only: bool = False
    ) -> Dict[str, Any]:

        """
        Executes the prototype automation:
        1. Verifies local DS1 installation.
        2. Extracts Priscilla assets into local cache.
        3. Registers the Cave Threshold world encounter.
        4. Synthesizes regulation patch spec with 100% carried drops.
        5. Injects into regulation.bin via RegTool.
        """
        system_logger.info("Starting Crossbreed Priscilla Automation Prototype Pipeline...", source="PrototypeOrchestrator")

        # 1. Verification of Legal Installation
        if not self.extractor.is_installed():
            raise RuntimeError(
                "Dark Souls: Prepare to Die Edition not detected on this machine. "
                "To prevent copyright infringement, EnemyForge requires a legal local installation to extract assets."
            )
        system_logger.info(f"Verified DS1 PTDE at: {self.extractor.data_dir}", source="PrototypeOrchestrator")

        # 2. Extract Priscilla's Assets
        extracted_files = self.extractor.extract_priscilla_assets(self.extracted_cache_dir)
        if extract_only:
            return {
                "status": "extracted_only",
                "prototype": "Crossbreed Priscilla Assets (Dark Souls 1 PTDE)",
                "source_game_path": str(self.extractor.data_dir),
                "extracted_assets_count": len(extracted_files),
                "extracted_assets_dir": str(self.extracted_cache_dir),
                "files": {k: str(v) for k, v in extracted_files.items()},
                "message": f"Successfully extracted {len(extracted_files)} files to {self.extracted_cache_dir}."
            }

        # 3. Build Preset and Encounter
        preset = create_priscilla_preset()
        encounter = custom_encounter or create_priscilla_encounter()

        # 4. Register Encounter in world_encounters.json if missing
        self._ensure_encounter_registered(encounter)

        # 5. Build Patch Specification
        config = EnemyForgeConfig(
            guaranteed_carried_loot=True,
            scale_attributes_by_tier=False,
            enable_invasion_aura=False,
            placement_mode=PlacementMode.THEMATIC_REGIONAL
        )
        spec = self.builder.build_patch_spec([(preset, encounter)], config)

        # 6. Apply to Regulation & MSB Map
        target_reg = Path(target_regulation).resolve() if target_regulation else (self.workspace_root / "mod" / "regulation.bin").resolve()
        source_reg = target_reg if target_reg.exists() else self.reg_manager.resolve_source_regulation()
        success = self.reg_manager.execute_patch(
            patch_spec=spec,
            source_reg=source_reg,
            target_reg=target_reg,
            msg_dir=self.workspace_root / "data"
        )
        if not success:
            raise RuntimeError("Regulation injection failed via RegTool.")

        # 7. Deploy Assets into Active Mod Profile (chr/ and parts/ directories)
        deployed_assets = self._deploy_assets(target_reg.parent, extracted_files)

        result_manifest = {
            "status": "success",

            "prototype": "Crossbreed Priscilla (Dark Souls 1 PTDE -> Elden Ring)",
            "source_game_path": str(self.extractor.data_dir),
            "extracted_assets_count": len(extracted_files),
            "extracted_assets_dir": str(self.extracted_cache_dir),
            "encounter": {
                "encounter_id": encounter.encounter_id,
                "name": encounter.name,
                "map_id": encounter.map_id,
                "coordinates": encounter.coordinates,
                "landmark": encounter.landmark
            },
            "npc_param_id": spec["enemies"][0]["npc_param_id"],
            "base_enemy_id": encounter.base_enemy_id,
            "carried_drops": build_priscilla_loot_spec(),
            "target_regulation": str(target_reg),
            "deployed_assets_count": len(deployed_assets),
            "deployed_assets": deployed_assets,
            "message": f"Successfully injected Crossbreed Priscilla into {target_reg} and map {encounter.map_id} at {encounter.name}!"
        }

        system_logger.info(
            f"Successfully injected Crossbreed Priscilla into Elden Ring at {encounter.name}!",
            source="PrototypeOrchestrator"
        )
        return result_manifest

    def _deploy_assets(self, mod_dir: Path, extracted_files: Dict[str, Path]) -> Dict[str, str]:
        """Deploys extracted character and equipment assets into active mod profile."""
        import shutil
        deployed: Dict[str, str] = {}
        chr_dir = mod_dir / "chr"
        parts_dir = mod_dir / "parts"
        chr_dir.mkdir(parents=True, exist_ok=True)
        parts_dir.mkdir(parents=True, exist_ok=True)

        for key, src_file in extracted_files.items():
            src = Path(src_file)
            if not src.exists():
                continue
            if "parts" in src.name.lower() or "wp_" in src.name.lower():
                dst = parts_dir / src.name
            else:
                dst = chr_dir / src.name
            try:
                shutil.copy2(src, dst)
                deployed[src.name] = str(dst)
                system_logger.info(f"Deployed asset {src.name} -> {dst}", source="PrototypeOrchestrator")
            except Exception as e:
                system_logger.warning(f"Could not deploy asset {src.name}: {e}", source="PrototypeOrchestrator")

        return deployed

    def _ensure_encounter_registered(self, encounter) -> None:
        """Persists the cave exit encounter in world_encounters.json if not present."""
        if not self.encounters_file.exists():
            return

        with open(self.encounters_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        limgrave = data.get("regions", {}).get("Limgrave", {})
        encounters = limgrave.get("encounters", [])

        if not any(e.get("encounter_id") == encounter.encounter_id for e in encounters):
            encounters.insert(0, {
                "encounter_id": encounter.encounter_id,
                "name": encounter.name,
                "landmark": encounter.landmark,
                "coordinates": encounter.coordinates,
                "map_id": encounter.map_id,
                "base_enemy_id": encounter.base_enemy_id,
                "description": encounter.description
            })
            limgrave["encounters"] = encounters
            data["regions"]["Limgrave"] = limgrave

            with open(self.encounters_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            system_logger.info(f"Registered {encounter.encounter_id} in world_encounters.json", source="PrototypeOrchestrator")
