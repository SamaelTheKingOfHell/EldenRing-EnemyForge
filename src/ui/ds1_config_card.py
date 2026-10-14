"""
Dark Souls 1 PTDE Configuration Card for EnemyForge Qt GUI.

Provides user configuration of local Dark Souls Prepare to Die Edition DATA path,
auto-detection across common Steam directories, and live diagnostic verification
of required game archives (dvdbnd0, dvdbnd1, DARKSOULS.exe).
Adheres to [CS-MODULAR], [CS-DECOUPLE], and [CS-NO-MOCK].
"""

from typing import Optional, Callable
from pathlib import Path

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QLineEdit, QFrame, QFileDialog
    )
    from PySide6.QtCore import Qt, Signal
except (ImportError, Exception):
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QLineEdit, QFrame, QFileDialog
    )
    from PyQt6.QtCore import Qt, Signal

from src.cross_game.ds1_extractor import DS1Extractor
from src.logger import system_logger


class DS1ConfigCard(QFrame):
    """Configuration card for local Dark Souls PTDE installation path and archive diagnostics."""
    path_changed = Signal(str)

    def __init__(self, initial_path: str = "", on_path_changed: Optional[Callable[[str], None]] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setProperty("class", "card")
        self.on_path_changed_cb = on_path_changed
        self.current_path = initial_path
        self._build_ui()
        self._set_initial_or_autodetect()
        self.path_input.textChanged.connect(self._on_text_changed)


    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        header = QLabel("🎮 DARK SOULS: PREPARE TO DIE EDITION CONFIGURATION")
        header.setProperty("class", "section-header")
        layout.addWidget(header)

        notice = QLabel(
            "Legal Compliance Gate: EnemyForge extracts monster models, animations, and sound tables "
            "directly from your legally owned installation. Zero proprietary assets are redistributed."
        )
        notice.setProperty("class", "subtext")
        notice.setWordWrap(True)
        layout.addWidget(notice)

        # Path input row
        row = QHBoxLayout()
        lbl = QLabel("PTDE DATA Path:")
        lbl.setFixedWidth(120)
        row.addWidget(lbl)

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select Dark Souls Prepare to Die Edition/DATA directory...")
        row.addWidget(self.path_input, stretch=1)


        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_folder)
        row.addWidget(self.browse_btn)

        self.autodetect_btn = QPushButton("🔍 Auto-Detect")
        self.autodetect_btn.clicked.connect(self._auto_detect)
        row.addWidget(self.autodetect_btn)

        layout.addLayout(row)

        # Diagnostics Grid Frame
        self.diag_frame = QFrame()
        self.diag_frame.setStyleSheet("background-color: #07080a; border: 1px solid rgba(197, 160, 89, 0.25); border-radius: 4px; padding: 8px;")
        diag_layout = QVBoxLayout(self.diag_frame)
        diag_layout.setContentsMargins(8, 6, 8, 6)
        diag_layout.setSpacing(4)

        self.status_title = QLabel("Installation Diagnostics:")
        self.status_title.setStyleSheet("font-weight: bold; color: #ffd475; font-size: 11px;")
        diag_layout.addWidget(self.status_title)

        self.exe_status = QLabel("  • DARKSOULS.exe: Checking...")
        self.bhd0_status = QLabel("  • Main Archive (dvdbnd0.bhd5/bdt): Checking...")
        self.bhd1_status = QLabel("  • Patch Archive (dvdbnd1.bhd5/bdt): Checking...")

        for w in (self.exe_status, self.bhd0_status, self.bhd1_status):
            w.setStyleSheet("color: #a8a29e; font-size: 11px; font-family: monospace;")
            diag_layout.addWidget(w)

        layout.addWidget(self.diag_frame)

    def _set_initial_or_autodetect(self):
        if self.current_path and Path(self.current_path).exists():
            self.path_input.setText(self.current_path)
        else:
            self._auto_detect()

    def _auto_detect(self):
        detected = DS1Extractor.detect_ptde_data_dir()
        if detected:
            self.path_input.setText(str(detected))
            system_logger.info(f"Auto-detected local DS1 PTDE at: {detected}", source="DS1Config")
        else:
            self._refresh_diagnostics("")

    def _browse_folder(self):
        curr = self.path_input.text().strip()
        start_dir = ""
        if curr:
            p = Path(curr)
            if p.is_dir():
                start_dir = str(p)
            elif p.parent.is_dir():
                start_dir = str(p.parent)
        win = self.window() if hasattr(self, "window") else None
        chosen = QFileDialog.getExistingDirectory(win, "Select Dark Souls Prepare to Die Edition DATA Folder", start_dir)
        if chosen:
            self.path_input.setText(chosen)

    def _on_text_changed(self, text: str):
        self.current_path = text.strip()
        self._refresh_diagnostics(self.current_path)
        self.path_changed.emit(self.current_path)
        if self.on_path_changed_cb:
            self.on_path_changed_cb(self.current_path)

    def _refresh_diagnostics(self, path_str: str):
        p = Path(path_str) if path_str else None
        extractor = DS1Extractor(data_dir=p)
        diag = extractor.get_diagnostics()

        if diag["has_exe"]:
            self.exe_status.setText("  ✓ DARKSOULS.exe: Verified Present")
            self.exe_status.setStyleSheet("color: #8ee3a4; font-size: 11px; font-family: monospace;")
        else:
            self.exe_status.setText("  ✗ DARKSOULS.exe: Not found in selected directory")
            self.exe_status.setStyleSheet("color: #ff8585; font-size: 11px; font-family: monospace;")

        if diag["dvdbnd0_valid"]:
            sz_mb = diag["dvdbnd0_size"] / (1024 * 1024)
            self.bhd0_status.setText(f"  ✓ Main Game Archive (dvdbnd0): Verified ({sz_mb:.1f} MB)")
            self.bhd0_status.setStyleSheet("color: #8ee3a4; font-size: 11px; font-family: monospace;")
        else:
            self.bhd0_status.setText("  ✗ Main Game Archive (dvdbnd0.bhd5/bdt): Missing")
            self.bhd0_status.setStyleSheet("color: #ff8585; font-size: 11px; font-family: monospace;")

        if diag["dvdbnd1_valid"]:
            sz_mb = diag["dvdbnd1_size"] / (1024 * 1024)
            self.bhd1_status.setText(f"  ✓ Patch/DLC Archive (dvdbnd1): Verified ({sz_mb:.1f} MB)")
            self.bhd1_status.setStyleSheet("color: #8ee3a4; font-size: 11px; font-family: monospace;")
        else:
            self.bhd1_status.setText("  ✗ Patch/DLC Archive (dvdbnd1.bhd5/bdt): Missing")
            self.bhd1_status.setStyleSheet("color: #ff8585; font-size: 11px; font-family: monospace;")

        if diag["is_valid"]:
            self.status_title.setText("✓ Installation Diagnostics: Valid Licensed Copy Verified")
            self.status_title.setStyleSheet("font-weight: bold; color: #8ee3a4; font-size: 11px;")
        else:
            self.status_title.setText("⚠️ Installation Diagnostics: Incomplete or Invalid Installation")
            self.status_title.setStyleSheet("font-weight: bold; color: #fca5a5; font-size: 11px;")
