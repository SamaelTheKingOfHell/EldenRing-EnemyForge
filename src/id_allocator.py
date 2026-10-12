"""
Deterministic ID allocator for PhantomForge.
Allocates collision-free IDs for NpcParam, ChrAsmParam, FaceParam, and ItemLotParam_enemy.
Adheres to [CS-MODULAR] and [CS-GRANULARITY].
"""

from typing import Dict, Tuple


class IdAllocator:
    """
    Allocates sequential, non-colliding IDs in the safe custom 9500000+ range.
    """

    def __init__(
        self,
        base_npc_id: int = 9500000,
        base_chr_asm_id: int = 9510000,
        base_face_id: int = 9520000,
        base_item_lot_id: int = 9530000
    ):
        self.base_npc_id = base_npc_id
        self.base_chr_asm_id = base_chr_asm_id
        self.base_face_id = base_face_id
        self.base_item_lot_id = base_item_lot_id
        self._counter = 0
        self._allocations: Dict[str, Tuple[int, int, int, int]] = {}

    def reset(self) -> None:
        self._counter = 0
        self._allocations.clear()

    def allocate_for_phantom(self, preset_id: str) -> Tuple[int, int, int, int]:
        """
        Allocates (npc_param_id, chr_asm_id, face_param_id, item_lot_id)
        for a given preset ID.
        """
        if preset_id in self._allocations:
            return self._allocations[preset_id]

        offset = self._counter
        self._counter += 1

        npc_id = self.base_npc_id + offset
        chr_asm_id = self.base_chr_asm_id + offset
        face_id = self.base_face_id + offset
        item_lot_id = self.base_item_lot_id + offset

        alloc = (npc_id, chr_asm_id, face_id, item_lot_id)
        self._allocations[preset_id] = alloc
        return alloc
