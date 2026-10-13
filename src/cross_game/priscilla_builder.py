"""
Crossbreed Priscilla Entity & World Encounter Synthesizer.
Builds the Elden Ring preset, combat statistics, carried drop tables, and world encounter
for Crossbreed Priscilla stationed right outside the Stranded Graveyard tutorial cave exit.
Adheres to [CS-MODULAR], [CS-DECOUPLE], and [CS-LOCALIZATION].
"""

from typing import Dict, Any, List
from src.models import CharacterPreset, EquipmentLoadout, WorldEncounter


def create_priscilla_preset() -> CharacterPreset:
    """Creates the CharacterPreset domain model representing Crossbreed Priscilla."""
    return CharacterPreset(
        preset_id="boss_crossbreed_priscilla",
        name="Crossbreed Priscilla",
        title="The Half-Dragon Exile",
        archetype="Cold Lifehunt Scythe Boss",
        gender=1,  # 1 = Female
        level=90,
        hp_max=8800,
        mp_max=500,
        stamina_max=400,
        poise=80,
        runes=45000,
        hair_mesh_id=10,
        sp_effect_aura_id=0,  # Elegant flesh and white fur model
        think_param_id=100000,
        spawn_region="Limgrave",
        spawn_zone="Stranded Graveyard Threshold",
        danger_tier=1,
        equipment=EquipmentLoadout(
            head_id=0,
            body_id=201100,  # Snow Witch Robe (White fur trim)
            body_name="White Fur Robe",
            arms_id=201200,  # Snow Witch Wristwraps
            arms_name="White Fur Manchettes",
            legs_id=201300,  # Snow Witch Skirt
            legs_name="White Fur Skirt",
            right_weapon_1_id=11030000,  # Grave Scythe (Lifehunt Scythe)
            right_weapon_1_name="Lifehunt Scythe",
            right_weapon_2_id=0,
            left_weapon_1_id=33200000,   # Cold Catalyst / Dragon Seal
            left_weapon_1_name="Dragon Communion Seal",
            left_weapon_2_id=0,
            arrow_id=0,
            bolt_id=0
        )
    )


def create_priscilla_encounter() -> WorldEncounter:
    """
    Creates the WorldEncounter placement right outside the opening tutorial cave
    (Stranded Graveyard wooden exit doors) at The First Step in Limgrave.
    """
    return WorldEncounter(
        encounter_id="limgrave_stranded_graveyard_cave_exit",
        name="Stranded Graveyard Threshold - The First Step",
        region="Limgrave",
        landmark="Outside the tutorial cave exit doors overlooking Limgrave",
        coordinates={"x": -185.0, "y": 88.5, "z": 342.0},
        map_id="m60_42_35_00",
        base_enemy_id=100020,
        danger_tier=1,
        description="Crossbreed Priscilla standing in the windswept grass right outside the wooden exit doors of the Stranded Graveyard."
    )


def build_priscilla_loot_spec() -> List[Dict[str, Any]]:
    """Generates the guaranteed 100% carried loot drops upon defeating Priscilla."""
    return [
        {
            "item_id": 11030000,
            "item_type": "weapon",
            "slot": "right_weapon_1",
            "name": "Lifehunt Scythe (Grave Scythe)",
            "probability": 1000,
            "quantity": 1
        },
        {
            "item_id": 201100,
            "item_type": "protector",
            "slot": "body",
            "name": "White Fur Robe (Snow Witch Robe)",
            "probability": 1000,
            "quantity": 1
        },
        {
            "item_id": 201200,
            "item_type": "protector",
            "slot": "arms",
            "name": "White Fur Manchettes",
            "probability": 1000,
            "quantity": 1
        },
        {
            "item_id": 201300,
            "item_type": "protector",
            "slot": "legs",
            "name": "White Fur Skirt",
            "probability": 1000,
            "quantity": 1
        },
        {
            "item_id": 10100,
            "item_type": "goods",
            "slot": "remembrance",
            "name": "Remembrance of the Crossbreed",
            "probability": 1000,
            "quantity": 1
        }
    ]
