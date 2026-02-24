import csv
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, 
    QLabel, QTableWidget, QTableWidgetItem, QAbstractItemView, 
    QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QBrush, QColor

class CSVTab(QWidget):
    def __init__(self, palette, parent=None):
        super().__init__(parent)
        self.palette_dict = palette
        self._csv_data = []
        self._csv_headers = []
        self._csv_timer = QTimer()
        self._csv_timer.setSingleShot(True)
        self._csv_timer.setInterval(180)
        self._csv_timer.timeout.connect(self._apply_search)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        csv_toolbar = QHBoxLayout()
        self.btn_open_csv = QPushButton("Open CSV File")
        self.btn_open_csv.setObjectName("primary")
        self.btn_open_csv.setFixedHeight(34)
        
        self.csv_search_box = QLineEdit()
        self.csv_search_box.setPlaceholderText("Search by tag name or value…")
        self.csv_search_box.setClearButtonEnabled(True)
        self.csv_search_box.setEnabled(False)
        self.csv_search_box.textChanged.connect(lambda: self._csv_timer.start())

        self.lbl_csv_hits = QLabel("")
        self.update_style()

        csv_toolbar.addWidget(self.btn_open_csv)
        csv_toolbar.addSpacing(6)
        csv_toolbar.addWidget(self.csv_search_box, 1)
        csv_toolbar.addWidget(self.lbl_csv_hits)
        layout.addLayout(csv_toolbar)

        self.csv_lbl_file = QLabel("No CSV loaded")
        layout.addWidget(self.csv_lbl_file)

        self.csv_table = QTableWidget()
        self.csv_table.setAlternatingRowColors(True)
        self.csv_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.csv_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.csv_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.csv_table.verticalHeader().setVisible(False)
        layout.addWidget(self.csv_table)

    def set_theme(self, palette):
        self.palette_dict = palette
        self.update_style()
        self._render_table(self._csv_table_rows() if hasattr(self, '_csv_table_rows') else self._csv_data, highlight=self.csv_search_box.text())

    def update_style(self):
        p = self.palette_dict
        self.lbl_csv_hits.setStyleSheet(f"color: {p['MUTED']}; font-size: 11px;")
        if hasattr(self, 'csv_lbl_file'):
            self.csv_lbl_file.setStyleSheet(f"color: {p['MUTED']}; font-size: 11px; padding: 2px 0;")

    def load_csv(self, path):
        try:
            with open(path, newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                self._csv_headers = reader.fieldnames or []
                self._csv_data = list(reader)

            self.csv_lbl_file.setText(f"  {os.path.basename(path)}  —  {len(self._csv_data)} rows, {len(self._csv_headers)} columns")
            self.csv_search_box.setEnabled(True)
            self.csv_search_box.clear()
            self._render_table(self._csv_data, highlight="")
            self.lbl_csv_hits.setText("")
            return True
        except Exception as e:
            QMessageBox.critical(self, "CSV Load Failed", str(e))
            return False

    def _render_table(self, rows, highlight=""):
        self.csv_table.clear()
        self.csv_table.setRowCount(len(rows))
        self.csv_table.setColumnCount(len(self._csv_headers))
        self.csv_table.setHorizontalHeaderLabels(self._csv_headers)

        hl = highlight.lower()
        p = self.palette_dict
        for r_idx, row in enumerate(rows):
            for c_idx, col in enumerate(self._csv_headers):
                val = str(row.get(col, ""))
                item = QTableWidgetItem(val)
                if hl and (hl in col.lower() or hl in val.lower()):
                    item.setBackground(QBrush(QColor(p['HIGHLIGHT_BG'])))
                    item.setForeground(QBrush(QColor(p['HIGHLIGHT_FG'])))
                self.csv_table.setItem(r_idx, c_idx, item)

        self.csv_table.resizeColumnsToContents()

    def _apply_search(self):
        q = self.csv_search_box.text().strip()
        if not q:
            self._render_table(self._csv_data, highlight="")
            self.lbl_csv_hits.setText("")
            return

        ql = q.lower()
        matching_rows = [
            row for row in self._csv_data
            if any(ql in col.lower() or ql in str(row.get(col, "")).lower()
                   for col in self._csv_headers)
        ]
        self._render_table(matching_rows, highlight=q)
        count = len(matching_rows)
        self.lbl_csv_hits.setText(f"{count} row{'s' if count != 1 else ''}")

    def clear(self):
        self._csv_data = []
        self._csv_headers = []
        self.csv_table.clear()
        self.csv_lbl_file.setText("No CSV loaded")
        self.csv_search_box.setEnabled(False)
        self.lbl_csv_hits.setText("")
