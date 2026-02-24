import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont


class ImagePreview(QWidget):
    """Sidebar widget that shows a thumbnail and basic info for the selected image."""

    def __init__(self, palette, parent=None):
        super().__init__(parent)
        self.palette_dict = palette
        self.setFixedWidth(260)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.lbl_title = QLabel("Image Preview")
        self.lbl_title.setFont(QFont("Inter", 12, QFont.DemiBold))
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setStyleSheet(f"color: {self.palette_dict['ACCENT']};")
        layout.addWidget(self.lbl_title)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background-color: {self.palette_dict['BORDER']};")
        layout.addWidget(sep)

        self.lbl_image = QLabel("No image selected")
        self.lbl_image.setAlignment(Qt.AlignCenter)
        self.lbl_image.setMinimumHeight(200)
        self.lbl_image.setStyleSheet(
            f"background-color: {self.palette_dict['SURFACE']};"
            f"border: 1px solid {self.palette_dict['BORDER']};"
            f"border-radius: 6px; color: {self.palette_dict['MUTED']};"
            f"padding: 8px;"
        )
        layout.addWidget(self.lbl_image)

        self.lbl_filename = QLabel("")
        self.lbl_filename.setWordWrap(True)
        self.lbl_filename.setAlignment(Qt.AlignCenter)
        self.lbl_filename.setFont(QFont("Inter", 11, QFont.Medium))
        self.lbl_filename.setStyleSheet(f"color: {self.palette_dict['TEXT']};")
        layout.addWidget(self.lbl_filename)

        self.lbl_details = QLabel("")
        self.lbl_details.setWordWrap(True)
        self.lbl_details.setAlignment(Qt.AlignCenter)
        self.lbl_details.setStyleSheet(f"color: {self.palette_dict['MUTED']}; font-size: 11px;")
        layout.addWidget(self.lbl_details)

        layout.addStretch()

    def set_theme(self, palette):
        self.palette_dict = palette
        p = palette
        self.lbl_title.setStyleSheet(f"color: {p['ACCENT']};")
        self.lbl_image.setStyleSheet(
            f"background-color: {p['SURFACE']};"
            f"border: 1px solid {p['BORDER']};"
            f"border-radius: 6px; color: {p['MUTED']};"
            f"padding: 8px;"
        )
        self.lbl_filename.setStyleSheet(f"color: {p['TEXT']};")
        self.lbl_details.setStyleSheet(f"color: {p['MUTED']}; font-size: 11px;")

    def show_image(self, file_path, entry=None):
        """Display thumbnail for the given file path."""
        p = self.palette_dict
        if not file_path or not os.path.isfile(file_path):
            self.lbl_image.setText("File not found")
            self.lbl_filename.setText("")
            self.lbl_details.setText("")
            return

        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            self.lbl_image.setText("Cannot preview this format")
            self.lbl_filename.setText(os.path.basename(file_path))
            self.lbl_details.setText("")
            return

        scaled = pixmap.scaled(240, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.lbl_image.setPixmap(scaled)
        self.lbl_image.setStyleSheet(
            f"background-color: {p['SURFACE']};"
            f"border: 1px solid {p['BORDER']};"
            f"border-radius: 6px; padding: 4px;"
        )
        self.lbl_filename.setText(os.path.basename(file_path))

        if entry:
            details = []
            w = entry.get("ImageWidth") or entry.get("ExifImageWidth")
            h = entry.get("ImageHeight") or entry.get("ExifImageHeight")
            if w and h:
                details.append(f"{w} x {h}")
            size = entry.get("FileSize")
            if size:
                details.append(str(size))
            model = f"{entry.get('Make', '')} {entry.get('Model', '')}".strip()
            if model:
                details.append(model)
            self.lbl_details.setText("\n".join(details))
        else:
            fsize = os.path.getsize(file_path)
            self.lbl_details.setText(f"{fsize / 1024:.1f} KB")

    def clear(self):
        self.lbl_image.clear()
        self.lbl_image.setText("No image selected")
        self.lbl_filename.setText("")
        self.lbl_details.setText("")
