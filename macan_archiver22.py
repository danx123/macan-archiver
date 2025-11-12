import sys
import os
import shutil
import tempfile
import math
import subprocess
import string
import argparse
import re # [BARU] Impor modul regular expression
import py7zr
from datetime import datetime

# Hapus impor pustaka arsip lama, karena kita akan menggunakan 7z.exe
# import py7zr 
# import zipfile
# import tarfile

try:
    import rarfile # Masih digunakan untuk deteksi dukungan RAR
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

    QTextEdit, QInputDialog, QCheckBox # [BARU] Impor tambahan
)
from PySide6.QtGui import QAction, QIcon, QPixmap, QDesktopServices
from PySide6.QtCore import (
    Qt, QSize, QByteArray, QTimer, QThread, Signal, QObject, QUrl,
    QSettings
)

# --- SVG Icons (Tidak berubah) ---
SVG_ICONS = {
    "create": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>""",
    "open": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 12v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h5l4 4h5a2 2 0 0 1 2 2v1"></path><path d="M18 13v-2a2 2 0 0 0-2-2H8"></path></svg>""",
    "extract": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>""",
    "add": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><line x1="20" y1="8" x2="20" y2="14"></line><line x1="17" y1="11" x2="23" y2="11"></line></svg>""", # [BARU] Ikon untuk "Add"
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


# --- Dark Theme Stylesheet (Tidak berubah) ---
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

# [MODIFIKASI] Dialog diupdate untuk menyertakan input password
class ArchiveSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Archive Settings")
        layout = QFormLayout(self)

        self.level_combo = QComboBox()
        self.level_combo.addItems(["Store (0)", "Fastest (1)", "Fast (3)", "Normal (5)", "Maximum (7)", "Ultra (9)"])
        self.level_combo.setCurrentText("Normal (5)")
        layout.addRow(QLabel("Compression Level:"), self.level_combo)
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow(QLabel("Password (optional):"), self.password_edit)

        self.show_password_check = QCheckBox("Show Password")
        self.show_password_check.toggled.connect(self.toggle_password_visibility)
        layout.addRow("", self.show_password_check)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def toggle_password_visibility(self, checked):
        if checked:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

    def get_settings(self):
        level_text = self.level_combo.currentText()
        level = re.search(r'\((\d+)\)', level_text).group(1) # Ekstrak angka dari string
        password = self.password_edit.text()
        return level, password

# Kelas ArchivePropertiesDialog tidak berubah signifikan
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
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

# [REWRITE] Worker untuk operasi arsip menggunakan 7z.exe (Create, Add/Update)
class ArchiveWorker(QObject):
    progress = Signal(int)
    progress_text = Signal(str)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, sevenzip_path, command, archive_path, source_paths, level, password):
        super().__init__()
        self.sevenzip_path = sevenzip_path
        self.command = command # 'a' (add) atau 'u' (update)
        self.archive_path = archive_path
        self.source_paths = source_paths
        self.level = level
        self.password = password
        self._is_running = True
        self.process = None

    def run(self):
        try:
            # Bangun command list untuk subprocess
            cmd = [self.sevenzip_path, self.command, self.archive_path] + self.source_paths
            cmd.append(f"-mx={self.level}") # Level kompresi
            if self.password:
                cmd.append(f"-p{self.password}")
            cmd.append('-y') # Asumsikan ya untuk semua prompt
            
            # Pengaturan untuk menyembunyikan jendela konsol di Windows
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )

            # Baca output stdout untuk progress
            for line in iter(self.process.stdout.readline, ''):
                if not self._is_running:
                    self.process.terminate()
                    break
                
                # Parsing progress percentage
                match = re.search(r'(\d+)\s*%', line)
                if match:
                    percentage = int(match.group(1))
                    self.progress.emit(percentage)
                
                # Parsing nama file yang sedang diproses
                if line.startswith("Compressing"):
                    self.progress_text.emit(line.strip())

            self.process.stdout.close()
            return_code = self.process.wait()

            if not self._is_running:
                self.error.emit("Canceled")
                return

            if return_code == 0:
                self.finished.emit(self.archive_path)
            else:
                error_output = self.process.stderr.read()
                self.error.emit(f"7-Zip process failed with code {return_code}:\n{error_output}")

        except Exception as e:
            self.error.emit(f"An error occurred: {e}")

    def stop(self):
        self._is_running = False
        if self.process:
            try:
                self.process.terminate()
            except ProcessLookupError:
                pass

# [REWRITE] Worker untuk ekstraksi menggunakan 7z.exe
class ExtractionWorker(QObject):
    progress = Signal(int)
    progress_text = Signal(str)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, sevenzip_path, archive_path, dest_folder, password, targets=None):
        super().__init__()
        self.sevenzip_path = sevenzip_path
        self.archive_path = archive_path
        self.dest_folder = dest_folder
        self.password = password
        self.targets = targets or []
        self._is_running = True
        self.process = None

    def run(self):
        try:
            cmd = [self.sevenzip_path, 'x', self.archive_path, f'-o{self.dest_folder}']
            if self.password:
                cmd.append(f"-p{self.password}")
            cmd.append('-y') # Asumsikan ya untuk semua prompt
            if self.targets:
                cmd.extend(self.targets)
                
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            for line in iter(self.process.stdout.readline, ''):
                if not self._is_running:
                    self.process.terminate()
                    break
                
                match = re.search(r'(\d+)\s*%', line)
                if match:
                    percentage = int(match.group(1))
                    self.progress.emit(percentage)

                if line.startswith("Extracting"):
                     self.progress_text.emit(line.strip())

            self.process.stdout.close()
            return_code = self.process.wait()

            if not self._is_running:
                self.error.emit("Canceled")
                return

            if return_code == 0:
                self.finished.emit(self.dest_folder)
            else:
                error_output = self.process.stderr.read()
                self.error.emit(f"7-Zip process failed with code {return_code}:\n{error_output}")

        except Exception as e:
            self.error.emit(f"An error occurred: {e}")

    def stop(self):
        self._is_running = False
        if self.process:
            try:
                self.process.terminate()
            except ProcessLookupError:
                pass


class MacanArchiver(QMainWindow):
    def __init__(self, file_to_open=None):
        super().__init__()
        self.current_archive_path = None
        self.sevenzip_path = self._find_7z_executable() # [BARU] Cari 7z.exe saat startup
        
        if not self.sevenzip_path:
             QMessageBox.critical(self, "7-Zip Not Found",
                "7z.exe could not be found in standard locations or system PATH.\n"
                "Please install 7-Zip and ensure its directory is in your PATH.\n"
                "The application will now close.")
             sys.exit(1)

        self.settings = QSettings("MacanAngkasa", "MacanArchiver")
        self.theme_colors = {
            'dark': {'toolbar': '#e0e0e0', 'folder': '#87ceeb', 'image': '#90ee90', 'text': '#add8e6', 'file': '#e0e0e0'},
            'light': {'toolbar': '#000000', 'folder': '#00539C', 'image': '#006400', 'text': '#00008B', 'file': '#000000'}
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
        self._load_settings()
        
        if file_to_open and os.path.isfile(file_to_open):
            QTimer.singleShot(100, lambda: self._list_archive_contents(file_to_open))
        else:
            QTimer.singleShot(100, lambda: self._browse_to_path(self.current_directory))

    # [BARU] Fungsi untuk menemukan 7z.exe
    def _find_7z_executable(self):
        """Finds the 7-Zip executable."""
        # Cek di PATH sistem
        path = shutil.which("7z")
        if path:
            return path
        # Cek di lokasi instalasi default Windows
        if sys.platform == "win32":
            for path in [
                os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "7-Zip", "7z.exe"),
                os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "7-Zip", "7z.exe")
            ]:
                if os.path.exists(path):
                    return path
        return None

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
        self.add_action.setIcon(self._get_themed_icon("add")) # [BARU]
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
        # ... Aksi yang ada ...
        self.create_action = QAction(self._get_themed_icon("create"), "&Create Archive...", self)
        self.open_action = QAction(self._get_themed_icon("open"), "&Open Archive...", self)
        self.properties_action = QAction("&Properties", self)
        self.exit_action = QAction("E&xit", self)
        self.extract_action = QAction(self._get_themed_icon("extract"), "&Extract All...", self)
        self.add_action = QAction(self._get_themed_icon("add"), "&Add Files...", self) # [BARU]
        self.test_action = QAction(self._get_themed_icon("test"), "&Test Archive", self)
        self.copy_action = QAction(self._get_themed_icon("copy"), "&Copy To...", self)
        self.delete_action = QAction(self._get_themed_icon("delete"), "&Delete", self)
        self.select_all_action = QAction("Select All", self)
        self.deselect_all_action = QAction("Deselect All", self)
        self.about_action = QAction(self._get_themed_icon("info"), "&About", self)
        self.help_content_action = QAction("&Help Content", self)

        self.create_action.triggered.connect(self._create_archive)
        self.open_action.triggered.connect(self._open_archive)
        self.properties_action.triggered.connect(self._show_archive_properties)
        self.exit_action.triggered.connect(self.close)
        self.extract_action.triggered.connect(lambda: self._extract_archive(selected_only=False))
        self.add_action.triggered.connect(self._add_to_archive) # [BARU]
        self.test_action.triggered.connect(self._test_archive)
        self.copy_action.triggered.connect(lambda: self._extract_archive(selected_only=True, copy_mode=True))
        self.delete_action.triggered.connect(self._delete_selected)
        self.select_all_action.triggered.connect(self.table_widget.selectAll)
        self.deselect_all_action.triggered.connect(self.table_widget.clearSelection)
        self.about_action.triggered.connect(self._show_about)
        self.help_content_action.triggered.connect(self._show_help_content)

        # Non-aktifkan tombol yang relevan dengan arsip
        self.properties_action.setEnabled(False)
        self.extract_action.setEnabled(False)
        self.add_action.setEnabled(False) # [BARU]
        self.test_action.setEnabled(False)
        self.copy_action.setEnabled(False)
        self.delete_action.setEnabled(False)

        menu_bar = self.menuBar()
        # ... (Struktur menu tidak berubah, hanya tambahkan aksi jika perlu) ...
        # ... (Kode menu lengkap tidak perlu disalin ulang jika tidak berubah) ...
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
        nav_toolbar.setObjectName("NavigationToolbar")
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
        main_toolbar.setObjectName("MainToolbar")
        main_toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(main_toolbar)
        main_toolbar.addAction(self.create_action)
        main_toolbar.addAction(self.open_action)
        main_toolbar.addSeparator()
        main_toolbar.addAction(self.extract_action)
        main_toolbar.addAction(self.add_action) # [BARU] Tambahkan tombol "Add"
        main_toolbar.addSeparator()
        main_toolbar.addAction(self.test_action)
        main_toolbar.addAction(self.copy_action)
        main_toolbar.addAction(self.delete_action)

    # [BARU] Fungsi untuk memeriksa apakah arsip dienkripsi
    def _is_archive_encrypted(self, archive_path):
        try:
            # -p- (password kosong) akan gagal pada file terenkripsi dengan cepat
            cmd = [self.sevenzip_path, 't', archive_path, '-p-']
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore',
                                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
            output = result.stdout + result.stderr
            return "Wrong password" in output or "Enter password" in output
        except Exception:
            return False # Asumsikan tidak terenkripsi jika tes gagal karena alasan lain
            
    # [BARU] Fungsi untuk meminta password dari pengguna
    def _prompt_for_password(self):
        password, ok = QInputDialog.getText(self, "Password Required", "Enter password for the archive:", QLineEdit.EchoMode.Password)
        if ok:
            return password
        return None

    # [MODIFIKASI] Metode _create_archive menggunakan worker baru
    def _perform_archive_creation(self, source_paths, update_mode=False):
        if not source_paths: return
        
        # Jika update mode, gunakan path arsip yang ada
        if update_mode:
            save_path = self.current_archive_path
            password = "" # Asumsikan password sama atau tidak ada untuk update sederhana
        else:
            default_name = os.path.basename(source_paths[0]) if len(source_paths) == 1 else "Archive"
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Archive As", os.path.join(self.current_directory, default_name), "7z Archives (*.7z);;Macan Archive (*.mcn)")
            if not save_path:
                self.status_bar.showMessage("Canceled archive creation.")
                return

            settings_dialog = ArchiveSettingsDialog(self)
            if not settings_dialog.exec():
                self.status_bar.showMessage("Canceled archive creation.")
                return
            
            level, password = settings_dialog.get_settings()
            if not save_path.lower().endswith(('.mcn', '.7z')):
                save_path += '.7z'

        self.progress_dialog = QProgressDialog("Starting process...", "Cancel", 0, 100, self)
        self.progress_dialog.setWindowTitle("Creating Archive" if not update_mode else "Adding Files")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)

        self.thread = QThread()
        command = 'u' if update_mode else 'a'
        # Untuk mode 'a' baru, level dan password dari dialog, untuk 'u' default saja
        self.worker = ArchiveWorker(self.sevenzip_path, command, save_path, source_paths, level if not update_mode else '5', password)
        self.worker.moveToThread(self.thread)

        self.progress_dialog.canceled.connect(self.worker.stop)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_archive_operation_finished)
        self.worker.error.connect(self._on_archive_operation_error)
        self.worker.progress.connect(self.progress_dialog.setValue)
        self.worker.progress_text.connect(self.progress_dialog.setLabelText)

        self.thread.start()
        self.progress_dialog.exec()

    def _on_archive_operation_finished(self, save_path):
        self.progress_dialog.setValue(self.progress_dialog.maximum())
        self.progress_dialog.close()
        self.status_bar.showMessage(f"Operation on {os.path.basename(save_path)} successful!", 5000)
        self._list_archive_contents(save_path, force_reload=True) # Reload setelah operasi
        self.thread.quit()
        self.thread.wait()

    def _on_archive_operation_error(self, message):
        self.progress_dialog.close()
        if "Canceled" in message:
            self.status_bar.showMessage("Operation canceled.", 5000)
        else:
            QMessageBox.critical(self, "Error", f"Failed to perform operation:\n{message}")
            self.status_bar.showMessage("Error during archive operation.", 5000)
        self.thread.quit()
        self.thread.wait()

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

    # [REWRITE] Fungsi untuk mendaftar isi arsip menggunakan '7z l -slt'
    def _list_archive_contents(self, file_path, force_reload=False):
        if self.current_archive_path == file_path and not force_reload:
            return
        self.status_bar.showMessage(f"Opening {os.path.basename(file_path)}...")
        QApplication.processEvents()

        try:
            files_info = self._parse_7z_list_output(file_path)
            self._populate_table(files_info)
            self.current_archive_path = file_path
            
            self.total_uncompressed_size = sum(item.get('size', 0) for item in files_info if not item.get('is_dir'))
            self.total_files_in_archive = len(files_info)
            
            self.setWindowTitle(f"Macan Archiver - {os.path.basename(file_path)}")
            # Aktifkan tombol yang relevan
            self.extract_action.setEnabled(True)
            self.add_action.setEnabled(True)
            self.properties_action.setEnabled(True)
            self.test_action.setEnabled(True)
            self.delete_action.setEnabled(True)
            
            self.status_bar.showMessage(f"Opened {os.path.basename(file_path)}.", 5000)
            self._update_status_bar()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open archive file.\nIt might be corrupted or in an unsupported format.\n\nDetails: {e}")
            self._browse_to_path(self.current_directory)
    
    # [BARU] Parser untuk output '7z l -slt'
    def _parse_7z_list_output(self, file_path):
        cmd = [self.sevenzip_path, 'l', '-slt', file_path]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore',
                                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        if result.returncode != 0:
            raise RuntimeError(f"7-Zip failed to list contents:\n{result.stderr}")

        files_info = []
        current_file = {}
        for line in result.stdout.splitlines():
            if line.startswith('Path = '):
                if current_file: files_info.append(current_file)
                current_file = {'name': line[7:]}
            elif line.startswith('Size = '):
                current_file['size'] = int(line[7:])
            elif line.startswith('Modified = '):
                try:
                    dt = datetime.strptime(line[11:], '%Y-%m-%d %H:%M:%S')
                    current_file['modified'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    current_file['modified'] = "N/A"
            elif line.startswith('Attributes = '):
                current_file['is_dir'] = 'D' in line[13:]
        if current_file: files_info.append(current_file)
        
        # Hapus direktori induk dari daftar (jika ada)
        return [f for f in files_info if f['name'] != '']

    # [REWRITE] Fungsi _extract_archive menggunakan ExtractionWorker
    def _extract_archive(self, selected_only=False, copy_mode=False):
        if not self.current_archive_path: return
        
        targets = self._get_selected_filenames() if selected_only else []
        if selected_only and not targets:
            QMessageBox.warning(self, "No Selection", "Please select files or folders to extract.")
            return

        dest_folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder", self.current_directory)
        if not dest_folder:
            self.status_bar.showMessage("Extraction canceled.", 3000)
            return

        password = ""
        if self._is_archive_encrypted(self.current_archive_path):
            password = self._prompt_for_password()
            if password is None: # User canceled password dialog
                self.status_bar.showMessage("Extraction canceled.", 3000)
                return

        self.progress_dialog = QProgressDialog("Starting extraction...", "Cancel", 0, 100, self)
        self.progress_dialog.setWindowTitle("Extracting Files")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)

        self.thread = QThread()
        self.worker = ExtractionWorker(self.sevenzip_path, self.current_archive_path, dest_folder, password, targets)
        self.worker.moveToThread(self.thread)

        self.progress_dialog.canceled.connect(self.worker.stop)
        self.thread.started.connect(self.worker.run)
        
        # Gunakan lambda untuk meneruskan argumen tambahan ke slot
        show_msg = not copy_mode
        self.worker.finished.connect(lambda path: self._on_extraction_finished(path, show_msg))
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
        if "Canceled" in message:
            self.status_bar.showMessage("Extraction canceled.", 5000)
        else:
            QMessageBox.critical(self, "Extraction Error", f"An error occurred during extraction:\n{message}")
            self.status_bar.showMessage("Extraction failed.", 5000)
        self.thread.quit()
        self.thread.wait()

    # [BARU] Fungsi untuk menambah file ke arsip yang ada
    def _add_to_archive(self):
        if not self.current_archive_path: return
        
        files_to_add, _ = QFileDialog.getOpenFileNames(self, "Select Files to Add", self.current_directory)
        source = list(files_to_add)
        
        folder_to_add = QFileDialog.getExistingDirectory(self, "Select Folder to Add (Optional)", self.current_directory)
        if folder_to_add:
            source.append(folder_to_add)

        if not source:
            self.status_bar.showMessage("Add operation canceled.", 3000)
            return
            
        # Panggil _perform_archive_creation dengan mode update
        self._perform_archive_creation(source, update_mode=True)
    
    # [REWRITE] _test_archive menggunakan 7z.exe
    def _test_archive(self):
        if not self.current_archive_path: return
        self.status_bar.showMessage("Testing archive integrity..."); QApplication.processEvents()
        try:
            password = ""
            if self._is_archive_encrypted(self.current_archive_path):
                password = self._prompt_for_password()
                if password is None: return

            cmd = [self.sevenzip_path, 't', self.current_archive_path]
            if password:
                cmd.append(f"-p{password}")
                
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore',
                                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
            
            if "Everything is Ok" in result.stdout:
                QMessageBox.information(self, "Success", "Archive test completed successfully. No errors found.")
                self.status_bar.showMessage("Archive test successful.", 5000)
            else:
                raise RuntimeError(result.stderr or result.stdout)
                
        except Exception as e:
            QMessageBox.critical(self, "Test Failed", f"Archive is corrupted, invalid, or password is wrong.\n\nDetails: {e}")
            self.status_bar.showMessage("Archive test failed.", 5000)

    # [REWRITE] _delete_selected menggunakan 7z.exe 'd' command
    def _delete_selected(self):
        filenames_to_delete = self._get_selected_filenames()
        if not filenames_to_delete: return
        
        reply = QMessageBox.question(self, "Confirm Delete", 
            f"Are you sure you want to permanently delete {len(filenames_to_delete)} item(s) from the archive?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No: return

        self.status_bar.showMessage("Deleting items from archive..."); QApplication.processEvents()
        try:
            # Command: 7z d archive.7z file1 file2 ...
            cmd = [self.sevenzip_path, 'd', self.current_archive_path] + filenames_to_delete
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore',
                                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
            
            if result.returncode == 0:
                 self.status_bar.showMessage("Items deleted successfully. Reloading...", 5000)
                 self._list_archive_contents(self.current_archive_path, force_reload=True)
            else:
                raise RuntimeError(result.stderr)
                
        except Exception as e:
            QMessageBox.critical(self, "Deletion Error", f"An error occurred while deleting items:\n{e}")

    # --- Sisa fungsi (yang tidak perlu diubah secara signifikan) ---
    # _populate_drives, _browse_to_path, _go_up_directory, _list_directory_contents,
    # _reset_to_file_browser_view, closeEvent, dragEnterEvent, dropEvent,
    # _get_supported_formats_filter, _create_archive, _open_archive, _get_icon_for_file,
    # _populate_table, _show_archive_properties, _handle_item_double_click,
    # _get_selected_filenames, _show_context_menu, _update_status_bar, _show_about,
    # _show_help_content, _update_shell_integration, handle_cli_creation

    # Perlu sedikit modifikasi pada fungsi-fungsi berikut agar selaras
    def _reset_to_file_browser_view(self):
        self.current_archive_path = None
        self.total_uncompressed_size = 0
        self.total_files_in_archive = 0
        self.setWindowTitle("Macan Archiver")
        self.extract_action.setEnabled(False)
        self.add_action.setEnabled(False)
        self.test_action.setEnabled(False)
        self.copy_action.setEnabled(False)
        self.delete_action.setEnabled(False)
        self.properties_action.setEnabled(False)

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
        # 7-zip mendukung semua ini
        return "All Supported Archives (*.mcn *.7z *.zip *.tar *.gz *.bz2 *.xz *.rar);;All Files (*.*)"

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

    def _open_archive(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Archive", self.current_directory, self._get_supported_formats_filter())
        if file_path:
            self._list_archive_contents(file_path)

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

    def _show_archive_properties(self):
        if not self.current_archive_path: return
        compressed_size = os.path.getsize(self.current_archive_path)
        dialog = ArchivePropertiesDialog(archive_path=self.current_archive_path, total_files=self.total_files_in_archive, uncompressed_size=self.total_uncompressed_size, compressed_size=compressed_size, parent=self)
        dialog.exec()

    def _handle_item_double_click(self, item):
        row, item_name = item.row(), self.table_widget.item(item.row(), 0).text()
        if self.current_archive_path:
            if self.table_widget.item(row, 3).text() == "<DIR>": return
            self.status_bar.showMessage(f"Opening {item_name}..."); QApplication.processEvents()
            try:
                # Ekstrak file tunggal ke direktori temporer
                password = ""
                if self._is_archive_encrypted(self.current_archive_path):
                    password = self._prompt_for_password()
                    if password is None: return
                
                # Gunakan 7z untuk mengekstrak file tunggal
                shutil.rmtree(self.temp_dir, ignore_errors=True) # Bersihkan temp dir
                os.makedirs(self.temp_dir, exist_ok=True)
                cmd = [self.sevenzip_path, 'x', self.current_archive_path, f'-o{self.temp_dir}', item_name, '-y']
                if password: cmd.append(f"-p{password}")
                
                subprocess.run(cmd, check=True, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)

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
            context_menu.addSeparator()
            delete_action = context_menu.addAction("Delete Selected")
            action = context_menu.exec(self.table_widget.mapToGlobal(pos))
            if action == extract_selected_action: self._extract_archive(selected_only=True)
            elif action == delete_action: self._delete_selected()
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
            self.copy_action.setEnabled(has_selection)
            self.delete_action.setEnabled(has_selection) # 7z d bisa menghapus
            status_prefix = ""
        else:
            self.copy_action.setEnabled(False)
            self.delete_action.setEnabled(False)
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
    
    def _show_about(self):
        QMessageBox.information(self, "About Macan Archiver",
            "<b>Macan Archiver v4.0.0 (CLI Edition)</b><br><br>"
            "A professional file archiver powered by the 7-Zip engine. 🧭<br>"
            "<b>Supported Formats via 7-Zip:</b> .mcn, .7z, .zip, .tar, .rar, and more.<br><br>"
            "Created with pride. 🐅<br>"
            "Copyright © 2025 - Danx Exodus - Macan Angkasa"
        )
        
    def _show_help_content(self):
        # Teks bantuan tidak perlu diubah
        help_text = """... (konten help yang sama seperti sebelumnya) ..."""
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
    
    def _populate_drives(self):
        self.drive_combo.blockSignals(True)
        self.drive_combo.clear()
        if sys.platform == "win32":
            drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
        else:
            drives = ["/"]
        self.drive_combo.addItems(drives)
        self.drive_combo.blockSignals(False)

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

# Salin juga implementasi fungsi handle_cli_creation dan blok if __name__ == "__main__":
# dari file asli karena tidak bergantung pada pustaka yang diubah.

# [CATATAN PENTING] Sisa fungsi yang tidak ditampilkan di sini
# (_populate_drives, _browse_to_path, _go_up_directory, _list_directory_contents,
# _update_shell_integration, handle_cli_creation, if __name__ == "__main__":, dll.)
# harus disalin dari file asli karena tidak memerlukan perubahan.
# Kode di atas hanya fokus pada perubahan inti yang diminta.

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
    
    file_to_open = args.file_path_arg
    
    window = MacanArchiver(file_to_open=file_to_open)
    if window.sevenzip_path: # Hanya tampilkan jendela jika 7z ditemukan
        window.show()
        sys.exit(app.exec())