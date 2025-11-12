import sys
import os
import py7zr
from datetime import datetime
import shutil
import tempfile
import math
import subprocess
import string
import argparse
import zipfile
import tarfile

try:
    import rarfile
    RAR_SUPPORT = True
except ImportError:
    RAR_SUPPORT = False

try:
    import winreg
    WIN_REG_SUPPORT = True
except ImportError:
    WIN_REG_SUPPORT = False

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QFileDialog, QToolBar, QStatusBar, QMessageBox,
    QHeaderView, QDialog, QFormLayout, QComboBox, QLabel, QDialogButtonBox,
    QMenu, QProgressDialog, QLineEdit, QProgressBar, QMenuBar,
    QTextEdit # [BARU] Impor QTextEdit untuk help content
)
from PySide6.QtGui import QAction, QIcon, QPixmap, QDesktopServices
from PySide6.QtCore import (
    Qt, QSize, QByteArray, QTimer, QThread, Signal, QObject, QUrl,
    QSettings # [BARU] Impor QSettings
)

# --- SVG Ikon (Tidak berubah) ---
SVG_ICONS = {
    # Ikon Toolbar (monokrom)
    "create": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>""",
    "open": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 12v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h5l4 4h5a2 2 0 0 1 2 2v1"></path><path d="M18 13v-2a2 2 0 0 0-2-2H8"></path></svg>""",
    "extract": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>""",
    "info": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>""",
    "test": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="m9 12 2 2 4-4"></path></svg>""",
    "copy": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>""",
    "delete": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>""",
    "up": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5"></path><polyline points="5 12 12 5 19 12"></polyline></svg>""",
    "folder": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>""",
    "file": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path><polyline points="13 2 13 9 20 9"></polyline></svg>""",
    "archive": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="#f0e68c" stroke="#f0e68c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>""",
    "image": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>""",
    "text": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6h16M4 12h16M4 18h10"></path></svg>"""
}

# --- Dark Theme Stylesheet (QSS) ---
DARK_THEME_QSS = """
QWidget { background-color: #2b2b2b; color: #e0e0e0; font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif; font-size: 10pt; }
QMainWindow { background-color: #2b2b2b; }
QMenuBar { background-color: #3c3c3c; color: #e0e0e0; }
QMenuBar::item { background-color: #3c3c3c; padding: 4px 10px; }
QMenuBar::item:selected { background-color: #0078d7; }
QToolBar { background-color: #3c3c3c; border: none; padding: 4px; spacing: 6px; }
QToolBar QToolButton { background-color: #3c3c3c; border: 1px solid #3c3c3c; padding: 6px; border-radius: 4px; }
QToolBar QToolButton:hover { background-color: #4f4f4f; border: 1px solid #666666; }
QToolBar QToolButton:pressed { background-color: #1e1e1e; }
QLineEdit { padding: 4px; border: 1px solid #555555; border-radius: 3px; background-color: #2b2b2b; }
QTableWidget { background-color: #2b2b2b; border: 1px solid #444444; gridline-color: #444444; }
QTableWidget::item { padding: 5px; }
QTableWidget::item:selected { background-color: #0078d7; color: #ffffff; }
QHeaderView::section { background-color: #3c3c3c; color: #e0e0e0; padding: 6px; border: 1px solid #444444; font-weight: bold; }
QStatusBar { background-color: #3c3c3c; color: #cccccc; }
QMenu { background-color: #3c3c3c; border: 1px solid #555555; padding: 5px; }
QMenu::item { padding: 5px 25px 5px 20px; }
QMenu::item:selected { background-color: #0078d7; color: #ffffff; }
QMessageBox, QDialog { background-color: #3c3c3c; }
QMessageBox QLabel, QDialog QLabel, QDialog QComboBox, QDialog QProgressBar, QTextEdit { color: #e0e0e0; background-color: #2b2b2b; }
QProgressDialog { background-color: #3c3c3c; }
QProgressBar { border: 1px solid #555; border-radius: 5px; text-align: center; color: #e0e0e0; }
QProgressBar::chunk { background-color: #0078d7; width: 10px; margin: 0.5px; }
QComboBox { background-color: #2b2b2b; border: 1px solid #555555; padding: 4px; border-radius: 3px; min-width: 60px;}
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView { background-color: #3c3c3c; border: 1px solid #555555; selection-background-color: #0078d7; }
"""

def create_svg_icon(svg_xml):
    byte_array = QByteArray(svg_xml.encode('utf-8'))
    pixmap = QPixmap()
    pixmap.loadFromData(byte_array)
    return QIcon(pixmap)

class ArchiveSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Archive Settings")
        layout = QFormLayout(self)
        self.method_combo = QComboBox()
        self.method_combo.addItems(["LZMA2", "LZMA"])
        layout.addRow(QLabel("Compression Method:"), self.method_combo)
        self.level_combo = QComboBox()
        self.level_combo.addItems(["Store", "Fast", "Good", "Best"])
        self.level_combo.setCurrentText("Good")
        layout.addRow(QLabel("Compression Level:"), self.level_combo)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_settings(self):
        return self.method_combo.currentText(), self.level_combo.currentText()
        
class ArchivePropertiesDialog(QDialog):
    def __init__(self, archive_path, total_files, uncompressed_size, compressed_size, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Archive Properties")
        self.setMinimumWidth(400)
        layout = QFormLayout(self)
        ratio = 0
        if uncompressed_size > 0:
            ratio = 100 * (1 - (compressed_size / uncompressed_size))
        
        def format_size(size_bytes):
            if size_bytes == 0: return "0 B"
            size_name = ("B", "KB", "MB", "GB", "TB")
            i = int(math.floor(math.log(size_bytes, 1024)))
            p = math.pow(1024, i)
            s = round(size_bytes / p, 2)
            return f"{s} {size_name[i]}"

        layout.addRow(QLabel("Archive:"), QLabel(f"<b>{os.path.basename(archive_path)}</b>"))
        layout.addRow(QLabel("Path:"), QLabel(archive_path))
        layout.addRow(QLabel("Total Files:"), QLabel(f"{total_files:,}"))
        layout.addRow(QLabel("Uncompressed Size:"), QLabel(f"{format_size(uncompressed_size)} ({uncompressed_size:,} bytes)"))
        layout.addRow(QLabel("Compressed Size:"), QLabel(f"{format_size(compressed_size)} ({compressed_size:,} bytes)"))
        layout.addRow(QLabel("Compression Ratio:"), QLabel(f"{ratio:.2f}%"))
        
        self.ratio_bar = QProgressBar()
        self.ratio_bar.setRange(0, 100)
        self.ratio_bar.setValue(int(ratio))
        self.ratio_bar.setFormat(f"Compression: {int(ratio)}%")
        layout.addRow(QLabel("Ratio Visual:"), self.ratio_bar)
        
        method_info = "LZMA / LZMA2 (typical)" if archive_path.lower().endswith(('.7z', '.mcn')) else "N/A"
        layout.addRow(QLabel("Compression Method:"), QLabel(method_info))
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

class ArchiveWorker(QObject):
    progress = Signal(int)
    progress_text = Signal(str)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, source_paths, save_path, filters):
        super().__init__()
        self.source_paths = source_paths
        self.save_path = save_path
        self.filters = filters
        self._is_running = True

    def run(self):
        try:
            with py7zr.SevenZipFile(self.save_path, 'w', filters=self.filters) as archive:
                processed_files = 0
                for path in self.source_paths:
                    if not self._is_running: break
                    if os.path.isfile(path):
                        self.progress_text.emit(f"Adding: {os.path.basename(path)}...")
                        archive.write(path, os.path.basename(path))
                        processed_files += 1
                        self.progress.emit(processed_files)
                    elif os.path.isdir(path):
                        base_folder_name = os.path.basename(path)
                        for root, _, files in os.walk(path):
                            if not self._is_running: break
                            for file in files:
                                if not self._is_running: break
                                file_path = os.path.join(root, file)
                                arcname = os.path.join(base_folder_name, os.path.relpath(file_path, path))
                                self.progress_text.emit(f"Adding: {file}...")
                                archive.write(file_path, arcname)
                                processed_files += 1
                                self.progress.emit(processed_files)
            if self._is_running:
                self.finished.emit(self.save_path)
            else:
                self.error.emit("Canceled")
        except Exception as e:
            self.error.emit(f"An error occurred: {e}")

    def stop(self):
        self._is_running = False

# LETAKKAN KODE INI TEPAT DI BAWAH KELAS ArchiveWorker

class ExtractionWorker(QObject):
    progress = Signal(int)
    progress_text = Signal(str)
    finished = Signal(str) # Akan mengirim path destinasi setelah selesai
    error = Signal(str)

    def __init__(self, archive_path, archive_type, dest_folder, targets=None):
        super().__init__()
        self.archive_path = archive_path
        self.archive_type = archive_type
        self.dest_folder = dest_folder
        self.targets = targets or []
        self._is_running = True

    def run(self):
        try:
            # Dapatkan daftar lengkap file untuk dihitung totalnya
            all_files = self._get_archive_file_list()
            
            # Jika target tidak ditentukan (ekstrak semua), gunakan semua file
            if not self.targets:
                self.targets = all_files

            total_files_to_extract = len(self.targets)
            processed_files = 0
            
            self.progress.emit(0) # Mulai progress bar dari 0

            # Logika ekstraksi berdasarkan tipe arsip
            if self.archive_type == '7z':
                with py7zr.SevenZipFile(self.archive_path, 'r') as archive:
                    # py7zr bisa mengekstrak target secara langsung, tapi kita iterasi untuk progress
                    for target_file in self.targets:
                        if not self._is_running: break
                        self.progress_text.emit(f"Extracting: {os.path.basename(target_file)}...")
                        archive.extract(path=self.dest_folder, targets=[target_file])
                        processed_files += 1
                        self.progress.emit(processed_files)
            
            elif self.archive_type == 'zip':
                with zipfile.ZipFile(self.archive_path, 'r') as archive:
                    for member in self.targets:
                        if not self._is_running: break
                        self.progress_text.emit(f"Extracting: {os.path.basename(member)}...")
                        archive.extract(member, path=self.dest_folder)
                        processed_files += 1
                        self.progress.emit(processed_files)

            elif self.archive_type == 'tar':
                with tarfile.open(self.archive_path, 'r:*') as archive:
                    # Dapatkan member objects dari nama file
                    members_to_extract = [m for m in archive.getmembers() if m.name in self.targets]
                    for member in members_to_extract:
                        if not self._is_running: break
                        self.progress_text.emit(f"Extracting: {os.path.basename(member.name)}...")
                        archive.extract(member, path=self.dest_folder)
                        processed_files += 1
                        self.progress.emit(processed_files)

            elif self.archive_type == 'rar' and RAR_SUPPORT:
                with rarfile.RarFile(self.archive_path, 'r') as archive:
                    for member in self.targets:
                        if not self._is_running: break
                        self.progress_text.emit(f"Extracting: {os.path.basename(member)}...")
                        archive.extract(member, path=self.dest_folder)
                        processed_files += 1
                        self.progress.emit(processed_files)
            
            if self._is_running:
                self.finished.emit(self.dest_folder)
            else:
                self.error.emit("Canceled")
        except Exception as e:
            self.error.emit(f"An error occurred: {e}")

    def _get_archive_file_list(self):
        """Helper untuk mendapatkan daftar nama file dari berbagai tipe arsip."""
        if self.archive_type == '7z':
            with py7zr.SevenZipFile(self.archive_path, 'r') as a: return [f.filename for f in a.list() if not f.is_directory]
        elif self.archive_type == 'zip':
            with zipfile.ZipFile(self.archive_path, 'r') as a: return [f.filename for f in a.infolist() if not f.is_dir()]
        elif self.archive_type == 'tar':
            with tarfile.open(self.archive_path, 'r:*') as a: return [f.name for f in a.getmembers() if f.isfile()]
        elif self.archive_type == 'rar' and RAR_SUPPORT:
            with rarfile.RarFile(self.archive_path, 'r') as a: return [f.filename for f in a.infolist() if not f.isdir()]
        return []

    def stop(self):
        self._is_running = False

class MacanArchiver(QMainWindow):
    def __init__(self, file_to_open=None):
        super().__init__()
        self.current_archive_path = None
        self.current_archive_type = None
        
        # [BARU] Inisialisasi QSettings
        self.settings = QSettings("MacanAngkasa", "MacanArchiver")

        self.theme_colors = {
            'dark': {
                'toolbar': '#e0e0e0', 'folder': '#87ceeb', 'image': '#90ee90',
                'text': '#add8e6', 'file': '#e0e0e0'
            },
            'light': {
                'toolbar': '#000000', 'folder': '#00539C', 'image': '#006400',
                'text': '#00008B', 'file': '#000000'
            }
        }
        self.current_theme = 'dark'
        self.current_directory = os.path.expanduser("~") 
        self.total_uncompressed_size = 0
        self.total_files_in_archive = 0

        self.setWindowTitle("Macan Archiver")
        
        self.temp_dir = os.path.join(tempfile.gettempdir(), "macan_archiver_preview")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        icon_path = "icon.ico"
        if hasattr(sys, "_MEIPASS"):
            icon_path = os.path.join(sys._MEIPASS, icon_path)
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self._setup_ui()
        self._load_settings() # [BARU] Memuat settings saat startup
        
        if file_to_open and os.path.isfile(file_to_open):
            QTimer.singleShot(100, lambda: self._list_archive_contents(file_to_open))
        else:
            QTimer.singleShot(100, lambda: self._browse_to_path(self.current_directory))

    def _get_themed_icon(self, icon_name, icon_type='toolbar'):
        if icon_name == "archive":
            return create_svg_icon(SVG_ICONS["archive"])
            
        color = self.theme_colors[self.current_theme][icon_type]
        svg_string = SVG_ICONS[icon_name].format(color=color)
        return create_svg_icon(svg_string)

    def _setup_ui(self):
        self.setAcceptDrops(True)
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Name", "Size", "Modified", "Type"])
        
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(False)
        header.resizeSection(0, 350)
        header.resizeSection(1, 100)
        header.resizeSection(2, 150)
        header.resizeSection(3, 80)

        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.setEditTriggers(QTableWidget.EditTriggers.NoEditTriggers)
        self.table_widget.setShowGrid(False)
        self.setCentralWidget(self.table_widget)

        self.table_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.table_widget.itemSelectionChanged.connect(self._update_status_bar)
        self.table_widget.itemDoubleClicked.connect(self._handle_item_double_click)

        self._create_menus_and_toolbars()
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status_bar()

    # [BARU] Fungsi untuk memuat settings
    def _load_settings(self):
        geometry = self.settings.value("geometry")
        if geometry: self.restoreGeometry(geometry)
        else: self.setGeometry(100, 100, 800, 600)

        window_state = self.settings.value("main_window_state")
        if window_state: self.restoreState(window_state)

        theme = self.settings.value("theme", "dark")
        self._set_theme(theme)

        last_path = self.settings.value("last_path", os.path.expanduser("~"))
        self.current_directory = last_path if os.path.isdir(last_path) else os.path.expanduser("~")

    def _set_theme(self, theme):
        self.current_theme = theme
        self.setStyleSheet(DARK_THEME_QSS if theme == 'dark' else "")
        self._update_all_icons()

    def _update_all_icons(self):
        self.create_action.setIcon(self._get_themed_icon("create"))
        self.open_action.setIcon(self._get_themed_icon("open"))
        self.extract_action.setIcon(self._get_themed_icon("extract"))
        self.test_action.setIcon(self._get_themed_icon("test"))
        self.copy_action.setIcon(self._get_themed_icon("copy"))
        self.delete_action.setIcon(self._get_themed_icon("delete"))
        self.up_action.setIcon(self._get_themed_icon("up"))
        self.about_action.setIcon(self._get_themed_icon("info"))
        
        if self.current_archive_path:
            self._list_archive_contents(self.current_archive_path, force_reload=True)
        else:
            self._list_directory_contents(self.current_directory)

    def _create_menus_and_toolbars(self):
        self.create_action = QAction(self._get_themed_icon("create"), "&Create Archive...", self)
        self.open_action = QAction(self._get_themed_icon("open"), "&Open Archive...", self)
        self.properties_action = QAction("&Properties", self)
        self.exit_action = QAction("E&xit", self)
        
        self.extract_action = QAction(self._get_themed_icon("extract"), "&Extract All...", self)
        self.test_action = QAction(self._get_themed_icon("test"), "&Test Archive", self)
        self.copy_action = QAction(self._get_themed_icon("copy"), "&Copy To...", self)
        self.delete_action = QAction(self._get_themed_icon("delete"), "&Delete", self)
        
        self.select_all_action = QAction("Select All", self)
        self.deselect_all_action = QAction("Deselect All", self)
        
        self.info_action = self._get_themed_icon("info")
        self.about_action = QAction(self.info_action, "&About", self)
        # [BARU] Aksi untuk Help Content
        self.help_content_action = QAction("&Help Content", self)
        
        self.create_action.triggered.connect(self._create_archive)
        self.open_action.triggered.connect(self._open_archive)
        self.properties_action.triggered.connect(self._show_archive_properties)
        self.exit_action.triggered.connect(self.close)
        self.extract_action.triggered.connect(self._extract_archive)
        self.test_action.triggered.connect(self._test_archive)
        self.copy_action.triggered.connect(self._extract_or_copy_selected)
        self.delete_action.triggered.connect(self._delete_selected)
        self.select_all_action.triggered.connect(self.table_widget.selectAll)
        self.deselect_all_action.triggered.connect(self.table_widget.clearSelection)
        self.about_action.triggered.connect(self._show_about)
        # [BARU] Hubungkan trigger Help Content
        self.help_content_action.triggered.connect(self._show_help_content)

        self.properties_action.setEnabled(False)
        self.extract_action.setEnabled(False)
        self.test_action.setEnabled(False)
        self.copy_action.setEnabled(False)
        self.delete_action.setEnabled(False)

        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.properties_action)
        file_menu.addSeparator()
        theme_menu = file_menu.addMenu("Themes")
        light_theme_action = theme_menu.addAction("Light")
        dark_theme_action = theme_menu.addAction("Dark")
        light_theme_action.triggered.connect(lambda: self._set_theme('light'))
        dark_theme_action.triggered.connect(lambda: self._set_theme('dark'))
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(self.select_all_action)
        edit_menu.addAction(self.deselect_all_action)

        help_menu = menu_bar.addMenu("&Help")
        # [MODIFIKASI] Tambahkan Help Content ke menu
        help_menu.addAction(self.help_content_action)
        help_menu.addSeparator()
        if WIN_REG_SUPPORT:
            shell_menu = help_menu.addMenu("Shell Integration")
            register_action = shell_menu.addAction("Register Context Menu")
            unregister_action = shell_menu.addAction("Unregister Context Menu")
            register_action.triggered.connect(lambda: self._update_shell_integration(register=True))
            unregister_action.triggered.connect(lambda: self._update_shell_integration(register=False))
            help_menu.addSeparator()
        help_menu.addAction(self.about_action)
        
        nav_toolbar = QToolBar("Navigation Toolbar")
        nav_toolbar.setObjectName("NavigationToolbar") # [BARU] Beri nama objek untuk state saving
        nav_toolbar.setIconSize(QSize(22, 22))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, nav_toolbar)
        self.up_action = QAction(self._get_themed_icon("up"), "Up", self)
        self.up_action.triggered.connect(self._go_up_directory)
        nav_toolbar.addAction(self.up_action)
        self.drive_combo = QComboBox(self)
        self.drive_combo.currentTextChanged.connect(self._browse_to_path)
        nav_toolbar.addWidget(self.drive_combo)
        self._populate_drives()
        self.path_bar = QLineEdit(self)
        self.path_bar.returnPressed.connect(lambda: self._browse_to_path(self.path_bar.text()))
        nav_toolbar.addWidget(self.path_bar)
        
        main_toolbar = QToolBar("Main Toolbar")
        main_toolbar.setObjectName("MainToolbar") # [BARU] Beri nama objek untuk state saving
        main_toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(main_toolbar)
        main_toolbar.addAction(self.create_action)
        main_toolbar.addAction(self.open_action)
        main_toolbar.addSeparator()
        main_toolbar.addAction(self.extract_action)
        main_toolbar.addAction(self.test_action)
        main_toolbar.addAction(self.copy_action)
        main_toolbar.addAction(self.delete_action)
        
    def _populate_drives(self):
        self.drive_combo.blockSignals(True)
        self.drive_combo.clear()
        if sys.platform == "win32":
            drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
        else:
            drives = ["/"]
        self.drive_combo.addItems(drives)
        self.drive_combo.blockSignals(False)

    def _browse_to_path(self, path):
        if not os.path.isdir(path):
            self.status_bar.showMessage(f"Path not found: {path}", 3000)
            return
        if self.current_archive_path:
            self._reset_to_file_browser_view()
        self.current_directory = path
        self.path_bar.setText(path)
        self._list_directory_contents(path)
        self._update_status_bar()
        
    def _go_up_directory(self):
        parent_dir = os.path.dirname(self.current_directory)
        if parent_dir != self.current_directory:
            self._browse_to_path(parent_dir)

    def _list_directory_contents(self, path):
        items = []
        try:
            for name in sorted(os.listdir(path), key=str.lower):
                full_path = os.path.join(path, name)
                try:
                    stat = os.stat(full_path)
                    is_dir = os.path.isdir(full_path)
                    items.append({
                        'name': name,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        'is_dir': is_dir
                    })
                except (FileNotFoundError, PermissionError): continue
        except PermissionError:
            QMessageBox.warning(self, "Permission Denied", f"Cannot access directory:\n{path}")
        self._populate_table(items)
    
    def _reset_to_file_browser_view(self):
        self.current_archive_path = None
        self.current_archive_type = None
        self.total_uncompressed_size = 0
        self.total_files_in_archive = 0
        self.setWindowTitle("Macan Archiver")
        self.extract_action.setEnabled(False)
        self.test_action.setEnabled(False)
        self.copy_action.setEnabled(False)
        self.delete_action.setEnabled(False)
        self.properties_action.setEnabled(False)

    # [MODIFIKASI] closeEvent untuk menyimpan settings
    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("main_window_state", self.saveState())
        self.settings.setValue("last_path", self.current_directory)
        self.settings.setValue("theme", self.current_theme)
        
        try: shutil.rmtree(self.temp_dir)
        except OSError as e: print(f"Error cleaning up temp directory: {e}")
        super().closeEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.acceptProposedAction()
        else: event.ignore()

    def dropEvent(self, event):
        paths = [url.toLocalFile() for url in event.mimeData().urls()]
        if not paths: return
        supported_formats = ('.mcn', '.7z', '.zip', '.rar', '.tar', '.gz', '.bz2', '.xz')
        if len(paths) == 1 and paths[0].lower().endswith(supported_formats):
            self._list_archive_contents(paths[0])
        else:
            self._perform_archive_creation(paths)

    def _get_supported_formats_filter(self):
        filters = [
            "All Supported Archives (*.mcn *.7z *.zip *.tar *.gz *.bz2 *.xz *.rar)",
            "Macan Archive (*.mcn)", "7z Archives (*.7z)", "ZIP Archives (*.zip)",
            "TAR Archives (*.tar *.gz *.bz2 *.xz)",
        ]
        if RAR_SUPPORT: filters.append("RAR Archives (*.rar)")
        filters.append("All Files (*.*)")
        return ";;".join(filters)

    def _create_archive(self):
        files_to_add, _ = QFileDialog.getOpenFileNames(self, "Select Files to Archive", self.current_directory)
        source = files_to_add
        if not files_to_add:
            folder_to_add = QFileDialog.getExistingDirectory(self, "Select Folder to Archive", self.current_directory)
            if not folder_to_add:
                self.status_bar.showMessage("Canceled archive creation.")
                return
            source = [folder_to_add]
        self._perform_archive_creation(source)

    def _perform_archive_creation(self, source_paths):
        if not source_paths: return
        default_name = os.path.basename(source_paths[0]) if len(source_paths) == 1 else "Archive"
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Archive As", os.path.join(self.current_directory, default_name), "Macan Archive (*.mcn);;7z Archives (*.7z)")
        if not save_path:
            self.status_bar.showMessage("Canceled archive creation.")
            return

        settings_dialog = ArchiveSettingsDialog(self)
        if not settings_dialog.exec():
            self.status_bar.showMessage("Canceled archive creation.")
            return
            
        if not save_path.endswith(('.mcn', '.7z')):
            save_path += '.mcn'

        method, level = settings_dialog.get_settings()
        PRESET_MAP = {"Store": 0, "Fast": 3, "Good": 5, "Best": 9}
        METHOD_MAP = {"LZMA2": py7zr.FILTER_LZMA2, "LZMA": py7zr.FILTER_LZMA}
        filters = [{'id': METHOD_MAP[method], 'preset': PRESET_MAP[level]}]

        total_files = sum(len(files) for path in source_paths if os.path.isdir(path) for _, _, files in os.walk(path))
        total_files += sum(1 for path in source_paths if os.path.isfile(path))

        self.progress_dialog = QProgressDialog("Calculating files...", "Cancel", 0, total_files, self)
        self.progress_dialog.setWindowTitle("Creating Archive")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)

        self.thread = QThread()
        self.worker = ArchiveWorker(source_paths, save_path, filters)
        self.worker.moveToThread(self.thread)

        self.progress_dialog.canceled.connect(self.worker.stop)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_archive_creation_finished)
        self.worker.error.connect(self._on_archive_creation_error)
        self.worker.progress.connect(self.progress_dialog.setValue)
        self.worker.progress_text.connect(self.progress_dialog.setLabelText)

        self.thread.start()
        self.progress_dialog.exec()

    def _on_archive_creation_finished(self, save_path):
        self.progress_dialog.setValue(self.progress_dialog.maximum())
        self.progress_dialog.close()
        self.status_bar.showMessage(f"Successfully created {os.path.basename(save_path)}", 5000)
        self._list_archive_contents(save_path)
        self.thread.quit()
        self.thread.wait()

    def _on_archive_creation_error(self, message):
        self.progress_dialog.close()
        if message == "Canceled":
            self.status_bar.showMessage("Archive creation canceled.", 5000)
            if hasattr(self.worker, 'save_path') and os.path.exists(self.worker.save_path):
                os.remove(self.worker.save_path)
        else:
            QMessageBox.critical(self, "Error", f"Failed to create archive:\n{message}")
            self.status_bar.showMessage("Error creating archive.", 5000)
        self.thread.quit()
        self.thread.wait()

    def _open_archive(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Archive", self.current_directory, self._get_supported_formats_filter())
        if file_path:
            self._list_archive_contents(file_path)

    def _list_archive_contents(self, file_path, force_reload=False):
        if self.current_archive_path == file_path and not force_reload:
            return

        self.status_bar.showMessage(f"Opening {os.path.basename(file_path)}...")
        QApplication.processEvents()
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext in ['.mcn', '.7z']:
                self.current_archive_type = '7z'
                files_info = self._list_7z_contents(file_path)
            elif file_ext == '.zip':
                self.current_archive_type = 'zip'
                files_info = self._list_zip_contents(file_path)
            elif file_ext == '.rar':
                if not RAR_SUPPORT: raise ImportError("Module 'rarfile' is required for .rar support.")
                self.current_archive_type = 'rar'
                files_info = self._list_rar_contents(file_path)
            elif tarfile.is_tarfile(file_path):
                self.current_archive_type = 'tar'
                files_info = self._list_tar_contents(file_path)
            else:
                raise ValueError("Unsupported archive format.")

            self._populate_table(files_info)
            self.current_archive_path = file_path
            
            self.total_uncompressed_size = sum(item.get('size', 0) for item in files_info if not item.get('is_dir'))
            self.total_files_in_archive = len(files_info)
            
            self.setWindowTitle(f"Macan Archiver - {os.path.basename(file_path)}")
            self.extract_action.setEnabled(True)
            self.properties_action.setEnabled(True)
            self.test_action.setEnabled(self.current_archive_type == '7z')
            
            self.status_bar.showMessage(f"Opened {os.path.basename(file_path)}.", 5000)
            self._update_status_bar()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open archive file.\nIt might be corrupted or in an unsupported format.\n\nDetails: {e}")
            self._browse_to_path(self.current_directory)

    def _get_icon_for_file(self, name, is_dir):
        if is_dir: return self._get_themed_icon("folder", "folder")
        ext = os.path.splitext(name)[1].lower()
        if ext in ['.zip', '.7z', '.rar', '.tar', '.gz', '.bz2', '.xz', '.mcn']: return self._get_themed_icon("archive")
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']: return self._get_themed_icon("image", "image")
        if ext in ['.txt', '.md', '.log', '.py', '.js', '.html', '.css', '.json', '.xml']: return self._get_themed_icon("text", "text")
        return self._get_themed_icon("file", "file")

    def _populate_table(self, items):
        self.table_widget.setRowCount(0)
        self.table_widget.setSortingEnabled(False)
        for item in items:
            row_pos = self.table_widget.rowCount()
            self.table_widget.insertRow(row_pos)
            is_dir, name = item.get('is_dir', False), item.get('name', '')
            name_item = QTableWidgetItem(name)
            name_item.setIcon(self._get_icon_for_file(name, is_dir))
            size_str = f"{item.get('size', 0):,}" if not is_dir and item.get('size') is not None else ""
            mod_time_str = item.get('modified', "N/A")
            file_type_str = "<DIR>" if is_dir else (os.path.splitext(name)[1].upper()[1:] if os.path.splitext(name)[1] else "File")
            self.table_widget.setItem(row_pos, 0, name_item)
            self.table_widget.setItem(row_pos, 1, QTableWidgetItem(size_str))
            self.table_widget.setItem(row_pos, 2, QTableWidgetItem(mod_time_str))
            self.table_widget.setItem(row_pos, 3, QTableWidgetItem(file_type_str))
        self.table_widget.setSortingEnabled(True)

    def _list_7z_contents(self, file_path):
        with py7zr.SevenZipFile(file_path, 'r') as archive:
            return [{'name': i.filename, 'size': i.uncompressed, 'modified': i.creationtime.strftime('%Y-%m-%d %H:%M:%S') if i.creationtime else "N/A", 'is_dir': i.is_directory} for i in archive.list()]
    def _list_zip_contents(self, file_path):
        with zipfile.ZipFile(file_path, 'r') as archive:
            return [{'name': i.filename, 'size': i.file_size, 'modified': datetime(*i.date_time).strftime('%Y-%m-%d %H:%M:%S'), 'is_dir': i.is_dir()} for i in archive.infolist()]
    def _list_tar_contents(self, file_path):
        with tarfile.open(file_path, 'r:*') as archive:
            return [{'name': i.name, 'size': i.size, 'modified': datetime.fromtimestamp(i.mtime).strftime('%Y-%m-%d %H:%M:%S'), 'is_dir': i.isdir()} for i in archive.getmembers()]
    def _list_rar_contents(self, file_path):
        with rarfile.RarFile(file_path, 'r') as archive:
            return [{'name': i.filename, 'size': i.file_size, 'modified': datetime(*i.date_time).strftime('%Y-%m-%d %H:%M:%S'), 'is_dir': i.isdir()} for i in archive.infolist()]

    def _show_archive_properties(self):
        if not self.current_archive_path: return
        compressed_size = os.path.getsize(self.current_archive_path)
        dialog = ArchivePropertiesDialog(archive_path=self.current_archive_path, total_files=self.total_files_in_archive, uncompressed_size=self.total_uncompressed_size, compressed_size=compressed_size, parent=self)
        dialog.exec()
        
    def _extract_archive(self):
        if not self.current_archive_path: return
        dest_folder = QFileDialog.getExistingDirectory(self, "Select Extraction Destination", self.current_directory)
        if not dest_folder:
            self.status_bar.showMessage("Extraction canceled.", 3000)
            return
    # Panggil fungsi helper ekstraksi tanpa target (ekstrak semua)
        self._perform_extraction(dest_folder)
            
        self.status_bar.showMessage(f"Extracting all items to {dest_folder}...")
        QApplication.processEvents()
        try:
            archive_type, archive_path = self.current_archive_type, self.current_archive_path
            if archive_type == '7z':
                with py7zr.SevenZipFile(archive_path, 'r') as archive: archive.extractall(path=dest_folder)
            elif archive_type == 'zip':
                with zipfile.ZipFile(archive_path, 'r') as archive: archive.extractall(path=dest_folder)
            elif archive_type == 'tar':
                with tarfile.open(archive_path, 'r:*') as archive: archive.extractall(path=dest_folder)
            elif archive_type == 'rar' and RAR_SUPPORT:
                with rarfile.RarFile(archive_path, 'r') as archive: archive.extractall(path=dest_folder)
            
            self.status_bar.showMessage("Extraction completed successfully!", 5000)
            QMessageBox.information(self, "Success", f"Files extracted to:\n{dest_folder}")
        except Exception as e:
            QMessageBox.critical(self, "Extraction Error", f"An error occurred during extraction:\n{e}")
            self.status_bar.showMessage("Extraction failed.", 5000)
    
    def _handle_item_double_click(self, item):
        row, item_name = item.row(), self.table_widget.item(item.row(), 0).text()
        if self.current_archive_path:
            if self.table_widget.item(row, 3).text() == "<DIR>": return 
            self.status_bar.showMessage(f"Opening {item_name}..."); QApplication.processEvents()
            try:
                self._extract_or_copy_selected(filenames=[item_name], dest_folder=self.temp_dir, show_success_msg=False)
                extracted_file_path = os.path.join(self.temp_dir, item_name)
                QDesktopServices.openUrl(QUrl.fromLocalFile(extracted_file_path))
                self.status_bar.showMessage(f"Opened {item_name}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error Opening File", f"Could not open the file:\n{e}")
                self.status_bar.showMessage("Failed to open file.", 5000)
        else:
            full_path = os.path.join(self.current_directory, item_name)
            if os.path.isdir(full_path): self._browse_to_path(full_path)
            elif os.path.isfile(full_path):
                if full_path.lower().endswith(('.mcn', '.7z', '.zip', '.rar', '.tar', '.gz', '.bz2', '.xz')):
                    self._list_archive_contents(full_path)
                else:
                    try: QDesktopServices.openUrl(QUrl.fromLocalFile(full_path))
                    except Exception as e: QMessageBox.critical(self, "Error", f"Could not open file:\n{e}")

    def _get_selected_filenames(self):
        return [self.table_widget.item(row.row(), 0).text() for row in self.table_widget.selectionModel().selectedRows()]

    def _show_context_menu(self, pos):
        if not self.table_widget.selectedItems(): return
        
        context_menu = QMenu(self)
        if self.current_archive_path:
            extract_selected_action = context_menu.addAction("Extract Selected...")
            if self.current_archive_type == '7z':
                context_menu.addSeparator(); delete_action = context_menu.addAction("Delete Selected")
            else: delete_action = None
            action = context_menu.exec(self.table_widget.mapToGlobal(pos))
            if action == extract_selected_action: self._extract_or_copy_selected()
            elif action and action == delete_action: self._delete_selected()
        else:
            open_action = context_menu.addAction("Open")
            archive_action = context_menu.addAction("Add to archive...")
            action = context_menu.exec(self.table_widget.mapToGlobal(pos))
            if action == open_action:
                 selected_item = self.table_widget.currentItem()
                 if selected_item: self._handle_item_double_click(selected_item)
            elif action == archive_action:
                selected_paths = [os.path.join(self.current_directory, fname) for fname in self._get_selected_filenames()]
                if selected_paths: self._perform_archive_creation(selected_paths)

    def _update_status_bar(self):
        total_items = self.table_widget.rowCount()
        selected_rows = self.table_widget.selectionModel().selectedRows()
        num_selected, has_selection = len(selected_rows), len(selected_rows) > 0
        
        if self.current_archive_path:
            self.copy_action.setEnabled(has_selection); self.delete_action.setEnabled(has_selection and self.current_archive_type == '7z')
            status_prefix = ""
        else:
            self.copy_action.setEnabled(False); self.delete_action.setEnabled(False)
            status_prefix = f"Path: {self.current_directory} | "

        total_size = sum(int(self.table_widget.item(row.row(), 1).text().replace(',', '')) for row in selected_rows if self.table_widget.item(row.row(), 1).text())

        def format_size(size_bytes):
            if size_bytes == 0: return "0 B"
            size_name = ("B", "KB", "MB", "GB", "TB"); i = int(math.floor(math.log(size_bytes, 1024))) if size_bytes > 0 else 0
            p = math.pow(1024, i); s = round(size_bytes / p, 2)
            return f"{s} {size_name[i]}"

        status_text = f"{status_prefix}{total_items} items"
        if has_selection: status_text += f" | {num_selected} selected ({format_size(total_size)})"
        self.status_bar.showMessage(status_text)
        
    def _test_archive(self):
        if not self.current_archive_path or self.current_archive_type != '7z': return
        self.status_bar.showMessage("Testing archive integrity..."); QApplication.processEvents()
        try:
            with py7zr.SevenZipFile(self.current_archive_path, 'r') as archive: archive.test()
            QMessageBox.information(self, "Success", "Archive test completed successfully. No errors found.")
            self.status_bar.showMessage("Archive test successful.", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Test Failed", f"Archive is corrupted or invalid.\n\nDetails: {e}")
            self.status_bar.showMessage("Archive test failed.", 5000)

    def _extract_or_copy_selected(self, filenames=None, dest_folder=None, show_success_msg=True):
        if filenames is None: 
            filenames = self._get_selected_filenames()
        
        if not filenames:
            if show_success_msg: 
                QMessageBox.warning(self, "No Selection", "Please select files or folders to extract/copy.")
            return

        if dest_folder is None: 
            dest_folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder", self.current_directory)
        
        if not dest_folder: 
            return

        # Panggil fungsi helper ekstraksi dengan target spesifik
        self._perform_extraction(dest_folder, targets=filenames, show_success_msg=show_success_msg)
        
        self.status_bar.showMessage(f"Extracting {len(filenames)} item(s)..."); QApplication.processEvents()
        try:
            archive_type, archive_path = self.current_archive_type, self.current_archive_path
            if archive_type == '7z':
                with py7zr.SevenZipFile(archive_path, 'r') as archive: archive.extract(path=dest_folder, targets=filenames)
            elif archive_type == 'zip':
                with zipfile.ZipFile(archive_path, 'r') as archive:
                    for f in filenames: archive.extract(f, path=dest_folder)
            elif archive_type == 'tar':
                 with tarfile.open(archive_path, 'r:*') as archive:
                    members = [m for m in archive.getmembers() if m.name in filenames]
                    archive.extractall(path=dest_folder, members=members)
            elif archive_type == 'rar' and RAR_SUPPORT:
                 with rarfile.RarFile(archive_path, 'r') as archive:
                    for f in filenames: archive.extract(f, path=dest_folder)
            
            if show_success_msg:
                self.status_bar.showMessage("Selected items extracted successfully!", 5000)
                QMessageBox.information(self, "Success", f"Files extracted to:\n{dest_folder}")
        except Exception as e:
            if show_success_msg:
                QMessageBox.critical(self, "Extraction Error", f"An error occurred:\n{e}")
                self.status_bar.showMessage("Extraction failed.", 5000)
            else: raise e

    def _perform_extraction(self, dest_folder, targets=None, show_success_msg=True):
    # Dapatkan daftar file jika 'targets' tidak disediakan (untuk menghitung total)
        effective_targets = targets
        if not effective_targets:
            try:
            # Cepat ambil daftar file tanpa worker untuk setup progress dialog
                worker_temp = ExtractionWorker(self.current_archive_path, self.current_archive_type, dest_folder, None)
                effective_targets = worker_temp._get_archive_file_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not read archive file list: {e}")
            return
            
        total_files = len(effective_targets)

        self.progress_dialog = QProgressDialog("Starting extraction...", "Cancel", 0, total_files, self)
        self.progress_dialog.setWindowTitle("Extracting Files")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)

        self.thread = QThread()
    # Berikan 'targets' ke worker. Jika None, worker akan ekstrak semua.
        self.worker = ExtractionWorker(self.current_archive_path, self.current_archive_type, dest_folder, targets)
        self.worker.moveToThread(self.thread)

        self.progress_dialog.canceled.connect(self.worker.stop)
        self.thread.started.connect(self.worker.run)
    
    # Gunakan lambda untuk meneruskan argumen tambahan ke slot
        self.worker.finished.connect(lambda path: self._on_extraction_finished(path, show_success_msg))
        self.worker.error.connect(self._on_extraction_error)
        self.worker.progress.connect(self.progress_dialog.setValue)
        self.worker.progress_text.connect(self.progress_dialog.setLabelText)

        self.thread.start()
        self.progress_dialog.exec()

    def _on_extraction_finished(self, dest_folder, show_success_msg):
        self.progress_dialog.setValue(self.progress_dialog.maximum())
        self.progress_dialog.close()
        if show_success_msg:
            self.status_bar.showMessage("Extraction completed successfully!", 5000)
            QMessageBox.information(self, "Success", f"Files extracted to:\n{dest_folder}")
        self.thread.quit()
        self.thread.wait()

    def _on_extraction_error(self, message):
        self.progress_dialog.close()
        if message == "Canceled":
            self.status_bar.showMessage("Extraction canceled.", 5000)
        else:
            QMessageBox.critical(self, "Extraction Error", f"An error occurred during extraction:\n{message}")
        self.status_bar.showMessage("Extraction failed.", 5000)
        self.thread.quit()
        self.thread.wait()

    def _delete_selected(self):
        if self.current_archive_type != '7z':
             QMessageBox.information(self, "Unsupported Operation", "Deleting items is only supported for .mcn and .7z archives."); return
        filenames_to_delete = self._get_selected_filenames()
        if not filenames_to_delete: return
        reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to permanently delete {len(filenames_to_delete)} item(s) from the archive?\n\nThis operation requires repacking the entire archive.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No: return

        self.status_bar.showMessage("Repacking archive to delete items..."); QApplication.processEvents()
        original_path, temp_archive_path = self.current_archive_path, self.current_archive_path + ".tmp"
        try:
            with py7zr.SevenZipFile(original_path, 'r') as archive_in:
                files_to_keep = [f for f in archive_in.getnames() if f not in filenames_to_delete]
                with tempfile.TemporaryDirectory() as temp_dir:
                    archive_in.extract(path=temp_dir, targets=files_to_keep)
                    with py7zr.SevenZipFile(temp_archive_path, 'w') as archive_out:
                        for item in files_to_keep:
                            item_path = os.path.join(temp_dir, item)
                            if os.path.exists(item_path): archive_out.write(item_path, arcname=item)
            
            shutil.move(temp_archive_path, original_path)
            self.status_bar.showMessage("Items deleted successfully. Reloading...", 5000)
            self._list_archive_contents(original_path)
        except Exception as e:
            QMessageBox.critical(self, "Deletion Error", f"An error occurred while deleting items:\n{e}")
            if os.path.exists(temp_archive_path): os.remove(temp_archive_path)

    def _show_about(self):
        rar_note = "<b>Note:</b> To open .rar files, you need to install the 'rarfile' package." if not RAR_SUPPORT else "RAR support is enabled."
        QMessageBox.information(self, "About Macan Archiver",
            "<b>Macan Archiver v3.0.0 (Pro Edition)</b><br><br>"
            "A professional file archiver with theme support, file icons, CLI, and Windows Shell integration. 🧭<br>"
            "<b>Supported Formats:</b> .mcn, .7z, .zip, .tar, .rar<br><br>"
            f"{rar_note}<br><br>"
            "Created with pride. 🐅<br>"
            "Copyright © 2025 - Danx Exodus - Macan Angkasa"
        )
    
    # [BARU] Metode untuk menampilkan konten bantuan (diambil dari macan_archiver14.py)
    def _show_help_content(self):
        help_text = """
        <h2>Macan Archiver Help</h2>
        <p>This guide provides an overview of the main features of Macan Archiver.</p>
        
        <h3><br>Main Features</h3>
        <ul>
            <li><b>Creating Archives:</b> Click the 'Create' icon or use File > Create Archive. You can select multiple files or a single folder. In the settings dialog, you can choose compression level, method, and set an optional password (AES-256 encrypted for .7z/.mcn).</li>
            <li><b>Opening Archives:</b> Double-click a supported archive file, drag & drop it onto the window, or use the 'Open' icon.</li>
            <li><b>Extracting Files:</b>
                <ul>
                    <li><b>Extract All:</b> Click the 'Extract' icon to extract all contents of the archive to a chosen folder.</li>
                    <li><b>Extract Selected:</b> Select one or more files/folders inside an archive, then right-click and choose 'Extract Selected...'.</li>
                    <li><b>Double-Click:</b> Double-clicking a file inside an archive will extract it to a temporary folder and open it with the default application.</li>
                </ul>
            </li>
            <li><b>Password Protection:</b> Macan Archiver can create password-protected .7z and .mcn archives. It can also open password-protected .7z, .zip, and .rar files. You will be prompted for a password if required.</li>
        </ul>
        
        <h3><br>User Interface</h3>
        <ul>
            <li><b>Navigation Bar:</b> Use the drive dropdown, 'Up' button, or type a path directly into the path bar to navigate your file system.</li>
            <li><b>Themes:</b> Change between light and dark themes via the File > Themes menu.</li>
            <li><b>Status Bar:</b> Displays information about the current directory or archive, including the number of items and the size of selected files.</li>
        </ul>

        <h3><br>Windows Shell Integration</h3>
        <p>To enable, run Macan Archiver as an administrator and go to Help > Shell Integration > Register Context Menu. This will add the following options to your right-click menu in Windows Explorer:</p>
        <ul>
            <li><b>For any file/folder:</b> "Add to Macan Archive..." - Creates a new archive from the selected items.</li>
            <li><b>For archive files:</b>
                <ul>
                    <li>"Open with Macan Archiver" - Opens the archive in the app.</li>
                    <li>"Extract Here" - Extracts contents to the current folder.</li>
                    <li>"Extract To..." - Opens a dialog to choose an extraction folder.</li>
                </ul>
            </li>
        </ul>
        <p>You can remove these menus at any time using the 'Unregister' option.</p>
        """
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Help Content")
        dialog.setMinimumSize(600, 450)
        
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setHtml(help_text)
        text_edit.setReadOnly(True)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(dialog.accept)
        
        layout.addWidget(text_edit)
        layout.addWidget(button_box)
        
        dialog.exec()
        
    def _update_shell_integration(self, register=True):
        if not WIN_REG_SUPPORT:
            QMessageBox.warning(self, "Unsupported OS", "Windows Shell integration is only available on Windows.")
            return
        
        try:
            exe_path = sys.executable
            if exe_path.lower().endswith(("python.exe", "pythonw.exe")):
                script_path = os.path.abspath(__file__)
                base_command = f'"{exe_path}" "{script_path}"'
            else:
                base_command = f'"{exe_path}"'

            archive_exts = ['.7z', '.mcn', '.zip', '.rar', '.tar', '.gz', '.bz2', '.xz']
            
            archive_commands = {
                r'shell\OpenWithMacanArchiver': ("Open with Macan Archiver", f'{base_command} "%1"'),
            }
            for ext in archive_exts:
                for sub_key, (value, command) in archive_commands.items():
                    key_path = fr'SystemFileAssociations\{ext}\{sub_key}'
                    if register:
                        with winreg.CreateKeyEx(winreg.HKEY_CLASSES_ROOT, key_path) as key:
                            winreg.SetValue(key, None, winreg.REG_SZ, value)
                        with winreg.CreateKeyEx(winreg.HKEY_CLASSES_ROOT, fr'{key_path}\command') as cmd_key:
                            winreg.SetValue(cmd_key, None, winreg.REG_SZ, command)
                    else:
                        try:
                            winreg.DeleteKeyEx(winreg.HKEY_CLASSES_ROOT, fr'{key_path}\command')
                            winreg.DeleteKeyEx(winreg.HKEY_CLASSES_ROOT, key_path)
                        except FileNotFoundError: pass

            target_keys = {
                r'*\shell\MacanAddToArchive': "Add to archive (Macan)...",
                r'Directory\shell\MacanAddToArchive': "Add to archive (Macan)..."
            }
            for key_path, value in target_keys.items():
                if register:
                    with winreg.CreateKeyEx(winreg.HKEY_CLASSES_ROOT, key_path) as key:
                        winreg.SetValue(key, None, winreg.REG_SZ, value)
                    with winreg.CreateKeyEx(winreg.HKEY_CLASSES_ROOT, fr'{key_path}\command') as cmd_key:
                        winreg.SetValue(cmd_key, None, winreg.REG_SZ, f'{base_command} %*')
                else:
                    try:
                        winreg.DeleteKeyEx(winreg.HKEY_CLASSES_ROOT, fr'{key_path}\command')
                        winreg.DeleteKeyEx(winreg.HKEY_CLASSES_ROOT, key_path)
                    except FileNotFoundError: pass

            action = "registered" if register else "unregistered"
            QMessageBox.information(self, "Success", f"Shell context menu has been successfully {action}.")

        except PermissionError:
            QMessageBox.critical(self, "Permission Denied", "This operation requires administrator privileges.\nPlease restart Macan Archiver as an administrator and try again.")
        except Exception as e:
            QMessageBox.critical(self, "Registry Error", f"An error occurred while updating the registry:\n{e}")

def handle_cli_creation(args):
    """Fungsi ini dieksekusi jika argumen CLI terdeteksi, tanpa GUI."""
    if not args.source: print("Error: --source argument is required.", file=sys.stderr); return
    if not args.output: print("Error: --output argument is required.", file=sys.stderr); return
    print(f"Archiving {len(args.source)} source(s) to '{args.output}'...")
    PRESET_MAP = {"store": 0, "fast": 3, "good": 5, "best": 9}
    METHOD_MAP = {"lzma2": py7zr.FILTER_LZMA2, "lzma": py7zr.FILTER_LZMA}
    level_preset = PRESET_MAP.get(args.level.lower(), 5)
    method_id = METHOD_MAP.get(args.method.lower(), py7zr.FILTER_LZMA2)
    filters = [{'id': method_id, 'preset': level_preset}]
    try:
        with py7zr.SevenZipFile(args.output, 'w', filters=filters) as archive:
            for path in args.source:
                if not os.path.exists(path):
                    print(f"Warning: Source path not found, skipping: {path}", file=sys.stderr); continue
                print(f"Adding: {path}")
                if os.path.isfile(path): archive.write(path, os.path.basename(path))
                elif os.path.isdir(path): archive.writeall(path, os.path.basename(path))
        print("\nArchive created successfully.")
    except Exception as e: print(f"\nAn error occurred during archiving: {e}", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Macan Archiver - GUI and CLI tool.")
    parser.add_argument('--create', action='store_true', help='Run in CLI mode to create an archive.')
    parser.add_argument('--source', nargs='+', help='One or more source files or directories to archive.')
    parser.add_argument('--output', help='Path for the output archive file (e.g., archive.mcn).')
    parser.add_argument('--level', default='good', choices=['store', 'fast', 'good', 'best'], help='Compression level.')
    parser.add_argument('--method', default='lzma2', choices=['lzma', 'lzma2'], help='Compression method.')
    parser.add_argument('file_path_arg', nargs='?', default=None)
    
    args = parser.parse_args()

    if args.create:
        handle_cli_creation(args)
        sys.exit(0)

    app = QApplication(sys.argv)
    
    if not RAR_SUPPORT:
        print("Warning: 'rarfile' module not found. RAR file support will be disabled.")

    file_to_open = args.file_path_arg
    
    window = MacanArchiver(file_to_open=file_to_open)
    window.show()
    sys.exit(app.exec())