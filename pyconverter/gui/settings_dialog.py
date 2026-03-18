from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QGroupBox,
)

from pyconverter.gui.theme import ThemeManager


class SettingsDialog(QDialog):
    def __init__(self, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self._theme_manager = theme_manager

        self.setWindowTitle("Settings")
        self.setMinimumWidth(350)

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
