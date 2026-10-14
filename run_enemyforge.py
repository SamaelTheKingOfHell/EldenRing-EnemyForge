"""
EnemyForge: Application Launcher & Entry Point.
Launches the interactive Souls-themed desktop interface or executes headlessly via CLI.
Adheres to [CS-MODULAR] and [CS-GRANULARITY].
"""

import sys
import os
import argparse
import webbrowser
import threading
import time
from pathlib import Path

# Add project root to sys.path and set CWD for double-click safety on Windows
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
try:
    os.chdir(BASE_DIR)
except Exception:
    pass

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


def run_prototype_priscilla(base_dir: Path) -> int:
    """Extracts Crossbreed Priscilla from local DS1 PTDE and injects her at the tutorial cave exit."""
    from src.cross_game.prototype_orchestrator import PrototypeOrchestrator
    orchestrator = PrototypeOrchestrator(base_dir)
    try:
        manifest = orchestrator.run_priscilla_prototype()
        print(f"\n=======================================================")
        print(f" PROTOTYPE INJECTION SUCCESSFUL: Crossbreed Priscilla")
        print(f" Source Installation: {manifest['source_game_path']}")
        print(f" Extracted Assets: {manifest['extracted_assets_count']} files")
        print(f" Location: {manifest['encounter']['name']}")
        print(f" Coordinates: {manifest['encounter']['coordinates']}")
        print(f" Carried Drops: Lifehunt Scythe, White Fur Robe, Remembrance")
        print(f"=======================================================\n")
        return 0
    except Exception as e:
        system_logger.error(f"Priscilla prototype failed: {e}", source="CLI")
        print(f"Error: {e}")
        return 1


def run_qt_app(base_dir: Path) -> int:
    """Launches native Qt GUI desktop interface."""
    try:
        from src.qt_app import main as qt_main
        system_logger.info("Starting EnemyForge native Qt desktop interface...", source="Launcher")
        qt_main()
        return 0
    except Exception as e:
        import traceback
        traceback.print_exc()
        system_logger.error(f"Failed to start Qt desktop interface: {e}", source="Launcher")
        print(f"\n[FATAL] Qt GUI launch failed: {e}")
        return 1



def run_web_server(base_dir: Path, port: int = 8484, no_browser: bool = False) -> int:
    """Starts cross-platform web server and browser."""
    server = start_server(base_dir, port=port)
    url = f"http://127.0.0.1:{port}"

    print(f"\n=======================================================")
    print(f" EnemyForge Web Server running at: {url}")
    print(f" Press Ctrl+C to terminate.")
    print(f"=======================================================\n")

    if not no_browser:
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


def main() -> int:
    parser = argparse.ArgumentParser(description="EnemyForge: Character Preset Enemy & Carried Loot Injector")
    parser.add_argument("--web", action="store_true", help="Launch interactive browser web interface instead of native Qt GUI")
    parser.add_argument("--cli", action="store_true", help="Run headlessly via CLI without starting any GUI")
    parser.add_argument("--prototype-priscilla", action="store_true", help="Extract and port Crossbreed Priscilla from local DS1 PTDE to the tutorial cave exit")
    parser.add_argument("--generate-npcs", action="store_true", help="Synthesize NPC enemies from regulation modded sets or archetypes")
    parser.add_argument("--count", type=int, default=8, help="Number of NPCs to synthesize (default: 8)")
    parser.add_argument("--rollback", action="store_true", help="Roll back mod regulation to base game vanilla state")
    parser.add_argument("--port", type=int, default=8484, help="Port for the interactive web interface (default: 8484)")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically launch web browser when using --web")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent

    # Setup file logging
    system_logger.attach_file_handler(base_dir / "logs")

    if args.prototype_priscilla:
        return run_prototype_priscilla(base_dir)

    if args.generate_npcs:
        return run_generate_npcs(base_dir, count=args.count)

    if args.rollback:
        return run_rollback(base_dir)

    if args.cli:
        return run_headless_forge(base_dir)

    if args.web:
        return run_web_server(base_dir, port=args.port, no_browser=args.no_browser)

    return run_qt_app(base_dir)


if __name__ == "__main__":
    sys.exit(main())

