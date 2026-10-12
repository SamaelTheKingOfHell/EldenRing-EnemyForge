"""
Unit tests for PhantomForge BackupManager and ManifestStore.
Adheres to [CS-NO-MOCK] and [CS-GRANULARITY].
"""

import unittest
import tempfile
from pathlib import Path
from src.backup_manager import BackupManager
from src.manifest_store import ManifestStore


class TestBackupAndManifest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_root = Path(self.temp_dir.name)
        self.backups_dir = self.test_root / "backups"
        self.manifest_file = self.test_root / "phantomforge_manifest.json"

        self.backup_mgr = BackupManager(self.backups_dir)
        self.manifest_store = ManifestStore(self.manifest_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_backup_creation_and_restore(self):
        # Create dummy file to simulate regulation
        dummy_file = self.test_root / "regulation.bin"
        dummy_file.write_bytes(b"ELDEN_RING_TEST_DATA_PRISTINE")

        backup_path = self.backup_mgr.create_snapshot(dummy_file)
        self.assertIsNotNone(backup_path)
        self.assertTrue(backup_path.exists())

        # Modify dummy file
        dummy_file.write_bytes(b"MODIFIED_CORRUPTED_DATA")

        # Restore from backup
        success = self.backup_mgr.restore_backup(dummy_file)
        self.assertTrue(success)
        self.assertEqual(dummy_file.read_bytes(), b"ELDEN_RING_TEST_DATA_PRISTINE")

    def test_manifest_save_and_clear(self):
        sample_phantoms = [
            {
                "name": "Test Phantom",
                "npc_param_id": 9500000,
                "chr_asm_id": 9510000,
                "face_param_id": 9520000,
                "item_lot_id": 9530000
            }
        ]

        self.manifest_store.save("backup.bin", sample_phantoms)
        manifest = self.manifest_store.load()

        self.assertEqual(manifest.injected_npc_ids, [9500000])
        self.assertEqual(manifest.injected_item_lot_ids, [9530000])

        self.manifest_store.clear()
        cleared_manifest = self.manifest_store.load()
        self.assertEqual(len(cleared_manifest.injected_npc_ids), 0)


if __name__ == "__main__":
    unittest.main()
