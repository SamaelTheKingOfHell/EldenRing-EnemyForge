"""
Unit tests for EnemyForge NPCGenerator and expanded world encounters.
Adheres to [CS-NO-MOCK] and [CS-GRANULARITY].
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from src.npc_generator import NPCGenerator
from src.world_placer import WorldPlacer


class TestNPCGenerator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ef_npc_gen_test_"))
        self.generator = NPCGenerator(output_presets_dir=self.temp_dir)
        self.base_dir = Path(__file__).resolve().parent.parent

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_thematic_presets(self):
        presets = self.generator.generate_thematic_presets(count=6)
        self.assertEqual(len(presets), 6, "Must generate exactly 6 thematic presets")

        for p in presets:
            self.assertTrue(p.name, "Generated NPC must have a name")
            self.assertTrue(p.title, "Generated NPC must have a title")
            self.assertGreater(p.level, 0, "Level must be greater than 0")
            self.assertEqual(p.drop_probability_percent, 100.0, "Carried loot must have 100% drop rate")
            self.assertTrue(p.guaranteed_loot)

            # Check that files were persisted to output directory
            saved_file = self.temp_dir / f"{p.preset_id}.json"
            self.assertTrue(saved_file.exists(), f"Preset file {saved_file} must exist on disk")

    def test_generate_from_gear_catalog_with_modded_sets(self):
        # Simulated gear catalog from a modded regulation.bin (e.g. injected by LootForge)
        sample_catalog = {
            "regulation_path": "mod/regulation.bin",
            "modded_protectors_count": 4,
            "modded_weapons_count": 1,
            "modded_protectors": [
                {"id": 9000000, "name": "Abyssal Knight Helm", "category": 0},
                {"id": 9000100, "name": "Abyssal Knight Armor", "category": 1},
                {"id": 9000200, "name": "Abyssal Knight Gauntlets", "category": 2},
                {"id": 9000300, "name": "Abyssal Knight Greaves", "category": 3}
            ],
            "modded_weapons": [
                {"id": 9000400, "name": "Abyssal Greatsword", "wep_type": 2}
            ]
        }

        presets = self.generator.generate_from_gear_catalog(sample_catalog, count_limit=5)
        self.assertGreaterEqual(len(presets), 1)

        modded_npc = next((p for p in presets if "abyssal" in p.preset_id.lower()), None)
        self.assertIsNotNone(modded_npc, "Must synthesize NPC for the Abyssal Knight modded set")

        # Verify equipped modded armor and weapon IDs
        self.assertEqual(modded_npc.equipment.head_id, 9000000)
        self.assertEqual(modded_npc.equipment.body_id, 9000100)
        self.assertEqual(modded_npc.equipment.arms_id, 9000200)
        self.assertEqual(modded_npc.equipment.legs_id, 9000300)
        self.assertEqual(modded_npc.equipment.right_weapon_1_id, 9000400)

        # Verify carried drops extraction
        carried = modded_npc.equipment.get_all_carried_items()
        item_ids = [c["item_id"] for c in carried]
        self.assertIn(9000000, item_ids)
        self.assertIn(9000100, item_ids)
        self.assertIn(9000200, item_ids)
        self.assertIn(9000300, item_ids)
        self.assertIn(9000400, item_ids)

    def test_expanded_world_encounters_catalog(self):
        encounters_file = self.base_dir / "data" / "world_encounters.json"
        placer = WorldPlacer(encounters_file)

        self.assertGreaterEqual(len(placer.all_encounters), 30, "World encounters catalog must contain at least 30 points")
        self.assertIn("Limgrave", placer.encounters_by_region)
        self.assertIn("Weeping Peninsula", placer.encounters_by_region)
        self.assertIn("Liurnia", placer.encounters_by_region)
        self.assertIn("Caelid", placer.encounters_by_region)
        self.assertIn("Altus Plateau", placer.encounters_by_region)
        self.assertIn("Mountaintops", placer.encounters_by_region)
        self.assertIn("Subterranean Rivers", placer.encounters_by_region)


if __name__ == "__main__":
    unittest.main()
