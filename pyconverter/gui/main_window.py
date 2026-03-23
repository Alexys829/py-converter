import json
import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QSize, QSettings
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStatusBar, QMenuBar, QMessageBox, QMenu,
)

from pyconverter.gui.icons import icon

from pyconverter.core.base_converter import ConversionTask
from pyconverter.core.format_detector import detect_format
from pyconverter.core.registry import ConverterRegistry
from pyconverter.core.history import ConversionHistory
from pyconverter.gui.file_drop_widget import FileDropWidget
from pyconverter.gui.conversion_panel import ConversionPanel
from pyconverter.gui.queue_widget import QueueWidget
from pyconverter.gui.progress_widget import OverallProgressWidget
from pyconverter.gui.workers import ConversionWorker
from pyconverter.gui.theme import ThemeManager
from pyconverter.gui.settings_dialog import SettingsDialog

RECENT_FILES_MAX = 10


class MainWindow(QMainWindow):
    def __init__(self, theme_manager: ThemeManager):
        super().__init__()
        self._theme_manager = theme_manager
        self._worker: ConversionWorker | None = None
        self._completed_count = 0
        self._failed_count = 0
        self._history = ConversionHistory()
        self._tasks: list[ConversionTask] = []
        self._settings = QSettings("PyConverter", "PyConverter")

        self.setWindowTitle("PyConverter")
        self.setMinimumSize(750, 650)

        self._setup_menu_bar()
        self._setup_ui()
        self._setup_status_bar()
        self._setup_shortcuts()

    # ── Menu ──

    def _setup_menu_bar(self):
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("Add Files...\tCtrl+O", self._browse_files)
        self._recent_menu = file_menu.addMenu("Recent Files")
        self._rebuild_recent_menu()
        file_menu.addSeparator()
        file_menu.addAction("Settings...", self._open_settings)
        file_menu.addSeparator()
        file_menu.addAction("Exit\tCtrl+Q", self.close)

        tools_menu = menu_bar.addMenu("Tools")
        tools_menu.addAction("Watch Folder...", self._open_watcher)
        tools_menu.addSeparator()
        tools_menu.addAction("Conversion Profiles...", self._open_profiles)
        tools_menu.addAction("Conversion History...", self._open_history)

        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("Features && Supported Formats...\tF1", self._show_help)
        help_menu.addSeparator()
        help_menu.addAction("Keyboard Shortcuts...", self._show_shortcuts)
        help_menu.addAction("About...", self._show_about)

    # ── Shortcuts ──

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+O"), self, self._browse_files)
        QShortcut(QKeySequence("Ctrl+Return"), self, self._start_conversion)
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("Ctrl+T"), self, self._toggle_theme)
        QShortcut(QKeySequence("Delete"), self, self._delete_selected_from_queue)
        QShortcut(QKeySequence("F1"), self, self._show_help)

    def _browse_files(self):
        from PySide6.QtWidgets import QFileDialog
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "All Files (*)")
        if files:
            self._on_files_dropped([Path(f) for f in files])

    def _delete_selected_from_queue(self):
        self._queue_widget._remove_selected()

    # ── UI ──

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("PyConverter")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        self._drop_widget = FileDropWidget()
        self._drop_widget.files_dropped.connect(self._on_files_dropped)
        layout.addWidget(self._drop_widget)

        self._conv_panel = ConversionPanel()
        layout.addWidget(self._conv_panel)

        self._queue_widget = QueueWidget()
        self._queue_widget.preview_requested.connect(self._on_preview_requested)
        layout.addWidget(self._queue_widget, stretch=1)

        self._estimate_label = QLabel("")
        self._estimate_label.setStyleSheet("color: #6c7086; font-size: 11px;")
        layout.addWidget(self._estimate_label)

        bottom = QHBoxLayout()

        self._progress_widget = OverallProgressWidget()
        bottom.addWidget(self._progress_widget, stretch=1)

        self._convert_btn = QPushButton(" Convert")
        self._convert_btn.setIcon(icon("convert", "#1e1e2e"))
        self._convert_btn.setIconSize(QSize(20, 20))
        self._convert_btn.setToolTip("Convert all files in queue (Ctrl+Enter)")
        self._convert_btn.clicked.connect(self._start_conversion)
        bottom.addWidget(self._convert_btn)

        self._cancel_btn = QPushButton(" Cancel")
        self._cancel_btn.setObjectName("cancelButton")
        self._cancel_btn.setIcon(icon("cancel", "#1e1e2e"))
        self._cancel_btn.setIconSize(QSize(18, 18))
        self._cancel_btn.setToolTip("Cancel conversion")
        self._cancel_btn.setEnabled(False)
        self._cancel_btn.clicked.connect(self._cancel_conversion)
        bottom.addWidget(self._cancel_btn)

        self._open_folder_btn = QPushButton(" Open Folder")
        self._open_folder_btn.setObjectName("textIconButton")
        self._open_folder_btn.setIcon(icon("folder_open"))
        self._open_folder_btn.setIconSize(QSize(18, 18))
        self._open_folder_btn.setToolTip("Open output folder")
        self._open_folder_btn.setEnabled(False)
        self._open_folder_btn.clicked.connect(self._open_output_folder)
        bottom.addWidget(self._open_folder_btn)

        layout.addLayout(bottom)

        self._last_output_dir: Path | None = None

    def _setup_status_bar(self):
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Ready  |  Ctrl+O: Add files  |  Ctrl+Enter: Convert")

    # ── Recent files ──

    def _get_recent_files(self) -> list[str]:
        data = self._settings.value("recent_files", "[]")
        try:
            return json.loads(data) if isinstance(data, str) else []
        except (json.JSONDecodeError, TypeError):
            return []

    def _add_recent_files(self, paths: list[Path]):
        recent = self._get_recent_files()
        for p in paths:
            s = str(p)
            if s in recent:
                recent.remove(s)
            recent.insert(0, s)
        recent = recent[:RECENT_FILES_MAX]
        self._settings.setValue("recent_files", json.dumps(recent))
        self._rebuild_recent_menu()

    def _rebuild_recent_menu(self):
        self._recent_menu.clear()
        recent = self._get_recent_files()
        if not recent:
            self._recent_menu.addAction("(empty)").setEnabled(False)
            return
        for path_str in recent:
            name = Path(path_str).name
            action = self._recent_menu.addAction(name)
            action.setToolTip(path_str)
            action.triggered.connect(lambda checked, p=path_str: self._open_recent(p))
        self._recent_menu.addSeparator()
        self._recent_menu.addAction("Clear Recent", self._clear_recent)

    def _open_recent(self, path_str: str):
        p = Path(path_str)
        if p.exists():
            self._on_files_dropped([p])
        else:
            QMessageBox.warning(self, "Warning", f"File not found:\n{path_str}")

    def _clear_recent(self):
        self._settings.setValue("recent_files", "[]")
        self._rebuild_recent_menu()

    # ── File handling ──

    def _on_files_dropped(self, paths: list[Path]):
        first_format = None
        for path in paths:
            self._queue_widget.add_file(path)
            if first_format is None:
                first_format = detect_format(path)

        if first_format:
            self._conv_panel.set_input_format(first_format)

        self._add_recent_files(paths)
        self._update_estimate()

        count = self._queue_widget.count()
        self._status_bar.showMessage(f"{count} file(s) in queue")

    def _on_preview_requested(self, file_path):
        from pyconverter.gui.preview_widget import PreviewDialog
        dialog = PreviewDialog(Path(file_path), self)
        dialog.exec()

    def _update_estimate(self):
        paths = self._queue_widget.get_file_paths()
        if not paths:
            self._estimate_label.setText("")
            return
        total = sum(p.stat().st_size for p in paths if p.exists())
        if total < 1024:
            size_str = f"{total} B"
        elif total < 1024 * 1024:
            size_str = f"{total / 1024:.1f} KB"
        else:
            size_str = f"{total / (1024 * 1024):.1f} MB"
        self._estimate_label.setText(f"Total input size: {size_str}  |  {len(paths)} file(s)")

    # ── Conversion ──

    def _start_conversion(self):
        file_paths = self._queue_widget.get_file_paths()
        if not file_paths:
            self._status_bar.showMessage("No files in queue")
            return

        output_format = self._conv_panel.selected_format
        if not output_format:
            self._status_bar.showMessage("Select an output format")
            return

        options = self._conv_panel.get_options()
        output_dir = self._conv_panel.output_dir

        self._tasks = []
        for path in file_paths:
            if output_dir:
                out_path = Path(output_dir) / f"{path.stem}.{output_format}"
            else:
                out_path = path.parent / f"{path.stem}.{output_format}"
            self._tasks.append(ConversionTask(
                input_path=path,
                output_path=out_path,
                output_format=output_format,
                options=options,
            ))

        self._completed_count = 0
        self._failed_count = 0
        self._progress_widget.reset()
        self._convert_btn.setEnabled(False)
        self._cancel_btn.setEnabled(True)
        self._open_folder_btn.setEnabled(False)
        self._status_bar.showMessage("Converting...")

        self._worker = ConversionWorker(self._tasks)
        self._worker.task_started.connect(self._on_task_started)
        self._worker.task_progress.connect(self._on_task_progress)
        self._worker.task_completed.connect(self._on_task_completed)
        self._worker.task_failed.connect(self._on_task_failed)
        self._worker.queue_finished.connect(self._on_queue_finished)
        self._worker.start()

    def _cancel_conversion(self):
        if self._worker:
            self._worker.cancel()
            self._status_bar.showMessage("Cancelling...")

    def _on_task_started(self, index: int):
        self._queue_widget.set_item_status(index, "Running")

    def _on_task_progress(self, index: int, progress: float):
        self._queue_widget.set_item_progress(index, progress)

    def _on_task_completed(self, index: int, output_path: str):
        self._queue_widget.set_item_status(index, "Done")
        self._queue_widget.set_item_progress(index, 1.0)
        self._completed_count += 1
        self._last_output_dir = Path(output_path).parent
        total = self._queue_widget.count()
        self._progress_widget.update_progress(self._completed_count + self._failed_count, total)

        if 0 <= index < len(self._tasks):
            task = self._tasks[index]
            in_fmt = detect_format(task.input_path) or ""
            try:
                conv = ConverterRegistry.find_converter(in_fmt, task.output_format)
                conv_name = conv.name()
            except Exception:
                conv_name = "Unknown"
            self._history.add(
                str(task.input_path), str(task.output_path),
                in_fmt, task.output_format, conv_name,
                success=True, options=task.options,
            )

    def _on_task_failed(self, index: int, error: str):
        self._queue_widget.set_item_status(index, "Failed")
        self._failed_count += 1
        total = self._queue_widget.count()
        self._progress_widget.update_progress(self._completed_count + self._failed_count, total)
        self._status_bar.showMessage(f"Error: {error}")

        if 0 <= index < len(self._tasks):
            task = self._tasks[index]
            in_fmt = detect_format(task.input_path) or ""
            self._history.add(
                str(task.input_path), str(task.output_path),
                in_fmt, task.output_format, "Unknown",
                success=False, error=error,
            )

    def _on_queue_finished(self):
        self._convert_btn.setEnabled(True)
        self._cancel_btn.setEnabled(False)
        if self._last_output_dir:
            self._open_folder_btn.setEnabled(True)
        total = self._queue_widget.count()
        msg = f"Done! {self._completed_count}/{total} converted"
        if self._failed_count:
            msg += f", {self._failed_count} failed"
        self._status_bar.showMessage(msg)
        self._worker = None

        self._send_notification(
            "PyConverter",
            f"{self._completed_count} file(s) converted successfully."
        )

    def _send_notification(self, title: str, message: str):
        try:
            if sys.platform == "linux":
                subprocess.Popen(
                    ["notify-send", title, message, "--app-name=PyConverter"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
            elif sys.platform == "win32":
                ps = (
                    f"[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, "
                    f"ContentType = WindowsRuntime] > $null; "
                    f"$xml = [Windows.UI.Notifications.ToastNotificationManager]::"
                    f"GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02); "
                    f"$text = $xml.GetElementsByTagName('text'); "
                    f"$text[0].AppendChild($xml.CreateTextNode('{title}')); "
                    f"$text[1].AppendChild($xml.CreateTextNode('{message}')); "
                    f"$toast = [Windows.UI.Notifications.ToastNotification]::new($xml); "
                    f"[Windows.UI.Notifications.ToastNotificationManager]::"
                    f"CreateToastNotifier('PyConverter').Show($toast)"
                )
                subprocess.Popen(
                    ["powershell", "-Command", ps],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
        except Exception:
            pass

    def _open_output_folder(self):
        if not self._last_output_dir or not self._last_output_dir.exists():
            return
        folder = str(self._last_output_dir)
        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])

    # ── Tools ──

    def _open_watcher(self):
        from pyconverter.gui.watcher_dialog import WatcherDialog
        dialog = WatcherDialog(self)
        dialog.exec()

    def _open_profiles(self):
        from pyconverter.gui.profiles_dialog import ProfilesDialog
        current_fmt = self._conv_panel.selected_format
        current_opts = self._conv_panel.get_options()
        dialog = ProfilesDialog(current_fmt, current_opts, self)
        dialog.profile_selected.connect(self._apply_profile)
        dialog.exec()

    def _apply_profile(self, output_format: str, options: dict):
        if output_format:
            idx = self._conv_panel._format_combo.findText(output_format)
            if idx >= 0:
                self._conv_panel._format_combo.setCurrentIndex(idx)
        self._status_bar.showMessage(f"Profile loaded: {output_format}")

    def _open_history(self):
        from pyconverter.gui.history_dialog import HistoryDialog
        dialog = HistoryDialog(self._history, self)
        dialog.exec()

    # ── View ──

    def _toggle_theme(self):
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        theme = self._theme_manager.toggle(app)
        self._status_bar.showMessage(f"Theme: {theme}")

    # ── Help ──

    def _show_help(self):
        from PySide6.QtWidgets import (
            QDialog, QTabWidget, QTextBrowser, QDialogButtonBox,
        )

        dialog = QDialog(self)
        dialog.setWindowTitle("Help")
        dialog.setMinimumSize(680, 500)
        dlg_layout = QVBoxLayout(dialog)

        tabs = QTabWidget()
        dlg_layout.addWidget(tabs, stretch=1)

        features_browser = QTextBrowser()
        features_browser.setOpenExternalLinks(False)
        features_browser.setHtml("""
        <h3>Conversion</h3>
        <table cellspacing="6">
            <tr><td><b>Drag & Drop</b></td><td>Drop files into the app or click Browse (Ctrl+O)</td></tr>
            <tr><td><b>Batch Conversion</b></td><td>Add multiple files and convert them all at once</td></tr>
            <tr><td><b>Parallel Processing</b></td><td>Up to 4 files converted simultaneously</td></tr>
            <tr><td><b>Auto-rename</b></td><td>If output file exists, automatically adds _1, _2, etc.</td></tr>
            <tr><td><b>File Preview</b></td><td>Preview images, text, and PDFs before converting</td></tr>
            <tr><td><b>Queue Management</b></td><td>Remove single files (X), remove selected (Delete), or clear all</td></tr>
            <tr><td><b>Conversion Options</b></td><td>Quality, resolution, compression, bitrate, etc. per format</td></tr>
            <tr><td><b>Image Compression</b></td><td>Optimize images without changing format (PNG to PNG)</td></tr>
            <tr><td><b>Audio from Video</b></td><td>Extract audio tracks from MP4, MKV, AVI, etc.</td></tr>
            <tr><td><b>Output Directory</b></td><td>Choose where to save converted files</td></tr>
            <tr><td><b>Open Folder</b></td><td>Quickly open output folder after conversion</td></tr>
        </table>
        <h3>Tools</h3>
        <table cellspacing="6">
            <tr><td><b>Watch Folder</b></td><td>Monitor a folder and auto-convert new files</td></tr>
            <tr><td><b>Profiles</b></td><td>Save conversion presets and reload them</td></tr>
            <tr><td><b>History</b></td><td>View past conversions with status and errors</td></tr>
        </table>
        <h3>General</h3>
        <table cellspacing="6">
            <tr><td><b>Recent Files</b></td><td>Quick access to last 10 files (File menu)</td></tr>
            <tr><td><b>Notifications</b></td><td>System notification when batch finishes</td></tr>
            <tr><td><b>Shortcuts</b></td><td>Ctrl+O, Ctrl+Enter, Delete, Ctrl+T, Ctrl+Q, F1</td></tr>
            <tr><td><b>Theme</b></td><td>Dark / Light Material Design (Ctrl+T)</td></tr>
            <tr><td><b>CLI</b></td><td>Command-line: convert, batch, formats</td></tr>
        </table>
        """)
        tabs.addTab(features_browser, "Features")

        lines = []
        for conv in ConverterRegistry.list_converters():
            inputs = ", ".join(f".{f}" for f in conv.supported_input_formats())
            outputs = ", ".join(f".{f}" for f in conv.supported_output_formats())
            options = conv.get_options(
                conv.supported_input_formats()[0],
                conv.supported_output_formats()[0],
            )
            opt_text = ", ".join(o.label for o in options) if options else "-"
            lines.append(
                f"<tr><td style='padding:4px'><b>{conv.name()}</b></td>"
                f"<td style='padding:4px'>{inputs}</td>"
                f"<td style='padding:4px'>{outputs}</td>"
                f"<td style='padding:4px'>{opt_text}</td></tr>"
            )

        conv_browser = QTextBrowser()
        conv_browser.setHtml(f"""
        <h3>Supported Conversions</h3>
        <table border="1" cellspacing="0" style="border-collapse:collapse; border-color:#555">
            <tr style="background-color:#333; color:#fff">
                <th style="padding:4px">Converter</th>
                <th style="padding:4px">Input</th>
                <th style="padding:4px">Output</th>
                <th style="padding:4px">Options</th>
            </tr>
            {"".join(lines)}
        </table>
        <br>
        <b>Notes:</b>
        <ul>
            <li>Audio/Video uses bundled ffmpeg (no system install needed)</li>
            <li>Audio converter accepts video files to extract audio</li>
            <li>Image compression: convert to same format with Optimize</li>
            <li>Auto-rename adds _1, _2, etc. if output exists</li>
        </ul>
        """)
        tabs.addTab(conv_browser, "Conversions")

        cli_browser = QTextBrowser()
        cli_browser.setHtml("""
        <h3>Command Line Interface</h3>
        <pre>python main.py convert file.png -f jpg
python main.py convert photo.png -f jpg --option quality 90
python main.py batch *.png -f webp -d output/
python main.py batch -r folder/ -f png -d output/
python main.py formats</pre>
        <h4>Options</h4>
        <table cellspacing="4">
            <tr><td><code>-f, --format</code></td><td>Target format (required)</td></tr>
            <tr><td><code>-o, --output</code></td><td>Output file path</td></tr>
            <tr><td><code>-d, --output-dir</code></td><td>Output directory (batch)</td></tr>
            <tr><td><code>-r, --recursive</code></td><td>Recurse directories (batch)</td></tr>
            <tr><td><code>--option KEY VALUE</code></td><td>Converter option (repeatable)</td></tr>
        </table>
        """)
        tabs.addTab(cli_browser, "CLI Usage")

        shortcuts_browser = QTextBrowser()
        shortcuts_browser.setHtml("""
        <h3>Keyboard Shortcuts</h3>
        <table cellspacing="8">
            <tr><td><b>Ctrl+O</b></td><td>Add files</td></tr>
            <tr><td><b>Ctrl+Enter</b></td><td>Start conversion</td></tr>
            <tr><td><b>Delete</b></td><td>Remove selected from queue</td></tr>
            <tr><td><b>Ctrl+T</b></td><td>Toggle theme</td></tr>
            <tr><td><b>Ctrl+Q</b></td><td>Exit</td></tr>
            <tr><td><b>F1</b></td><td>Help</td></tr>
        </table>
        """)
        tabs.addTab(shortcuts_browser, "Shortcuts")

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn_box.rejected.connect(dialog.accept)
        dlg_layout.addWidget(btn_box)

        dialog.exec()

    def _show_shortcuts(self):
        QMessageBox.information(self, "Keyboard Shortcuts", """
<table cellspacing="8">
<tr><td><b>Ctrl+O</b></td><td>Add files</td></tr>
<tr><td><b>Ctrl+Enter</b></td><td>Start conversion</td></tr>
<tr><td><b>Delete</b></td><td>Remove selected from queue</td></tr>
<tr><td><b>Ctrl+T</b></td><td>Toggle theme</td></tr>
<tr><td><b>Ctrl+Q</b></td><td>Exit</td></tr>
<tr><td><b>F1</b></td><td>Help</td></tr>
</table>
        """)

    def _show_about(self):
        from pyconverter import __version__
        QMessageBox.about(
            self,
            "About PyConverter",
            f"<h3>PyConverter v{__version__}</h3>"
            f"<p>Universal cross-platform file converter.</p>"
            f"<p>Supports images, documents, data, audio, and video.</p>"
            f"<p>Parallel conversion, Material Design, keyboard shortcuts.</p>",
        )

    def _open_settings(self):
        dialog = SettingsDialog(self._theme_manager, self)
        dialog.exec()
