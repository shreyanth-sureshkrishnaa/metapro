import sys
import os
import subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QMessageBox, QLabel,
    QSplitter, QFrame, QStatusBar, QTabWidget, QDialog,
    QFormLayout, QLineEdit, QTextEdit, QDialogButtonBox
)
from PySide6.QtCore import Qt
from styles import DARK_PALETTE, LIGHT_PALETTE, get_stylesheet
from utils import run_exiftool, strip_metadata, generate_html_report
from widgets.map_view import MapView
from widgets.metadata_tab import MetadataTab
from widgets.csv_tab import CSVTab
from widgets.timeline_tab import TimelineTab
from widgets.device_tab import DeviceTab
from widgets.image_preview import ImagePreview


class ReportDialog(QDialog):
    """Dialog to collect case metadata before generating a report."""

    def __init__(self, palette, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Forensic Report")
        self.setMinimumWidth(420)
        self.setStyleSheet(f"background-color: {palette['BG']}; color: {palette['TEXT']};")

        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.case_name = QLineEdit()
        self.case_name.setPlaceholderText("e.g. Case #2026-0042")
        self.case_name.setText("Metadata Analysis Report")
        layout.addRow("Case Name:", self.case_name)

        self.investigator = QLineEdit()
        self.investigator.setPlaceholderText("e.g. Det. Smith")
        layout.addRow("Investigator:", self.investigator)

        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Optional case notes or context...")
        self.notes.setMaximumHeight(100)
        layout.addRow("Notes:", self.notes)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_info(self):
        return {
            "case_name": self.case_name.text().strip() or "Metadata Analysis Report",
            "investigator": self.investigator.text().strip() or "N/A",
            "notes": self.notes.toPlainText().strip(),
        }


class MetaPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("metapro  |  Forensic Metadata Analyzer")
        self.resize(1540, 900)
        self.current_palette = DARK_PALETTE
        self.data_cache = []
        self._setup_ui()

    def _setup_ui(self):
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready  —  Open a folder or file to begin analysis")

        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(16, 12, 16, 8)
        root_layout.setSpacing(10)

        # ── Header ────────────────────────────────────────────────────────
        header = QHBoxLayout()
        title = QLabel("metapro")
        title.setObjectName("title")
        sub = QLabel("Forensic Metadata Analyzer")
        sub.setObjectName("subtitle")
        sub.setAlignment(Qt.AlignBottom)
        header.addWidget(title)
        header.addSpacing(10)
        header.addWidget(sub)
        header.addStretch()

        self.btn_theme = QPushButton("Theme")
        self.btn_theme.setFixedHeight(34)
        self.btn_theme.setToolTip("Toggle Light / Dark theme")
        self.btn_theme.clicked.connect(self.toggle_theme)

        self.btn_file = QPushButton("Open File")
        self.btn_file.setObjectName("primary")
        self.btn_file.setFixedHeight(34)
        self.btn_file.clicked.connect(self.load_file)

        self.btn_folder = QPushButton("Open Folder")
        self.btn_folder.setObjectName("primary")
        self.btn_folder.setFixedHeight(34)
        self.btn_folder.clicked.connect(self.load_folder)

        self.btn_sanitize = QPushButton("Sanitize Copy")
        self.btn_sanitize.setFixedHeight(34)
        self.btn_sanitize.setToolTip("Strip all metadata from loaded files and save clean copies")
        self.btn_sanitize.setEnabled(False)
        self.btn_sanitize.clicked.connect(self.sanitize_files)

        self.btn_report = QPushButton("Generate Report")
        self.btn_report.setFixedHeight(34)
        self.btn_report.setToolTip("Generate a self-contained HTML forensic report")
        self.btn_report.setEnabled(False)
        self.btn_report.clicked.connect(self.generate_report)

        self.btn_export = QPushButton("Export CSV")
        self.btn_export.setObjectName("success")
        self.btn_export.setFixedHeight(34)
        self.btn_export.setEnabled(False)
        self.btn_export.clicked.connect(self.export_csv)

        header.addWidget(self.btn_theme)
        header.addSpacing(4)
        header.addWidget(self.btn_file)
        header.addWidget(self.btn_folder)
        header.addSpacing(8)
        header.addWidget(self.btn_sanitize)
        header.addWidget(self.btn_report)
        header.addWidget(self.btn_export)
        root_layout.addLayout(header)

        # ── Divider ───────────────────────────────────────────────────────
        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFrameShape(QFrame.HLine)
        root_layout.addWidget(divider)

        # ── Main content area ────────────────────────────────────────────
        h_splitter = QSplitter(Qt.Horizontal)
        h_splitter.setChildrenCollapsible(False)

        # ── Left: Image Preview ───────────────────────────────────────────
        self.image_preview = ImagePreview(self.current_palette)
        h_splitter.addWidget(self.image_preview)

        # ── Center: Tabs ──────────────────────────────────────────────────
        self.tabs = QTabWidget()

        self.metadata_tab = MetadataTab(self.current_palette)
        self.tabs.addTab(self.metadata_tab, "  Metadata  ")

        self.timeline_tab = TimelineTab(self.current_palette)
        self.tabs.addTab(self.timeline_tab, "  Timeline  ")

        self.device_tab = DeviceTab(self.current_palette)
        self.tabs.addTab(self.device_tab, "  Devices  ")

        self.csv_tab = CSVTab(self.current_palette)
        self.csv_tab.btn_open_csv.clicked.connect(self.load_csv_for_search)
        self.tabs.addTab(self.csv_tab, "  CSV Search  ")

        h_splitter.addWidget(self.tabs)

        # ── Right: Map ────────────────────────────────────────────────────
        self.map_view = MapView(self.current_palette)
        h_splitter.addWidget(self.map_view)

        h_splitter.setStretchFactor(0, 0)  # preview: fixed width
        h_splitter.setStretchFactor(1, 4)  # tabs: largest
        h_splitter.setStretchFactor(2, 2)  # map

        root_layout.addWidget(h_splitter, 1)

        # ── Connect image preview to tree selection ───────────────────────
        self.metadata_tab.tree.currentItemChanged.connect(self._on_tree_selection)

    # ── Theme ─────────────────────────────────────────────────────────────────

    def toggle_theme(self):
        self.current_palette = LIGHT_PALETTE if self.current_palette is DARK_PALETTE else DARK_PALETTE
        QApplication.instance().setStyleSheet(get_stylesheet(self.current_palette))
        self.metadata_tab.set_theme(self.current_palette)
        self.csv_tab.set_theme(self.current_palette)
        self.map_view.set_theme(self.current_palette)
        self.timeline_tab.set_theme(self.current_palette)
        self.device_tab.set_theme(self.current_palette)
        self.image_preview.set_theme(self.current_palette)
        mode = "Light" if self.current_palette is LIGHT_PALETTE else "Dark"
        self.statusBar().showMessage(f"Switched to {mode} theme")

    # ── Image preview on tree selection ────────────────────────────────────────

    def _on_tree_selection(self, current, previous):
        if not current:
            return
        # Top-level items are filenames
        item = current
        if item.parent():
            item = item.parent()  # go to file-level
        filename = item.text(0).strip()
        # Find matching entry
        for entry in self.data_cache:
            if os.path.basename(entry.get("SourceFile", "")) == filename:
                self.image_preview.show_image(entry.get("SourceFile", ""), entry)
                return

    # ── Data loading ──────────────────────────────────────────────────────────

    def load_file(self):
        filters = "Images (*.jpg *.jpeg *.png *.tiff *.tif *.heic *.cr2 *.nef *.arw *.dng *.bmp *.gif *.webp);;All Files (*)"
        path, _ = QFileDialog.getOpenFileName(self, "Select Image File", "", filters)
        if not path:
            return
        self._load(path, recursive=False)

    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if not folder:
            return
        self._load(folder, recursive=True)

    def _load(self, path, recursive):
        try:
            args = ["-r", path] if recursive else [path]
            data = run_exiftool(args)
            if not data:
                QMessageBox.warning(self, "No Files", "No supported files found at the specified path.")
                return
            self.data_cache = data
            self.metadata_tab.set_data(data)
            self.map_view.update_map(data)
            self.timeline_tab.set_data(data)
            self.device_tab.set_data(data)
            self.btn_export.setEnabled(True)
            self.btn_sanitize.setEnabled(True)
            self.btn_report.setEnabled(True)
            count = len(data)
            self.statusBar().showMessage(f"Loaded {count} file{'s' if count != 1 else ''}  —  {path}")
            self.tabs.setCurrentIndex(0)
            # Auto-show preview for single file
            if count == 1:
                entry = data[0]
                self.image_preview.show_image(entry.get("SourceFile", ""), entry)
        except FileNotFoundError:
            QMessageBox.critical(
                self, "exiftool Not Found",
                "exiftool is required but not installed.\n\n"
                "Install with:\n  sudo apt install libimage-exiftool-perl"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read metadata:\n{e}")

    def load_csv_for_search(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if not path:
            return
        if self.csv_tab.load_csv(path):
            self.statusBar().showMessage(f"CSV loaded: {path}")

    # ── Sanitize ──────────────────────────────────────────────────────────────

    def sanitize_files(self):
        if not self.data_cache:
            return
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory for Sanitized Files")
        if not output_dir:
            return
        source_files = [e.get("SourceFile", "") for e in self.data_cache if e.get("SourceFile")]
        success, errors = strip_metadata(source_files, output_dir)
        msg = f"Successfully sanitized {success} file{'s' if success != 1 else ''}."
        if errors:
            msg += f"\n\n{len(errors)} error(s):\n" + "\n".join(errors[:10])
        QMessageBox.information(self, "Sanitization Complete", msg)
        self.statusBar().showMessage(f"Sanitized {success} files to {output_dir}")

    # ── Report generation ─────────────────────────────────────────────────────

    def generate_report(self):
        if not self.data_cache:
            return
        dialog = ReportDialog(self.current_palette, self)
        if dialog.exec() != QDialog.Accepted:
            return
        case_info = dialog.get_info()
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Forensic Report", "forensic_report.html", "HTML Files (*.html)"
        )
        if not save_path:
            return
        try:
            generate_html_report(self.data_cache, save_path, case_info)
            QMessageBox.information(
                self, "Report Generated",
                f"Forensic report saved to:\n{save_path}"
            )
            self.statusBar().showMessage(f"Report saved: {save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Report Failed", str(e))

    # ── CSV Export ────────────────────────────────────────────────────────────

    def export_csv(self):
        save_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if not save_path:
            return
        source_path = self.data_cache[0].get("SourceFile", "")
        if len(self.data_cache) == 1:
            args = ["-csv", source_path]
        else:
            args = ["-csv", "-r", os.path.dirname(source_path)]
        try:
            with open(save_path, 'w') as f:
                subprocess.run(["exiftool"] + args, stdout=f, check=True)
            QMessageBox.information(self, "Export Complete", f"CSV saved to:\n{save_path}")
            self.statusBar().showMessage(f"Exported to {save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(get_stylesheet(DARK_PALETTE))
    window = MetaPro()
    window.show()
    sys.exit(app.exec())