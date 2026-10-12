"""
Domain models and data schemas for PhantomForge.
Adheres to [CS-MODULAR] and [CS-GRANULARITY].
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class PlacementMode(str, Enum):
    """World placement and encounter distribution strategy."""
    THEMATIC_REGIONAL = "thematic_regional"
    ROAMING_INVASIONS = "roaming_invasions"
    CHAMPION_DUELS = "champion_duels"
    CHAOS_EXPEDITION = "chaos_expedition"


@dataclass
class EquipmentLoadout:
    """Equipment worn and wielded by a character preset."""
    head_id: int = 0
    head_name: str = ""
    body_id: int = 0
    body_name: str = ""
    arms_id: int = 0
    arms_name: str = ""
    legs_id: int = 0
    legs_name: str = ""
    right_weapon_1_id: int = 0
    right_weapon_1_name: str = ""
    right_weapon_2_id: int = 0
    right_weapon_2_name: str = ""
    left_weapon_1_id: int = 0
    left_weapon_1_name: str = ""
    left_weapon_2_id: int = 0
    left_weapon_2_name: str = ""
    arrow_id: int = 0
    bolt_id: int = 0

    def get_all_carried_items(self) -> List[Dict[str, Any]]:
        """Extracts list of non-zero items carried in this loadout."""
        items: List[Dict[str, Any]] = []

        # Protectors / Armor
        for slot, item_id, name in [
            ("head", self.head_id, self.head_name),
            ("body", self.body_id, self.body_name),
            ("arms", self.arms_id, self.arms_name),
            ("legs", self.legs_id, self.legs_name)
        ]:
            if item_id > 0:
                items.append({
                    "item_id": item_id,
                    "slot": slot,
                    "item_type": "protector",
                    "name": name or f"{slot.capitalize()} Armor"
                })

        # Weapons & Catalysts & Shields
        for slot, item_id, name in [
            ("right_weapon_1", self.right_weapon_1_id, self.right_weapon_1_name),
            ("right_weapon_2", self.right_weapon_2_id, self.right_weapon_2_name),
            ("left_weapon_1", self.left_weapon_1_id, self.left_weapon_1_name),
            ("left_weapon_2", self.left_weapon_2_id, self.left_weapon_2_name)
        ]:
            if item_id > 0:
                items.append({
                    "item_id": item_id,
                    "slot": slot,
                    "item_type": "weapon",
                    "name": name or "Weapon"
                })

        return items


@dataclass
class CharacterPreset:
    """Complete character preset definition."""
    preset_id: str
    name: str
    title: str
    archetype: str
    gender: int  # 0 = Male, 1 = Female
    level: int
    equipment: EquipmentLoadout
    hp_max: int = 2500
    mp_max: int = 200
    stamina_max: int = 180
    poise: int = 50
    runes: int = 15000
    think_param_id: int = 100000
    sp_effect_aura_id: int = 7000  # Default Red Invader Aura
    guaranteed_loot: bool = True
    drop_probability_percent: float = 100.0
    hair_mesh_id: int = 1
    spawn_region: str = "Limgrave"
    spawn_zone: str = "Stormhill Crossroads"
    danger_tier: int = 1
    source_file: Optional[str] = None


@dataclass
class WorldEncounter:
    """World spawn point or roaming encounter location."""
    encounter_id: str
    name: str
    region: str
    landmark: str
    coordinates: Dict[str, float]
    map_id: str
    base_enemy_id: int
    danger_tier: int
    description: str = ""


@dataclass
class PhantomEnemy:
    """Instantiated phantom enemy ready for regulation patching."""
    preset: CharacterPreset
    encounter: WorldEncounter
    npc_param_id: int
    chr_asm_id: int
    face_param_id: int
    item_lot_id: int
    carried_loot_items: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class PhantomForgeConfig:
    """User and generator configuration settings."""
    game_dir: str = ""
    active_regulation_path: str = ""
    target_mod_dir: str = "mod"
    placement_mode: PlacementMode = PlacementMode.THEMATIC_REGIONAL
    guaranteed_carried_loot: bool = True
    global_drop_chance_percent: float = 100.0
    enable_invasion_aura: bool = True
    scale_attributes_by_tier: bool = True
    mystery_mode: bool = False
    ui_language: str = "en"


@dataclass
class PhantomForgeManifest:
    """Tracks forged phantoms and injected IDs for 1-click clean uninstall."""
    version: str = "1.0.0"
    timestamp: str = ""
    regulation_backup_file: str = ""
    forged_phantoms: List[Dict[str, Any]] = field(default_factory=list)
    injected_npc_ids: List[int] = field(default_factory=list)
    injected_chr_asm_ids: List[int] = field(default_factory=list)
    injected_face_param_ids: List[int] = field(default_factory=list)
    injected_item_lot_ids: List[int] = field(default_factory=list)
