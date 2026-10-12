"""
World Placer for PhantomForge.
Maps character presets to tactical world encounters and map regions across the Lands Between.
Adheres to [CS-MODULAR] and [CS-GRANULARITY].
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from src.models import CharacterPreset, WorldEncounter, PlacementMode
from src.logger import system_logger


class WorldPlacer:
    """Orchestrates world encounter mapping according to selected placement strategy."""

    def __init__(self, encounters_file: Path):
        self.encounters_file = Path(encounters_file).resolve()
        self.encounters_by_region: Dict[str, List[WorldEncounter]] = {}
        self.all_encounters: List[WorldEncounter] = []
        self._load_encounters()

    def _load_encounters(self) -> None:
        if not self.encounters_file.exists():
            system_logger.warning(f"Encounters file not found: {self.encounters_file}", source="WorldPlacer")
            return

        with open(self.encounters_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for region_name, rdata in data.get("regions", {}).items():
            tier = int(rdata.get("danger_tier", 1))
            self.encounters_by_region[region_name] = []
            for enc in rdata.get("encounters", []):
                encounter = WorldEncounter(
                    encounter_id=enc["encounter_id"],
                    name=enc["name"],
                    region=region_name,
                    landmark=enc.get("landmark", ""),
                    coordinates=enc.get("coordinates", {}),
                    map_id=enc.get("map_id", "m10_00_00_00"),
                    base_enemy_id=int(enc.get("base_enemy_id", 100000)),
                    danger_tier=tier,
                    description=enc.get("description", "")
                )
                self.encounters_by_region[region_name].append(encounter)
                self.all_encounters.append(encounter)

        system_logger.info(f"Loaded {len(self.all_encounters)} world encounters across {len(self.encounters_by_region)} regions.", source="WorldPlacer")

    def assign_encounters(
        self,
        presets: List[CharacterPreset],
        mode: PlacementMode = PlacementMode.THEMATIC_REGIONAL,
        seed: Optional[int] = None
    ) -> List[Tuple[CharacterPreset, WorldEncounter]]:
        """Assigns each preset to a unique or thematic world encounter."""
        if not self.all_encounters:
            raise RuntimeError("No world encounters available for placement.")

        rng = random.Random(seed) if seed is not None else random.Random()
        assignments: List[Tuple[CharacterPreset, WorldEncounter]] = []
        used_encounter_ids = set()

        for idx, preset in enumerate(presets):
            encounter = self._select_encounter_for_preset(preset, mode, rng, used_encounter_ids)
            used_encounter_ids.add(encounter.encounter_id)
            assignments.append((preset, encounter))
            system_logger.info(
                f"Assigned '{preset.name}' -> [{encounter.region}] {encounter.name} ({encounter.landmark})",
                source="WorldPlacer"
            )

        return assignments

    def _select_encounter_for_preset(
        self,
        preset: CharacterPreset,
        mode: PlacementMode,
        rng: random.Random,
        used_ids: set
    ) -> WorldEncounter:
        available = [e for e in self.all_encounters if e.encounter_id not in used_ids]
        if not available:
            # Recycle pool if phantoms exceed encounter points
            available = list(self.all_encounters)

        if mode == PlacementMode.THEMATIC_REGIONAL:
            # Match preferred region or danger tier
            region_matches = [e for e in available if e.region.lower() == preset.spawn_region.lower()]
            if region_matches:
                return region_matches[0]

            tier_matches = [e for e in available if e.danger_tier == preset.danger_tier]
            if tier_matches:
                return tier_matches[0]

        elif mode == PlacementMode.CHAOS_EXPEDITION:
            return rng.choice(available)

        # Fallback to closest available encounter
        return available[0]
