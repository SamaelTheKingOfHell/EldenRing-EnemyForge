"""
Parameter schema and metadata descriptors for EnemyForge.

Defines input parameter types, categories/purposes, defaults, and bounds
for the enemy generator and encounter placement engine.
Adheres to [CS-MODULAR] and [CS-DECOUPLE].
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple, Union
from src.models import PlacementMode


class ParamType(Enum):
    """Supported parameter primitive and presentation types."""
    BOOL = auto()
    INT = auto()
    FLOAT = auto()
    ENUM = auto()
    STRING = auto()
    PATH_FILE = auto()
    PATH_DIR = auto()


class ParamPurpose(Enum):
    """
    Functional purpose and grouping for parameters.
    Governs placement and card container organization in the UI.
    """
    PATHS = "Active Regulation & Paths"
    SPAWN_RULES = "Encounter & Placement Rules"
    NPC_SYNTHESIS = "Autonomous NPC Synthesizer"
    PROTOTYPE = "Cross-Game Boss Prototype"


@dataclass
class ParamDescriptor:
    """
    Metadata describing an engine/generator parameter.
    Decouples parameter definition from UI layout and widget rendering.
    """
    key: str
    label: str
    param_type: ParamType
    purpose: ParamPurpose
    description: str = ""
    default: Any = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    step: Optional[Union[int, float]] = None
    unit: Optional[str] = None
    enum_class: Optional[type] = None
    enum_options: Optional[List[Tuple[str, Any]]] = None
    file_filter: Optional[str] = None


def get_generator_param_descriptors() -> List[ParamDescriptor]:
    """
    Returns the comprehensive list of input parameters for EnemyForge,
    categorized by purpose and typed for automatic UI generation.
    """
    return [
        # --- Group 1: Paths & Regulation ---
        ParamDescriptor(
            key="active_regulation_path",
            label="Active Regulation Path",
            param_type=ParamType.PATH_FILE,
            purpose=ParamPurpose.PATHS,
            description="Path to your active regulation.bin (e.g. Mod Engine 2 mod/regulation.bin).",
            default="",
            file_filter="Regulation Files (*.bin);;All Files (*.*)"
        ),
        ParamDescriptor(
            key="target_mod_dir",
            label="Target Mod Directory",
            param_type=ParamType.PATH_DIR,
            purpose=ParamPurpose.PATHS,
            description="Destination directory where patched regulation.bin will be written (default: mod).",
            default="mod"
        ),
        ParamDescriptor(
            key="base_game_dir",
            label="Game Installation Directory",
            param_type=ParamType.PATH_DIR,
            purpose=ParamPurpose.PATHS,
            description="Elden Ring game root folder containing vanilla regulation.bin.",
            default=""
        ),

        # --- Group 2: Encounter & Placement Rules ---
        ParamDescriptor(
            key="placement_mode",
            label="Placement Mode",
            param_type=ParamType.ENUM,
            purpose=ParamPurpose.SPAWN_RULES,
            description="Strategy used to distribute enemy encounters across the Lands Between.",
            default=PlacementMode.THEMATIC_REGIONAL.value,
            enum_class=PlacementMode,
            enum_options=[
                ("Thematic Regional (Matched to Region & Level)", PlacementMode.THEMATIC_REGIONAL),
                ("Roaming Invasions (Red Phantom NPC Invasions)", PlacementMode.ROAMING_INVASIONS),
                ("Champion Duels (Evergaols & Coliseum Arenas)", PlacementMode.CHAMPION_DUELS),
                ("Chaos Expedition (Randomized High-Risk Spawns)", PlacementMode.CHAOS_EXPEDITION),
            ]
        ),
        ParamDescriptor(
            key="scaling_factor",
            label="Combat Scaling Factor",
            param_type=ParamType.FLOAT,
            purpose=ParamPurpose.SPAWN_RULES,
            description="Global HP and damage multiplier applied to spawned enemies (1.0 = standard vanilla scale).",
            default=1.0,
            min_value=0.25,
            max_value=5.0,
            step=0.1,
            unit="x"
        ),
        ParamDescriptor(
            key="enable_loot_drops",
            label="Guarantee 100% Carried Loot Drops",
            param_type=ParamType.BOOL,
            purpose=ParamPurpose.SPAWN_RULES,
            description="Defeating enemies guarantees 100% drops of their exact equipped weapons, shields, and armor.",
            default=True
        ),

        # --- Group 3: Autonomous NPC Synthesizer ---
        ParamDescriptor(
            key="npc_count",
            label="NPC Synthesis Count",
            param_type=ParamType.INT,
            purpose=ParamPurpose.NPC_SYNTHESIS,
            description="Number of hostile NPC presets to synthesize automatically from gear catalog or archetypes.",
            default=8,
            min_value=1,
            max_value=32,
            step=1,
            unit="enemies"
        ),
    ]
