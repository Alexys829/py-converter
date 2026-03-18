from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QLineEdit, QGroupBox, QMessageBox, QComboBox,
)

from pyconverter.core.profiles import ConversionProfile
from pyconverter.core.registry import ConverterRegistry


class ProfilesDialog(QDialog):
    profile_selected = Signal(str, dict)  # output_format, options

    def __init__(self, current_format: str = "", current_options: dict | None = None, parent=None):
        super().__init__(parent)
        self._current_format = current_format
        self._current_options = current_options or {}

        self.setWindowTitle("Conversion Profiles")
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout(self)

        # Saved profiles list
        list_group = QGroupBox("Saved Profiles")
        list_layout = QVBoxLayout(list_group)

        self._profile_list = QListWidget()
        self._profile_list.itemDoubleClicked.connect(self._load_profile)
        list_layout.addWidget(self._profile_list)

        list_btns = QHBoxLayout()

        load_btn = QPushButton("Load")
        load_btn.setToolTip("Load selected profile")
        load_btn.clicked.connect(self._load_selected)
        list_btns.addWidget(load_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("cancelButton")
        delete_btn.setToolTip("Delete selected profile")
        delete_btn.clicked.connect(self._delete_selected)
        list_btns.addWidget(delete_btn)

        list_btns.addStretch()
        list_layout.addLayout(list_btns)
        layout.addWidget(list_group, stretch=1)

        # Save new profile
        save_group = QGroupBox("Save Current Settings as Profile")
        save_layout = QHBoxLayout(save_group)

        save_layout.addWidget(QLabel("Name:"))
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("e.g. JPG High Quality")
        save_layout.addWidget(self._name_input, stretch=1)

        save_btn = QPushButton("Save")
        save_btn.setToolTip("Save current settings as a new profile")
        save_btn.clicked.connect(self._save_profile)
        save_layout.addWidget(save_btn)

        layout.addWidget(save_group)

        # Close
        close_btn = QPushButton("Close")
        close_btn.setToolTip("Close this dialog")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self._refresh_list()

    def _refresh_list(self):
        self._profile_list.clear()
        for name in ConversionProfile.list_profiles():
            self._profile_list.addItem(name)

    def _save_profile(self):
        name = self._name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Enter a profile name.")
            return

        profile = ConversionProfile(
            name=name,
            output_format=self._current_format,
            options=self._current_options,
        )
        profile.save()
        self._name_input.clear()
        self._refresh_list()

    def _load_selected(self):
        item = self._profile_list.currentItem()
        if item:
            self._load_profile(item)

    def _load_profile(self, item):
        try:
            profile = ConversionProfile.load(item.text())
            self.profile_selected.emit(profile.output_format, profile.options)
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load profile: {e}")

    def _delete_selected(self):
        item = self._profile_list.currentItem()
        if not item:
            return
        reply = QMessageBox.question(
            self, "Delete Profile",
            f"Delete profile '{item.text()}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            ConversionProfile.delete(item.text())
            self._refresh_list()
