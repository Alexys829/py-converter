from pathlib import Path
from PySide6.QtCore import QThread, Signal, QObject, QRunnable, QThreadPool, Slot
from pyconverter.core.base_converter import ConversionTask
from pyconverter.core.registry import ConverterRegistry


def auto_rename(path: Path) -> Path:
    """If path exists, add _1, _2, etc. before the extension."""
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 1
    while True:
        new_path = parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1


class _TaskSignals(QObject):
    started = Signal(int)
    progress = Signal(int, float)
    completed = Signal(int, str)
    failed = Signal(int, str)


class _ConversionRunnable(QRunnable):
    def __init__(self, index: int, task: ConversionTask, signals: _TaskSignals):
        super().__init__()
        self._index = index
        self._task = task
        self._signals = signals
        self.setAutoDelete(True)

    @Slot()
    def run(self):
        self._signals.started.emit(self._index)
        try:
            # Auto-rename if output exists
            self._task.output_path = auto_rename(self._task.output_path)

            converter = ConverterRegistry.find_converter(
                self._task.input_path.suffix.lower().lstrip("."),
                self._task.output_format,
            )
            result = converter.convert(
                self._task,
                progress_callback=lambda p: self._signals.progress.emit(self._index, p),
            )
            self._signals.completed.emit(self._index, str(result))
        except Exception as e:
            self._signals.failed.emit(self._index, str(e))


class ConversionWorker(QThread):
    """Manages parallel conversion of multiple files."""
    task_started = Signal(int)
    task_progress = Signal(int, float)
    task_completed = Signal(int, str)
    task_failed = Signal(int, str)
    queue_finished = Signal()

    def __init__(self, tasks: list[ConversionTask], max_workers: int = 4, parent=None):
        super().__init__(parent)
        self._tasks = tasks
        self._max_workers = max_workers
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        pool = QThreadPool()
        pool.setMaxThreadCount(self._max_workers)

        signals = _TaskSignals()
        signals.started.connect(self.task_started.emit)
        signals.progress.connect(self.task_progress.emit)
        signals.completed.connect(self.task_completed.emit)
        signals.failed.connect(self.task_failed.emit)

        for i, task in enumerate(self._tasks):
            if self._cancelled:
                break
            runnable = _ConversionRunnable(i, task, signals)
            pool.start(runnable)

        pool.waitForDone()
        self.queue_finished.emit()
