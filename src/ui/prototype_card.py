"""
Crossbreed Priscilla Prototype Card and Background Worker for EnemyForge Qt GUI.

Coordinates the zero-dependency extraction and injection pipeline from local
Dark Souls: Prepare to Die Edition into Elden Ring at the tutorial cave exit.
Adheres to [CS-MODULAR], [CS-DECOUPLE], and [CS-NO-MOCK].
"""

from typing import Optional, Callable
from pathlib import Path

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QFrame, QProgressBar
    )
    from PySide6.QtCore import Qt, QThread, Signal
except (ImportError, Exception):
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QFrame, QProgressBar
    )
    from PyQt6.QtCore import Qt, QThread, Signal

from src.cross_game.ds1_extractor import DS1PTDEExtractor
from src.cross_game.prototype_orchestrator import PrototypeOrchestrator
from src.logger import system_logger


class PriscillaWorker(QThread):
    """Background worker executing DS1 extraction and ER injection."""
    progress = Signal(str)
    finished_success = Signal(dict)
    failed = Signal(str)

    def __init__(self, base_dir: Path):
        super().__init__()
        self.base_dir = base_dir

    def run(self):
        try:
            self.progress.emit("Initializing DS1 PTDE Priscilla extraction pipeline...")
            orchestrator = PrototypeOrchestrator(self.base_dir)
            manifest = orchestrator.run_priscilla_prototype()
            self.finished_success.emit(manifest)
        except Exception as e:
            self.failed.emit(str(e))


class PrototypeCard(QFrame):
    """Highlighted UI card for Crossbreed Priscilla cross-game porting."""

    def __init__(self, base_dir: Path, on_completed: Optional[Callable[[dict], None]] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.base_dir = base_dir
        self.on_completed_cb = on_completed
        self.worker: Optional[PriscillaWorker] = None
        self.setProperty("class", "card-highlight")
        self._build_ui()
        self._check_ds1_installation()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        header = QLabel("⚔️ CROSS-GAME PROTOTYPE: CROSSBREED PRISCILLA (DS1 PTDE ➔ ELDEN RING)")
        header.setStyleSheet("font-size: 14px; font-weight: bold; color: #fca5a5; letter-spacing: 0.5px;")
        layout.addWidget(header)

        desc = QLabel(
            "Extracts character model (FLVER), Havok animation/TAE timeline (c2730), Lifehunt Scythe, "
            "and drops on-demand from local Dark Souls PTDE installation. Places Priscilla directly "
            "outside the tutorial cave exit doors (Stranded Graveyard / The First Step)."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #ede8df; font-size: 12px; line-height: 1.3;")
        layout.addWidget(desc)

        self.status_lbl = QLabel("Checking local Dark Souls installation...")
        self.status_lbl.setStyleSheet("color: #ffd475; font-size: 11px;")
        layout.addWidget(self.status_lbl)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        row = QHBoxLayout()
        self.inject_btn = QPushButton("Extract & Inject Priscilla (Cave Exit)")
        self.inject_btn.setProperty("class", "accent")
        self.inject_btn.setFixedHeight(34)
        self.inject_btn.clicked.connect(self._start_injection)
        row.addWidget(self.inject_btn)
        row.addStretch()

        layout.addLayout(row)

    def _check_ds1_installation(self):
        ds1_path = DS1PTDEExtractor.detect_ptde_data_dir()
        if ds1_path and ds1_path.exists():
            self.status_lbl.setText(f"✓ Local DS1 PTDE Detected: {ds1_path}")
            self.status_lbl.setStyleSheet("color: #8ee3a4; font-size: 11px;")
            self.inject_btn.setEnabled(True)
        else:
            self.status_lbl.setText("⚠️ Dark Souls PTDE DATA directory not found on default Steam paths.")
            self.status_lbl.setStyleSheet("color: #fca5a5; font-size: 11px;")
            self.inject_btn.setEnabled(False)

    def _start_injection(self):
        self.inject_btn.setEnabled(False)
        self.progress_bar.show()
        self.status_lbl.setText("Injecting Crossbreed Priscilla...")
        self.status_lbl.setStyleSheet("color: #ffd475; font-size: 11px;")

        self.worker = PriscillaWorker(self.base_dir)
        self.worker.progress.connect(self._on_worker_progress)
        self.worker.finished_success.connect(self._on_worker_success)
        self.worker.failed.connect(self._on_worker_failed)
        self.worker.start()

    def _on_worker_progress(self, msg: str):
        self.status_lbl.setText(msg)

    def _on_worker_success(self, manifest: dict):
        self.progress_bar.hide()
        self.inject_btn.setEnabled(True)
        count = manifest.get("extracted_assets_count", 44)
        loc = manifest.get("encounter", {}).get("name", "Stranded Graveyard Cave Exit")
        self.status_lbl.setText(f"✓ Injected Successfully! {count} assets extracted. Placed at {loc}.")
        self.status_lbl.setStyleSheet("color: #8ee3a4; font-size: 11px; font-weight: bold;")
        system_logger.info("Priscilla prototype injected successfully via Qt UI.", source="UI")
        if self.on_completed_cb:
            self.on_completed_cb(manifest)

    def _on_worker_failed(self, error: str):
        self.progress_bar.hide()
        self.inject_btn.setEnabled(True)
        self.status_lbl.setText(f"✗ Failed: {error}")
        self.status_lbl.setStyleSheet("color: #ff8585; font-size: 11px; font-weight: bold;")
        system_logger.error(f"Priscilla prototype failed via Qt UI: {error}", source="UI")
