"""
PyQt6 / PySide6 Desktop GUI for EnemyForge.

Features:
- Dark Souls fantasy theme with gold accents and responsive layout
- Prominent Mod Manager warning banner
- Schema-driven parameter configuration cards [CS-DECOUPLE]
- Interactive Preset & Carried Loot Inspector
- Asynchronous Cross-Game Priscilla prototype extractor and injector
- Real-time streaming Developer Console drawer [CS-DEBUG]
- One-click rollback and pristine vanilla restoration [CS-SAFETY]
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QFrame, QScrollArea, QMessageBox,
        QSplitter
    )
    from PySide6.QtCore import Qt, QTimer
except (ImportError, Exception):
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QFrame, QScrollArea, QMessageBox,
        QSplitter
    )
    from PyQt6.QtCore import Qt, QTimer

from src.models import EnemyForgeConfig, PlacementMode
from src.preset_loader import PresetLoader
from src.world_placer import WorldPlacer
from src.regulation_manager import RegulationManager
from src.npc_generator import NPCGenerator
from src.logger import system_logger
from src.ui.theme import DARK_SOULS_QSS
from src.ui.param_schema import get_generator_param_descriptors
from src.ui.param_widget_factory import ParamWidgetFactory
from src.ui.preset_inspector import PresetInspectorWidget
from src.ui.prototype_card import PrototypeCard
from src.ui.console_drawer import ConsoleDrawer
from src.ui.forge_worker import ForgeWorker


class EnemyForgeMainWindow(QMainWindow):
    """Main Qt Desktop Window for EnemyForge."""

    def __init__(self, base_dir: Path):
        super().__init__()
        self.base_dir = base_dir
        self.config = EnemyForgeConfig()
        self.preset_loader = PresetLoader(base_dir / "data" / "presets", base_dir / "input_presets")
        self.encounters_path = base_dir / "data" / "world_encounters.json"
        self.placer = WorldPlacer(self.encounters_path)
        self.reg_manager = RegulationManager(base_dir)

        self.presets = []
        self.encounters = []
        self.worker: Optional[ForgeWorker] = None
        self.banner_collapsed = False

        self.setWindowTitle("EnemyForge: Elden Ring Enemy & Carried Loot Injector (Qt Edition)")
        self.resize(1180, 860)
        self.setMinimumSize(880, 560)
        self.setStyleSheet(DARK_SOULS_QSS)

        self._build_ui()
        self._load_data()

        self.log_timer = QTimer(self)
        self.log_timer.timeout.connect(self.console_drawer.poll_logs)
        self.log_timer.start(1200)

    def _build_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(14, 12, 14, 12)
        main_layout.setSpacing(8)

        # Header
        header = QHBoxLayout()
        title = QLabel("ENEMYFORGE: ELDEN RING SPAWN & CARRIED LOOT INJECTOR")
        title.setStyleSheet("font-size: 17px; font-weight: bold; color: #ffd475; letter-spacing: 1.5px;")
        header.addWidget(title)

        self.preset_badge = QLabel("0 Presets")
        self.preset_badge.setStyleSheet("background-color: #161924; color: #c5a059; border: 1px solid rgba(197, 160, 89, 0.35); border-radius: 4px; padding: 3px 8px; font-size: 11px; font-weight: bold;")
        header.addWidget(self.preset_badge)
        header.addStretch()

        self.banner_toggle_btn = QPushButton("▲ Collapse Notice")
        self.banner_toggle_btn.clicked.connect(self._toggle_banner)
        header.addWidget(self.banner_toggle_btn)

        self.dev_console_btn = QPushButton("⚙ Dev Console")
        self.dev_console_btn.clicked.connect(self._toggle_dev_console)
        header.addWidget(self.dev_console_btn)
        main_layout.addLayout(header)

        # Splitter Layout
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_splitter.setChildrenCollapsible(False)
        self.main_splitter.setHandleWidth(8)

        # Top Configuration Container (Scrollable)
        top_scroll = QScrollArea()
        top_scroll.setWidgetResizable(True)
        top_scroll.setFrameShape(QFrame.Shape.NoFrame)

        top_container = QWidget()
        top_layout = QVBoxLayout(top_container)
        top_layout.setContentsMargins(0, 0, 4, 0)
        top_layout.setSpacing(10)

        # Banner Frame
        self.banner_frame = QFrame()
        self.banner_frame.setProperty("class", "banner")
        banner_vbox = QVBoxLayout(self.banner_frame)
        banner_vbox.setContentsMargins(12, 10, 12, 10)
        banner_title = QLabel("⚠️ USING MOD ENGINE 2 OR A MOD MANAGER? READ THIS FIRST:")
        banner_title.setStyleSheet("font-weight: bold; color: #ffd475; font-size: 13px;")
        banner_vbox.addWidget(banner_title)
        self.banner_desc = QLabel(
            "EnemyForge injects roaming enemies, bosses, and their guaranteed carried drop tables "
            "directly into your mod's regulation.bin without overwriting other mods."
        )
        self.banner_desc.setWordWrap(True)
        banner_vbox.addWidget(self.banner_desc)
        top_layout.addWidget(self.banner_frame)

        # Parameter cards
        descriptors = get_generator_param_descriptors()
        paths_card, self.path_ctrls = ParamWidgetFactory.build_paths_card(
            descriptors, self.config, self._on_param_changed,
            on_mod_engine=self._set_mod_engine_reg,
            on_vanilla=self._set_vanilla_reg,
            on_backup=self._create_backup,
            on_rollback=self._rollback,
            parent=top_container
        )
        top_layout.addWidget(paths_card)

        # Spawn rules and synthesis row
        rules_row = QHBoxLayout()
        rules_card, _ = ParamWidgetFactory.build_spawn_rules_card(
            descriptors, self.config, self._on_param_changed, parent=top_container
        )
        rules_row.addWidget(rules_card, stretch=1)

        synth_card, _ = ParamWidgetFactory.build_synthesizer_card(
            descriptors, on_synthesize=self._synthesize_npcs, parent=top_container
        )
        rules_row.addWidget(synth_card, stretch=1)
        top_layout.addLayout(rules_row)

        # Prototype Card for Crossbreed Priscilla
        self.proto_card = PrototypeCard(self.base_dir, on_completed=self._on_prototype_completed, parent=top_container)
        top_layout.addWidget(self.proto_card)

        top_scroll.setWidget(top_container)
        self.main_splitter.addWidget(top_scroll)

        # Middle / Bottom Inspector Section
        bottom_container = QWidget()
        bottom_layout = QVBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 4, 0, 0)
        bottom_layout.setSpacing(8)

        self.inspector = PresetInspectorWidget(bottom_container)
        bottom_layout.addWidget(self.inspector, stretch=1)

        # Action Bar
        action_layout = QHBoxLayout()
        self.rollback_btn = QPushButton("Rollback to Vanilla Regulation")
        self.rollback_btn.setProperty("class", "danger")
        self.rollback_btn.clicked.connect(self._rollback)
        action_layout.addWidget(self.rollback_btn)

        self.refresh_btn = QPushButton("🔄 Refresh Presets")
        self.refresh_btn.clicked.connect(self._load_data)
        action_layout.addWidget(self.refresh_btn)
        action_layout.addStretch()

        self.forge_btn = QPushButton("Forge Enemies & Inject Regulation")
        self.forge_btn.setProperty("class", "primary")
        self.forge_btn.setFixedHeight(38)
        self.forge_btn.clicked.connect(self._forge_enemies)
        action_layout.addWidget(self.forge_btn)

        bottom_layout.addLayout(action_layout)
        self.main_splitter.addWidget(bottom_container)
        self.main_splitter.setSizes([450, 350])
        main_layout.addWidget(self.main_splitter)

        self.console_drawer = ConsoleDrawer(self)

    def _load_data(self):
        self.presets = self.preset_loader.discover_and_load()
        self.placer = WorldPlacer(self.encounters_path)
        self.encounters = self.placer.all_encounters
        self.inspector.set_data(self.presets, self.encounters)
        self.preset_badge.setText(f"{len(self.presets)} Presets Discovered")
        system_logger.info(f"Loaded {len(self.presets)} presets and {len(self.encounters)} world encounters.", source="UI")

    def _on_param_changed(self, key: str, val: Any):
        if hasattr(self.config, key):
            setattr(self.config, key, val)
            system_logger.debug(f"Param changed: {key} = {val}", source="UI")

    def _toggle_banner(self):
        self.banner_collapsed = not self.banner_collapsed
        self.banner_desc.setVisible(not self.banner_collapsed)
        self.banner_toggle_btn.setText("▼ Expand Notice" if self.banner_collapsed else "▲ Collapse Notice")

    def _toggle_dev_console(self):
        if self.console_drawer.isVisible():
            self.console_drawer.hide()
        else:
            self.console_drawer.show()

    def _set_mod_engine_reg(self):
        p = str(self.base_dir / "mod" / "regulation.bin")
        self.path_ctrls["active_regulation_path"].setText(p)
        self._on_param_changed("active_regulation_path", p)

    def _set_vanilla_reg(self):
        p = str(self.base_dir / "data" / "regulation.bin.vanilla_fallback")
        self.path_ctrls["active_regulation_path"].setText(p)
        self._on_param_changed("active_regulation_path", p)

    def _create_backup(self):
        src = self.reg_manager.resolve_source_regulation()
        if not src or not src.exists():
            QMessageBox.warning(self, "Backup Warning", "No valid source regulation.bin found to back up.")
            return
        bak = self.reg_manager.backup_manager.create_backup(src)
        QMessageBox.information(self, "Backup Created", f"Successfully created backup:\n{bak.name}")

    def _rollback(self):
        reply = QMessageBox.question(
            self, "Confirm Rollback",
            "Are you sure you want to restore the pristine vanilla regulation.bin?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            target = self.base_dir / "mod" / "regulation.bin"
            if self.reg_manager.rollback_to_vanilla(target):
                QMessageBox.information(self, "Rollback Complete", "Target regulation restored to base game state.")
            else:
                QMessageBox.critical(self, "Rollback Failed", "Failed to restore vanilla regulation.")

    def _synthesize_npcs(self, count: int):
        generator = NPCGenerator(output_presets_dir=self.base_dir / "input_presets")
        generated = generator.generate_thematic_presets(count=count)
        QMessageBox.information(self, "Synthesis Complete", f"Synthesized {len(generated)} NPC enemy presets into input_presets/!")
        self._load_data()

    def _on_prototype_completed(self, manifest: dict):
        self._load_data()
        QMessageBox.information(
            self, "Priscilla Injected",
            f"Crossbreed Priscilla successfully injected!\n"
            f"Location: {manifest.get('encounter', {}).get('name')}\n"
            f"Drops: Lifehunt Scythe, White Fur Robe, Remembrance."
        )

    def _forge_enemies(self):
        if not self.presets:
            QMessageBox.warning(self, "Forge Warning", "No enemy presets loaded to forge.")
            return

        self.forge_btn.setEnabled(False)
        self.forge_btn.setText("Forging Regulation...")
        self.worker = ForgeWorker(self.base_dir, self.config, self.presets, self.encounters_path)
        self.worker.finished_success.connect(self._on_forge_success)
        self.worker.failed.connect(self._on_forge_failed)
        self.worker.start()

    def _on_forge_success(self, msg: str):
        self.forge_btn.setEnabled(True)
        self.forge_btn.setText("Forge Enemies & Inject Regulation")
        QMessageBox.information(self, "Forge Complete", msg)

    def _on_forge_failed(self, err: str):
        self.forge_btn.setEnabled(True)
        self.forge_btn.setText("Forge Enemies & Inject Regulation")
        QMessageBox.critical(self, "Forge Error", err)


def main():
    """Main desktop launcher for EnemyForge."""
    app = QApplication(sys.argv)
    base_dir = Path(__file__).resolve().parent.parent
    window = EnemyForgeMainWindow(base_dir)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
