# ─── Color Palettes ────────────────────────────────────────────────────────────

DARK_PALETTE = {
    "BG": "#0d1117",
    "SURFACE": "#161b22",
    "BORDER": "#30363d",
    "ACCENT": "#58a6ff",
    "ACCENT2": "#3fb950",
    "TEXT": "#e6edf3",
    "MUTED": "#8b949e",
    "BTN_BG": "#21262d",
    "BTN_HOV": "#30363d",
    "HIGHLIGHT_BG": "#2d3f1f",
    "HIGHLIGHT_FG": "#3fb950",
    "DANGER": "#f85149",
}

LIGHT_PALETTE = {
    "BG": "#f6f8fa",
    "SURFACE": "#ffffff",
    "BORDER": "#d0d7de",
    "ACCENT": "#0969da",
    "ACCENT2": "#1a7f37",
    "TEXT": "#1f2328",
    "MUTED": "#656d76",
    "BTN_BG": "#f3f4f6",
    "BTN_HOV": "#ebecf0",
    "HIGHLIGHT_BG": "#dafbe1",
    "HIGHLIGHT_FG": "#1a7f37",
    "DANGER": "#cf222e",
}

def get_stylesheet(palette):
    p = palette
    return f"""
QMainWindow, QWidget {{
    background-color: {p['BG']};
    color: {p['TEXT']};
    font-family: 'Inter', 'Segoe UI Variable Text', 'Segoe UI', 'SF Pro text', sans-serif;
    font-size: 13px;
}}
QLabel#title {{
    font-size: 22px;
    font-weight: 700;
    color: {p['ACCENT']};
    padding: 6px 0px;
}}
QLabel#subtitle {{
    color: {p['MUTED']};
    font-size: 12px;
}}
QPushButton {{
    background-color: {p['BTN_BG']};
    color: {p['TEXT']};
    border: 1px solid {p['BORDER']};
    border-radius: 6px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {p['BTN_HOV']};
    border-color: {p['ACCENT']};
    color: {p['ACCENT']};
}}
QPushButton#primary {{
    background-color: {p['ACCENT']};
    color: {p['BG']};
    border: none;
    font-weight: 700;
}}
QPushButton#primary:hover {{
    background-color: {p['ACCENT'] if p == DARK_PALETTE else '#0550ae'};
    opacity: 0.9;
}}
QPushButton#success {{
    background-color: {p['HIGHLIGHT_BG']};
    color: {p['HIGHLIGHT_FG']};
    border: 1px solid {p['HIGHLIGHT_FG']};
    font-weight: 600;
}}
QPushButton#success:hover {{
    background-color: {p['HIGHLIGHT_FG']};
    color: {p['BG']};
}}
QPushButton:disabled {{
    background-color: {p['SURFACE']};
    color: {p['MUTED']};
    border-color: {p['BORDER']};
}}
QLineEdit {{
    background-color: {p['SURFACE']};
    color: {p['TEXT']};
    border: 1px solid {p['BORDER']};
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
    selection-background-color: {p['ACCENT']};
}}
QLineEdit:focus {{
    border-color: {p['ACCENT']};
}}
QLineEdit::placeholder {{
    color: {p['MUTED']};
}}
QTreeWidget {{
    background-color: {p['SURFACE']};
    alternate-background-color: {p['BG']};
    border: 1px solid {p['BORDER']};
    border-radius: 6px;
    color: {p['TEXT']};
    gridline-color: {p['BORDER']};
    outline: none;
}}
QTreeWidget::item {{
    padding: 4px 6px;
    border-bottom: 1px solid {p['BORDER']};
}}
QTreeWidget::item:selected {{
    background-color: {p['ACCENT']}33;
    color: {p['ACCENT']};
}}
QTreeWidget::item:hover {{
    background-color: {p['BTN_HOV']};
}}
QTableWidget {{
    background-color: {p['SURFACE']};
    alternate-background-color: {p['BG']};
    border: 1px solid {p['BORDER']};
    border-radius: 6px;
    color: {p['TEXT']};
    gridline-color: {p['BORDER']};
    outline: none;
}}
QTableWidget::item {{
    padding: 4px 8px;
}}
QTableWidget::item:selected {{
    background-color: {p['ACCENT']}33;
    color: {p['ACCENT']};
}}
QHeaderView::section {{
    background-color: {p['BTN_BG']};
    color: {p['MUTED']};
    border: none;
    border-bottom: 1px solid {p['BORDER']};
    border-right: 1px solid {p['BORDER']};
    padding: 6px 8px;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
QTabWidget::pane {{
    border: 1px solid {p['BORDER']};
    border-radius: 6px;
    background: {p['SURFACE']};
}}
QTabBar::tab {{
    background: {p['BTN_BG']};
    color: {p['MUTED']};
    border: 1px solid {p['BORDER']};
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    padding: 6px 18px;
    font-size: 12px;
    font-weight: 500;
}}
QTabBar::tab:selected {{
    background: {p['SURFACE']};
    color: {p['ACCENT']};
    border-color: {p['BORDER']};
}}
QTabBar::tab:hover:!selected {{
    color: {p['TEXT']};
    background: {p['BTN_HOV']};
}}
QSplitter::handle {{
    background-color: {p['BORDER']};
}}
QFrame#divider {{
    background-color: {p['BORDER']};
    max-height: 1px;
}}
QStatusBar {{
    background-color: {p['SURFACE']};
    color: {p['MUTED']};
    border-top: 1px solid {p['BORDER']};
    font-size: 11px;
}}
QScrollBar:vertical {{
    background: {p['SURFACE']};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {p['BORDER']};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {p['MUTED']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {p['SURFACE']};
    height: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {p['BORDER']};
    border-radius: 4px;
    min-width: 20px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {p['MUTED']};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}
"""
