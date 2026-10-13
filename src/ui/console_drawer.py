"""
Floating Developer Console drawer for EnemyForge Qt GUI.

Streams real-time structured logs from system_logger with auto-scroll and clear functionality.
Adheres to [CS-MODULAR] and [CS-DEBUG].
"""

from typing import Optional
try:
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QWidget
    from PySide6.QtCore import Qt
except (ImportError, Exception):
    from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QWidget
    from PyQt6.QtCore import Qt

from src.logger import system_logger


class ConsoleDrawer(QDialog):
    """Floating developer console dialog displaying real-time system logs."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("EnemyForge Developer Console")
        self.resize(620, 360)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.console_text = QTextEdit()
        self.console_text.setReadOnly(True)
        self.console_text.setStyleSheet(
            "background-color: #07080a; color: #8ee3a4; font-family: monospace; font-size: 11px;"
        )
        layout.addWidget(self.console_text)

        btn_row = QHBoxLayout()
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.console_text.clear)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.hide)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def poll_logs(self):
        """Fetches latest in-memory logs and updates the console."""
        recent = system_logger.get_in_memory_logs(limit=40)
        if recent:
            txt = "\n".join(f"[{l['timestamp']}] [{l['level']}] [{l['source']}] {l['message']}" for l in recent)
            if self.console_text.toPlainText() != txt:
                self.console_text.setPlainText(txt)
                self.console_text.verticalScrollBar().setValue(self.console_text.verticalScrollBar().maximum())
