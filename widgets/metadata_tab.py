import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QTreeWidget, 
    QTreeWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QBrush

class MetadataTab(QWidget):
    def __init__(self, palette, parent=None):
        super().__init__(parent)
        self.palette_dict = palette
        self._data_cache = []
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(180)
        self._search_timer.timeout.connect(self._apply_search)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        search_row = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search tags or values…")
        self.search_box.setClearButtonEnabled(True)
        self.search_box.textChanged.connect(lambda: self._search_timer.start())
        
        self.lbl_search_hits = QLabel("")
        self.update_style()
        
        search_row.addWidget(self.search_box)
        search_row.addWidget(self.lbl_search_hits)
        layout.addLayout(search_row)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["  Tag", "  Value"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setAnimated(True)
        self.tree.header().setSectionResizeMode(0, QHeaderView.Interactive)
        self.tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tree.header().setDefaultSectionSize(220)
        layout.addWidget(self.tree)

    def set_theme(self, palette):
        self.palette_dict = palette
        self.update_style()
        self.populate_tree(query=self.search_box.text())

    def update_style(self):
        self.lbl_search_hits.setStyleSheet(f"color: {self.palette_dict['MUTED']}; font-size: 11px;")

    def set_data(self, data):
        self._data_cache = data
        self.search_box.clear()
        self.populate_tree()

    def populate_tree(self, query=""):
        self.tree.clear()
        q = query.lower().strip()
        total_hits = 0
        p = self.palette_dict

        for entry in self._data_cache:
            filename = os.path.basename(entry.get("SourceFile", "Unknown file"))
            matching_children = []
            for key, value in sorted(entry.items()):
                if key == "ExifToolVersion":
                    continue
                str_val = str(value)
                if q and q not in key.lower() and q not in str_val.lower():
                    continue
                matching_children.append((key, str_val))

            if q and not matching_children:
                continue

            file_item = QTreeWidgetItem(self.tree, [filename, ""])
            file_item.setFont(0, QFont("Inter", 11, QFont.Medium))
            file_item.setForeground(0, QColor(p['ACCENT']))
            file_item.setExpanded(True)

            for key, str_val in matching_children:
                child = QTreeWidgetItem(file_item, [f"  {key}", f"  {str_val}"])
                if q:
                    child.setBackground(0, QBrush(QColor(p['HIGHLIGHT_BG'])))
                    child.setBackground(1, QBrush(QColor(p['HIGHLIGHT_BG'])))
                    child.setForeground(0, QColor(p['HIGHLIGHT_FG']))
                else:
                    child.setForeground(0, QColor(p['TEXT']))
                    child.setForeground(1, QColor(p['MUTED']))
                total_hits += 1

        self.tree.resizeColumnToContents(0)
        if q:
            self.lbl_search_hits.setText(f"{total_hits} result{'s' if total_hits != 1 else ''}")
        else:
            self.lbl_search_hits.setText("")

    def _apply_search(self):
        self.populate_tree(query=self.search_box.text())

    def clear(self):
        self._data_cache = []
        self.tree.clear()
        self.search_box.clear()
        self.lbl_search_hits.setText("")
