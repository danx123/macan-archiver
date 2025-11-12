import sys
import os
import py7zr
from datetime import datetime
import shutil
import tempfile
import math

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QFileDialog, QToolBar, QStatusBar, QMessageBox,
    QHeaderView, QDialog, QFormLayout, QComboBox, QLabel, QDialogButtonBox,
    QMenu
)
from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtCore import Qt, QSize, QByteArray, QTimer

# --- [BARU] SVG Icons (XML format) ---
# Menambahkan ikon untuk Test, Copy, dan Delete
SVG_ICONS = {
    "create": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
  <polyline points="14 2 14 8 20 8"></polyline>
  <line x1="12" y1="18" x2="12" y2="12"></line>
  <line x1="9" y1="15" x2="15" y2="15"></line>
</svg>""",
    "open": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M20 12v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h5l4 4h5a2 2 0 0 1 2 2v1"></path>
  <path d="M18 13v-2a2 2 0 0 0-2-2H8"></path>
</svg>""",
    "extract": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
  <polyline points="7 10 12 15 17 10"></polyline>
  <line x1="12" y1="15" x2="12" y2="3"></line>
</svg>""",
    "info": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"></circle>
  <line x1="12" y1="16" x2="12" y2="12"></line>
  <line x1="12" y1="8" x2="12.01" y2="8"></line>
</svg>""",
    "test": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
  <path d="m9 12 2 2 4-4"></path>
</svg>""",
    "copy": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
</svg>""",
    "delete": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="3 6 5 6 21 6"></polyline>
  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
  <line x1="10" y1="11" x2="10" y2="17"></line>
  <line x1="14" y1="11" x2="14" y2="17"></line>
</svg>"""
}

# --- Dark Theme Stylesheet (QSS) ---
DARK_THEME_QSS = """
QWidget {
    background-color: #2b2b2b;
    color: #e0e0e0;
    font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
    font-size: 10pt;
}
QMainWindow {
    background-color: #2b2b2b;
}
QToolBar {
    background-color: #3c3c3c;
    border: none;
    padding: 4px;
    spacing: 6px;
}
QToolBar QToolButton {
    background-color: #3c3c3c;
    border: 1px solid #3c3c3c;
    padding: 6px;
    border-radius: 4px;
}
QToolBar QToolButton:hover {
    background-color: #4f4f4f;
    border: 1px solid #666666;
}
QToolBar QToolButton:pressed {
    background-color: #1e1e1e;
}
QTableWidget {
    background-color: #2b2b2b;
    border: 1px solid #444444;
    gridline-color: #444444;
}
QTableWidget::item {
    padding: 5px;
}
QTableWidget::item:selected {
    background-color: #0078d7;
    color: #ffffff;
}
QHeaderView::section {
    background-color: #3c3c3c;
    color: #e0e0e0;
    padding: 6px;
    border: 1px solid #444444;
    font-weight: bold;
}
QStatusBar {
    background-color: #3c3c3c;
    color: #cccccc;
}
/* [BARU] Styling untuk QMenu (Context Menu) */
QMenu {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    padding: 5px;
}
QMenu::item {
    padding: 5px 25px 5px 20px;
}
QMenu::item:selected {
    background-color: #0078d7;
    color: #ffffff;
}
QMessageBox, QDialog {
    background-color: #3c3c3c;
}
QMessageBox QLabel, QDialog QLabel, QDialog QComboBox {
    color: #e0e0e0;
}
QComboBox {
    background-color: #2b2b2b;
    border: 1px solid #555555;
    padding: 4px;
    border-radius: 3px;
}
QComboBox::drop-down {
    border: none;
}
QComboBox QAbstractItemView {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    selection-background-color: #0078d7;
}
"""

def create_svg_icon(svg_xml):
    """Membuat QIcon dari string XML SVG."""
    byte_array = QByteArray(svg_xml.encode('utf-8'))
    # Langkah 1: Buat instance QPixmap kosong
    pixmap = QPixmap()
    # Langkah 2: Muat data ke dalam instance tersebut
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


class MacanArchiver(QMainWindow):
    # [MODIFIKASI] __init__ untuk menerima argumen file
    def __init__(self, file_to_open=None):
        super().__init__()
        self.current_archive_path = None
        self.setWindowTitle("Macan Archiver")
        self.setGeometry(100, 100, 800, 600)
        icon_path = "icon.ico"
        if hasattr(sys, "_MEIPASS"):
            icon_path = os.path.join(sys._MEIPASS, icon_path)
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self._setup_ui()
        
        # [BARU] Buka file jika path diberikan saat startup
        if file_to_open and os.path.isfile(file_to_open):
            QTimer.singleShot(100, lambda: self._list_archive_contents(file_to_open))

    # [MODIFIKASI] _setup_ui untuk context menu dan status bar
    def _setup_ui(self):
        self.setStyleSheet(DARK_THEME_QSS)
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Name", "Size (bytes)", "Modified", "Type"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.setEditTriggers(QTableWidget.EditTriggers.NoEditTriggers)
        self.table_widget.setShowGrid(False)
        self.setCentralWidget(self.table_widget)

        # [BARU] Aktifkan context menu dan hubungkan sinyal perubahan seleksi
        self.table_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.table_widget.itemSelectionChanged.connect(self._update_status_bar)

        self._create_actions()
        self._create_toolbar()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status_bar()

    # [MODIFIKASI] _create_actions untuk tombol baru
    def _create_actions(self):
        self.create_action = QAction(create_svg_icon(SVG_ICONS["create"]), "&Create Archive...", self)
        self.create_action.triggered.connect(self._create_archive)
        
        self.open_action = QAction(create_svg_icon(SVG_ICONS["open"]), "&Open Archive...", self)
        self.open_action.triggered.connect(self._open_archive)
        
        self.extract_action = QAction(create_svg_icon(SVG_ICONS["extract"]), "&Extract All...", self)
        self.extract_action.triggered.connect(self._extract_archive)
        self.extract_action.setEnabled(False)

        # [BARU] Actions untuk Test, Copy, Delete
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

    # [MODIFIKASI] _create_toolbar untuk tombol baru
    def _create_toolbar(self):
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
        return "Macan Archive (*.mcn);;7z Archives (*.7z);;All Files (*.*)"

    def _create_archive(self):
        files_to_add, _ = QFileDialog.getOpenFileNames(self, "Select Files to Archive")
        if not files_to_add:
            folder_to_add = QFileDialog.getExistingDirectory(self, "Select Folder to Archive")
            if not folder_to_add:
                self.status_bar.showMessage("Canceled archive creation.")
                return
            source = folder_to_add
        else:
            source = files_to_add
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Archive As", "", "Macan Archive (*.mcn);;7z Archives (*.7z)")
        if not save_path:
            self.status_bar.showMessage("Canceled archive creation.")
            return
        settings_dialog = ArchiveSettingsDialog(self)
        if not settings_dialog.exec():
            self.status_bar.showMessage("Canceled archive creation.")
            return
        method, level = settings_dialog.get_settings()
        PRESET_MAP = {"Store": 0, "Fast": 3, "Good": 5, "Best": 9}
        METHOD_MAP = {"LZMA2": py7zr.FILTER_LZMA2, "LZMA": py7zr.FILTER_LZMA}
        filters = [{'id': METHOD_MAP[method], 'preset': PRESET_MAP[level]}]
        if not save_path.endswith(('.mcn', '.7z')):
            save_path += '.mcn'
        self.status_bar.showMessage(f"Creating archive ({method}/{level})...")
        QApplication.processEvents()
        try:
            with py7zr.SevenZipFile(save_path, 'w', filters=filters) as archive:
                if isinstance(source, list):
                    for file in source:
                        archive.write(file, os.path.basename(file))
                else:
                    archive.writeall(source, os.path.basename(source))
            self.status_bar.showMessage(f"Successfully created {os.path.basename(save_path)}", 5000)
            self._list_archive_contents(save_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create archive:\n{e}")
            self.status_bar.showMessage("Error creating archive.", 5000)

    def _open_archive(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Archive", "", self._get_supported_formats_filter())
        if file_path:
            self._list_archive_contents(file_path)

    # [MODIFIKASI] _list_archive_contents untuk mengelola state tombol
    def _list_archive_contents(self, file_path):
        self.status_bar.showMessage(f"Opening {os.path.basename(file_path)}...")
        QApplication.processEvents()
        try:
            with py7zr.SevenZipFile(file_path, 'r') as archive:
                files = archive.list()
            self.table_widget.setRowCount(0)
            for item in files:
                row_position = self.table_widget.rowCount()
                self.table_widget.insertRow(row_position)
                size_str = f"{item.uncompressed:,}" if not item.is_directory else ""
                mod_time = item.creationtime.strftime('%Y-%m-%d %H:%M:%S') if item.creationtime else "N/A"
                file_type = "Folder" if item.is_directory else "File"
                self.table_widget.setItem(row_position, 0, QTableWidgetItem(item.filename))
                self.table_widget.setItem(row_position, 1, QTableWidgetItem(size_str))
                self.table_widget.setItem(row_position, 2, QTableWidgetItem(mod_time))
                self.table_widget.setItem(row_position, 3, QTableWidgetItem(file_type))
            
            self.current_archive_path = file_path
            self.setWindowTitle(f"Macan Archiver - {os.path.basename(file_path)}")
            self.extract_action.setEnabled(True)
            self.test_action.setEnabled(True) # Aktifkan tombol Test
            self.status_bar.showMessage(f"Opened {os.path.basename(file_path)}.", 5000)
            self._update_status_bar() # Update status bar setelah memuat
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open archive file.\nIt might be corrupted or in an unsupported format.\n\nDetails: {e}")
            self.current_archive_path = None
            self.setWindowTitle("Macan Archiver")
            self.table_widget.setRowCount(0)
            self.extract_action.setEnabled(False)
            self.test_action.setEnabled(False) # Nonaktifkan tombol
            self.copy_action.setEnabled(False)
            self.delete_action.setEnabled(False)
            self._update_status_bar() # Reset status bar

    def _extract_archive(self):
        if not self.current_archive_path:
            QMessageBox.warning(self, "No Archive", "Please open an archive first.")
            return
        dest_folder = QFileDialog.getExistingDirectory(self, "Select Extraction Destination")
        if not dest_folder:
            self.status_bar.showMessage("Extraction canceled.", 3000)
            return
        self.status_bar.showMessage(f"Extracting all items to {dest_folder}...")
        QApplication.processEvents()
        try:
            with py7zr.SevenZipFile(self.current_archive_path, 'r') as archive:
                archive.extractall(path=dest_folder)
            self.status_bar.showMessage("Extraction completed successfully!", 5000)
            QMessageBox.information(self, "Success", f"Files extracted to:\n{dest_folder}")
        except Exception as e:
            QMessageBox.critical(self, "Extraction Error", f"An error occurred during extraction:\n{e}")
            self.status_bar.showMessage("Extraction failed.", 5000)
    
    # --- [BARU] Semua fungsi di bawah ini baru ditambahkan ---
    
    def _get_selected_filenames(self):
        """Mendapatkan daftar nama file yang dipilih di tabel."""
        selected_rows = self.table_widget.selectionModel().selectedRows()
        if not selected_rows:
            return []
        return [self.table_widget.item(row.row(), 0).text() for row in selected_rows]

    def _show_context_menu(self, pos):
        """Menampilkan menu konteks saat klik kanan."""
        if not self.table_widget.selectedItems():
            return
        context_menu = QMenu(self)
        extract_selected_action = context_menu.addAction("Extract Selected...")
        copy_to_action = context_menu.addAction("Copy To...")
        context_menu.addSeparator()
        delete_action = context_menu.addAction("Delete Selected")
        
        action = context_menu.exec(self.table_widget.mapToGlobal(pos))

        if action in [extract_selected_action, copy_to_action]:
            self._extract_or_copy_selected()
        elif action == delete_action:
            self._delete_selected()

    def _update_status_bar(self):
        """Memperbarui teks di status bar berdasarkan status aplikasi dan seleksi."""
        if not self.current_archive_path:
            self.status_bar.showMessage("Ready. Welcome to Macan Archiver!")
            return

        total_items = self.table_widget.rowCount()
        selected_rows = self.table_widget.selectionModel().selectedRows()
        num_selected = len(selected_rows)
        
        has_selection = num_selected > 0
        self.copy_action.setEnabled(has_selection)
        self.delete_action.setEnabled(has_selection)

        total_size = 0
        if has_selection:
            for row in selected_rows:
                size_text = self.table_widget.item(row.row(), 1).text()
                try:
                    total_size += int(size_text.replace(',', ''))
                except (ValueError, AttributeError):
                    pass
        
        def format_size(size_bytes):
            if size_bytes == 0: return "0 B"
            size_name = ("B", "KB", "MB", "GB", "TB")
            i = int(math.floor(math.log(size_bytes, 1024)))
            p = math.pow(1024, i)
            s = round(size_bytes / p, 2)
            return f"{s} {size_name[i]}"

        status_text = f"{total_items} items"
        if has_selection:
            status_text += f"   |   {num_selected} selected ({format_size(total_size)})"
        
        self.status_bar.showMessage(status_text)
        
    def _test_archive(self):
        """Menguji integritas arsip yang sedang dibuka."""
        if not self.current_archive_path: return
        self.status_bar.showMessage("Testing archive integrity...")
        QApplication.processEvents()
        try:
            with py7zr.SevenZipFile(self.current_archive_path, 'r') as archive:
                archive.test()
            QMessageBox.information(self, "Success", "Archive test completed successfully. No errors found.")
            self.status_bar.showMessage("Archive test successful.", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Test Failed", f"Archive is corrupted or invalid.\n\nDetails: {e}")
            self.status_bar.showMessage("Archive test failed.", 5000)

    def _extract_or_copy_selected(self):
        """Mengekstrak atau menyalin file yang dipilih ke folder tujuan."""
        filenames = self._get_selected_filenames()
        if not filenames:
            QMessageBox.warning(self, "No Selection", "Please select files or folders to extract/copy.")
            return

        dest_folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if not dest_folder: return
        
        self.status_bar.showMessage(f"Extracting {len(filenames)} item(s)...")
        QApplication.processEvents()
        try:
            with py7zr.SevenZipFile(self.current_archive_path, 'r') as archive:
                archive.extract(path=dest_folder, targets=filenames)
            self.status_bar.showMessage("Selected items extracted successfully!", 5000)
            QMessageBox.information(self, "Success", f"Files extracted to:\n{dest_folder}")
        except Exception as e:
            QMessageBox.critical(self, "Extraction Error", f"An error occurred:\n{e}")
            self.status_bar.showMessage("Extraction failed.", 5000)

    def _delete_selected(self):
        """Menghapus file yang dipilih dari arsip dengan cara mengemas ulang."""
        filenames_to_delete = self._get_selected_filenames()
        if not filenames_to_delete:
            QMessageBox.warning(self, "No Selection", "Please select items to delete.")
            return

        reply = QMessageBox.question(self, "Confirm Delete",
                                     f"Are you sure you want to permanently delete {len(filenames_to_delete)} item(s) from the archive?\n\nThis operation requires repacking the entire archive.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No: return

        self.status_bar.showMessage("Repacking archive to delete items...")
        QApplication.processEvents()

        original_path = self.current_archive_path
        temp_archive_path = original_path + ".tmp"

        try:
            files_to_keep = []
            with py7zr.SevenZipFile(original_path, 'r') as archive_in:
                all_files = archive_in.getnames()
                files_to_keep = [f for f in all_files if f not in filenames_to_delete]
                
                # Ekstrak hanya file yang akan disimpan ke direktori temporer
                with tempfile.TemporaryDirectory() as temp_dir:
                    archive_in.extract(path=temp_dir, targets=files_to_keep)
                    
                    # Buat arsip baru dari file yang sudah diekstrak
                    with py7zr.SevenZipFile(temp_archive_path, 'w') as archive_out:
                        for item in files_to_keep:
                            item_path = os.path.join(temp_dir, item)
                            if os.path.exists(item_path):
                                archive_out.write(item_path, arcname=item)
            
            # Ganti file asli dengan file temporer yang sudah dimodifikasi
            shutil.move(temp_archive_path, original_path)
            
            self.status_bar.showMessage("Items deleted successfully. Reloading...", 5000)
            self._list_archive_contents(original_path) # Muat ulang tampilan
        except Exception as e:
            QMessageBox.critical(self, "Deletion Error", f"An error occurred while deleting items:\n{e}")
            self.status_bar.showMessage("Deletion failed.", 5000)
            if os.path.exists(temp_archive_path):
                os.remove(temp_archive_path)

    # [MODIFIKASI] _show_about untuk versi baru
    def _show_about(self):
        QMessageBox.information(
            self, "About Macan Archiver",
            "<b>Macan Archiver v2.0.0</b><br><br>"
            "A premium-looking file archiver built with PySide6 and py7zr.<br>"
            "Features compression settings, archive testing, context menus, and more.<br>"
            "Created with pride. 🐅<br>"
            "Copyright © 2025 - Danx Exodus - Macan Angkasa"
        )


# [MODIFIKASI] Main block untuk menangani argumen command line
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    file_path_arg = None
    if len(sys.argv) > 1:
        file_path_arg = sys.argv[1]

    window = MacanArchiver(file_to_open=file_path_arg)
    window.show()
    sys.exit(app.exec())