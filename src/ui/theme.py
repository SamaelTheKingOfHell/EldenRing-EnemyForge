"""
Dark Souls / Elden Ring themed QSS stylesheet for EnemyForge Qt Application.
Adheres to [CS-MODULAR] by encapsulating styling into a dedicated module.
"""

DARK_SOULS_QSS = """
QMainWindow, QWidget {
    background-color: #0c0d12;
    color: #ede8df;
    font-family: "Segoe UI", -apple-system, sans-serif;
    font-size: 13px;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QSplitter::handle:vertical {
    background-color: #1a1e2b;
    border: 1px solid rgba(197, 160, 89, 0.4);
    border-radius: 3px;
    height: 7px;
    margin: 2px 25px;
}

QSplitter::handle:vertical:hover {
    background-color: #c5a059;
    border: 1px solid #ffd475;
}

QSplitter::handle:horizontal {
    background-color: #1a1e2b;
    border: 1px solid rgba(197, 160, 89, 0.4);
    border-radius: 3px;
    width: 7px;
    margin: 25px 2px;
}

QSplitter::handle:horizontal:hover {
    background-color: #c5a059;
    border: 1px solid #ffd475;
}

QFrame.banner {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(197, 160, 89, 0.15), stop:1 rgba(18, 20, 28, 0.95));
    border: 1px solid #ffd475;
    border-left: 5px solid #ffd475;
    border-radius: 8px;
    padding: 12px;
}

QFrame.card {
    background-color: rgba(18, 20, 28, 0.85);
    border: 1px solid rgba(197, 160, 89, 0.35);
    border-radius: 8px;
    padding: 14px;
}

QFrame.card-highlight {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(40, 25, 45, 0.85), stop:1 rgba(18, 20, 28, 0.95));
    border: 1px solid rgba(220, 38, 38, 0.5);
    border-left: 4px solid #dc2626;
    border-radius: 8px;
    padding: 14px;
}

QLabel.title {
    font-size: 20px;
    font-weight: bold;
    color: #ffd475;
    letter-spacing: 1.5px;
}

QLabel.section-header {
    font-size: 14px;
    font-weight: bold;
    color: #c5a059;
    letter-spacing: 0.5px;
}

QLabel.subtext {
    font-size: 11px;
    color: #a8a29e;
}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #07080a;
    border: 1px solid rgba(197, 160, 89, 0.4);
    border-radius: 4px;
    padding: 6px 10px;
    color: #ede8df;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #ffd475;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QPushButton {
    background-color: #1a1e2b;
    border: 1px solid rgba(197, 160, 89, 0.4);
    border-radius: 4px;
    padding: 7px 14px;
    color: #ede8df;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #262c3e;
    border: 1px solid #ffd475;
}

QPushButton:disabled {
    background-color: #10121a;
    border: 1px solid rgba(100, 100, 100, 0.3);
    color: #666a75;
}

QPushButton.primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #c5a059, stop:1 #8c6e32);
    color: #0c0d12;
    font-weight: bold;
    border: 1px solid #ffd475;
}

QPushButton.primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #dfba73, stop:1 #a8853f);
}

QPushButton.danger {
    background-color: rgba(224, 82, 82, 0.15);
    border: 1px solid rgba(224, 82, 82, 0.5);
    color: #ff8585;
}

QPushButton.danger:hover {
    background-color: rgba(224, 82, 82, 0.3);
    border: 1px solid #ff5252;
}

QPushButton.accent {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7f1d1d, stop:1 #450a0a);
    color: #fca5a5;
    font-weight: bold;
    border: 1px solid #ef4444;
}

QPushButton.accent:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #991b1b, stop:1 #581010);
}

QTabWidget::pane {
    border: 1px solid rgba(197, 160, 89, 0.3);
    background-color: #0d0f17;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #12141e;
    color: #a8a29e;
    border: 1px solid rgba(197, 160, 89, 0.2);
    border-bottom: none;
    padding: 7px 16px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 3px;
}

QTabBar::tab:selected {
    background-color: #1a1e2b;
    color: #ffd475;
    border: 1px solid #ffd475;
    border-bottom: none;
    font-weight: bold;
}

QTableWidget {
    background-color: #08090c;
    border: 1px solid rgba(197, 160, 89, 0.3);
    gridline-color: rgba(197, 160, 89, 0.15);
    selection-background-color: rgba(197, 160, 89, 0.25);
    selection-color: #ffd475;
}

QHeaderView::section {
    background-color: #12141c;
    color: #c5a059;
    padding: 7px;
    border: 1px solid rgba(197, 160, 89, 0.2);
    font-weight: bold;
}

QScrollBar:vertical {
    background: #08090c;
    width: 10px;
}

QScrollBar::handle:vertical {
    background: #c5a059;
    border-radius: 4px;
}

QScrollBar:horizontal {
    background: #08090c;
    height: 10px;
}

QScrollBar::handle:horizontal {
    background: #c5a059;
    border-radius: 4px;
}
"""
