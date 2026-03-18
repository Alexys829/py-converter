from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar


class OverallProgressWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._label = QLabel("Overall Progress:")
        layout.addWidget(self._label)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        layout.addWidget(self._progress, stretch=1)

        self._count_label = QLabel("0 / 0")
        self._count_label.setFixedWidth(60)
        layout.addWidget(self._count_label)

    def update_progress(self, completed: int, total: int):
        if total > 0:
            self._progress.setValue(int((completed / total) * 100))
        else:
            self._progress.setValue(0)
        self._count_label.setText(f"{completed} / {total}")

    def reset(self):
        self._progress.setValue(0)
        self._count_label.setText("0 / 0")
