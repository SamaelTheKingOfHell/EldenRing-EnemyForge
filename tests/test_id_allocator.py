"""
Unit tests for PhantomForge IdAllocator.
Verifies collision-free ID partitioning.
Adheres to [CS-NO-MOCK] and [CS-GRANULARITY].
"""

import unittest
from src.id_allocator import IdAllocator


class TestIdAllocator(unittest.TestCase):
    def test_non_colliding_sequential_allocation(self):
        allocator = IdAllocator(
            base_npc_id=9500000,
            base_chr_asm_id=9510000,
            base_face_id=9520000,
            base_item_lot_id=9530000
        )

        all_npc = []
        all_chr = []
        all_face = []
        all_lot = []

        for i in range(50):
            npc_id, chr_id, face_id, lot_id = allocator.allocate_for_phantom(f"preset_{i}")
            all_npc.append(npc_id)
            all_chr.append(chr_id)
            all_face.append(face_id)
            all_lot.append(lot_id)

        self.assertEqual(len(set(all_npc)), 50, "Zero NPC ID collisions")
        self.assertEqual(len(set(all_chr)), 50, "Zero ChrAsm ID collisions")
        self.assertEqual(len(set(all_face)), 50, "Zero FaceParam ID collisions")
        self.assertEqual(len(set(all_lot)), 50, "Zero ItemLot ID collisions")

        # Idempotency check
        re_npc, re_chr, re_face, re_lot = allocator.allocate_for_phantom("preset_0")
        self.assertEqual(re_npc, all_npc[0])
        self.assertEqual(re_chr, all_chr[0])


if __name__ == "__main__":
    unittest.main()
