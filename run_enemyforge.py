"""
EnemyForge: Application Launcher & Entry Point.
Launches the interactive Souls-themed desktop interface or executes headlessly via CLI.
Adheres to [CS-MODULAR] and [CS-GRANULARITY].
"""

import sys
import argparse
import webbrowser
from pathlib import Path
from src.server import start_server
from src.logger import system_logger
from src.preset_loader import PresetLoader
from src.world_placer import WorldPlacer
from src.enemy_builder import EnemyBuilder
from src.regulation_manager import RegulationManager
from src.npc_generator import NPCGenerator
from src.models import EnemyForgeConfig, PlacementMode


def run_headless_forge(base_dir: Path) -> int:
    """Executes enemy creation and regulation patching headlessly via CLI."""
    system_logger.info("Executing headless EnemyForge pipeline...", source="CLI")
    config = EnemyForgeConfig()

    loader = PresetLoader(base_dir / "data" / "presets", base_dir / "input_presets")
    presets = loader.discover_and_load()
    if not presets:
        system_logger.error("No presets found to forge.", source="CLI")
        return 1

    placer = WorldPlacer(base_dir / "data" / "world_encounters.json")
    assignments = placer.assign_encounters(presets, mode=config.placement_mode)

    builder = EnemyBuilder()
    patch_spec = builder.build_patch_spec(assignments, config)

    reg_manager = RegulationManager(base_dir)
    source_reg = reg_manager.resolve_source_regulation()
    target_reg = base_dir / config.target_mod_dir / "regulation.bin"

    success = reg_manager.execute_patch(
        patch_spec=patch_spec,
        source_reg=source_reg,
        target_reg=target_reg,
        msg_dir=base_dir / "data"
    )

    if success:
        system_logger.info(f"Successfully forged {len(presets)} enemies into {target_reg}!", source="CLI")
        return 0
    else:
        system_logger.error("Headless forge failed.", source="CLI")
        return 1


def run_generate_npcs(base_dir: Path, count: int = 8) -> int:
    """Synthesizes NPC enemies from regulation modded sets or thematic archetypes."""
    system_logger.info(f"Synthesizing {count} NPC enemies from regulation / archetypes...", source="CLI")
    reg_manager = RegulationManager(base_dir)
    source_reg = reg_manager.resolve_source_regulation()
    catalog = None
    if source_reg and source_reg.exists():
        temp_catalog = base_dir / "data" / "gear_catalog.json"
        catalog = reg_manager.inspect_gear(source_reg, temp_catalog)

    generator = NPCGenerator(output_presets_dir=base_dir / "input_presets")
    if catalog and (catalog.get("modded_protectors") or catalog.get("modded_weapons")):
        generated = generator.generate_from_gear_catalog(catalog, count_limit=count)
    else:
        generated = generator.generate_thematic_presets(count=count)

    system_logger.info(f"Synthesized {len(generated)} NPC enemies into input_presets/!", source="CLI")
    return 0


def run_rollback(base_dir: Path) -> int:
    """Rolls back the target regulation to the base game vanilla fallback."""
    system_logger.info("Executing rollback to pristine base vanilla regulation...", source="CLI")
    reg_manager = RegulationManager(base_dir)
    target_reg = base_dir / "mod" / "regulation.bin"
    success = reg_manager.rollback_to_vanilla(target_reg)
    if success:
        system_logger.info("Rollback complete! Target regulation restored to base game state.", source="CLI")
        return 0
    else:
        system_logger.error("Rollback failed.", source="CLI")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="EnemyForge: Character Preset Enemy & Carried Loot Injector")
    parser.add_argument("--cli", action="store_true", help="Run headlessly via CLI without starting the web UI")
    parser.add_argument("--generate-npcs", action="store_true", help="Synthesize NPC enemies from regulation modded sets or archetypes")
    parser.add_argument("--count", type=int, default=8, help="Number of NPCs to synthesize (default: 8)")
    parser.add_argument("--rollback", action="store_true", help="Roll back mod regulation to base game vanilla state")
    parser.add_argument("--port", type=int, default=8484, help="Port for the interactive interface (default: 8484)")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically launch web browser")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent

    # Setup file logging
    system_logger.attach_file_handler(base_dir / "logs")

    if args.generate_npcs:
        return run_generate_npcs(base_dir, count=args.count)

    if args.rollback:
        return run_rollback(base_dir)

    if args.cli:
        return run_headless_forge(base_dir)

    server = start_server(base_dir, port=args.port)
    url = f"http://127.0.0.1:{args.port}"

    print(f"\n=======================================================")
    print(f" EnemyForge is running at: {url}")
    print(f" Press Ctrl+C to terminate.")
    print(f"=======================================================\n")

    if not args.no_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down EnemyForge...")
        server.server_close()
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
