# ─── Color Palettes ────────────────────────────────────────────────────────────

DARK_PALETTE = {
    "BG":           "#0a0a0f",   # near-void dark — not black, not navy
    "SURFACE":      "#111118",   # elevated layer
    "BORDER":       "#1e1e2a",   # barely-there separator
    "ACCENT":       "#c084fc",   # violet — refined, not loud
    "ACCENT2":      "#34d399",   # emerald
    "TEXT":         "#ececf1",   # off-white, zero eye strain
    "MUTED":        "#52526b",   # cool slate-gray
    "BTN_BG":       "#16161f",
    "BTN_HOV":      "#1e1e2a",
    "HIGHLIGHT_BG": "#0d2b22",
    "HIGHLIGHT_FG": "#34d399",
    "DANGER":       "#fb7185",   # rose — readable, not aggressive
}

LIGHT_PALETTE = {
    "BG":           "#f0f0f5",   # cool off-white — not harsh
    "SURFACE":      "#ffffff",
    "BORDER":       "#e2e2ec",   # cool lavender-gray
    "ACCENT":       "#7c3aed",   # violet-700 — grounded, authoritative
    "ACCENT2":      "#059669",   # emerald-600
    "TEXT":         "#0f0f1a",   # near-black with a cool tint
    "MUTED":        "#8888a8",   # cool medium gray
    "BTN_BG":       "#ebebf3",
    "BTN_HOV":      "#e2e2ec",
    "HIGHLIGHT_BG": "#d1fae5",
    "HIGHLIGHT_FG": "#065f46",
    "DANGER":       "#e11d48",
}

# Figtree: geometric humanist — warm but precise, zero genericness.
# Falls back to Nunito (rounded, readable) then system sans.
FONT_STACK = (
    "'Figtree', 'Nunito', 'Sora', ui-sans-serif, system-ui, sans-serif"
)
MONO_STACK = (
    "'Monaspace Neon', 'Cascadia Code', 'JetBrains Mono', ui-monospace, monospace"
)


def get_stylesheet(palette):
    p = palette
    is_dark = p["BG"] == DARK_PALETTE["BG"]

    # Glow effect on accent elements — only in dark mode
    glow = f"0 0 12px {p['ACCENT']}44" if is_dark else "none"
    focus_glow = f"0 0 0 3px {p['ACCENT']}28" if is_dark else f"0 0 0 3px {p['ACCENT']}18"

    return f"""
QMainWindow, QWidget {{
    background-color: {p['BG']};
    color: {p['TEXT']};
    font-family: {FONT_STACK};
    font-size: 13px;
    font-weight: 400;
}}

/* ── Titles ──────────────────────────────────────────── */
QLabel#title {{
    font-size: 17px;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: {p['TEXT']};
    padding: 4px 0;
}}
QLabel#subtitle {{
    color: {p['MUTED']};
    font-size: 11.5px;
    font-weight: 400;
    letter-spacing: 0.15px;
}}

/* ── Buttons ─────────────────────────────────────────── */
QPushButton {{
    background-color: {p['BTN_BG']};
    color: {p['TEXT']};
    border: 1px solid {p['BORDER']};
    border-radius: 8px;
    padding: 7px 16px;
    font-family: {FONT_STACK};
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0.1px;
}}
QPushButton:hover {{
    background-color: {p['BTN_HOV']};
    border-color: {p['ACCENT']};
    color: {p['ACCENT']};
}}
QPushButton:pressed {{
    background-color: {p['BORDER']};
    color: {p['ACCENT']};
}}
QPushButton#primary {{
    background-color: {p['ACCENT']};
    color: #ffffff;
    border: none;
    font-weight: 650;
    letter-spacing: 0.2px;
}}
QPushButton#primary:hover {{
    background-color: {p['ACCENT']};
    color: #ffffff;
    border: none;
}}
QPushButton#primary:pressed {{
    background-color: {p['ACCENT']};
    color: rgba(255,255,255,0.8);
}}
QPushButton#success {{
    background-color: {p['HIGHLIGHT_BG']};
    color: {p['HIGHLIGHT_FG']};
    border: 1px solid {p['ACCENT2']};
    font-weight: 600;
}}
QPushButton#success:hover {{
    background-color: {p['ACCENT2']};
    color: #ffffff;
    border-color: {p['ACCENT2']};
}}
QPushButton:disabled {{
    background-color: transparent;
    color: {p['MUTED']};
    border-color: {p['BORDER']};
}}

/* ── Text Input ──────────────────────────────────────── */
QLineEdit {{
    background-color: {p['SURFACE']};
    color: {p['TEXT']};
    border: 1px solid {p['BORDER']};
    border-radius: 8px;
    padding: 7px 12px;
    font-family: {FONT_STACK};
    font-size: 13px;
    selection-background-color: {p['ACCENT']}66;
    selection-color: {p['TEXT']};
}}
QLineEdit:focus {{
    border: 1px solid {p['ACCENT']};
    background-color: {p['SURFACE']};
}}
QLineEdit::placeholder {{
    color: {p['MUTED']};
    font-style: italic;
}}

/* ── Tree Widget ─────────────────────────────────────── */
QTreeWidget {{
    background-color: {p['SURFACE']};
    alternate-background-color: {p['BG']};
    border: 1px solid {p['BORDER']};
    border-radius: 10px;
    color: {p['TEXT']};
    gridline-color: {p['BORDER']};
    outline: none;
    show-decoration-selected: 1;
}}
QTreeWidget::item {{
    padding: 5px 8px;
    border-bottom: 1px solid {p['BORDER']};
}}
QTreeWidget::item:last {{
    border-bottom: none;
}}
QTreeWidget::item:selected {{
    background-color: {p['ACCENT']}22;
    color: {p['ACCENT']};
    border-radius: 6px;
    border-bottom: 1px solid {p['ACCENT']}22;
}}
QTreeWidget::item:hover:!selected {{
    background-color: {p['BTN_HOV']};
    border-radius: 6px;
}}

/* ── Table Widget ────────────────────────────────────── */
QTableWidget {{
    background-color: {p['SURFACE']};
    alternate-background-color: {p['BTN_BG']};
    border: 1px solid {p['BORDER']};
    border-radius: 10px;
    color: {p['TEXT']};
    gridline-color: {p['BORDER']};
    outline: none;
}}
QTableWidget::item {{
    padding: 7px 11px;
    font-family: {FONT_STACK};
    border-bottom: 1px solid {p['BORDER']};
}}
QTableWidget::item:selected {{
    background-color: {p['ACCENT']}22;
    color: {p['ACCENT']};
}}
QHeaderView::section {{
    background-color: {p['BTN_BG']};
    color: {p['MUTED']};
    border: none;
    border-bottom: 1px solid {p['BORDER']};
    border-right: 1px solid {p['BORDER']};
    padding: 7px 11px;
    font-family: {FONT_STACK};
    font-weight: 600;
    font-size: 10.5px;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}}
QHeaderView::section:first {{
    border-top-left-radius: 10px;
}}
QHeaderView::section:last {{
    border-top-right-radius: 10px;
    border-right: none;
}}

/* ── Tabs ────────────────────────────────────────────── */
QTabWidget::pane {{
    border: 1px solid {p['BORDER']};
    border-radius: 10px;
    background: {p['SURFACE']};
    top: -1px;
}}
QTabBar::tab {{
    background: transparent;
    color: {p['MUTED']};
    border: none;
    border-bottom: 2px solid transparent;
    padding: 9px 18px;
    font-family: {FONT_STACK};
    font-size: 12.5px;
    font-weight: 500;
    letter-spacing: 0.1px;
}}
QTabBar::tab:selected {{
    color: {p['ACCENT']};
    border-bottom: 2px solid {p['ACCENT']};
    font-weight: 650;
}}
QTabBar::tab:hover:!selected {{
    color: {p['TEXT']};
    border-bottom: 2px solid {p['BORDER']};
}}

/* ── Misc Chrome ─────────────────────────────────────── */
QSplitter::handle {{
    background-color: {p['BORDER']};
    width: 1px;
    height: 1px;
}}
QSplitter::handle:hover {{
    background-color: {p['ACCENT']};
}}
QFrame#divider {{
    background-color: {p['BORDER']};
    max-height: 1px;
}}
QStatusBar {{
    background-color: {p['SURFACE']};
    color: {p['MUTED']};
    border-top: 1px solid {p['BORDER']};
    font-family: {FONT_STACK};
    font-size: 11px;
    font-weight: 400;
    letter-spacing: 0.1px;
}}
QStatusBar::item {{
    border: none;
}}

/* ── Scrollbars ──────────────────────────────────────── */
QScrollBar:vertical {{
    background: transparent;
    width: 5px;
    margin: 4px 2px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {p['BORDER']};
    border-radius: 3px;
    min-height: 28px;
}}
QScrollBar::handle:vertical:hover {{
    background: {p['ACCENT']};
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{ height: 0; border: none; }}

QScrollBar:horizontal {{
    background: transparent;
    height: 5px;
    margin: 2px 4px;
    border-radius: 3px;
}}
QScrollBar::handle:horizontal {{
    background: {p['BORDER']};
    border-radius: 3px;
    min-width: 28px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {p['ACCENT']};
}}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{ width: 0; border: none; }}
"""