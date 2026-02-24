import os
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QAbstractItemView, QHeaderView, QLineEdit
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QFont
from utils import get_best_datetime, extract_gps, detect_anomalies


class TimelineTab(QWidget):
    def __init__(self, palette, parent=None):
        super().__init__(parent)
        self.palette_dict = palette
        self._data_cache = []
        self._timeline = []
        self._filter_timer = QTimer()
        self._filter_timer.setSingleShot(True)
        self._filter_timer.setInterval(200)
        self._filter_timer.timeout.connect(self._apply_filter)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        toolbar = QHBoxLayout()
        self.filter_box = QLineEdit()
        self.filter_box.setPlaceholderText("Filter timeline by filename, device, or flag...")
        self.filter_box.setClearButtonEnabled(True)
        self.filter_box.textChanged.connect(lambda: self._filter_timer.start())

        self.lbl_info = QLabel("")
        self.lbl_info.setStyleSheet(f"color: {self.palette_dict['MUTED']}; font-size: 11px;")

        toolbar.addWidget(self.filter_box, 1)
        toolbar.addWidget(self.lbl_info)
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["File", "Date / Time", "Time Gap", "Device", "GPS", "Flags"])
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setDefaultSectionSize(150)
        layout.addWidget(self.table)

    def set_theme(self, palette):
        self.palette_dict = palette
        self.lbl_info.setStyleSheet(f"color: {palette['MUTED']}; font-size: 11px;")
        self._render(self._timeline)

    def set_data(self, data):
        self._data_cache = data
        self._build_timeline()
        self.filter_box.clear()
        self._render(self._timeline)

    def _build_timeline(self):
        entries = []
        for entry in self._data_cache:
            fname = os.path.basename(entry.get("SourceFile", "Unknown"))
            dt = get_best_datetime(entry)
            device = f"{entry.get('Make', '')} {entry.get('Model', '')}".strip() or "Unknown"
            coords = extract_gps(entry)
            gps_str = f"{coords[0]:.5f}, {coords[1]:.5f}" if coords else ""
            anomalies = detect_anomalies(entry)
            entries.append({
                "file": fname,
                "dt": dt,
                "dt_str": dt.strftime("%Y-%m-%d  %H:%M:%S") if dt else "N/A",
                "device": device,
                "gps": gps_str,
                "anomalies": anomalies,
                "flags_str": " | ".join(anomalies) if anomalies else "",
            })
        entries.sort(key=lambda x: x["dt"] or datetime.min)

        # Calculate time gaps
        for i, e in enumerate(entries):
            if i == 0 or not e["dt"] or not entries[i - 1]["dt"]:
                e["gap"] = ""
                e["gap_large"] = False
            else:
                delta = e["dt"] - entries[i - 1]["dt"]
                e["gap"] = self._format_delta(delta)
                e["gap_large"] = delta > timedelta(hours=24)

        self._timeline = entries

        # Summary
        total = len(entries)
        with_gps = sum(1 for e in entries if e["gps"])
        with_flags = sum(1 for e in entries if e["anomalies"])
        self.lbl_info.setText(f"{total} files  |  {with_gps} GPS-tagged  |  {with_flags} flagged")

    def _format_delta(self, delta):
        total_sec = int(delta.total_seconds())
        if total_sec < 0:
            return "< 0"
        days = total_sec // 86400
        hours = (total_sec % 86400) // 3600
        minutes = (total_sec % 3600) // 60
        if days > 0:
            return f"{days}d {hours}h"
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    def _render(self, entries):
        p = self.palette_dict
        self.table.setRowCount(len(entries))
        for r, e in enumerate(entries):
            items = [
                QTableWidgetItem(e["file"]),
                QTableWidgetItem(e["dt_str"]),
                QTableWidgetItem(e["gap"]),
                QTableWidgetItem(e["device"]),
                QTableWidgetItem(e["gps"]),
                QTableWidgetItem(e["flags_str"]),
            ]
            for c, item in enumerate(items):
                # Large time gap highlight
                if c == 2 and e.get("gap_large"):
                    item.setForeground(QBrush(QColor(p["DANGER"])))
                    item.setFont(QFont("Inter", 11, QFont.Bold))
                # Anomaly highlight
                if c == 5 and e["anomalies"]:
                    item.setForeground(QBrush(QColor(p["DANGER"])))
                    item.setFont(QFont("Inter", 10, QFont.Medium))
                self.table.setItem(r, c, item)

    def _apply_filter(self):
        q = self.filter_box.text().strip().lower()
        if not q:
            self._render(self._timeline)
            return
        filtered = [
            e for e in self._timeline
            if q in e["file"].lower() or q in e["device"].lower()
            or q in e["flags_str"].lower() or q in e["gps"].lower()
            or q in e["dt_str"].lower()
        ]
        self._render(filtered)

    def clear(self):
        self._data_cache = []
        self._timeline = []
        self.table.setRowCount(0)
        self.filter_box.clear()
        self.lbl_info.setText("")
