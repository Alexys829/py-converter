import os
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QGroupBox, QLineEdit, QFileDialog, QMessageBox,
)

from pyconverter.gui.theme import ThemeManager

APP_NAME = "PyConverter"
DESKTOP_FILE_PATH = Path.home() / ".local" / "share" / "applications" / "pyconverter.desktop"


class SettingsDialog(QDialog):
    def __init__(self, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self._theme_manager = theme_manager

        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Theme group
        theme_group = QGroupBox("Appearance")
        theme_layout = QHBoxLayout(theme_group)
        theme_layout.addWidget(QLabel("Theme:"))
        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["dark", "light"])
        self._theme_combo.setCurrentText(theme_manager.current)
        theme_layout.addWidget(self._theme_combo)
        layout.addWidget(theme_group)

        # Desktop integration (Linux only)
        if sys.platform == "linux":
            layout.addWidget(self._build_desktop_section())

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.setToolTip("Apply settings and close")
        ok_btn.clicked.connect(self._apply_and_close)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setToolTip("Discard changes")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

    def _apply_and_close(self):
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        self._theme_manager.set_theme(self._theme_combo.currentText(), app)
        self.accept()

    # ── Desktop Integration (Linux) ──────────────────────────

    def _build_desktop_section(self) -> QGroupBox:
        group = QGroupBox("Desktop Integration (AppImage)")
        layout = QVBoxLayout(group)
        layout.setSpacing(12)

        # AppImage path
        path_row = QHBoxLayout()
        path_row.addWidget(QLabel("AppImage path:"))
        self._appimage_input = QLineEdit()
        self._appimage_input.setPlaceholderText("/path/to/PyConverter-x86_64.AppImage")
        detected = os.environ.get("APPIMAGE")
        if detected:
            self._appimage_input.setText(detected)
        path_row.addWidget(self._appimage_input)
        browse_btn = QPushButton("Browse")
        browse_btn.setFixedWidth(80)
        browse_btn.setToolTip("Select AppImage file")
        browse_btn.clicked.connect(self._on_browse_appimage)
        path_row.addWidget(browse_btn)
        layout.addLayout(path_row)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        add_btn = QPushButton("Add to App Menu")
        add_btn.setToolTip("Create desktop entry to show in application menu")
        add_btn.clicked.connect(self._on_add_to_menu)
        btn_row.addWidget(add_btn)

        remove_btn = QPushButton("Remove from App Menu")
        remove_btn.setObjectName("cancelButton")
        remove_btn.setToolTip("Remove desktop entry from application menu")
        remove_btn.clicked.connect(self._on_remove_from_menu)
        btn_row.addWidget(remove_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Status
        self._desktop_status = QLabel()
        self._desktop_status.setStyleSheet("font-size: 11px;")
        self._update_desktop_status()
        layout.addWidget(self._desktop_status)

        return group

    def _on_browse_appimage(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select AppImage", "", "AppImage (*.AppImage);;All Files (*)"
        )
        if path:
            self._appimage_input.setText(path)

    def _on_add_to_menu(self):
        appimage_path = self._appimage_input.text().strip()
        if not appimage_path:
            QMessageBox.warning(self, "Desktop Integration",
                                "Please specify the AppImage path first.")
            return
        if not os.path.isfile(appimage_path):
            QMessageBox.warning(self, "Desktop Integration",
                                f"File not found:\n{appimage_path}")
            return
        try:
            desktop_content = (
                "[Desktop Entry]\n"
                "Type=Application\n"
                f"Name={APP_NAME}\n"
                "Comment=Universal file converter\n"
                f"Exec={appimage_path}\n"
                "Terminal=false\n"
                "Categories=Utility;FileTools;\n"
                "Keywords=convert;file;image;pdf;audio;video;\n"
                f"StartupWMClass={APP_NAME.lower()}\n"
            )
            DESKTOP_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
            DESKTOP_FILE_PATH.write_text(desktop_content)
            os.chmod(str(DESKTOP_FILE_PATH), 0o755)
            self._update_desktop_status()
            QMessageBox.information(self, "Desktop Integration",
                                    f"{APP_NAME} has been added to the application menu.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _on_remove_from_menu(self):
        if DESKTOP_FILE_PATH.exists():
            DESKTOP_FILE_PATH.unlink()
            self._update_desktop_status()
            QMessageBox.information(self, "Desktop Integration",
                                    f"{APP_NAME} has been removed from the application menu.")
        else:
            QMessageBox.information(self, "Desktop Integration",
                                    "Desktop file not found. Nothing to remove.")

    def _update_desktop_status(self):
        if DESKTOP_FILE_PATH.exists():
            self._desktop_status.setText(f"Status: Installed ({DESKTOP_FILE_PATH})")
            self._desktop_status.setStyleSheet("color: #a6e3a1; font-size: 11px;")
        else:
            self._desktop_status.setText("Status: Not installed")
            self._desktop_status.setStyleSheet("color: #6c7086; font-size: 11px;")
