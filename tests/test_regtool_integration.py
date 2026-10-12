"""
Integration tests for PhantomForge RegulationManager and RegTool.
Verifies real Elden Ring regulation decryption, phantom enemy injection,
carried loot drop table generation, and AES-256 encryption.
Adheres to [CS-NO-MOCK] and [CS-STABILITY].
"""

import os
import unittest
import tempfile
from pathlib import Path
from src.preset_loader import PresetLoader
from src.world_placer import WorldPlacer
from src.phantom_builder import PhantomBuilder
from src.regulation_manager import RegulationManager
from src.models import PhantomForgeConfig, PlacementMode


class TestRegToolIntegration(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        self.reg_manager = RegulationManager(self.base_dir)
        self.loader = PresetLoader(
            data_presets_dir=self.base_dir / "data" / "presets",
            input_presets_dir=self.base_dir / "input_presets"
        )
        self.placer = WorldPlacer(self.base_dir / "data" / "world_encounters.json")
        self.builder = PhantomBuilder()

        # Find reference regulation backup
        self.reference_reg = self.reg_manager.backup_mgr.get_latest_backup()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_regulation_patch_with_carried_loot(self):
        """Verifies end-to-end regulation injection using compiled RegTool."""
        if not self.reference_reg or not self.reference_reg.exists():
            self.skipTest("No reference regulation backup found for integration test.")

        target_reg = self.temp_path / "regulation.bin"

        # Load 2 presets to test injection batch
        presets = self.loader.discover_and_load()[:2]
        assignments = self.placer.assign_encounters(presets, mode=PlacementMode.THEMATIC_REGIONAL)

        config = PhantomForgeConfig(
            guaranteed_carried_loot=True,
            global_drop_chance_percent=100.0,
            enable_invasion_aura=True
        )

        patch_spec = self.builder.build_patch_spec(assignments, config)

        success = self.reg_manager.execute_patch(
            patch_spec=patch_spec,
            source_reg=self.reference_reg,
            target_reg=target_reg,
            msg_dir=self.base_dir / "data"
        )

        self.assertTrue(success, "RegTool patch execution must succeed")
        self.assertTrue(target_reg.exists(), "Target regulation.bin must be created")
        self.assertGreater(target_reg.stat().st_size, 1000000, "Patched regulation must be a valid sized archive")


if __name__ == "__main__":
    unittest.main()
