from pathlib import Path

from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
)

from pyconverter.gui.icons import icon


class FileDropWidget(QWidget):
    files_dropped = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(120)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._icon_label = QLabel()
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        from pyconverter.gui.icons import icon_pixmap
        self._icon_label.setPixmap(icon_pixmap("cloud_upload", "#6c7086", 48))
        layout.addWidget(self._icon_label)

        self._label = QLabel("Drop files here or click Browse")
        self._label.setObjectName("dropLabel")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._label)

        self._browse_btn = QPushButton()
        self._browse_btn.setIcon(icon("browse"))
        self._browse_btn.setIconSize(QSize(18, 18))
        self._browse_btn.setText(" Browse Files")
        self._browse_btn.setFixedWidth(160)
        self._browse_btn.setToolTip("Browse files to convert")
        self._browse_btn.clicked.connect(self._browse)
        layout.addWidget(self._browse_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setStyleSheet("""
            FileDropWidget {
                border: 2px dashed #45475a;
                border-radius: 16px;
            }
            FileDropWidget[dragOver="true"] {
                border-color: #89b4fa;
                background-color: rgba(137, 180, 250, 0.08);
            }
        """)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setProperty("dragOver", True)
            self.style().unpolish(self)
            self.style().polish(self)

    def dragLeaveEvent(self, event):
        self.setProperty("dragOver", False)
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event):
        self.setProperty("dragOver", False)
        self.style().unpolish(self)
        self.style().polish(self)

        paths = []
        for url in event.mimeData().urls():
            path = Path(url.toLocalFile())
            if path.is_file():
                paths.append(path)
        if paths:
            self.files_dropped.emit(paths)

    def _browse(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files to Convert", "", "All Files (*)"
        )
        if files:
            self.files_dropped.emit([Path(f) for f in files])
