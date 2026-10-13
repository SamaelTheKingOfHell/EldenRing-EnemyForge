"""
Enemy Builder for EnemyForge.
Constructs Elden Ring parameter injection specifications and carried loot drop tables.
Adheres to [CS-MODULAR], [CS-DECOUPLE], and [CS-GRANULARITY].
"""

from typing import List, Dict, Any, Tuple, Optional
from src.models import CharacterPreset, WorldEncounter, EnemyForgeConfig, EnemyInstance
from src.id_allocator import IdAllocator
from src.logger import system_logger


class EnemyBuilder:
    """
    Transforms character presets and world encounters into concrete
    FromSoftware regulation patch specifications, ensuring every enemy drops
    the complete gear loadout they carry.
    """

    def __init__(self, id_allocator: Optional[IdAllocator] = None):
        self.id_allocator = id_allocator or IdAllocator()

    def build_patch_spec(
        self,
        assignments: List[Tuple[CharacterPreset, WorldEncounter]],
        config: EnemyForgeConfig
    ) -> Dict[str, Any]:
        """
        Builds the unified patch specification document consumed by RegTool.
        """
        enemies_spec: List[Dict[str, Any]] = []
        instantiated_enemies: List[EnemyInstance] = []

        for preset, encounter in assignments:
            npc_id, chr_asm_id, face_id, item_lot_id = self.id_allocator.allocate_for_phantom(preset.preset_id)

            # 1. Resolve Carried Equipment and Generate Carried Loot Drops
            carried_items = preset.equipment.get_all_carried_items()
            carried_drops: List[Dict[str, Any]] = []

            for item in carried_items:
                # Probability: 1000 = 100% in Elden Ring ItemLotParam_enemy
                prob_point = 1000 if config.guaranteed_carried_loot else int((config.global_drop_chance_percent / 100.0) * 1000)
                carried_drops.append({
                    "item_id": item["item_id"],
                    "item_type": item["item_type"],
                    "slot": item["slot"],
                    "name": item["name"],
                    "probability": max(1, min(1000, prob_point)),
                    "quantity": 1
                })

            # 2. Scale Attributes by Danger Tier if enabled
            tier_multiplier = 1.0 + ((encounter.danger_tier - 1) * 0.15) if config.scale_attributes_by_tier else 1.0
            eff_hp = int(preset.hp_max * tier_multiplier)
            eff_runes = int(preset.runes * tier_multiplier)

            # 3. Determine Visual Appearance (Flesh-and-blood enemy vs Phantom Aura)
            # Default to flesh/normal human (0) unless invasion aura is explicitly enabled
            aura_id = preset.sp_effect_aura_id if config.enable_invasion_aura else 0

            # 4. Build Enemy Spec entry
            spec_entry = {
                "preset_id": preset.preset_id,
                "name": preset.name,
                "title": preset.title,
                "npc_param_id": npc_id,
                "chr_asm_id": chr_asm_id,
                "face_param_id": face_id,
                "item_lot_id": item_lot_id,
                "think_param_id": preset.think_param_id,
                "gender": preset.gender,
                "hair_mesh_id": preset.hair_mesh_id,
                "sp_effect_aura_id": aura_id,
                "hp_max": eff_hp,
                "mp_max": preset.mp_max,
                "stamina_max": preset.stamina_max,
                "poise": preset.poise,
                "get_soul": eff_runes,
                "equipment": {
                    "head_id": preset.equipment.head_id,
                    "body_id": preset.equipment.body_id,
                    "arms_id": preset.equipment.arms_id,
                    "legs_id": preset.equipment.legs_id,
                    "right_weapon_1_id": preset.equipment.right_weapon_1_id,
                    "right_weapon_2_id": preset.equipment.right_weapon_2_id,
                    "left_weapon_1_id": preset.equipment.left_weapon_1_id,
                    "left_weapon_2_id": preset.equipment.left_weapon_2_id,
                    "arrow_id": preset.equipment.arrow_id,
                    "bolt_id": preset.equipment.bolt_id
                },
                "carried_drops": carried_drops,
                "world_placement": {
                    "encounter_id": encounter.encounter_id,
                    "region": encounter.region,
                    "landmark": encounter.landmark,
                    "coordinates": encounter.coordinates,
                    "map_id": encounter.map_id,
                    "danger_tier": encounter.danger_tier
                }
            }

            enemies_spec.append(spec_entry)

            enemy_instance = EnemyInstance(
                preset=preset,
                encounter=encounter,
                npc_param_id=npc_id,
                chr_asm_id=chr_asm_id,
                face_param_id=face_id,
                item_lot_id=item_lot_id,
                carried_loot_items=carried_drops
            )
            instantiated_enemies.append(enemy_instance)

            system_logger.info(
                f"Built enemy spec '{preset.name}': NPC {npc_id}, ChrAsm {chr_asm_id}, "
                f"Lot {item_lot_id} with {len(carried_drops)} carried drop(s).",
                source="EnemyBuilder"
            )

        return {
            "version": "1.0.0",
            "forge_type": "world_enemies",
            "total_enemies": len(enemies_spec),
            "total_phantoms": len(enemies_spec),
            "enemies": enemies_spec,
            # Backward-compatible keys for RegTool
            "phantoms": enemies_spec
        }


# Backward-compatible alias
PhantomBuilder = EnemyBuilder
