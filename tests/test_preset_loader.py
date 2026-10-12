"""
Unit tests for PhantomForge PresetLoader.
Adheres to [CS-NO-MOCK] and [CS-GRANULARITY].
"""

import unittest
from pathlib import Path
from src.preset_loader import PresetLoader


class TestPresetLoader(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.loader = PresetLoader(
            data_presets_dir=self.base_dir / "data" / "presets",
            input_presets_dir=self.base_dir / "input_presets"
        )

    def test_discover_builtin_presets(self):
        presets = self.loader.discover_and_load()
        self.assertGreaterEqual(len(presets), 8, "Must discover at least 8 built-in templates")

        preset_ids = [p.preset_id for p in presets]
        self.assertIn("eleanor_bloody_finger", preset_ids)
        self.assertIn("severus_crucible_knight", preset_ids)
        self.assertIn("sellen_carian_spellblade", preset_ids)
        self.assertIn("gorgon_bullgoat_juggernaut", preset_ids)

    def test_carried_equipment_extraction(self):
        presets = self.loader.discover_and_load()
        eleanor = next(p for p in presets if p.preset_id == "eleanor_bloody_finger")

        carried_items = eleanor.equipment.get_all_carried_items()
        self.assertGreaterEqual(len(carried_items), 5, "Eleanor must carry full armor set and weapons")

        slots = [item["slot"] for item in carried_items]
        self.assertIn("head", slots)
        self.assertIn("body", slots)
        self.assertIn("arms", slots)
        self.assertIn("legs", slots)
        self.assertIn("right_weapon_1", slots)

        # Rivers of Blood ID check
        rob = next(item for item in carried_items if item["slot"] == "right_weapon_1")
        self.assertEqual(rob["item_id"], 3220000)


if __name__ == "__main__":
    unittest.main()
