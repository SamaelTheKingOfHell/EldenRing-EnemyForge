"""
Unit tests for PhantomForge WorldPlacer.
Verifies encounter distribution modes.
Adheres to [CS-NO-MOCK] and [CS-GRANULARITY].
"""

import unittest
from pathlib import Path
from src.preset_loader import PresetLoader
from src.world_placer import WorldPlacer
from src.models import PlacementMode


class TestWorldPlacer(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.loader = PresetLoader(
            data_presets_dir=self.base_dir / "data" / "presets",
            input_presets_dir=self.base_dir / "input_presets"
        )
        self.placer = WorldPlacer(self.base_dir / "data" / "world_encounters.json")

    def test_thematic_regional_assignment(self):
        presets = self.loader.discover_and_load()
        assignments = self.placer.assign_encounters(presets, mode=PlacementMode.THEMATIC_REGIONAL)

        self.assertEqual(len(assignments), len(presets))

        for preset, encounter in assignments:
            self.assertIsNotNone(encounter.encounter_id)
            self.assertIsNotNone(encounter.region)
            self.assertGreater(len(encounter.landmark), 0)

    def test_chaos_expedition_randomization(self):
        presets = self.loader.discover_and_load()
        assignments1 = self.placer.assign_encounters(presets, mode=PlacementMode.CHAOS_EXPEDITION, seed=42)
        assignments2 = self.placer.assign_encounters(presets, mode=PlacementMode.CHAOS_EXPEDITION, seed=999)

        encs1 = [e.encounter_id for _, e in assignments1]
        encs2 = [e.encounter_id for _, e in assignments2]

        self.assertEqual(len(encs1), len(presets))
        self.assertEqual(len(encs2), len(presets))


if __name__ == "__main__":
    unittest.main()
