"""
Automated unit tests for EnemyForge Qt GUI application.

Verifies:
- Headless Qt window initialization [CS-NO-MOCK]
- Preset and encounter data loading in inspector tables
- Path inputs and preset regulation buttons
- Parameter mutation synchronization
- Priscilla prototype card initialization
- Developer console drawer toggling
"""

import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path

# Headless Qt environment
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from src.qt_app import QApplication, EnemyForgeMainWindow
from src.models import EnemyForgeConfig, PlacementMode


class TestEnemyForgeQtApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if not cls.app:
            cls.app = QApplication(["test", "-platform", "offscreen"])

    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.window = EnemyForgeMainWindow(self.base_dir)
        self.window.show()

    def tearDown(self):
        self.window.close()

    def test_window_initialization(self):
        """Verify window initializes with correct title, stylesheet, and widgets."""
        self.assertIn("EnemyForge", self.window.windowTitle())
        self.assertIsNotNone(self.window.inspector)
        self.assertIsNotNone(self.window.proto_card)
        self.assertIsNotNone(self.window.console_drawer)

    def test_presets_and_encounters_loaded(self):
        """Verify that presets and world encounters are populated into the inspector tables."""
        self.assertGreater(len(self.window.presets), 0)
        self.assertGreater(len(self.window.encounters), 0)
        self.assertEqual(self.window.inspector.presets_table.rowCount(), len(self.window.presets))
        self.assertEqual(self.window.inspector.encounters_table.rowCount(), len(self.window.encounters))

    def test_preset_selection_renders_carried_drops(self):
        """Verify that selecting a preset renders equipment loadout and 100% carried drops."""
        self.window.inspector.presets_table.selectRow(0)
        detail = self.window.inspector.detail_text.toPlainText()
        self.assertIn("Guaranteed 100% Carried Drop List", detail)
        self.assertIn("Equipped Armor", detail)

    def test_parameter_updates_config(self):
        """Verify that changing controls updates the live config."""
        self.window._on_param_changed("scaling_factor", 2.5)
        self.assertEqual(self.window.config.scaling_factor, 2.5)

        self.window._on_param_changed("placement_mode", PlacementMode.CHAOS_EXPEDITION)
        self.assertEqual(self.window.config.placement_mode, PlacementMode.CHAOS_EXPEDITION)

    def test_mod_engine_and_vanilla_quick_buttons(self):
        """Verify quick regulation path preset buttons."""
        self.window._set_mod_engine_reg()
        expected_me2 = str(self.base_dir / "mod" / "regulation.bin")
        self.assertEqual(self.window.path_ctrls["active_regulation_path"].text(), expected_me2)

        self.window._set_vanilla_reg()
        expected_van = str(self.base_dir / "data" / "regulation.bin.vanilla_fallback")
        self.assertEqual(self.window.path_ctrls["active_regulation_path"].text(), expected_van)

    def test_dev_console_toggle(self):
        """Verify developer console drawer can be toggled."""
        self.assertFalse(self.window.console_drawer.isVisible())
        self.window._toggle_dev_console()
        self.assertTrue(self.window.console_drawer.isVisible())
        self.window._toggle_dev_console()
        self.assertFalse(self.window.console_drawer.isVisible())

    def test_banner_collapse_toggle(self):
        """Verify Mod Manager banner can be collapsed and expanded."""
        self.assertFalse(self.window.banner_collapsed)
        self.assertFalse(self.window.banner_desc.isHidden())
        self.window._toggle_banner()
        self.assertTrue(self.window.banner_collapsed)
        self.assertTrue(self.window.banner_desc.isHidden())
        self.window._toggle_banner()
        self.assertFalse(self.window.banner_collapsed)
        self.assertFalse(self.window.banner_desc.isHidden())

        self.assertTrue(self.window.banner_desc.isVisible())


if __name__ == "__main__":
    unittest.main()
