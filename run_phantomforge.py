"""
PhantomForge: Application Launcher & Entry Point.
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
from src.phantom_builder import PhantomBuilder
from src.regulation_manager import RegulationManager
from src.models import PhantomForgeConfig, PlacementMode


def run_headless_forge(base_dir: Path) -> int:
    """Executes phantom creation and regulation patching headlessly via CLI."""
    system_logger.info("Executing headless PhantomForge pipeline...", source="CLI")
    config = PhantomForgeConfig()

    loader = PresetLoader(base_dir / "data" / "presets", base_dir / "input_presets")
    presets = loader.discover_and_load()
    if not presets:
        system_logger.error("No presets found to forge.", source="CLI")
        return 1

    placer = WorldPlacer(base_dir / "data" / "world_encounters.json")
    assignments = placer.assign_encounters(presets, mode=config.placement_mode)

    builder = PhantomBuilder()
    patch_spec = builder.build_patch_spec(assignments, config)

    reg_manager = RegulationManager(base_dir)
    latest_bak = reg_manager.backup_mgr.get_latest_backup()
    source_reg = latest_bak or (base_dir / "regulation.bin")
    target_reg = base_dir / config.target_mod_dir / "regulation.bin"

    success = reg_manager.execute_patch(
        patch_spec=patch_spec,
        source_reg=source_reg,
        target_reg=target_reg,
        msg_dir=base_dir / "data"
    )

    if success:
        system_logger.info(f"Successfully forged {len(presets)} phantoms into {target_reg}!", source="CLI")
        return 0
    else:
        system_logger.error("Headless forge failed.", source="CLI")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="PhantomForge: Character Preset Enemy & Carried Loot Injector")
    parser.add_argument("--cli", action="store_true", help="Run headlessly via CLI without starting the web UI")
    parser.add_argument("--port", type=int, default=8484, help="Port for the interactive interface (default: 8484)")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically launch web browser")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent

    # Setup file logging
    system_logger.attach_file_handler(base_dir / "logs")

    if args.cli:
        return run_headless_forge(base_dir)

    server = start_server(base_dir, port=args.port)
    url = f"http://127.0.0.1:{args.port}"

    print(f"\n=======================================================")
    print(f" PhantomForge is running at: {url}")
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
        print("\nShutting down PhantomForge...")
        server.server_close()
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
