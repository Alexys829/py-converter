import time
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from pyconverter.core.base_converter import ConversionTask
from pyconverter.core.format_detector import detect_format
from pyconverter.core.registry import ConverterRegistry


class FolderWatcher(QThread):
    """Monitors a folder for new files and auto-converts them."""
    file_converted = Signal(str, str)  # input_path, output_path
    file_failed = Signal(str, str)  # input_path, error
    watching_started = Signal(str)  # watch_dir
    watching_stopped = Signal()

    def __init__(self, watch_dir: str, output_format: str,
                 output_dir: str | None = None, options: dict | None = None,
                 recursive: bool = False, parent=None):
        super().__init__(parent)
        self._watch_dir = Path(watch_dir)
        self._output_format = output_format
        self._output_dir = Path(output_dir) if output_dir else None
        self._options = options or {}
        self._recursive = recursive
        self._running = False
        self._seen_files: set[str] = set()

    def stop(self):
        self._running = False

    def run(self):
        self._running = True
        self.watching_started.emit(str(self._watch_dir))

        # Snapshot existing files so we don't convert them
        self._seen_files = {str(p) for p in self._scan_files()}

        while self._running:
            current_files = self._scan_files()
            for file_path in current_files:
                key = str(file_path)
                if key in self._seen_files:
                    continue
                self._seen_files.add(key)

                # Small delay to ensure file is fully written
                time.sleep(0.5)
                if not file_path.exists():
                    continue

                self._convert_file(file_path)

            time.sleep(2)  # Poll interval

        self.watching_stopped.emit()

    def _scan_files(self) -> list[Path]:
        if not self._watch_dir.exists():
            return []
        if self._recursive:
            return [p for p in self._watch_dir.rglob("*") if p.is_file()]
        return [p for p in self._watch_dir.iterdir() if p.is_file()]

    def _convert_file(self, file_path: Path):
        in_fmt = detect_format(file_path)
        if not in_fmt:
            return

        try:
            converter = ConverterRegistry.find_converter(in_fmt, self._output_format)
        except Exception:
            return  # No converter for this format, skip silently

        if self._output_dir:
            out_dir = self._output_dir
        else:
            out_dir = file_path.parent / "converted"
        out_dir.mkdir(parents=True, exist_ok=True)

        out_path = out_dir / f"{file_path.stem}.{self._output_format}"
        task = ConversionTask(file_path, out_path, self._output_format, self._options)

        try:
            result = converter.convert(task)
            self.file_converted.emit(str(file_path), str(result))
        except Exception as e:
            self.file_failed.emit(str(file_path), str(e))
