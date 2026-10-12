"""
Preset loader and scanner for PhantomForge.
Ingests character preset definitions from input dropzones and built-in templates.
Adheres to [CS-MODULAR] and [CS-GRANULARITY].
"""

import json
from pathlib import Path
from typing import List, Optional
from src.models import CharacterPreset, EquipmentLoadout
from src.logger import system_logger


class PresetLoader:
    """Discovers and validates character preset JSON files."""

    def __init__(self, data_presets_dir: Path, input_presets_dir: Path):
        self.data_presets_dir = Path(data_presets_dir).resolve()
        self.input_presets_dir = Path(input_presets_dir).resolve()

    def discover_and_load(self) -> List[CharacterPreset]:
        """Loads presets from both built-in data directory and user dropzone."""
        presets: List[CharacterPreset] = []
        seen_ids = set()

        # 1. User dropzone presets take priority
        if self.input_presets_dir.exists():
            for f in sorted(self.input_presets_dir.glob("*.json")):
                preset = self._parse_preset_file(f)
                if preset and preset.preset_id not in seen_ids:
                    seen_ids.add(preset.preset_id)
                    presets.append(preset)
                    system_logger.info(f"Loaded user preset: '{preset.name}' from {f.name}", source="PresetLoader")

        # 2. Built-in templates
        if self.data_presets_dir.exists():
            for f in sorted(self.data_presets_dir.glob("*.json")):
                preset = self._parse_preset_file(f)
                if preset and preset.preset_id not in seen_ids:
                    seen_ids.add(preset.preset_id)
                    presets.append(preset)
                    system_logger.debug(f"Loaded built-in template: '{preset.name}'", source="PresetLoader")

        system_logger.info(f"Preset discovery finished. Total loaded: {len(presets)}", source="PresetLoader")
        return presets

    def _parse_preset_file(self, file_path: Path) -> Optional[CharacterPreset]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            preset_id = data.get("preset_id") or file_path.stem
            name = data.get("name", "Unnamed Phantom")
            title = data.get("title", "Hostile Tarnished")
            archetype = data.get("archetype", "Standard Duelist")
            gender = int(data.get("gender", 0))
            level = int(data.get("level", 100))

            # Equipment Loadout
            equip_data = data.get("equipment", {})
            loadout = EquipmentLoadout(
                head_id=int(equip_data.get("head_id", 0)),
                head_name=str(equip_data.get("head_name", "")),
                body_id=int(equip_data.get("body_id", 0)),
                body_name=str(equip_data.get("body_name", "")),
                arms_id=int(equip_data.get("arms_id", 0)),
                arms_name=str(equip_data.get("arms_name", "")),
                legs_id=int(equip_data.get("legs_id", 0)),
                legs_name=str(equip_data.get("legs_name", "")),
                right_weapon_1_id=int(equip_data.get("right_weapon_1_id", 0)),
                right_weapon_1_name=str(equip_data.get("right_weapon_1_name", "")),
                right_weapon_2_id=int(equip_data.get("right_weapon_2_id", 0)),
                right_weapon_2_name=str(equip_data.get("right_weapon_2_name", "")),
                left_weapon_1_id=int(equip_data.get("left_weapon_1_id", 0)),
                left_weapon_1_name=str(equip_data.get("left_weapon_1_name", "")),
                left_weapon_2_id=int(equip_data.get("left_weapon_2_id", 0)),
                left_weapon_2_name=str(equip_data.get("left_weapon_2_name", "")),
                arrow_id=int(equip_data.get("arrow_id", 0)),
                bolt_id=int(equip_data.get("bolt_id", 0))
            )

            # Attribute Scaling
            scaling = data.get("scaling", {})
            hp_max = int(scaling.get("hp_max", 2500))
            mp_max = int(scaling.get("mp_max", 200))
            stamina_max = int(scaling.get("stamina_max", 180))
            poise = int(scaling.get("poise", 50))
            runes = int(scaling.get("runes", 15000))

            # AI and Aura
            ai_data = data.get("ai", {})
            think_id = int(ai_data.get("think_param_id", 100000))
            aura_data = data.get("aura", {})
            aura_id = int(aura_data.get("sp_effect_aura_id", 7000))

            # Carried Loot Settings
            loot_data = data.get("carried_loot", {})
            guaranteed = bool(loot_data.get("guaranteed_drop", True))
            drop_prob = float(loot_data.get("drop_probability_percent", 100.0))

            # Spawn Preference
            spawn_pref = data.get("spawn_preference", {})
            region = str(spawn_pref.get("region", "Limgrave"))
            zone = str(spawn_pref.get("zone", "Stormhill Crossroads"))
            danger = int(spawn_pref.get("danger_tier", 1))

            appearance = data.get("appearance", {})
            hair_id = int(appearance.get("hair_mesh_id", 1))

            return CharacterPreset(
                preset_id=preset_id,
                name=name,
                title=title,
                archetype=archetype,
                gender=gender,
                level=level,
                equipment=loadout,
                hp_max=hp_max,
                mp_max=mp_max,
                stamina_max=stamina_max,
                poise=poise,
                runes=runes,
                think_param_id=think_id,
                sp_effect_aura_id=aura_id,
                guaranteed_loot=guaranteed,
                drop_probability_percent=drop_prob,
                hair_mesh_id=hair_id,
                spawn_region=region,
                spawn_zone=zone,
                danger_tier=danger,
                source_file=str(file_path)
            )

        except Exception as ex:
            system_logger.error(f"Failed to parse preset file '{file_path.name}': {ex}", source="PresetLoader")
            return None
