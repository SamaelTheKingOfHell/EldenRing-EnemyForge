"""
Preset and World Encounter Inspector widget for EnemyForge Qt GUI.

Provides interactive table viewing of discovered character presets, equipment loadouts,
guaranteed carried drop tables, and world spawn encounters.
Adheres to [CS-MODULAR] and [CS-DECOUPLE].
"""

from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
        QFrame, QTabWidget, QTextEdit
    )
    from PySide6.QtCore import Qt
except (ImportError, Exception):
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
        QFrame, QTabWidget, QTextEdit
    )
    from PyQt6.QtCore import Qt

from src.models import CharacterPreset, WorldEncounter


class PresetInspectorWidget(QWidget):
    """Dual-tab inspector for discovered enemy presets and registered world encounters."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.presets: List[CharacterPreset] = []
        self.encounters: List[WorldEncounter] = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: Presets & Carried Loot
        presets_tab = QWidget()
        presets_layout = QVBoxLayout(presets_tab)
        presets_layout.setContentsMargins(8, 8, 8, 8)

        preset_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Presets Table
        self.presets_table = QTableWidget()
        self.presets_table.setColumnCount(4)
        self.presets_table.setHorizontalHeaderLabels(["Enemy Name", "Gender", "Lvl", "Archetype"])
        self.presets_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.presets_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.presets_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.presets_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.presets_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.presets_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.presets_table.itemSelectionChanged.connect(self._on_preset_selected)
        preset_splitter.addWidget(self.presets_table)

        # Right: Detail Card
        detail_card = QFrame()
        detail_card.setProperty("class", "card")
        detail_layout = QVBoxLayout(detail_card)
        detail_layout.setContentsMargins(12, 10, 12, 10)
        detail_layout.setSpacing(6)

        self.detail_title = QLabel("Select an Enemy Preset")
        self.detail_title.setProperty("class", "section-header")
        detail_layout.addWidget(self.detail_title)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setStyleSheet("background-color: #07080a; color: #ede8df; border: 1px solid rgba(197, 160, 89, 0.3);")
        detail_layout.addWidget(self.detail_text)

        preset_splitter.addWidget(detail_card)
        preset_splitter.setSizes([380, 420])
        presets_layout.addWidget(preset_splitter)

        self.tabs.addTab(presets_tab, "⚔️ Discovered Presets & Loot")

        # Tab 2: World Encounters
        encounters_tab = QWidget()
        encounters_layout = QVBoxLayout(encounters_tab)
        encounters_layout.setContentsMargins(8, 8, 8, 8)

        self.encounters_table = QTableWidget()
        self.encounters_table.setColumnCount(5)
        self.encounters_table.setHorizontalHeaderLabels(["Region", "Encounter ID", "Map ID", "Coordinates (X, Y, Z)", "Description"])
        self.encounters_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.encounters_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.encounters_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.encounters_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.encounters_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.encounters_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        encounters_layout.addWidget(self.encounters_table)

        self.tabs.addTab(encounters_tab, "🗺️ World Encounter Spawns")

    def set_data(self, presets: List[CharacterPreset], encounters: List[WorldEncounter]):
        """Populates tables with live presets and world encounters."""
        self.presets = presets
        self.encounters = encounters

        # Populate Presets Table
        self.presets_table.setRowCount(len(presets))
        for row, p in enumerate(presets):
            gender_str = "Female" if getattr(p, "gender", 0) == 1 else "Male"
            self.presets_table.setItem(row, 0, QTableWidgetItem(p.name))
            self.presets_table.setItem(row, 1, QTableWidgetItem(gender_str))
            self.presets_table.setItem(row, 2, QTableWidgetItem(str(getattr(p, "level", 1))))
            self.presets_table.setItem(row, 3, QTableWidgetItem(getattr(p, "archetype", "Unknown")))

        if presets:
            self.presets_table.selectRow(0)

        # Populate Encounters Table
        self.encounters_table.setRowCount(len(encounters))
        for row, enc in enumerate(encounters):
            coords = enc.coordinates
            coord_str = f"({coords.get('x', 0):.1f}, {coords.get('y', 0):.1f}, {coords.get('z', 0):.1f})"
            self.encounters_table.setItem(row, 0, QTableWidgetItem(enc.region))
            self.encounters_table.setItem(row, 1, QTableWidgetItem(enc.encounter_id))
            self.encounters_table.setItem(row, 2, QTableWidgetItem(enc.map_id))
            self.encounters_table.setItem(row, 3, QTableWidgetItem(coord_str))
            self.encounters_table.setItem(row, 4, QTableWidgetItem(enc.description))

    def _on_preset_selected(self):
        sel = self.presets_table.selectedIndexes()
        if not sel:
            return
        row = sel[0].row()
        if 0 <= row < len(self.presets):
            preset = self.presets[row]
            self._render_preset_detail(preset)

    def _render_preset_detail(self, preset: CharacterPreset):
        self.detail_title.setText(f"Preset: {preset.name}")
        eq = getattr(preset, "equipment", None)

        lines = [
            f"=== {preset.name} ===",
            f"Archetype: {getattr(preset, 'archetype', 'Custom')}",
            f"Level: {getattr(preset, 'level', 1)} | Gender: {'Female' if getattr(preset, 'gender', 0) == 1 else 'Male'}",
            "",
            "--- Equipped Armor ---",
        ]
        if eq:
            lines.append(f"  Head: {getattr(eq, 'head_name', None) or 'None'} (ID: {getattr(eq, 'head_id', 0)})")
            lines.append(f"  Body: {getattr(eq, 'body_name', None) or 'None'} (ID: {getattr(eq, 'body_id', 0)})")
            lines.append(f"  Arms: {getattr(eq, 'arms_name', None) or 'None'} (ID: {getattr(eq, 'arms_id', 0)})")
            lines.append(f"  Legs: {getattr(eq, 'legs_name', None) or 'None'} (ID: {getattr(eq, 'legs_id', 0)})")
            lines.append("")
            lines.append("--- Equipped Weapons & Shields ---")
            lines.append(f"  Right 1: {getattr(eq, 'right_hand_1_name', None) or 'None'} (ID: {getattr(eq, 'right_hand_1_id', 0)})")
            lines.append(f"  Right 2: {getattr(eq, 'right_hand_2_name', None) or 'None'} (ID: {getattr(eq, 'right_hand_2_id', 0)})")
            lines.append(f"  Left 1:  {getattr(eq, 'left_hand_1_name', None) or 'None'} (ID: {getattr(eq, 'left_hand_1_id', 0)})")
            lines.append(f"  Left 2:  {getattr(eq, 'left_hand_2_name', None) or 'None'} (ID: {getattr(eq, 'left_hand_2_id', 0)})")
            lines.append("")
            lines.append("--- Guaranteed 100% Carried Drop List ---")
            drops = []
            for slot, name_attr in [
                ("Head", "head_name"), ("Body", "body_name"), ("Arms", "arms_name"), ("Legs", "legs_name"),
                ("R-Hand 1", "right_hand_1_name"), ("R-Hand 2", "right_hand_2_name"),
                ("L-Hand 1", "left_hand_1_name"), ("L-Hand 2", "left_hand_2_name")
            ]:
                val = getattr(eq, name_attr, None)
                if val:
                    drops.append(f"  ✓ 100% Drop: {val} [{slot}]")
            if drops:
                lines.extend(drops)
            else:
                lines.append("  (No equipped gear registered)")
        else:
            lines.append("  (No equipment profile)")

        self.detail_text.setPlainText("\n".join(lines))
