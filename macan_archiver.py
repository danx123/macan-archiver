import sys
import os
import py7zr
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QFileDialog, QToolBar, QStatusBar, QMessageBox,
    QHeaderView
)
from PySide6.QtGui import QAction, QIcon, QPixmap, QPainter
from PySide6.QtCore import Qt, QSize, QByteArray

# --- SVG Icons (XML format, not base64) ---
# Ikon-ikon ini dibuat sederhana dan langsung disematkan dalam kode.
# Kamu bisa menggantinya dengan file .svg eksternal jika mau.
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
QMessageBox {
    background-color: #3c3c3c;
}
QMessageBox QLabel {
    color: #e0e0e0;
}
"""

def create_svg_icon(svg_xml):
    """Membuat QIcon dari string XML SVG."""
    byte_array = QByteArray(svg_xml.encode('utf-8'))
    pixmap = QPixmap()
    pixmap.loadFromData(byte_array)
    return QIcon(pixmap)

class MacanArchiver(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_archive_path = None
        self.setWindowTitle("Macan Archiver")
        self.setGeometry(100, 100, 800, 600)
        self._setup_ui()

    def _setup_ui(self):
        """Mempersiapkan seluruh UI aplikasi."""
        self.setStyleSheet(DARK_THEME_QSS)
        
        # Central Widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Name", "Size (bytes)", "Modified", "Type"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.setEditTriggers(QTableWidget.EditTriggers.NoEditTriggers)
        self.table_widget.setShowGrid(False)

        self.setCentralWidget(self.table_widget)

        self._create_actions()
        self._create_toolbar()
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Selamat datang di Macan Archiver!")

    def _create_actions(self):
        """Membuat semua actions untuk toolbar."""
        self.create_action = QAction(create_svg_icon(SVG_ICONS["create"]), "&Create Archive...", self)
        self.create_action.triggered.connect(self._create_archive)
        
        self.open_action = QAction(create_svg_icon(SVG_ICONS["open"]), "&Open Archive...", self)
        self.open_action.triggered.connect(self._open_archive)

        self.extract_action = QAction(create_svg_icon(SVG_ICONS["extract"]), "&Extract All...", self)
        self.extract_action.triggered.connect(self._extract_archive)
        self.extract_action.setEnabled(False) # Awalnya nonaktif

        self.about_action = QAction(create_svg_icon(SVG_ICONS["info"]), "&About", self)
        self.about_action.triggered.connect(self._show_about)

    def _create_toolbar(self):
        """Membuat toolbar utama."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        toolbar.addAction(self.create_action)
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.extract_action)
        toolbar.addSeparator()
        toolbar.addAction(self.about_action)

    def _get_supported_formats_filter(self):
        """Filter format file yang didukung untuk dialog."""
        return "Macan Archive (*.mcn);;7z Archives (*.7z);;All Files (*.*)"

    def _create_archive(self):
        """Logika untuk membuat arsip baru."""
        files_to_add, _ = QFileDialog.getOpenFileNames(self, "Select Files to Archive")
        if not files_to_add:
            # Jika tidak ada file yang dipilih, coba pilih folder
            folder_to_add = QFileDialog.getExistingDirectory(self, "Select Folder to Archive")
            if not folder_to_add:
                self.status_bar.showMessage("Canceled archive creation.")
                return
            source = folder_to_add
        else:
            source = files_to_add

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Archive As",
            "",
            "Macan Archive (*.mcn);;7z Archives (*.7z)"
        )

        if not save_path:
            self.status_bar.showMessage("Canceled archive creation.")
            return

        # Pastikan ekstensi .mcn jika tidak ada
        if not save_path.endswith(('.mcn', '.7z')):
            save_path += '.mcn'
            
        self.status_bar.showMessage(f"Creating archive at {save_path}...")
        QApplication.processEvents() # Update UI

        try:
            with py7zr.SevenZipFile(save_path, 'w') as archive:
                if isinstance(source, list): # Jika sumbernya adalah list file
                    for file in source:
                        archive.write(file, os.path.basename(file))
                else: # Jika sumbernya adalah folder
                    archive.writeall(source, os.path.basename(source))
            
            self.status_bar.showMessage(f"Successfully created {os.path.basename(save_path)}", 5000)
            self._list_archive_contents(save_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create archive:\n{e}")
            self.status_bar.showMessage("Error creating archive.", 5000)

    def _open_archive(self):
        """Membuka dan menampilkan isi arsip."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Archive", "", self._get_supported_formats_filter())
        
        if file_path:
            self._list_archive_contents(file_path)

    def _list_archive_contents(self, file_path):
        """Membaca dan menampilkan isi file arsip ke dalam tabel."""
        self.status_bar.showMessage(f"Opening {os.path.basename(file_path)}...")
        try:
            with py7zr.SevenZipFile(file_path, 'r') as archive:
                files = archive.list()
            
            self.table_widget.setRowCount(0) # Bersihkan tabel
            for item in files:
                row_position = self.table_widget.rowCount()
                self.table_widget.insertRow(row_position)
                
                # Format ukuran file
                size_str = f"{item.uncompressed:,}"
                
                # Format tanggal modifikasi
                mod_time = item.creationtime.strftime('%Y-%m-%d %H:%M:%S') if item.creationtime else "N/A"
                
                # Tentukan tipe (Folder/File)
                file_type = "Folder" if item.is_directory else "File"
                
                self.table_widget.setItem(row_position, 0, QTableWidgetItem(item.filename))
                self.table_widget.setItem(row_position, 1, QTableWidgetItem(size_str))
                self.table_widget.setItem(row_position, 2, QTableWidgetItem(mod_time))
                self.table_widget.setItem(row_position, 3, QTableWidgetItem(file_type))

            self.current_archive_path = file_path
            self.setWindowTitle(f"Macan Archiver - {os.path.basename(file_path)}")
            self.extract_action.setEnabled(True)
            self.status_bar.showMessage(f"Opened {os.path.basename(file_path)}.", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open archive file.\nIt might be corrupted or in an unsupported format.\n\nDetails: {e}")
            self.current_archive_path = None
            self.extract_action.setEnabled(False)
            self.setWindowTitle("Macan Archiver")
            self.status_bar.showMessage("Failed to open archive.", 5000)

    def _extract_archive(self):
        """Mengekstrak semua file dari arsip yang sedang dibuka."""
        if not self.current_archive_path:
            QMessageBox.warning(self, "No Archive", "Please open an archive first.")
            return

        dest_folder = QFileDialog.getExistingDirectory(self, "Select Extraction Destination")
        if not dest_folder:
            self.status_bar.showMessage("Extraction canceled.", 3000)
            return
            
        self.status_bar.showMessage(f"Extracting to {dest_folder}...")
        QApplication.processEvents()

        try:
            with py7zr.SevenZipFile(self.current_archive_path, 'r') as archive:
                archive.extractall(path=dest_folder)
            
            self.status_bar.showMessage("Extraction completed successfully!", 5000)
            QMessageBox.information(self, "Success", f"Files extracted to:\n{dest_folder}")
        except Exception as e:
            QMessageBox.critical(self, "Extraction Error", f"An error occurred during extraction:\n{e}")
            self.status_bar.showMessage("Extraction failed.", 5000)
            
    def _show_about(self):
        """Menampilkan dialog 'About'."""
        QMessageBox.information(
            self,
            "About Macan Archiver",
            "<b>Macan Archiver v1.0</b><br><br>"
            "A premium-looking file archiver built with PySide6 and py7zr.<br>"
            "Created with pride. 🐅"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MacanArchiver()
    window.show()
    sys.exit(app.exec())