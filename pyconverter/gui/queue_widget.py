from pathlib import Path

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QProgressBar, QPushButton,
)

from pyconverter.gui.icons import icon


class QueueItemWidget(QWidget):
    remove_clicked = Signal(int)

    def __init__(self, file_path: Path, index: int, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self._index = index
        self.setMinimumHeight(36)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)

        self._name_label = QLabel(file_path.name)
        self._name_label.setMinimumWidth(200)
        layout.addWidget(self._name_label)

        self._status_label = QLabel("Pending")
        self._status_label.setFixedWidth(80)
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._status_label)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setFixedWidth(150)
        layout.addWidget(self._progress)

        self._remove_btn = QPushButton()
        self._remove_btn.setObjectName("dangerIconButton")
        self._remove_btn.setIcon(icon("close", "#f38ba8", 16))
        self._remove_btn.setIconSize(QSize(16, 16))
        self._remove_btn.setToolTip("Remove")
        self._remove_btn.clicked.connect(lambda: self.remove_clicked.emit(self._index))
        layout.addWidget(self._remove_btn)

    def set_status(self, status: str):
        self._status_label.setText(status)

    def set_progress(self, value: float):
        self._progress.setValue(int(value * 100))


class QueueWidget(QWidget):
    preview_requested = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items: list[QueueItemWidget] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QHBoxLayout()
        header.addWidget(QLabel("Conversion Queue"))
        header.addStretch()

        self._preview_btn = QPushButton()
        self._preview_btn.setObjectName("textIconButton")
        self._preview_btn.setIcon(icon("preview"))
        self._preview_btn.setIconSize(QSize(18, 18))
        self._preview_btn.setToolTip("Preview selected file")
        self._preview_btn.clicked.connect(self._on_preview)
        header.addWidget(self._preview_btn)

        self._remove_sel_btn = QPushButton()
        self._remove_sel_btn.setObjectName("textIconButton")
        self._remove_sel_btn.setIcon(icon("delete"))
        self._remove_sel_btn.setIconSize(QSize(18, 18))
        self._remove_sel_btn.setToolTip("Remove selected")
        self._remove_sel_btn.clicked.connect(self._remove_selected)
        header.addWidget(self._remove_sel_btn)

        self._clear_btn = QPushButton()
        self._clear_btn.setObjectName("textIconButton")
        self._clear_btn.setIcon(icon("clear"))
        self._clear_btn.setIconSize(QSize(18, 18))
        self._clear_btn.setToolTip("Clear queue")
        self._clear_btn.clicked.connect(self.clear_queue)
        header.addWidget(self._clear_btn)

        layout.addLayout(header)

        self._list = QListWidget()
        layout.addWidget(self._list)

    def add_file(self, file_path: Path) -> int:
        index = len(self._items)
        item_widget = QueueItemWidget(file_path, index)
        item_widget.remove_clicked.connect(self._remove_at_index)
        self._items.append(item_widget)

        list_item = QListWidgetItem()
        hint = item_widget.sizeHint()
        list_item.setSizeHint(QSize(hint.width(), max(hint.height(), 40)))
        self._list.addItem(list_item)
        self._list.setItemWidget(list_item, item_widget)

        return index

    def set_item_status(self, index: int, status: str):
        if 0 <= index < len(self._items):
            self._items[index].set_status(status)

    def set_item_progress(self, index: int, progress: float):
        if 0 <= index < len(self._items):
            self._items[index].set_progress(progress)

    def clear_queue(self):
        self._items.clear()
        self._list.clear()

    def count(self) -> int:
        return len(self._items)

    def get_file_paths(self) -> list[Path]:
        return [item.file_path for item in self._items]

    def _remove_at_index(self, index: int):
        if 0 <= index < len(self._items):
            self._items.pop(index)
            self._list.takeItem(index)
            for i, item in enumerate(self._items):
                item._index = i

    def _remove_selected(self):
        selected = self._list.selectedIndexes()
        if not selected:
            return
        indices = sorted([idx.row() for idx in selected], reverse=True)
        for idx in indices:
            self._remove_at_index(idx)

    def _on_preview(self):
        current_row = self._list.currentRow()
        if 0 <= current_row < len(self._items):
            self.preview_requested.emit(self._items[current_row].file_path)
