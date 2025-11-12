# 🐅 Macan Archiver v4.7.0

Macan Archiver is a premium file archiver application based on PySide6 (Qt for Python) with a modern interface (dark & light theme).
It supports various popular archive formats with full features: drag & drop, context menus, integrity testing, and direct file management from the GUI.

---

## ✨ Key Features
- Multi-Format Archive Support
- `.mcn` (Macan's custom format)
- `.7z`
- `.zip`
- `.tar`, `.gz`, `.bz2`, `.xz`
- `.rar` (optional, requires the `rarfile` module)
- Create Archive — create a new archive with the LZMA/LZMA2 compression method and Store-Best level.
- Create SFX.
- **Open Archive** — Open an archive file and display its contents in an interactive table.
- **Extract Archive** — Extract all or selected files with a single click.
- **Test Archive (7z/MCN)** — Verify the integrity of the archive to ensure it's not corrupted.
- **Delete Items (7z/MCN)** — Delete files within the archive with automatic repacking.
- **Context Menu & Drag & Drop** — Modern UX, just drag files into the application.
- **Dark Theme Premium** — Elegant enterprise software-style interface.
---
📝 Changelog:
🐞 Fixed * Addressed a critical bug in the "Copy Selected" (context menu) functionality where attempting to copy multiple items from an archive would fail unpredictably. * The bug could cause either **only one item** to be copied (despite selecting multiple) or, in some cases, the **entire archive's contents** to be extracted and copied, ignoring the user's selection. * Reworked the `_copy_selected_files_to_clipboard` method to be significantly more robust. Instead of passing filenames as command-line arguments (which caused the failure), the function now: 1. Writes the list of selected files to a temporary `listfile.txt`. 2. Calls `7z.exe` using the `@<listfile>` switch, which reliably handles any number of files. * The "Copy Selected" action now correctly extracts *only* the chosen files/folders to the temporary directory, ensuring that pasting into Windows Explorer works as expected.

---
## 📸 Screenshot
<img width="798" height="637" alt="Screenshot 2025-10-25 170854" src="https://github.com/user-attachments/assets/b648ba3a-c357-480a-adb4-2fb81718a920" />
<img width="798" height="635" alt="Screenshot 2025-10-25 170909" src="https://github.com/user-attachments/assets/e1e93748-5dc5-492c-93b3-3383d0e46330" />



---

## 🖼️ Appearance
- Toolbar with modern SVG icons (Create, Open, Extract, Test, Copy, Delete, About).
- Interactive table with columns:
- Name
- Size
- Modification Date
- Type (File / Folder)
- Status bar displays the number of files, their size, and the selection.

---

## 📦 Dependencies
- Python 3.9+
- [PySide6](https://pypi.org/project/PySide6/)
- [py7zr](https://pypi.org/project/py7zr/)
- [rarfile](https://pypi.org/project/rarfile/) *(optional, for .rar support)*

---

## 🚀 How to Run
1. Clone the repo or download the source.
2. Install dependencies:
```bash
pip install PySide6 py7zr
pip install rarfile # optional for RAR support
