from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QScrollArea, QPlainTextEdit,
)

IMAGE_FORMATS = {"png", "jpg", "jpeg", "webp", "bmp", "tiff", "tif", "ico", "gif"}
TEXT_FORMATS = {"txt", "md", "html", "csv", "json", "xml", "yaml", "yml", "css", "js", "py"}


class PreviewDialog(QDialog):
    """Preview dialog for files before conversion."""

    def __init__(self, file_path: Path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Preview - {file_path.name}")
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout(self)
        ext = file_path.suffix.lower().lstrip(".")

        # File info
        size = file_path.stat().st_size
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"
        info = QLabel(f"{file_path.name}  |  {ext.upper()}  |  {size_str}")
        info.setStyleSheet("font-weight: bold; padding: 4px;")
        layout.addWidget(info)

        if ext in IMAGE_FORMATS:
            self._show_image(file_path, layout)
        elif ext == "pdf":
            self._show_pdf(file_path, layout)
        elif ext in TEXT_FORMATS:
            self._show_text(file_path, layout)
        else:
            label = QLabel("Preview not available for this file type.")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)

    def _show_image(self, path: Path, layout):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        label = QLabel()
        pixmap = QPixmap(str(path))
        if pixmap.width() > 600 or pixmap.height() > 500:
            pixmap = pixmap.scaled(600, 500, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(label)
        layout.addWidget(scroll, stretch=1)

        # Show dimensions
        orig = QPixmap(str(path))
        dim = QLabel(f"Dimensions: {orig.width()} x {orig.height()} px")
        layout.addWidget(dim)

    def _show_pdf(self, path: Path, layout):
        try:
            import fitz
            doc = fitz.open(str(path))
            page_count = len(doc)

            info = QLabel(f"Pages: {page_count}")
            layout.addWidget(info)

            # Show first page as image
            if page_count > 0:
                page = doc[0]
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                from PySide6.QtGui import QImage
                img = QImage(pix.samples, pix.width, pix.height, pix.stride,
                             QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(img)
                if pixmap.width() > 600:
                    pixmap = pixmap.scaled(600, 800, Qt.AspectRatioMode.KeepAspectRatio,
                                           Qt.TransformationMode.SmoothTransformation)
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                label = QLabel()
                label.setPixmap(pixmap)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                scroll.setWidget(label)
                layout.addWidget(scroll, stretch=1)
            doc.close()
        except ImportError:
            layout.addWidget(QLabel("PyMuPDF not installed - PDF preview unavailable"))

    def _show_text(self, path: Path, layout):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            text = "(Could not read file)"

        editor = QPlainTextEdit()
        editor.setPlainText(text[:10000])  # Limit preview size
        editor.setReadOnly(True)
        layout.addWidget(editor, stretch=1)

        if len(text) > 10000:
            layout.addWidget(QLabel(f"(Showing first 10,000 of {len(text)} characters)"))
