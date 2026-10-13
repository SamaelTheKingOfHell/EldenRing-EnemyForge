"""
Asynchronous Forge Worker thread for EnemyForge Qt GUI.

Executes enemy encounter assignment, patch specification generation,
and regulation patching in a background thread to prevent UI freezing.
Adheres to [CS-MODULAR] and [CS-DECOUPLE].
"""

from pathlib import Path
try:
    from PySide6.QtCore import QThread, Signal
except (ImportError, Exception):
    from PyQt6.QtCore import QThread, Signal

from src.models import EnemyForgeConfig
from src.world_placer import WorldPlacer
from src.enemy_builder import EnemyBuilder
from src.regulation_manager import RegulationManager


class ForgeWorker(QThread):
    """Executes enemy building and regulation injection asynchronously."""
    finished_success = Signal(str)
    failed = Signal(str)

    def __init__(self, base_dir: Path, config: EnemyForgeConfig, presets: list, encounters_path: Path):
        super().__init__()
        self.base_dir = base_dir
        self.config = config
        self.presets = presets
        self.encounters_path = encounters_path

    def run(self):
        try:
            placer = WorldPlacer(self.encounters_path)
            assignments = placer.assign_encounters(self.presets, mode=self.config.placement_mode)
            builder = EnemyBuilder()
            patch_spec = builder.build_patch_spec(assignments, self.config)

            reg_manager = RegulationManager(self.base_dir)
            source_reg = reg_manager.resolve_source_regulation()
            target_reg = self.base_dir / self.config.target_mod_dir / "regulation.bin"

            success = reg_manager.execute_patch(
                patch_spec=patch_spec,
                source_reg=source_reg,
                target_reg=target_reg,
                msg_dir=self.base_dir / "data"
            )
            if success:
                self.finished_success.emit(f"Successfully forged {len(assignments)} enemies into {target_reg}!")
            else:
                self.failed.emit("Regulation patching failed. Check developer console logs.")
        except Exception as e:
            self.failed.emit(str(e))
