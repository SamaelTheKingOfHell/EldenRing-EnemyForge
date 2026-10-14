"""
EnemyForge PyQt6 / PySide6 Desktop GUI.
Tabs: Hostile Presets & Roaming Spawns, Cross-Game Monster Forge, Developer Console.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QFrame, QMessageBox, QTabWidget, QTextEdit
    )
    from PySide6.QtCore import Qt, QTimer
except (ImportError, Exception):
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QFrame, QMessageBox, QTabWidget, QTextEdit
    )
    from PyQt6.QtCore import Qt, QTimer

from src.models import EnemyForgeConfig
from src.preset_loader import PresetLoader
from src.world_placer import WorldPlacer
from src.regulation_manager import RegulationManager
from src.npc_generator import NPCGenerator
from src.cross_game.ds1_extractor import DS1Extractor
from src.logger import system_logger
from src.ui.theme import DARK_SOULS_QSS
from src.ui.presets_tab import HostilePresetsTab
from src.ui.ds1_config_card import DS1ConfigCard
from src.ui.priscilla_pipeline_widget import PriscillaPipelineWidget
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

        self.presets, self.encounters = [], []
        self.worker: Optional[ForgeWorker] = None
        self.banner_collapsed = False

        self.setWindowTitle("EnemyForge: Elden Ring Enemy & Carried Loot Injector (Qt Edition)")
        self.resize(1200, 880); self.setMinimumSize(900, 600); self.setStyleSheet(DARK_SOULS_QSS)

        self._build_ui()
        self._load_data()

        self.log_timer = QTimer(self)
        self.log_timer.timeout.connect(self._poll_logs)
        self.log_timer.start(1200)

    @property
    def inspector(self): return self.presets_tab.inspector

    @property
    def path_ctrls(self): return self.presets_tab.path_ctrls

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

        b_style = "border-radius: 4px; padding: 3px 8px; font-size: 11px; font-weight: bold;"
        self.preset_badge = QLabel("0 Presets")
        self.preset_badge.setStyleSheet(f"background-color: #161924; color: #c5a059; border: 1px solid rgba(197, 160, 89, 0.35); {b_style}")
        header.addWidget(self.preset_badge)
        self.ds1_badge = QLabel("DS1: Checking...")
        self.ds1_badge.setStyleSheet(f"background-color: #161924; color: #ffd475; border: 1px solid rgba(197, 160, 89, 0.35); {b_style}")
        header.addWidget(self.ds1_badge); header.addStretch()

        self.banner_toggle_btn = QPushButton("▲ Collapse Notice")
        self.banner_toggle_btn.clicked.connect(self._toggle_banner)
        header.addWidget(self.banner_toggle_btn)

        self.dev_console_btn = QPushButton("⚙ Dev Console")
        self.dev_console_btn.clicked.connect(self._toggle_dev_console)
        header.addWidget(self.dev_console_btn)
        main_layout.addLayout(header)

        # Mod Manager Notice Banner
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
        main_layout.addWidget(self.banner_frame)

        # Main Tabbed Interface
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, stretch=1)

        # Tab 1: Hostile Presets & Roaming Spawns
        self.presets_tab = HostilePresetsTab(
            base_dir=self.base_dir,
            config=self.config,
            on_param_changed=self._on_param_changed,
            on_set_mod_engine=self._set_mod_engine_reg,
            on_set_vanilla=self._set_vanilla_reg,
            on_create_backup=self._create_backup,
            on_rollback=self._rollback,
            on_synthesize=self._synthesize_npcs,
            on_refresh=self._load_data,
            on_forge=self._forge_enemies,
            parent=self.tabs
        )
        self.tabs.addTab(self.presets_tab, "⚔️ Hostile Presets & Roaming Spawns")

        # Tab 2: Cross-Game Monster Forge (Dark Souls ➔ Elden Ring)
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        tab2_layout.setContentsMargins(4, 8, 4, 4)
        tab2_layout.setSpacing(10)

        self.ds1_card = DS1ConfigCard(
            initial_path=self.config.ds1_ptde_dir,
            on_path_changed=self._on_ds1_path_changed,
            parent=tab2
        )
        tab2_layout.addWidget(self.ds1_card)

        self.pipeline_widget = PriscillaPipelineWidget(
            base_dir=self.base_dir,
            ds1_path_getter=lambda: self.ds1_card.current_path,
            target_reg_getter=self._get_target_reg,
            parent=tab2
        )
        self.pipeline_widget.pipeline_finished.connect(self._on_priscilla_finished)
        tab2_layout.addWidget(self.pipeline_widget, stretch=1)

        self.tabs.addTab(tab2, "❄️ Cross-Game: Crossbreed Priscilla (DS1 ➔ ER)")
        self.proto_card = self.pipeline_widget  # Backwards compatibility

        # Tab 3: Embedded Developer Console
        tab3 = QWidget()
        tab3_layout = QVBoxLayout(tab3)
        tab3_layout.setContentsMargins(6, 8, 6, 6)
        self.embedded_console = QTextEdit()
        self.embedded_console.setReadOnly(True)
        self.embedded_console.setStyleSheet("background-color: #07080a; color: #8ee3a4; font-family: monospace; font-size: 11px;")
        tab3_layout.addWidget(self.embedded_console)
        tab3_clear = QPushButton("Clear Console")
        tab3_clear.clicked.connect(self.embedded_console.clear)
        tab3_layout.addWidget(tab3_clear, alignment=Qt.AlignmentFlag.AlignLeft)
        self.tabs.addTab(tab3, "📜 Developer Console & Logs")
        self.console_drawer = ConsoleDrawer(self)

    def _load_data(self):
        self.presets = self.preset_loader.discover_and_load()
        self.placer = WorldPlacer(self.encounters_path)
        self.encounters = self.placer.all_encounters
        self.presets_tab.set_data(self.presets, self.encounters)
        self.pipeline_widget.set_encounters(self.encounters)
        self.preset_badge.setText(f"{len(self.presets)} Presets Discovered")
        self._update_ds1_badge()
        system_logger.info(f"Loaded {len(self.presets)} presets and {len(self.encounters)} world encounters.", source="UI")

    def _update_ds1_badge(self):
        if not hasattr(self, "ds1_badge") or not hasattr(self, "ds1_card"):
            return
        extractor = DS1Extractor(data_dir=Path(self.ds1_card.current_path) if self.ds1_card.current_path else None)
        ok = extractor.is_installed()
        self.ds1_badge.setText("✓ DS1 PTDE Connected" if ok else "⚠️ DS1 PTDE Not Found")
        bg, fg, bd = ("#062b16", "#8ee3a4", "#10b981") if ok else ("#2b1010", "#fca5a5", "#ef4444")
        self.ds1_badge.setStyleSheet(f"background-color: {bg}; color: {fg}; border: 1px solid {bd}; border-radius: 4px; padding: 3px 8px; font-size: 11px; font-weight: bold;")

    def _on_ds1_path_changed(self, new_path: str):
        self.config.ds1_ptde_dir = new_path
        self._update_ds1_badge()

    def _on_param_changed(self, key: str, val: Any):
        if hasattr(self.config, key):
            setattr(self.config, key, val)
            system_logger.debug(f"Param changed: {key} = {val}", source="UI")

    def _toggle_banner(self):
        self.banner_collapsed = not self.banner_collapsed
        self.banner_desc.setVisible(not self.banner_collapsed)
        self.banner_toggle_btn.setText("▼ Expand Notice" if self.banner_collapsed else "▲ Collapse Notice")

    def _toggle_dev_console(self):
        self.console_drawer.hide() if self.console_drawer.isVisible() else self.console_drawer.show()

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
            self, "Confirm Rollback", "Are you sure you want to restore the pristine vanilla regulation.bin?",
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

    def _on_priscilla_finished(self, manifest: dict):
        self._load_data()
        loc = manifest.get('encounter', {}).get('name')
        QMessageBox.information(self, "Priscilla Pipeline Success", f"Crossbreed Priscilla pipeline completed!\nLocation: {loc}\nDrops: Lifehunt Scythe, White Fur Robe, Remembrance.")

    def _forge_enemies(self):
        if not self.presets:
            QMessageBox.warning(self, "Forge Warning", "No enemy presets loaded to forge.")
            return
        self.presets_tab.forge_btn.setEnabled(False)
        self.presets_tab.forge_btn.setText("Forging Regulation...")
        self.worker = ForgeWorker(self.base_dir, self.config, self.presets, self.encounters_path)
        self.worker.finished_success.connect(self._on_forge_success)
        self.worker.failed.connect(self._on_forge_failed)
        self.worker.start()

    def _reset_forge_btn(self):
        self.presets_tab.forge_btn.setEnabled(True)
        self.presets_tab.forge_btn.setText("Forge Enemies & Inject Regulation")

    def _get_target_reg(self) -> str:
        ctrl = getattr(self, "path_ctrls", {}).get("target_regulation")
        return ctrl.text().strip() if ctrl else str(self.config.target_regulation or "")

    def _on_forge_success(self, msg: str):
        self._reset_forge_btn(); QMessageBox.information(self, "Forge Complete", msg)

    def _on_forge_failed(self, err: str):
        self._reset_forge_btn(); QMessageBox.critical(self, "Forge Error", err)

    def _poll_logs(self):
        self.console_drawer.poll_logs()
        recent = system_logger.get_in_memory_logs(limit=40)
        if recent:
            txt = "\n".join(f"[{l['timestamp']}] [{l['level']}] [{l['source']}] {l['message']}" for l in recent)
            if self.embedded_console.toPlainText() != txt:
                self.embedded_console.setPlainText(txt)
                self.embedded_console.verticalScrollBar().setValue(self.embedded_console.verticalScrollBar().maximum())


def main():
    """Main desktop launcher for EnemyForge."""
    app = QApplication(sys.argv)
    base_dir = Path(__file__).resolve().parent.parent
    window = EnemyForgeMainWindow(base_dir)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
