"""
Autonomous NPC Generator for EnemyForge.
Synthesizes hostile NPC enemies equipped with patched/modded sets from regulation.bin
or curated thematic combat archetypes, placing them across the Lands Between.
Adheres to [CS-MODULAR], [CS-DECOUPLE], and [CS-GRANULARITY].
"""

import re
import json
import random
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.models import CharacterPreset, EquipmentLoadout
from src.logger import system_logger


class NPCGenerator:
    """
    Procedurally synthesizes unique Tarnished NPC enemies and invaders.
    Inspects active regulation.bin to prioritize custom/modded armor and weapon sets,
    ensuring modded games get custom modded enemies that drop their equipment on defeat.
    """

    def __init__(self, output_presets_dir: Optional[Path] = None):
        self.output_presets_dir = Path(output_presets_dir).resolve() if output_presets_dir else None

        # Curated Base Game Archetypes for fallback / procedural synthesis
        self.thematic_templates: List[Dict[str, Any]] = [
            {
                "archetype_id": "crucible_inquisitor",
                "name_pool": ["Inquisitor Morvath", "Crucible Outcast Valerius", "Sir Severus of the Tree"],
                "title": "Aspect of the Crucible",
                "archetype": "Crucible Paladin",
                "gender": 0,
                "level": 115,
                "hp_max": 3800,
                "runes": 32000,
                "danger_tier": 4,
                "spawn_region": "Altus Plateau",
                "spawn_zone": "Rampartside Path Junction",
                "equipment": {
                    "head_id": 1610000, "head_name": "Crucible Axe Helm",
                    "body_id": 1610100, "body_name": "Crucible Axe Armor",
                    "arms_id": 1610200, "arms_name": "Crucible Gauntlets",
                    "legs_id": 1610300, "legs_name": "Crucible Greaves",
                    "right_weapon_1_id": 2080000, "right_weapon_1_name": "Ordovis's Greatsword",
                    "left_weapon_1_id": 31050000, "left_weapon_1_name": "Crucible Hornshield"
                }
            },
            {
                "archetype_id": "carian_moonblade",
                "name_pool": ["Lunaria, Blade of Caria", "Spellblade Justinian", "Carian Royal Infiltrator"],
                "title": "Moongazing Spellblade",
                "archetype": "Carian Spellblade",
                "gender": 1,
                "level": 95,
                "hp_max": 2900,
                "runes": 24000,
                "danger_tier": 2,
                "spawn_region": "Liurnia",
                "spawn_zone": "Three Sisters Moonrise Terrace",
                "equipment": {
                    "head_id": 1700000, "head_name": "Carian Knight Helm",
                    "body_id": 1700100, "body_name": "Carian Knight Armor",
                    "arms_id": 1700200, "arms_name": "Carian Knight Gauntlets",
                    "legs_id": 1700300, "legs_name": "Carian Knight Greaves",
                    "right_weapon_1_id": 2060000, "right_weapon_1_name": "Carian Knight's Sword",
                    "left_weapon_1_id": 33000000, "left_weapon_1_name": "Carian Regal Scepter"
                }
            },
            {
                "archetype_id": "cleanrot_vanguard",
                "name_pool": ["Vanguard Malakor", "Cleanrot Duelist Finlay", "Rot-Blessed Kyra"],
                "title": "Vanguard of the Haligtree",
                "archetype": "Cleanrot Knight",
                "gender": 1,
                "level": 105,
                "hp_max": 3300,
                "runes": 28000,
                "danger_tier": 3,
                "spawn_region": "Caelid",
                "spawn_zone": "Swamp of Aeonia Scarlet Dunes",
                "equipment": {
                    "head_id": 1810000, "head_name": "Cleanrot Helm",
                    "body_id": 1810100, "body_name": "Cleanrot Armor",
                    "arms_id": 1810200, "arms_name": "Cleanrot Gauntlets",
                    "legs_id": 1810300, "legs_name": "Cleanrot Greaves",
                    "right_weapon_1_id": 10040000, "right_weapon_1_name": "Cleanrot Spear",
                    "left_weapon_1_id": 11020000, "left_weapon_1_name": "Halo Scythe"
                }
            },
            {
                "archetype_id": "bloodhound_stalker",
                "name_pool": ["Darriwil's Shadow", "Bloodhound Ronald", "Stalker Fenrir"],
                "title": "Feral Bloodhound Exile",
                "archetype": "Bloodhound Stalker",
                "gender": 0,
                "level": 80,
                "hp_max": 2700,
                "runes": 18000,
                "danger_tier": 1,
                "spawn_region": "Limgrave",
                "spawn_zone": "Forlorn Hound Evergaol Bluff",
                "equipment": {
                    "head_id": 1600000, "head_name": "Bloodhound Knight Helm",
                    "body_id": 1600100, "body_name": "Bloodhound Knight Armor",
                    "arms_id": 1600200, "arms_name": "Bloodhound Knight Gauntlets",
                    "legs_id": 1600300, "legs_name": "Bloodhound Knight Greaves",
                    "right_weapon_1_id": 7030000, "right_weapon_1_name": "Bloodhound's Fang",
                    "left_weapon_1_id": 15000000, "left_weapon_1_name": "Bloodhound Claws"
                }
            },
            {
                "archetype_id": "frenzied_heretic",
                "name_pool": ["Vyke's Acolyte Brand", "Frenzied Zealot Ignis", "Three Fingers Disciple"],
                "title": "Disciple of Yellow Embers",
                "archetype": "Frenzied Flame Zealot",
                "gender": 0,
                "level": 120,
                "hp_max": 3900,
                "runes": 36000,
                "danger_tier": 5,
                "spawn_region": "Mountaintops",
                "spawn_zone": "Yelough Anix Ruins Madness Crater",
                "equipment": {
                    "head_id": 1920000, "head_name": "Fingerprint Helm",
                    "body_id": 1920100, "body_name": "Fingerprint Armor",
                    "arms_id": 1920200, "arms_name": "Fingerprint Gauntlets",
                    "legs_id": 1920300, "legs_name": "Fingerprint Greaves",
                    "right_weapon_1_id": 10070000, "right_weapon_1_name": "Vyke's War Spear",
                    "left_weapon_1_id": 34000000, "left_weapon_1_name": "Frenzied Flame Seal"
                }
            },
            {
                "archetype_id": "black_knife_shadow",
                "name_pool": ["Alecto's Kin Cynthia", "Shadow Assassin Vael", "Night-Carver Morra"],
                "title": "Numen Shadow Assassin",
                "archetype": "Black Knife Assassin",
                "gender": 1,
                "level": 130,
                "hp_max": 3600,
                "runes": 42000,
                "danger_tier": 5,
                "spawn_region": "Mountaintops",
                "spawn_zone": "Ordina Liturgical Town Periphery",
                "equipment": {
                    "head_id": 1960000, "head_name": "Black Knife Hood",
                    "body_id": 1960100, "body_name": "Black Knife Armor",
                    "arms_id": 1960200, "arms_name": "Black Knife Gauntlets",
                    "legs_id": 1960300, "legs_name": "Black Knife Greaves",
                    "right_weapon_1_id": 1130000, "right_weapon_1_name": "Black Knife",
                    "left_weapon_1_id": 1140000, "left_weapon_1_name": "Blade of Calling"
                }
            }
        ]

    def generate_from_gear_catalog(
        self,
        gear_catalog: Dict[str, Any],
        count_limit: int = 10
    ) -> List[CharacterPreset]:
        """
        Parses gear catalog from regulation inspection.
        Creates custom NPCs for each discovered modded set.
        """
        modded_protectors = gear_catalog.get("modded_protectors", [])
        modded_weapons = gear_catalog.get("modded_weapons", [])

        if not modded_protectors and not modded_weapons:
            system_logger.info("No modded gear rows found in catalog. Using thematic archetypes.", source="NPCGenerator")
            return self.generate_thematic_presets(count_limit)

        # 1. Group modded protectors by set stem
        sets: Dict[str, Dict[str, Any]] = {}
        for p in modded_protectors:
            name = p.get("name", "")
            clean_stem = self._extract_set_stem(name)
            if clean_stem not in sets:
                sets[clean_stem] = {"helm": None, "armor": None, "gaunt": None, "leg": None, "name": clean_stem}
            
            cat = p.get("category", 0)
            if cat == 0:
                sets[clean_stem]["helm"] = p
            elif cat == 1:
                sets[clean_stem]["armor"] = p
            elif cat == 2:
                sets[clean_stem]["gaunt"] = p
            elif cat == 3:
                sets[clean_stem]["leg"] = p

        system_logger.info(f"Identified {len(sets)} modded protector set(s) from regulation inspection.", source="NPCGenerator")

        generated_presets: List[CharacterPreset] = []
        weapon_idx = 0

        regions = ["Limgrave", "Weeping Peninsula", "Liurnia", "Caelid", "Altus Plateau", "Mountaintops", "Subterranean Rivers"]
        zones = [
            "Stormhill Crossroads", "Bridge of Sacrifice Redoubt", "Three Sisters Moonrise Terrace",
            "Swamp of Aeonia Scarlet Dunes", "Windmill Village Southern Ascent", "Freezing Lake Blizzard Expanse"
        ]

        for set_stem, set_data in sets.items():
            if len(generated_presets) >= count_limit:
                break

            # Associate weapon
            weapon = None
            if modded_weapons:
                # Find matching weapon name or cycle
                matching = [w for w in modded_weapons if set_stem.lower() in w.get("name", "").lower()]
                weapon = matching[0] if matching else modded_weapons[weapon_idx % len(modded_weapons)]
                weapon_idx += 1

            preset = self._synthesize_preset_from_set(set_stem, set_data, weapon)
            generated_presets.append(preset)

            if self.output_presets_dir:
                self._save_preset_json(preset)

        # If modded sets were fewer than requested limit, supplement with thematic archetypes
        if len(generated_presets) < count_limit:
            needed = count_limit - len(generated_presets)
            thematics = self.generate_thematic_presets(needed)
            generated_presets.extend(thematics)

        return generated_presets

    def generate_thematic_presets(self, count: int = 6) -> List[CharacterPreset]:
        """Synthesizes NPC enemies from built-in thematic Elden Ring archetypes."""
        results: List[CharacterPreset] = []
        rng = random.Random(42)

        for i in range(min(count, len(self.thematic_templates))):
            tmpl = self.thematic_templates[i]
            npc_name = rng.choice(tmpl["name_pool"])
            preset_id = f"gen_{tmpl['archetype_id']}_{i+1}"

            eq = tmpl["equipment"]
            loadout = EquipmentLoadout(
                head_id=eq.get("head_id", 0), head_name=eq.get("head_name", ""),
                body_id=eq.get("body_id", 0), body_name=eq.get("body_name", ""),
                arms_id=eq.get("arms_id", 0), arms_name=eq.get("arms_name", ""),
                legs_id=eq.get("legs_id", 0), legs_name=eq.get("legs_name", ""),
                right_weapon_1_id=eq.get("right_weapon_1_id", 0), right_weapon_1_name=eq.get("right_weapon_1_name", ""),
                left_weapon_1_id=eq.get("left_weapon_1_id", 0), left_weapon_1_name=eq.get("left_weapon_1_name", "")
            )

            preset = CharacterPreset(
                preset_id=preset_id,
                name=npc_name,
                title=tmpl["title"],
                archetype=tmpl["archetype"],
                gender=tmpl["gender"],
                level=tmpl["level"],
                equipment=loadout,
                hp_max=tmpl["hp_max"],
                runes=tmpl["runes"],
                danger_tier=tmpl["danger_tier"],
                spawn_region=tmpl["spawn_region"],
                spawn_zone=tmpl["spawn_zone"],
                guaranteed_loot=True,
                drop_probability_percent=100.0,
                sp_effect_aura_id=7000
            )

            results.append(preset)
            if self.output_presets_dir:
                self._save_preset_json(preset)

        return results

    def _synthesize_preset_from_set(
        self,
        set_stem: str,
        set_data: Dict[str, Any],
        weapon: Optional[Dict[str, Any]]
    ) -> CharacterPreset:
        """Constructs a complete CharacterPreset wearing a modded armor set and weapon."""
        preset_id = f"modded_npc_{re.sub(r'[^a-zA-Z0-9_]', '_', set_stem.lower())}"
        
        # Name generation based on set stem
        title_prefixes = ["Sir", "Lady", "Outcast", "Champion", "Wandering Blade", "Exiled Knight"]
        chosen_prefix = random.choice(title_prefixes)
        npc_name = f"{chosen_prefix} of the {set_stem}"

        h = set_data.get("helm") or {}
        b = set_data.get("armor") or {}
        g = set_data.get("gaunt") or {}
        l = set_data.get("leg") or {}

        w_id = weapon.get("id", 2010000) if weapon else 2010000
        w_name = weapon.get("name", "Knight's Greatsword") if weapon else "Knight's Greatsword"

        loadout = EquipmentLoadout(
            head_id=h.get("id", 0), head_name=h.get("name", f"{set_stem} Helm"),
            body_id=b.get("id", 0), body_name=b.get("name", f"{set_stem} Armor"),
            arms_id=g.get("id", 0), arms_name=g.get("name", f"{set_stem} Gauntlets"),
            legs_id=l.get("id", 0), legs_name=l.get("name", f"{set_stem} Greaves"),
            right_weapon_1_id=w_id, right_weapon_1_name=w_name
        )

        return CharacterPreset(
            preset_id=preset_id,
            name=npc_name,
            title=f"Wielder of the {set_stem} Relic",
            archetype=f"{set_stem} Champion",
            gender=0 if "Sir" in chosen_prefix or "Knight" in chosen_prefix else 1,
            level=110,
            equipment=loadout,
            hp_max=3500,
            mp_max=220,
            stamina_max=200,
            poise=60,
            runes=30000,
            danger_tier=4,
            spawn_region="Altus Plateau",
            spawn_zone="Windmill Village Southern Ascent",
            guaranteed_loot=True,
            drop_probability_percent=100.0,
            sp_effect_aura_id=7000
        )

    def _extract_set_stem(self, name: str) -> str:
        """Strips armor category suffixes (Helm, Armor, Gauntlets, Greaves) to extract set name."""
        stem = re.sub(r'\b(Helm|Helmet|Hood|Crown|Mask|Armor|Robes|Cuirass|Chestpiece|Gauntlets|Gloves|Manchettes|Bracers|Greaves|Leggings|Boots|Trousers)\b', '', name, flags=re.IGNORECASE)
        stem = stem.replace("[]", "").strip()
        return stem or name

    def _save_preset_json(self, preset: CharacterPreset) -> Path:
        """Saves preset as standalone JSON file in user presets dropzone."""
        if not self.output_presets_dir:
            raise ValueError("Output directory not configured")

        self.output_presets_dir.mkdir(parents=True, exist_ok=True)
        out_file = self.output_presets_dir / f"{preset.preset_id}.json"

        data = {
            "preset_id": preset.preset_id,
            "name": preset.name,
            "title": preset.title,
            "archetype": preset.archetype,
            "gender": preset.gender,
            "level": preset.level,
            "equipment": {
                "head_id": preset.equipment.head_id,
                "head_name": preset.equipment.head_name,
                "body_id": preset.equipment.body_id,
                "body_name": preset.equipment.body_name,
                "arms_id": preset.equipment.arms_id,
                "arms_name": preset.equipment.arms_name,
                "legs_id": preset.equipment.legs_id,
                "legs_name": preset.equipment.legs_name,
                "right_weapon_1_id": preset.equipment.right_weapon_1_id,
                "right_weapon_1_name": preset.equipment.right_weapon_1_name,
                "left_weapon_1_id": preset.equipment.left_weapon_1_id,
                "left_weapon_1_name": preset.equipment.left_weapon_1_name
            },
            "scaling": {
                "hp_max": preset.hp_max,
                "mp_max": preset.mp_max,
                "stamina_max": preset.stamina_max,
                "poise": preset.poise,
                "runes": preset.runes
            },
            "ai": {
                "think_param_id": preset.think_param_id
            },
            "aura": {
                "sp_effect_aura_id": preset.sp_effect_aura_id
            },
            "carried_loot": {
                "guaranteed_drop": preset.guaranteed_loot,
                "drop_probability_percent": preset.drop_probability_percent
            },
            "spawn_preference": {
                "region": preset.spawn_region,
                "zone": preset.spawn_zone,
                "danger_tier": preset.danger_tier
            },
            "appearance": {
                "hair_mesh_id": preset.hair_mesh_id
            },
            "is_generated": True
        }

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        system_logger.info(f"Exported generated NPC preset to: {out_file.name}", source="NPCGenerator")
        return out_file
