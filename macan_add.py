import sys
import os
import re
import subprocess
import shutil
from PySide6.QtWidgets import (
    QApplication, QDialog, QFormLayout, QComboBox, QLabel,
    QDialogButtonBox, QLineEdit, QCheckBox, QFileDialog, QMessageBox,
    QProgressDialog
)
from PySide6.QtCore import Qt, QThread, QObject, Signal


def _find_7z_executable():
    """Mencari path 7z.exe di lokasi umum."""
    path_from_env = shutil.which("7z")
    if path_from_env:
        return path_from_env


    for base_path in [os.environ.get("ProgramFiles", "C:\\Program Files"), os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")]:
        candidate = os.path.join(base_path, "7-Zip", "7z.exe")
        if os.path.exists(candidate):
            return candidate
    return None


class ArchiveSettingsDialog(QDialog):
    """Dialog untuk mengatur opsi pembuatan arsip."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add to Archive")
        layout = QFormLayout(self)
        
        self.split_options = {
            "No splitting": "", "100 MB": "100m", "700 MB (CD)": "700m",
            "4480 MB (DVD)": "4480m", "25000 MB (Blu-ray)": "25000m"
        }


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


        self.split_combo = QComboBox()
        self.split_combo.setEditable(True)
        self.split_combo.addItems(self.split_options.keys())
        self.split_combo.lineEdit().setPlaceholderText("Custom size (e.g., 100m, 2g)")
        self.split_combo.setCurrentIndex(0)
        layout.addRow(QLabel("Split into volumes:"), self.split_combo)


        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


    def toggle_password_visibility(self, checked):
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password)


    def get_settings(self):
        level_text = self.level_combo.currentText()
        level = re.search(r'\((\d+)\)', level_text).group(1)
        password = self.password_edit.text()
        
        split_text = self.split_combo.currentText()
        split_size = self.split_options.get(split_text, split_text.strip())
        
        return level, password, split_size


class ArchiveWorker(QObject):
    """Worker untuk menjalankan proses 7z di thread terpisah."""
    progress = Signal(int)
    progress_text = Signal(str)
    finished = Signal(str)
    error = Signal(str)


    def __init__(self, sevenzip_path, archive_path, source_paths, level, password, split_size):
        super().__init__()
        self.sevenzip_path = sevenzip_path
        self.archive_path = archive_path
        self.source_paths = source_paths
        self.level = level
        self.password = password
        self.split_size = split_size
        self._is_running = True
        self.process = None


    def run(self):
        cmd = [self.sevenzip_path, 'a', self.archive_path] + self.source_paths
        cmd.append(f"-mx={self.level}")
        if self.password: cmd.append(f"-p{self.password}")
        if self.split_size and re.match(r'^\d+[kmgKMG]?$', self.split_size): cmd.append(f'-v{self.split_size}')
        cmd.append('-y')
        
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
            
        try:
            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW,
                text=True, encoding='utf-8', errors='ignore'
            )


            for line in iter(self.process.stdout.readline, ''):
                if not self._is_running:
                    self.process.terminate()
                    break
                
                match = re.search(r'(\d+)\s*%', line)
                if match: self.progress.emit(int(match.group(1)))
                if line.startswith("Compressing"): self.progress_text.emit(line.strip())


            self.process.stdout.close()
            return_code = self.process.wait()


            if not self._is_running:
                self.error.emit("Canceled")
                return


            if return_code == 0:
                self.finished.emit(self.archive_path)
            else:
                self.error.emit(f"7-Zip process failed:\n{self.process.stderr.read()}")
        except Exception as e:
            self.error.emit(f"An error occurred: {e}")


    def stop(self):
        self._is_running = False
        if self.process:
            try: self.process.terminate()
            except ProcessLookupError: pass


def main():
    """Fungsi utama untuk menjalankan proses pembuatan arsip."""
    source_paths = sys.argv[1:]
    if not source_paths:
        # Pesan ini akan muncul jika dijalankan dari command line tanpa argumen
        print("Usage: MacanAdd.exe <file1> <file2> ... <folder1>")
        return


    sevenzip_path = _find_7z_executable()
    if not sevenzip_path:
        app = QApplication([])
        QMessageBox.critical(None, "7-Zip Not Found", "7z.exe could not be found. Please install 7-Zip.")
        return


    app = QApplication(sys.argv)
    
    settings_dialog = ArchiveSettingsDialog()
    if not settings_dialog.exec():
        return
    
    level, password, split_size = settings_dialog.get_settings()
    
    first_item_path = source_paths[0]
    default_dir = os.path.dirname(first_item_path) if os.path.isfile(first_item_path) else first_item_path
    default_name = os.path.basename(first_item_path)
    
    save_path, _ = QFileDialog.getSaveFileName(
        None, "Save Archive As",
        os.path.join(default_dir, default_name),
        "Macan Archive (*.mcn);;7z Archives (*.7z);;All Files (*.*)"
    )
    
    if not save_path:
        return


    if not save_path.lower().endswith(('.mcn', '.7z')):
        save_path += '.mcn'


    progress_dialog = QProgressDialog("Starting process...", "Cancel", 0, 100)
    progress_dialog.setWindowTitle("Creating Archive")
    progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
    progress_dialog.setAutoClose(False)
    progress_dialog.setAutoReset(False)


    thread = QThread()
    worker = ArchiveWorker(sevenzip_path, save_path, source_paths, level, password, split_size)
    worker.moveToThread(thread)


    def on_error(msg):
        progress_dialog.close()
        if "Canceled" not in msg:
            QMessageBox.critical(None, "Error", msg)
        thread.quit()


    def on_finished(path):
        progress_dialog.setValue(100)
        progress_dialog.close()
        QMessageBox.information(None, "Success", f"Archive '{os.path.basename(path)}' created successfully.")
        thread.quit()


    progress_dialog.canceled.connect(worker.stop)
    thread.started.connect(worker.run)
    worker.finished.connect(on_finished)
    worker.error.connect(on_error)
    worker.progress.connect(progress_dialog.setValue)
    worker.progress_text.connect(progress_dialog.setLabelText)
    thread.finished.connect(app.quit)


    thread.start()
    progress_dialog.exec()
    app.exec()


if __name__ == "__main__":
    main()

