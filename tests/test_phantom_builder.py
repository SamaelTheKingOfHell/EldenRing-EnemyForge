"""
Unit tests for PhantomForge PhantomBuilder.
Verifies phantom enemy spec generation and carried loot drop tables.
Adheres to [CS-NO-MOCK] and [CS-GRANULARITY].
"""

import unittest
from pathlib import Path
from src.preset_loader import PresetLoader
from src.world_placer import WorldPlacer
from src.phantom_builder import PhantomBuilder
from src.id_allocator import IdAllocator
from src.models import PhantomForgeConfig, PlacementMode


class TestPhantomBuilder(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.loader = PresetLoader(
            data_presets_dir=self.base_dir / "data" / "presets",
            input_presets_dir=self.base_dir / "input_presets"
        )
        self.placer = WorldPlacer(self.base_dir / "data" / "world_encounters.json")
        self.allocator = IdAllocator()
        self.builder = PhantomBuilder(self.allocator)
        self.config = PhantomForgeConfig(
            guaranteed_carried_loot=True,
            global_drop_chance_percent=100.0,
            enable_invasion_aura=True,
            scale_attributes_by_tier=True
        )

    def test_carried_loot_drops_generation(self):
        presets = self.loader.discover_and_load()
        assignments = self.placer.assign_encounters(presets, mode=PlacementMode.THEMATIC_REGIONAL)

        patch_spec = self.builder.build_patch_spec(assignments, self.config)
        self.assertEqual(patch_spec["total_phantoms"], len(presets))

        for phantom in patch_spec["phantoms"]:
            # Every phantom must have valid assigned IDs
            self.assertGreaterEqual(phantom["npc_param_id"], 9500000)
            self.assertGreaterEqual(phantom["chr_asm_id"], 9510000)
            self.assertGreaterEqual(phantom["item_lot_id"], 9530000)

            # CARRIED LOOT INVARIANT:
            # They must drop the loot that they carry!
            carried_drops = phantom["carried_drops"]
            self.assertGreaterEqual(len(carried_drops), 1, f"Phantom '{phantom['name']}' must have carried drops")

            # Check that probability is 1000 (100% guaranteed)
            for drop in carried_drops:
                self.assertGreater(drop["item_id"], 0)
                self.assertEqual(drop["probability"], 1000, "Must drop with 100% guaranteed chance")
                self.assertEqual(drop["quantity"], 1)

    def test_custom_drop_chance_scaling(self):
        presets = self.loader.discover_and_load()[:1]
        assignments = self.placer.assign_encounters(presets)

        scaled_config = PhantomForgeConfig(
            guaranteed_carried_loot=False,
            global_drop_chance_percent=50.0
        )
        spec = self.builder.build_patch_spec(assignments, scaled_config)
        first_phantom = spec["phantoms"][0]

        for drop in first_phantom["carried_drops"]:
            self.assertEqual(drop["probability"], 500, "50% drop chance must map to 500 points")


if __name__ == "__main__":
    unittest.main()
