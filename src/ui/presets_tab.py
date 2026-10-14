"""
Hostile Presets and Roaming Spawns Tab Widget for EnemyForge Qt GUI.

Encapsulates parameter controls, preset inspection, and regulation patching actions.
Adheres to [CS-MODULAR] and [CS-DECOUPLE].
"""

from typing import Callable, Any, Optional, List
from pathlib import Path

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
        QScrollArea, QFrame
    )
    from PySide6.QtCore import Qt
except (ImportError, Exception):
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
        QScrollArea, QFrame
    )
    from PyQt6.QtCore import Qt

from src.models import EnemyForgeConfig, CharacterPreset, WorldEncounter
from src.ui.param_schema import get_generator_param_descriptors
from src.ui.param_widget_factory import ParamWidgetFactory
from src.ui.preset_inspector import PresetInspectorWidget


class HostilePresetsTab(QWidget):
    """Tab 1: Hostile Presets, Roaming Spawns, Carried Loot Inspector, and Patch Actions."""

    def __init__(
        self,
        base_dir: Path,
        config: EnemyForgeConfig,
        on_param_changed: Callable[[str, Any], None],
        on_set_mod_engine: Callable[[], None],
        on_set_vanilla: Callable[[], None],
        on_create_backup: Callable[[], None],
        on_rollback: Callable[[], None],
        on_synthesize: Callable[[int], None],
        on_refresh: Callable[[], None],
        on_forge: Callable[[], None],
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.base_dir = base_dir
        self.config = config
        self.on_param_changed = on_param_changed
        self.on_set_mod_engine = on_set_mod_engine
        self.on_set_vanilla = on_set_vanilla
        self.on_create_backup = on_create_backup
        self.on_rollback = on_rollback
        self.on_synthesize = on_synthesize
        self.on_refresh = on_refresh
        self.on_forge = on_forge

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 8, 4, 4)
        layout.setSpacing(8)

        # Top scroll container for configuration cards
        top_scroll = QScrollArea()
        top_scroll.setWidgetResizable(True)
        top_scroll.setFrameShape(QFrame.Shape.NoFrame)
        top_scroll.setMaximumHeight(260)

        top_container = QWidget()
        top_layout = QVBoxLayout(top_container)
        top_layout.setContentsMargins(0, 0, 4, 0)
        top_layout.setSpacing(8)

        descriptors = get_generator_param_descriptors()
        paths_card, self.path_ctrls = ParamWidgetFactory.build_paths_card(
            descriptors, self.config, self.on_param_changed,
            on_mod_engine=self.on_set_mod_engine,
            on_vanilla=self.on_set_vanilla,
            on_backup=self.on_create_backup,
            on_rollback=self.on_rollback,
            parent=top_container
        )
        top_layout.addWidget(paths_card)

        rules_row = QHBoxLayout()
        rules_card, _ = ParamWidgetFactory.build_spawn_rules_card(
            descriptors, self.config, self.on_param_changed, parent=top_container
        )
        rules_row.addWidget(rules_card, stretch=1)

        synth_card, _ = ParamWidgetFactory.build_synthesizer_card(
            descriptors, on_synthesize=self.on_synthesize, parent=top_container
        )
        rules_row.addWidget(synth_card, stretch=1)
        top_layout.addLayout(rules_row)

        top_scroll.setWidget(top_container)
        layout.addWidget(top_scroll)

        # Preset Inspector Widget
        self.inspector = PresetInspectorWidget(self)
        layout.addWidget(self.inspector, stretch=1)

        # Action Bar
        action_layout = QHBoxLayout()
        self.rollback_btn = QPushButton("Rollback to Vanilla Regulation")
        self.rollback_btn.setProperty("class", "danger")
        self.rollback_btn.clicked.connect(self.on_rollback)
        action_layout.addWidget(self.rollback_btn)

        self.refresh_btn = QPushButton("🔄 Refresh Presets")
        self.refresh_btn.clicked.connect(self.on_refresh)
        action_layout.addWidget(self.refresh_btn)
        action_layout.addStretch()

        self.forge_btn = QPushButton("Forge Enemies & Inject Regulation")
        self.forge_btn.setProperty("class", "primary")
        self.forge_btn.setFixedHeight(38)
        self.forge_btn.clicked.connect(self.on_forge)
        action_layout.addWidget(self.forge_btn)

        layout.addLayout(action_layout)

    def set_data(self, presets: List[CharacterPreset], encounters: List[WorldEncounter]):
        self.inspector.set_data(presets, encounters)
