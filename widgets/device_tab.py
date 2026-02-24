import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QHeaderView
)
from PySide6.QtGui import QBrush, QColor, QFont
from utils import get_device_summary


class DeviceTab(QWidget):
    def __init__(self, palette, parent=None):
        super().__init__(parent)
        self.palette_dict = palette
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self.lbl_info = QLabel("Load files to see device attribution")
        self.lbl_info.setStyleSheet(f"color: {self.palette_dict['MUTED']}; font-size: 11px;")
        layout.addWidget(self.lbl_info)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Device", "Software", "Count", "Sample Files"])
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setDefaultSectionSize(180)
        layout.addWidget(self.table)

    def set_theme(self, palette):
        self.palette_dict = palette
        self.lbl_info.setStyleSheet(f"color: {palette['MUTED']}; font-size: 11px;")

    def set_data(self, data_cache):
        summary = get_device_summary(data_cache)
        p = self.palette_dict

        self.lbl_info.setText(f"{len(summary)} unique device/software combinations across {sum(d['count'] for d in summary)} files")
        self.table.setRowCount(len(summary))

        for r, d in enumerate(summary):
            files_str = ", ".join(d["files"])
            if d["count"] > len(d["files"]):
                files_str += f" (+{d['count'] - len(d['files'])} more)"

            items = [
                QTableWidgetItem(d["device"]),
                QTableWidgetItem(d["software"]),
                QTableWidgetItem(str(d["count"])),
                QTableWidgetItem(files_str),
            ]
            # Highlight count
            items[2].setTextAlignment(Qt.AlignCenter)
            items[2].setFont(QFont("Inter", 12, QFont.Bold))
            items[2].setForeground(QBrush(QColor(p["ACCENT"])))
            # Muted sample files
            items[3].setForeground(QBrush(QColor(p["MUTED"])))

            for c, item in enumerate(items):
                self.table.setItem(r, c, item)

        self.table.resizeColumnsToContents()

    def clear(self):
        self.table.setRowCount(0)
        self.lbl_info.setText("Load files to see device attribution")


from PySide6.QtCore import Qt
