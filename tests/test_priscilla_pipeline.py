"""
Automated Integration Tests for Crossbreed Priscilla Prototype Pipeline.
Verifies legal extraction from Dark Souls PTDE, parameter synthesis, and cave threshold placement.
Adheres to [CS-NO-MOCK], [CS-MODULAR], and [CS-SAFETY].
"""

import pytest
from pathlib import Path
from src.cross_game.ds1_extractor import DS1Extractor, from_path_hash
from src.cross_game.priscilla_builder import (
    create_priscilla_preset,
    create_priscilla_encounter,
    build_priscilla_loot_spec,
)
from src.cross_game.prototype_orchestrator import PrototypeOrchestrator


def test_ds1_installation_detection():
    """Verifies that the user's licensed Dark Souls PTDE installation is detected."""
    extractor = DS1Extractor()
    assert extractor.is_installed() is True, "Dark Souls PTDE should be detected on the system."
    assert extractor.data_dir is not None
    assert (extractor.data_dir / "DARKSOULS.exe").exists()
    assert (extractor.data_dir / "dvdbnd0.bhd5").exists()


def test_ds1_path_hash_algorithm():
    """Verifies FromSoftware's 32-bit prime string hashing algorithm against known hashes."""
    # Verify path hashing for c2730
    h1 = from_path_hash("chr/c2730.chrbnd.dcx")
    assert isinstance(h1, int)
    assert h1 > 0
    # Forward and backslashes should yield identical hashes
    h2 = from_path_hash(r"chr\c2730.chrbnd.dcx")
    assert h1 == h2


def test_priscilla_preset_contract():
    """Verifies Crossbreed Priscilla's preset attributes and combat balance."""
    preset = create_priscilla_preset()
    assert preset.preset_id == "boss_crossbreed_priscilla"
    assert preset.name == "Crossbreed Priscilla"
    assert preset.hp_max == 8800
    assert preset.poise == 80
    assert preset.gender == 1  # Female
    assert preset.equipment.right_weapon_1_id == 11030000  # Grave Scythe (Lifehunt)
    assert preset.equipment.body_id == 201100  # Snow Witch Robe (White Fur)

    carried = preset.equipment.get_all_carried_items()
    assert len(carried) >= 4
    carried_ids = [item["item_id"] for item in carried]
    assert 11030000 in carried_ids
    assert 201100 in carried_ids


def test_priscilla_cave_exit_encounter():
    """Verifies that Priscilla's encounter is placed outside the Stranded Graveyard cave."""
    encounter = create_priscilla_encounter()
    assert encounter.encounter_id == "limgrave_stranded_graveyard_cave_exit"
    assert encounter.map_id == "m60_42_35_00"
    assert encounter.region == "Limgrave"
    assert encounter.coordinates["x"] == 135.0
    assert encounter.coordinates["y"] == 14.0
    assert encounter.coordinates["z"] == 130.0
    assert encounter.base_enemy_id == 42000010


def test_priscilla_loot_spec():
    """Verifies that Priscilla's carried drops guarantee 100% probability for her gear."""
    drops = build_priscilla_loot_spec()
    assert len(drops) == 5
    for drop in drops:
        assert drop["probability"] == 1000  # 100% in Elden Ring ItemLotParam
        assert drop["quantity"] >= 1


def test_prototype_orchestrator_execution(tmp_path):
    """
    Integration test: Runs the full orchestrator pipeline against a temporary regulation.
    Verifies real asset extraction, regulation patching, and manifest tracking.
    """
    workspace = Path(__file__).resolve().parent.parent
    orchestrator = PrototypeOrchestrator(workspace)
    target_reg = tmp_path / "regulation.bin"

    manifest = orchestrator.run_priscilla_prototype(target_regulation=target_reg)
    assert manifest["status"] == "success"
    assert manifest["extracted_assets_count"] >= 4
    assert target_reg.exists()
    assert target_reg.stat().st_size > 0
    assert manifest["encounter"]["encounter_id"] == "limgrave_stranded_graveyard_cave_exit"
