"""
Parameter Widget Factory for EnemyForge Qt GUI.

Constructs and binds styled UI controls and parameter cards based on ParamDescriptor types.
Adheres to [CS-MODULAR] and [CS-DECOUPLE].
"""

from typing import Dict, Any, Callable, List, Optional, Tuple
from pathlib import Path

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
        QCheckBox, QFrame, QFileDialog
    )
    from PySide6.QtCore import Qt
except (ImportError, Exception):
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
        QCheckBox, QFrame, QFileDialog
    )
    from PyQt6.QtCore import Qt

from src.ui.param_schema import ParamDescriptor, ParamType, ParamPurpose


class ParamWidgetFactory:
    """Data-driven widget generator for engine parameters and configuration cards."""

    @staticmethod
    def create_control(
        desc: ParamDescriptor,
        initial_value: Any,
        on_change: Callable[[str, Any], None],
        parent: Optional[QWidget] = None
    ) -> Tuple[QWidget, Any]:
        """Creates a single typed input control for the given parameter descriptor."""
        if desc.param_type == ParamType.BOOL:
            cb = QCheckBox(desc.label, parent)
            cb.setChecked(bool(initial_value))
            cb.setToolTip(desc.description)
            cb.toggled.connect(lambda checked: on_change(desc.key, checked))
            return cb, cb

        elif desc.param_type == ParamType.ENUM:
            combo = QComboBox(parent)
            combo.setToolTip(desc.description)
            if desc.enum_options:
                for label, val in desc.enum_options:
                    combo.addItem(label, val)

            for i in range(combo.count()):
                item_data = combo.itemData(i)
                enum_val = getattr(item_data, "value", item_data)
                curr_val = getattr(initial_value, "value", initial_value)
                if item_data == initial_value or enum_val == curr_val:
                    combo.setCurrentIndex(i)
                    break

            combo.currentIndexChanged.connect(lambda idx: on_change(desc.key, combo.itemData(idx)))
            return combo, combo

        elif desc.param_type == ParamType.INT:
            spin = QSpinBox(parent)
            spin.setRange(
                desc.min_value if desc.min_value is not None else 0,
                desc.max_value if desc.max_value is not None else 999999
            )
            spin.setSingleStep(desc.step if desc.step is not None else 1)
            spin.setValue(int(initial_value) if initial_value is not None else (desc.default or 0))
            if desc.unit:
                spin.setSuffix(f" {desc.unit}")
            spin.setToolTip(desc.description)
            spin.valueChanged.connect(lambda val: on_change(desc.key, val))
            return spin, spin

        elif desc.param_type == ParamType.FLOAT:
            spin = QDoubleSpinBox(parent)
            spin.setRange(
                desc.min_value if desc.min_value is not None else 0.0,
                desc.max_value if desc.max_value is not None else 100.0
            )
            spin.setSingleStep(desc.step if desc.step is not None else 0.1)
            spin.setValue(float(initial_value) if initial_value is not None else (desc.default or 1.0))
            if desc.unit:
                spin.setSuffix(f" {desc.unit}")
            spin.setToolTip(desc.description)
            spin.valueChanged.connect(lambda val: on_change(desc.key, val))
            return spin, spin

        elif desc.param_type in (ParamType.PATH_FILE, ParamType.PATH_DIR):
            row_widget = QWidget(parent)
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(6)

            line_edit = QLineEdit(row_widget)
            line_edit.setText(str(initial_value or ""))
            line_edit.setToolTip(desc.description)
            line_edit.textChanged.connect(lambda text: on_change(desc.key, text.strip()))
            row_layout.addWidget(line_edit, stretch=1)

            btn_text = "📄 Browse File..." if desc.param_type == ParamType.PATH_FILE else "📁 Browse Folder..."
            browse_btn = QPushButton(btn_text, row_widget)

            def _browse():
                curr = line_edit.text().strip()
                start_dir = ""
                if curr:
                    p = Path(curr)
                    if desc.param_type == ParamType.PATH_FILE:
                        if p.is_file():
                            start_dir = str(p.parent)
                        elif p.parent.exists():
                            start_dir = str(p.parent)
                        elif p.exists():
                            start_dir = str(p)
                    else:
                        if p.is_dir():
                            start_dir = str(p)
                        elif p.parent.is_dir():
                            start_dir = str(p.parent)

                win = parent.window() if parent else None
                if desc.param_type == ParamType.PATH_FILE:
                    f_filter = desc.file_filter or "All Files (*)"
                    path, _ = QFileDialog.getOpenFileName(win, f"Select {desc.label}", start_dir, f_filter)
                else:
                    path = QFileDialog.getExistingDirectory(win, f"Select {desc.label}", start_dir)
                if path:
                    line_edit.setText(path)

            browse_btn.clicked.connect(_browse)
            row_layout.addWidget(browse_btn)
            return row_widget, line_edit

        else:
            line = QLineEdit(parent)
            line.setText(str(initial_value) if initial_value is not None else "")
            line.setToolTip(desc.description)
            line.textChanged.connect(lambda text: on_change(desc.key, text))
            return line, line

    @classmethod
    def build_paths_card(
        cls,
        descriptors: List[ParamDescriptor],
        config: Any,
        on_change: Callable[[str, Any], None],
        on_mod_engine: Callable[[], None],
        on_vanilla: Callable[[], None],
        on_backup: Callable[[], None],
        on_rollback: Callable[[], None],
        parent: Optional[QWidget] = None
    ) -> Tuple[QFrame, Dict[str, Any]]:
        """Constructs Paths & Regulation card with quick action presets."""
        card = QFrame(parent)
        card.setProperty("class", "card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        header = QLabel("📁 REGULATION & PATH SETTINGS")
        header.setProperty("class", "section-header")
        layout.addWidget(header)

        ctrls = {}
        for desc in [d for d in descriptors if d.purpose == ParamPurpose.PATHS]:
            row = QHBoxLayout()
            lbl = QLabel(f"{desc.label}:")
            lbl.setFixedWidth(170)
            row.addWidget(lbl)

            val = getattr(config, desc.key, desc.default)
            w_cont, w_input = cls.create_control(desc, val, on_change, card)
            row.addWidget(w_cont, stretch=1)
            ctrls[desc.key] = w_input
            layout.addLayout(row)

        # Quick action button strip
        btn_row = QHBoxLayout()
        me2_btn = QPushButton("Use Mod Engine 2 (mod/regulation.bin)")
        me2_btn.clicked.connect(on_mod_engine)
        btn_row.addWidget(me2_btn)

        van_btn = QPushButton("Use Vanilla Fallback")
        van_btn.clicked.connect(on_vanilla)
        btn_row.addWidget(van_btn)

        bak_btn = QPushButton("Create Pre-Write Backup")
        bak_btn.clicked.connect(on_backup)
        btn_row.addWidget(bak_btn)

        roll_btn = QPushButton("Rollback to Vanilla")
        roll_btn.setProperty("class", "danger")
        roll_btn.clicked.connect(on_rollback)
        btn_row.addWidget(roll_btn)

        layout.addLayout(btn_row)
        return card, ctrls

    @classmethod
    def build_spawn_rules_card(
        cls,
        descriptors: List[ParamDescriptor],
        config: Any,
        on_change: Callable[[str, Any], None],
        parent: Optional[QWidget] = None
    ) -> Tuple[QFrame, Dict[str, Any]]:
        """Constructs Encounter & Spawn Rules card."""
        card = QFrame(parent)
        card.setProperty("class", "card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        header = QLabel("⚔️ ENCOUNTER & SPAWN RULES")
        header.setProperty("class", "section-header")
        layout.addWidget(header)

        ctrls = {}
        for desc in [d for d in descriptors if d.purpose == ParamPurpose.SPAWN_RULES]:
            row = QHBoxLayout()
            val = getattr(config, desc.key, desc.default)
            w_cont, w_input = cls.create_control(desc, val, on_change, card)

            if desc.param_type != ParamType.BOOL:
                lbl = QLabel(f"{desc.label}:")
                lbl.setFixedWidth(170)
                row.addWidget(lbl)
                row.addWidget(w_cont, stretch=1)
            else:
                row.addWidget(w_cont, stretch=1)

            ctrls[desc.key] = w_input
            layout.addLayout(row)

        return card, ctrls

    @classmethod
    def build_synthesizer_card(
        cls,
        descriptors: List[ParamDescriptor],
        on_synthesize: Callable[[int], None],
        parent: Optional[QWidget] = None
    ) -> Tuple[QFrame, Dict[str, Any]]:
        """Constructs Autonomous NPC Synthesizer card."""
        card = QFrame(parent)
        card.setProperty("class", "card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        header = QLabel("🤖 AUTONOMOUS NPC ENEMY SYNTHESIZER")
        header.setProperty("class", "section-header")
        layout.addWidget(header)

        desc_lbl = QLabel(
            "Auto-generates hostile NPC encounters by inspecting modded gear from regulation.bin "
            "or synthesizing from thematic archetypes (Bleed, Blackflame, Frost, Carian, Frenzy)."
        )
        desc_lbl.setProperty("class", "subtext")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)

        row = QHBoxLayout()
        count_desc = next(d for d in descriptors if d.key == "npc_count")
        lbl = QLabel("NPC Count:")
        lbl.setFixedWidth(90)
        row.addWidget(lbl)

        spin = QSpinBox(card)
        spin.setRange(count_desc.min_value, count_desc.max_value)
        spin.setValue(count_desc.default)
        spin.setSuffix(f" {count_desc.unit}")
        row.addWidget(spin)

        synth_btn = QPushButton("Synthesize NPC Enemies")
        synth_btn.clicked.connect(lambda: on_synthesize(spin.value()))
        row.addWidget(synth_btn, stretch=1)

        layout.addLayout(row)
        return card, {"count_spin": spin, "synth_btn": synth_btn}
