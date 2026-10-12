"""
Unit tests for PhantomForge localization catalog parity.
Enforces [CS-LOCALIZATION] mandatory rule: 100% key parity across all language dictionaries.
"""

import json
import unittest
from pathlib import Path


class TestLocalizationParity(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.loc_dir = self.base_dir / "data" / "localization"

    def test_catalogs_exist_and_non_empty(self):
        en_file = self.loc_dir / "en.json"
        pt_file = self.loc_dir / "pt_br.json"

        self.assertTrue(en_file.exists(), "en.json must exist")
        self.assertTrue(pt_file.exists(), "pt_br.json must exist")

        with open(en_file, "r", encoding="utf-8") as f:
            en_data = json.load(f)

        with open(pt_file, "r", encoding="utf-8") as f:
            pt_data = json.load(f)

        self.assertGreater(len(en_data), 0, "en.json must not be empty")
        self.assertGreater(len(pt_data), 0, "pt_br.json must not be empty")

    def test_strict_key_parity(self):
        """Mandatory [CS-LOCALIZATION] check: exact key match between en.json and pt_br.json."""
        with open(self.loc_dir / "en.json", "r", encoding="utf-8") as f:
            en_keys = set(json.load(f).keys())

        with open(self.loc_dir / "pt_br.json", "r", encoding="utf-8") as f:
            pt_keys = set(json.load(f).keys())

        missing_in_pt = en_keys - pt_keys
        extra_in_pt = pt_keys - en_keys

        self.assertEqual(
            missing_in_pt,
            set(),
            f"[CS-LOCALIZATION VIOLATION] Keys missing in pt_br.json: {missing_in_pt}"
        )
        self.assertEqual(
            extra_in_pt,
            set(),
            f"[CS-LOCALIZATION VIOLATION] Extra keys in pt_br.json: {extra_in_pt}"
        )


if __name__ == "__main__":
    unittest.main()
