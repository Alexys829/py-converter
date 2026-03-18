from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QComboBox, QCheckBox, QGroupBox, QFileDialog,
    QListWidget, QListWidgetItem,
)

from pyconverter.core.registry import ConverterRegistry
from pyconverter.core.watcher import FolderWatcher


class WatcherDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._watcher: FolderWatcher | None = None

        self.setWindowTitle("Watch Folder")
        self.setMinimumSize(550, 450)

        layout = QVBoxLayout(self)

        # Config group
        config_group = QGroupBox("Configuration")
        config_layout = QVBoxLayout(config_group)

        # Watch dir
        dir_row = QHBoxLayout()
        dir_row.addWidget(QLabel("Watch Folder:"))
        self._dir_input = QLineEdit()
        self._dir_input.setPlaceholderText("Select a folder to monitor...")
        dir_row.addWidget(self._dir_input, stretch=1)
        browse_btn = QPushButton("Browse...")
        browse_btn.setFixedWidth(80)
        browse_btn.setToolTip("Select folder to monitor")
        browse_btn.clicked.connect(self._browse_dir)
        dir_row.addWidget(browse_btn)
        config_layout.addLayout(dir_row)

        # Output dir
        out_row = QHBoxLayout()
        out_row.addWidget(QLabel("Output Folder:"))
        self._out_dir_input = QLineEdit()
        self._out_dir_input.setPlaceholderText("(default: subfolder 'converted')")
        out_row.addWidget(self._out_dir_input, stretch=1)
        out_browse_btn = QPushButton("Browse...")
        out_browse_btn.setFixedWidth(80)
        out_browse_btn.setToolTip("Select output folder")
        out_browse_btn.clicked.connect(self._browse_out_dir)
        out_row.addWidget(out_browse_btn)
        config_layout.addLayout(out_row)

        # Format
        fmt_row = QHBoxLayout()
        fmt_row.addWidget(QLabel("Convert to:"))
        self._format_combo = QComboBox()
        all_outputs = set()
        for conv in ConverterRegistry.list_converters():
            all_outputs.update(conv.supported_output_formats())
        self._format_combo.addItems(sorted(all_outputs))
        fmt_row.addWidget(self._format_combo)
        fmt_row.addStretch()

        self._recursive_check = QCheckBox("Include subfolders")
        fmt_row.addWidget(self._recursive_check)
        config_layout.addLayout(fmt_row)

        layout.addWidget(config_group)

        # Controls
        ctrl_row = QHBoxLayout()
        self._start_btn = QPushButton("Start Watching")
        self._start_btn.setToolTip("Start monitoring the folder for new files")
        self._start_btn.clicked.connect(self._start_watching)
        ctrl_row.addWidget(self._start_btn)

        self._stop_btn = QPushButton("Stop")
        self._stop_btn.setObjectName("cancelButton")
        self._stop_btn.setToolTip("Stop monitoring")
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self._stop_watching)
        ctrl_row.addWidget(self._stop_btn)

        ctrl_row.addStretch()

        self._status_label = QLabel("Stopped")
        self._status_label.setStyleSheet("font-weight: bold;")
        ctrl_row.addWidget(self._status_label)

        layout.addLayout(ctrl_row)

        # Log
        log_group = QGroupBox("Activity Log")
        log_layout = QVBoxLayout(log_group)
        self._log_list = QListWidget()
        log_layout.addWidget(self._log_list)
        layout.addWidget(log_group, stretch=1)

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Watch Folder")
        if d:
            self._dir_input.setText(d)

    def _browse_out_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if d:
            self._out_dir_input.setText(d)

    def _start_watching(self):
        watch_dir = self._dir_input.text().strip()
        if not watch_dir:
            return

        out_dir = self._out_dir_input.text().strip() or None
        output_format = self._format_combo.currentText()
        recursive = self._recursive_check.isChecked()

        self._watcher = FolderWatcher(
            watch_dir=watch_dir,
            output_format=output_format,
            output_dir=out_dir,
            recursive=recursive,
        )
        self._watcher.watching_started.connect(self._on_started)
        self._watcher.watching_stopped.connect(self._on_stopped)
        self._watcher.file_converted.connect(self._on_converted)
        self._watcher.file_failed.connect(self._on_failed)
        self._watcher.start()

        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)

    def _stop_watching(self):
        if self._watcher:
            self._watcher.stop()

    def _on_started(self, path: str):
        self._status_label.setText(f"Watching: {path}")
        self._status_label.setStyleSheet("font-weight: bold; color: #a6e3a1;")
        self._log_list.addItem(f"Started watching: {path}")

    def _on_stopped(self):
        self._status_label.setText("Stopped")
        self._status_label.setStyleSheet("font-weight: bold;")
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._log_list.addItem("Watching stopped")
        self._watcher = None

    def _on_converted(self, input_path: str, output_path: str):
        from pathlib import Path
        self._log_list.addItem(f"OK: {Path(input_path).name} -> {Path(output_path).name}")
        self._log_list.scrollToBottom()

    def _on_failed(self, input_path: str, error: str):
        from pathlib import Path
        self._log_list.addItem(f"FAIL: {Path(input_path).name} - {error}")
        self._log_list.scrollToBottom()

    def closeEvent(self, event):
        if self._watcher:
            self._watcher.stop()
            self._watcher.wait(2000)
        super().closeEvent(event)
