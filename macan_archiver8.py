import sys
import os
import py7zr
from datetime import datetime
import shutil
import tempfile
import math
import subprocess
import string

# --- [BARU] Menambahkan library untuk format arsip lain ---
import zipfile
import tarfile
try:
    import rarfile
    RAR_SUPPORT = True
except ImportError:
    RAR_SUPPORT = False

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QFileDialog, QToolBar, QStatusBar, QMessageBox,
    QHeaderView, QDialog, QFormLayout, QComboBox, QLabel, QDialogButtonBox,
    QMenu, QProgressDialog, QLineEdit
)
from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtCore import Qt, QSize, QByteArray, QTimer, QThread, Signal, QObject

# --- SVG Icons (XML format) ---
# (Disembunyikan untuk keringkasan, tidak ada perubahan)
SVG_ICONS = {
    "create": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>""",
    "open": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 12v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h5l4 4h5a2 2 0 0 1 2 2v1"></path><path d="M18 13v-2a2 2 0 0 0-2-2H8"></path></svg>""",
    "extract": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>""",
    "info": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>""",
    "test": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="m9 12 2 2 4-4"></path></svg>""",
    "copy": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>""",
    "delete": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>""",
    "up": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5"></path><polyline points="5 12 12 5 19 12"></polyline></svg>"""
}

# --- Dark Theme Stylesheet (QSS) ---
# (Disembunyikan untuk keringkasan, tidak ada perubahan)
DARK_THEME_QSS = """
QWidget { background-color: #2b2b2b; color: #e0e0e0; font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif; font-size: 10pt; }
QMainWindow { background-color: #2b2b2b; }
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
QMessageBox QLabel, QDialog QLabel, QDialog QComboBox { color: #e0e0e0; }
QProgressDialog { background-color: #3c3c3c; }
QComboBox { background-color: #2b2b2b; border: 1px solid #555555; padding: 4px; border-radius: 3px; min-width: 60px;}
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView { background-color: #3c3c3c; border: 1px solid #555555; selection-background-color: #0078d7; }
"""

def create_svg_icon(svg_xml):
    """Membuat QIcon dari string XML SVG."""
    byte_array = QByteArray(svg_xml.encode('utf-8'))
    pixmap = QPixmap()
    pixmap.loadFromData(byte_array)
    return QIcon(pixmap)

class ArchiveSettingsDialog(QDialog):
    # (Tidak ada perubahan di kelas ini)
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

class ArchiveWorker(QObject):
    # (Tidak ada perubahan di kelas ini)
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


class MacanArchiver(QMainWindow):
    def __init__(self, file_to_open=None):
        super().__init__()
        self.current_archive_path = None
        self.current_archive_type = None
        # [BARU] Path untuk penjelajah file
        self.current_directory = os.path.expanduser("~") 
        
        self.setWindowTitle("Macan Archiver")
        self.setGeometry(100, 100, 800, 600)
        
        self.temp_dir = os.path.join(tempfile.gettempdir(), "macan_archiver_preview")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        icon_path = "icon.ico"
        if hasattr(sys, "_MEIPASS"):
            icon_path = os.path.join(sys._MEIPASS, icon_path)
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self._setup_ui()
        
        if file_to_open and os.path.isfile(file_to_open):
            QTimer.singleShot(100, lambda: self._list_archive_contents(file_to_open))
        else:
             # [BARU] Tampilkan isi direktori default saat startup
            QTimer.singleShot(100, lambda: self._browse_to_path(self.current_directory))


    def _setup_ui(self):
        self.setAcceptDrops(True)
        self.setStyleSheet(DARK_THEME_QSS)
        
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Name", "Size", "Modified", "Type"])
        
        # --- [FIX REVISI] Mengatur kolom agar interaktif dengan lebar awal yang proporsional ---
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive) # Terapkan ke semua kolom sekaligus
        header.setStretchLastSection(False) # Pastikan kolom terakhir tidak meregang otomatis

        # Atur lebar awal yang ideal untuk setiap kolom
        header.resizeSection(0, 350)  # Kolom "Name"
        header.resizeSection(1, 100)  # Kolom "Size"
        header.resizeSection(2, 150)  # Kolom "Modified"
        header.resizeSection(3, 80)   # Kolom "Type"

        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.setEditTriggers(QTableWidget.EditTriggers.NoEditTriggers)
        self.table_widget.setShowGrid(False)
        self.setCentralWidget(self.table_widget)

        self.table_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.table_widget.itemSelectionChanged.connect(self._update_status_bar)
        
        # [MODIFIKASI] Hubungkan sinyal double-click ke handler baru
        self.table_widget.itemDoubleClicked.connect(self._handle_item_double_click)

        self._create_actions()
        # [BARU] Membuat toolbar navigasi terpisah
        self._create_navigation_toolbar()
        self._create_main_toolbar()
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status_bar()

    # --- [FITUR 3] Bagian untuk Penjelajah File ---
    def _create_navigation_toolbar(self):
        nav_toolbar = QToolBar("Navigation Toolbar")
        nav_toolbar.setIconSize(QSize(22, 22))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, nav_toolbar)

        # Tombol 'Up' untuk kembali ke folder induk
        self.up_action = QAction(create_svg_icon(SVG_ICONS["up"]), "Up", self)
        self.up_action.triggered.connect(self._go_up_directory)
        nav_toolbar.addAction(self.up_action)

        # Dropdown untuk daftar drive
        self.drive_combo = QComboBox(self)
        self.drive_combo.currentTextChanged.connect(self._browse_to_path)
        nav_toolbar.addWidget(self.drive_combo)
        self._populate_drives()

        # Bar untuk menampilkan dan mengedit path
        self.path_bar = QLineEdit(self)
        self.path_bar.returnPressed.connect(lambda: self._browse_to_path(self.path_bar.text()))
        nav_toolbar.addWidget(self.path_bar)
    
    def _populate_drives(self):
        self.drive_combo.blockSignals(True) # Cegah sinyal saat mengisi item
        self.drive_combo.clear()
        if sys.platform == "win32":
            drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
        else: # Linux, macOS
            drives = ["/"]
        self.drive_combo.addItems(drives)
        self.drive_combo.blockSignals(False)

    def _browse_to_path(self, path):
        if not os.path.isdir(path):
            self.status_bar.showMessage(f"Path not found: {path}", 3000)
            return

        # Keluar dari mode arsip jika sedang menelusuri file sistem
        if self.current_archive_path:
            self._reset_to_file_browser_view()

        self.current_directory = path
        self.path_bar.setText(path)
        self._list_directory_contents(path)
        self._update_status_bar()
        
    def _go_up_directory(self):
        parent_dir = os.path.dirname(self.current_directory)
        # Hanya pindah jika direktori induk berbeda (mencegah loop di root)
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
                    item = {
                        'name': name,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        'is_dir': is_dir
                    }
                    items.append(item)
                except (FileNotFoundError, PermissionError):
                    continue # Lewati file yang tidak bisa diakses
        except PermissionError:
            QMessageBox.warning(self, "Permission Denied", f"Cannot access directory:\n{path}")

        self._populate_table(items)
    # --- Akhir dari Bagian Penjelajah File ---
    
    def _reset_to_file_browser_view(self):
        """Mengembalikan UI ke mode penjelajah file."""
        self.current_archive_path = None
        self.current_archive_type = None
        self.setWindowTitle("Macan Archiver")
        self.extract_action.setEnabled(False)
        self.test_action.setEnabled(False)
        self.copy_action.setEnabled(False)
        self.delete_action.setEnabled(False)


    def closeEvent(self, event):
        try:
            shutil.rmtree(self.temp_dir)
        except OSError as e:
            print(f"Error cleaning up temp directory: {e}")
        super().closeEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if not urls:
            return
        paths = [url.toLocalFile() for url in urls]
        supported_formats = ('.mcn', '.7z', '.zip', '.rar', '.tar', '.gz', '.bz2', '.xz')
        if len(paths) == 1 and paths[0].lower().endswith(supported_formats):
            self._list_archive_contents(paths[0])
        else:
            self._perform_archive_creation(paths)

    def _create_actions(self):
        # (Tidak ada perubahan di bagian ini)
        self.create_action = QAction(create_svg_icon(SVG_ICONS["create"]), "&Create Archive...", self)
        self.create_action.triggered.connect(self._create_archive)
        self.open_action = QAction(create_svg_icon(SVG_ICONS["open"]), "&Open Archive...", self)
        self.open_action.triggered.connect(self._open_archive)
        self.extract_action = QAction(create_svg_icon(SVG_ICONS["extract"]), "&Extract All...", self)
        self.extract_action.triggered.connect(self._extract_archive)
        self.extract_action.setEnabled(False)
        self.test_action = QAction(create_svg_icon(SVG_ICONS["test"]), "&Test Archive", self)
        self.test_action.triggered.connect(self._test_archive)
        self.test_action.setEnabled(False)
        self.copy_action = QAction(create_svg_icon(SVG_ICONS["copy"]), "&Copy To...", self)
        self.copy_action.triggered.connect(self._extract_or_copy_selected)
        self.copy_action.setEnabled(False)
        self.delete_action = QAction(create_svg_icon(SVG_ICONS["delete"]), "&Delete", self)
        self.delete_action.triggered.connect(self._delete_selected)
        self.delete_action.setEnabled(False)
        self.about_action = QAction(create_svg_icon(SVG_ICONS["info"]), "&About", self)
        self.about_action.triggered.connect(self._show_about)

    def _create_main_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        toolbar.addAction(self.create_action)
        toolbar.addAction(self.open_action)
        toolbar.addSeparator()
        toolbar.addAction(self.extract_action)
        toolbar.addAction(self.test_action)
        toolbar.addAction(self.copy_action)
        toolbar.addAction(self.delete_action)
        toolbar.addSeparator()
        toolbar.addAction(self.about_action)

    def _get_supported_formats_filter(self):
        # (Tidak ada perubahan di bagian ini)
        filters = [
            "All Supported Archives (*.mcn *.7z *.zip *.tar *.gz *.bz2 *.xz *.rar)",
            "Macan Archive (*.mcn)",
            "7z Archives (*.7z)",
            "ZIP Archives (*.zip)",
            "TAR Archives (*.tar *.gz *.bz2 *.xz)",
        ]
        if RAR_SUPPORT:
            filters.append("RAR Archives (*.rar)")
        filters.append("All Files (*.*)")
        return ";;".join(filters)

    def _create_archive(self):
        # (Tidak ada perubahan di bagian ini)
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
        # (Tidak ada perubahan signifikan di bagian ini)
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

        total_files = 0
        for path in source_paths:
            if os.path.isfile(path):
                total_files += 1
            elif os.path.isdir(path):
                for _, _, files in os.walk(path):
                    total_files += len(files)

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
        self.worker.progress.connect(lambda val: self.progress_dialog.setValue(val))
        self.worker.progress_text.connect(lambda text: self.progress_dialog.setLabelText(text))

        self.thread.start()
        self.progress_dialog.exec()

    def _on_archive_creation_finished(self, save_path):
        # (Tidak ada perubahan di bagian ini)
        self.progress_dialog.setValue(self.progress_dialog.maximum())
        self.progress_dialog.close()
        self.status_bar.showMessage(f"Successfully created {os.path.basename(save_path)}", 5000)
        self._list_archive_contents(save_path)
        self.thread.quit()
        self.thread.wait()

    def _on_archive_creation_error(self, message):
        # (Tidak ada perubahan di bagian ini)
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

    def _list_archive_contents(self, file_path):
        # (Tidak ada perubahan signifikan di bagian ini)
        self.status_bar.showMessage(f"Opening {os.path.basename(file_path)}...")
        QApplication.processEvents()
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext in ['.mcn', '.7z']:
                self.current_archive_type = '7z'
                self._list_7z_contents(file_path)
            elif file_ext == '.zip':
                self.current_archive_type = 'zip'
                self._list_zip_contents(file_path)
            elif file_ext == '.rar':
                if not RAR_SUPPORT:
                    raise ImportError("Modul 'rarfile' tidak ditemukan. Pastikan sudah terinstal.")
                self.current_archive_type = 'rar'
                self._list_rar_contents(file_path)
            elif tarfile.is_tarfile(file_path):
                self.current_archive_type = 'tar'
                self._list_tar_contents(file_path)
            else:
                raise ValueError("Unsupported archive format.")

            self.current_archive_path = file_path
            self.setWindowTitle(f"Macan Archiver - {os.path.basename(file_path)}")
            self.extract_action.setEnabled(True)
            
            is_7z = self.current_archive_type == '7z'
            self.test_action.setEnabled(is_7z)
            self.delete_action.setEnabled(False) # Deletion still requires selection

            self.status_bar.showMessage(f"Opened {os.path.basename(file_path)}.", 5000)
            self._update_status_bar()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open archive file.\nIt might be corrupted or in an unsupported format.\n\nDetails: {e}")
            # Kembali ke penjelajah file jika gagal membuka arsip
            self._browse_to_path(self.current_directory)


    # --- [FIX 2] Mengubah tampilan kolom "Type" ---
    def _populate_table(self, items):
        self.table_widget.setRowCount(0)
        self.table_widget.setSortingEnabled(False) # Matikan sorting saat mengisi data
        for item in items:
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)
            
            size_str = f"{item.get('size', 0):,}" if not item.get('is_dir') and item.get('size') is not None else ""
            mod_time_str = item.get('modified', "N/A")
            
            if item.get('is_dir'):
                file_type_str = "<DIR>"
            else:
                name = item.get('name', '')
                _, ext = os.path.splitext(name)
                file_type_str = ext.lower() if ext else "File"
            
            self.table_widget.setItem(row_position, 0, QTableWidgetItem(item.get('name')))
            self.table_widget.setItem(row_position, 1, QTableWidgetItem(size_str))
            self.table_widget.setItem(row_position, 2, QTableWidgetItem(mod_time_str))
            self.table_widget.setItem(row_position, 3, QTableWidgetItem(file_type_str))
        self.table_widget.setSortingEnabled(True)

    # (Fungsi _list_*_contents tidak berubah)
    def _list_7z_contents(self, file_path):
        with py7zr.SevenZipFile(file_path, 'r') as archive:
            files_info = [
                {
                    'name': item.filename,
                    'size': item.uncompressed,
                    'modified': item.creationtime.strftime('%Y-%m-%d %H:%M:%S') if item.creationtime else "N/A",
                    'is_dir': item.is_directory
                }
                for item in archive.list()
            ]
        self._populate_table(files_info)
    def _list_zip_contents(self, file_path):
        with zipfile.ZipFile(file_path, 'r') as archive:
            files_info = [
                {
                    'name': item.filename,
                    'size': item.file_size,
                    'modified': datetime(*item.date_time).strftime('%Y-%m-%d %H:%M:%S'),
                    'is_dir': item.is_dir()
                }
                for item in archive.infolist()
            ]
        self._populate_table(files_info)
    def _list_tar_contents(self, file_path):
        with tarfile.open(file_path, 'r:*') as archive:
            files_info = [
                {
                    'name': item.name,
                    'size': item.size,
                    'modified': datetime.fromtimestamp(item.mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'is_dir': item.isdir()
                }
                for item in archive.getmembers()
            ]
        self._populate_table(files_info)
    def _list_rar_contents(self, file_path):
        with rarfile.RarFile(file_path, 'r') as archive:
            files_info = [
                {
                    'name': item.filename,
                    'size': item.file_size,
                    'modified': datetime(*item.date_time).strftime('%Y-%m-%d %H:%M:%S'),
                    'is_dir': item.isdir()
                }
                for item in archive.infolist()
            ]
        self._populate_table(files_info)


    def _extract_archive(self):
        # (Tidak ada perubahan di bagian ini)
        if not self.current_archive_path:
            QMessageBox.warning(self, "No Archive", "Please open an archive first.")
            return
        dest_folder = QFileDialog.getExistingDirectory(self, "Select Extraction Destination", self.current_directory)
        if not dest_folder:
            self.status_bar.showMessage("Extraction canceled.", 3000)
            return
            
        self.status_bar.showMessage(f"Extracting all items to {dest_folder}...")
        QApplication.processEvents()
        
        try:
            archive_type = self.current_archive_type
            archive_path = self.current_archive_path
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
    
    # [MODIFIKASI] Handler double-click yang membedakan mode arsip dan file browser
    def _handle_item_double_click(self, item):
        row = item.row()
        item_name = self.table_widget.item(row, 0).text()
        item_type = self.table_widget.item(row, 3).text()

        if self.current_archive_path:
            # --- Mode Arsip ---
            if item_type == "<DIR>":
                return # Abaikan jika yang di-klik adalah folder di dalam arsip
            
            self.status_bar.showMessage(f"Opening {item_name}...")
            QApplication.processEvents()
            
            try:
                self._extract_or_copy_selected(filenames=[item_name], dest_folder=self.temp_dir, show_success_msg=False)
                extracted_file_path = os.path.join(self.temp_dir, item_name)
                
                if sys.platform == "win32": os.startfile(extracted_file_path)
                elif sys.platform == "darwin": subprocess.run(["open", extracted_file_path])
                else: subprocess.run(["xdg-open", extracted_file_path])
                
                self.status_bar.showMessage(f"Opened {item_name}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error Opening File", f"Could not open the file:\n{e}")
                self.status_bar.showMessage("Failed to open file.", 5000)
        else:
            # --- Mode File Browser ---
            full_path = os.path.join(self.current_directory, item_name)
            if os.path.isdir(full_path):
                self._browse_to_path(full_path)
            elif os.path.isfile(full_path):
                supported_formats = ('.mcn', '.7z', '.zip', '.rar', '.tar', '.gz', '.bz2', '.xz')
                if full_path.lower().endswith(supported_formats):
                    self._list_archive_contents(full_path) # Buka sebagai arsip
                else:
                    try:
                        # Buka file biasa dengan aplikasi default sistem
                        if sys.platform == "win32": os.startfile(full_path)
                        elif sys.platform == "darwin": subprocess.run(["open", full_path])
                        else: subprocess.run(["xdg-open", full_path])
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Could not open file:\n{e}")

    def _get_selected_filenames(self):
        selected_rows = self.table_widget.selectionModel().selectedRows()
        if not selected_rows: return []
        return [self.table_widget.item(row.row(), 0).text() for row in selected_rows]

    def _show_context_menu(self, pos):
        # (Tidak ada perubahan signifikan di bagian ini)
        if not self.table_widget.selectedItems(): return
        
        context_menu = QMenu(self)
        
        if self.current_archive_path:
            extract_selected_action = context_menu.addAction("Extract Selected...")
            copy_to_action = context_menu.addAction("Copy To...")
            
            if self.current_archive_type == '7z':
                context_menu.addSeparator()
                delete_action = context_menu.addAction("Delete Selected")
            else: delete_action = None
            action = context_menu.exec(self.table_widget.mapToGlobal(pos))
            if action in [extract_selected_action, copy_to_action]: self._extract_or_copy_selected()
            elif action and action == delete_action: self._delete_selected()
        else:
            # [BARU] Context menu untuk file browser
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
        num_selected = len(selected_rows)
        has_selection = num_selected > 0
        
        # [MODIFIKASI] Enable/disable tombol berdasarkan mode (arsip vs browser)
        if self.current_archive_path:
            self.copy_action.setEnabled(has_selection)
            self.delete_action.setEnabled(has_selection and self.current_archive_type == '7z')
            status_prefix = ""
        else:
            self.copy_action.setEnabled(False)
            self.delete_action.setEnabled(False)
            status_prefix = f"Current Path: {self.current_directory}   |   "

        total_size = 0
        if has_selection:
            for row in selected_rows:
                size_text = self.table_widget.item(row.row(), 1).text()
                try: total_size += int(size_text.replace(',', ''))
                except (ValueError, AttributeError): pass
        
        def format_size(size_bytes):
            if size_bytes == 0: return "0 B"
            size_name = ("B", "KB", "MB", "GB", "TB")
            i = int(math.floor(math.log(size_bytes, 1024)))
            p = math.pow(1024, i)
            s = round(size_bytes / p, 2)
            return f"{s} {size_name[i]}"

        status_text = f"{status_prefix}{total_items} items"
        if has_selection:
            status_text += f"   |   {num_selected} selected ({format_size(total_size)})"
        
        self.status_bar.showMessage(status_text)
        
    def _test_archive(self):
        # (Tidak ada perubahan di bagian ini)
        if not self.current_archive_path or self.current_archive_type != '7z': return
        self.status_bar.showMessage("Testing archive integrity...")
        QApplication.processEvents()
        try:
            with py7zr.SevenZipFile(self.current_archive_path, 'r') as archive: archive.test()
            QMessageBox.information(self, "Success", "Archive test completed successfully. No errors found.")
            self.status_bar.showMessage("Archive test successful.", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Test Failed", f"Archive is corrupted or invalid.\n\nDetails: {e}")
            self.status_bar.showMessage("Archive test failed.", 5000)

    def _extract_or_copy_selected(self, filenames=None, dest_folder=None, show_success_msg=True):
        # (Tidak ada perubahan signifikan di bagian ini)
        if filenames is None: filenames = self._get_selected_filenames()
        if not filenames:
            if show_success_msg: QMessageBox.warning(self, "No Selection", "Please select files or folders to extract/copy.")
            return

        if dest_folder is None:
            dest_folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder", self.current_directory)
        if not dest_folder: return
        
        self.status_bar.showMessage(f"Extracting {len(filenames)} item(s)...")
        QApplication.processEvents()
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

    def _delete_selected(self):
        # (Tidak ada perubahan signifikan di bagian ini)
        if self.current_archive_type != '7z':
             QMessageBox.information(self, "Unsupported Operation", "Deleting items is only supported for .mcn and .7z archives.")
             return
        filenames_to_delete = self._get_selected_filenames()
        if not filenames_to_delete: return

        reply = QMessageBox.question(self, "Confirm Delete",
                                     f"Are you sure you want to permanently delete {len(filenames_to_delete)} item(s) from the archive?\n\nThis operation requires repacking the entire archive.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No: return

        self.status_bar.showMessage("Repacking archive to delete items...")
        QApplication.processEvents()
        original_path = self.current_archive_path
        temp_archive_path = original_path + ".tmp"
        try:
            with py7zr.SevenZipFile(original_path, 'r') as archive_in:
                all_files = archive_in.getnames()
                files_to_keep = [f for f in all_files if f not in filenames_to_delete]
                with tempfile.TemporaryDirectory() as temp_dir:
                    archive_in.extract(path=temp_dir, targets=files_to_keep)
                    with py7zr.SevenZipFile(temp_archive_path, 'w') as archive_out:
                        for item in files_to_keep:
                            item_path = os.path.join(temp_dir, item)
                            if os.path.exists(item_path):
                                archive_out.write(item_path, arcname=item)
            
            shutil.move(temp_archive_path, original_path)
            self.status_bar.showMessage("Items deleted successfully. Reloading...", 5000)
            self._list_archive_contents(original_path)
        except Exception as e:
            QMessageBox.critical(self, "Deletion Error", f"An error occurred while deleting items:\n{e}")
            if os.path.exists(temp_archive_path): os.remove(temp_archive_path)

    def _show_about(self):
        # (Tidak ada perubahan di bagian ini)
        rar_note = "<b>Note:</b> To open .rar files, you need to install the 'rarfile' package (pip install rarfile) and have the 'rarfile' command-line utility available in your system's PATH." if not RAR_SUPPORT else "RAR support is enabled."
        QMessageBox.information(
            self, "About Macan Archiver",
            "<b>Macan Archiver v2.3.0 (Navigator Edition)</b><br><br>"
            "A premium-looking file archiver built with PySide6.<br>"
            "Now with integrated file system browsing. 🧭<br>"
            "<b>Supported Formats:</b> .mcn, .7z, .zip, .tar, .rar<br><br>"
            f"Features Drag & Drop, archive testing (7z), context menus, and more. 📂<br>"
            f"{rar_note}<br><br>"
            "Created with pride. 🐅<br>"
            "Copyright © 2025 - Danx Exodus - Macan Angkasa"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    file_path_arg = sys.argv[1] if len(sys.argv) > 1 else None

    if not RAR_SUPPORT:
        print("Warning: 'rarfile' module not found. RAR file support will be disabled.")
        print("You can install it using: pip install rarfile")

    window = MacanArchiver(file_to_open=file_path_arg)
    window.show()
    sys.exit(app.exec())