import fitz
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QFileDialog, QSpinBox,
    QGroupBox, QMessageBox, QWidget, QTabWidget, QComboBox,
    QLineEdit, QCheckBox,
)

from pyconverter.gui.icons import icon


class PageThumbnail(QWidget):
    def __init__(self, pixmap: QPixmap, page_num: int, source: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        img_label = QLabel()
        img_label.setPixmap(pixmap.scaled(120, 160, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation))
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(img_label)

        text = f"Page {page_num + 1}"
        if source:
            text += f"\n({Path(source).name})"
        info_label = QLabel(text)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("font-size: 11px;")
        layout.addWidget(info_label)


def _page_to_pixmap(page: fitz.Page, dpi: int = 72) -> QPixmap:
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat)
    img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
    return QPixmap.fromImage(img)


# ─────────────────────────────────────────────
#  Tab 1: Page Editor
# ─────────────────────────────────────────────

class _PageEditorTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pages: list[dict] = []
        self._current_pdf: str | None = None

        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()

        open_btn = QPushButton(" Open PDF")
        open_btn.setIcon(icon("folder_open"))
        open_btn.setIconSize(QSize(18, 18))
        open_btn.setToolTip("Open a PDF file to edit")
        open_btn.clicked.connect(self._open_pdf)
        toolbar.addWidget(open_btn)

        add_btn = QPushButton(" Add Pages")
        add_btn.setObjectName("textIconButton")
        add_btn.setIcon(icon("add_file"))
        add_btn.setIconSize(QSize(18, 18))
        add_btn.setToolTip("Append pages from another PDF")
        add_btn.clicked.connect(self._add_pages_from_pdf)
        toolbar.addWidget(add_btn)

        toolbar.addStretch()

        remove_btn = QPushButton(" Remove")
        remove_btn.setObjectName("cancelButton")
        remove_btn.setIcon(icon("delete", "#1e1e2e"))
        remove_btn.setIconSize(QSize(18, 18))
        remove_btn.setToolTip("Remove selected pages")
        remove_btn.clicked.connect(self._remove_selected)
        toolbar.addWidget(remove_btn)

        layout.addLayout(toolbar)

        # Insert + Move controls
        ctrl = QHBoxLayout()

        ctrl.addWidget(QLabel("Insert at:"))
        self._insert_pos_spin = QSpinBox()
        self._insert_pos_spin.setMinimum(1)
        self._insert_pos_spin.setMaximum(1)
        ctrl.addWidget(self._insert_pos_spin)

        insert_btn = QPushButton(" Insert")
        insert_btn.setObjectName("textIconButton")
        insert_btn.setIcon(icon("add_file"))
        insert_btn.setIconSize(QSize(18, 18))
        insert_btn.setToolTip("Insert pages from another PDF at this position")
        insert_btn.clicked.connect(self._insert_pages_at_position)
        ctrl.addWidget(insert_btn)

        ctrl.addStretch()

        up_btn = QPushButton()
        up_btn.setObjectName("textIconButton")
        up_btn.setIcon(icon("move_up"))
        up_btn.setIconSize(QSize(20, 20))
        up_btn.setToolTip("Move selected page up")
        up_btn.clicked.connect(self._move_up)
        ctrl.addWidget(up_btn)

        down_btn = QPushButton()
        down_btn.setObjectName("textIconButton")
        down_btn.setIcon(icon("move_down"))
        down_btn.setIconSize(QSize(20, 20))
        down_btn.setToolTip("Move selected page down")
        down_btn.clicked.connect(self._move_down)
        ctrl.addWidget(down_btn)

        layout.addLayout(ctrl)

        # Page list
        self._page_list = QListWidget()
        self._page_list.setViewMode(QListWidget.ViewMode.IconMode)
        self._page_list.setIconSize(QSize(120, 160))
        self._page_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self._page_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self._page_list.setSpacing(8)
        layout.addWidget(self._page_list, stretch=1)

        # Bottom: info + save
        bottom = QHBoxLayout()
        self._info_label = QLabel("No PDF loaded")
        bottom.addWidget(self._info_label, stretch=1)

        save_btn = QPushButton(" Save")
        save_btn.setIcon(icon("convert", "#1e1e2e"))
        save_btn.setIconSize(QSize(18, 18))
        save_btn.setToolTip("Save changes to the current PDF")
        save_btn.clicked.connect(self._save_pdf)
        bottom.addWidget(save_btn)

        save_as_btn = QPushButton(" Save As")
        save_as_btn.setObjectName("textIconButton")
        save_as_btn.setIcon(icon("folder_open"))
        save_as_btn.setIconSize(QSize(18, 18))
        save_as_btn.setToolTip("Save as a new PDF file")
        save_as_btn.clicked.connect(self._save_pdf_as)
        bottom.addWidget(save_as_btn)

        layout.addLayout(bottom)

    def _open_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if not path:
            return
        self._current_pdf = path
        self._pages.clear()
        self._load_pages(path)
        self._refresh()

    def _load_pages(self, path: str, insert_at: int | None = None) -> int:
        doc = fitz.open(path)
        count = 0
        for i in range(len(doc)):
            entry = {"source": path, "page_num": i, "pixmap": _page_to_pixmap(doc[i])}
            if insert_at is not None:
                self._pages.insert(insert_at + count, entry)
            else:
                self._pages.append(entry)
            count += 1
        doc.close()
        return count

    def _refresh(self):
        self._page_list.clear()
        for i, pd in enumerate(self._pages):
            thumb = PageThumbnail(pd["pixmap"], i, pd["source"])
            item = QListWidgetItem()
            item.setSizeHint(thumb.sizeHint())
            self._page_list.addItem(item)
            self._page_list.setItemWidget(item, thumb)
        total = len(self._pages)
        self._insert_pos_spin.setMaximum(max(total + 1, 1))
        self._insert_pos_spin.setValue(total + 1)
        self._info_label.setText(f"{total} page(s)")

    def _add_pages_from_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Add Pages", "", "PDF Files (*.pdf)")
        if path:
            self._load_pages(path)
            self._refresh()

    def _insert_pages_at_position(self):
        path, _ = QFileDialog.getOpenFileName(self, "Insert Pages", "", "PDF Files (*.pdf)")
        if path:
            self._load_pages(path, insert_at=self._insert_pos_spin.value() - 1)
            self._refresh()

    def _remove_selected(self):
        indices = sorted([idx.row() for idx in self._page_list.selectedIndexes()], reverse=True)
        for idx in indices:
            if 0 <= idx < len(self._pages):
                self._pages.pop(idx)
        self._refresh()

    def _move_up(self):
        sel = self._page_list.selectedIndexes()
        if sel and (idx := sel[0].row()) > 0:
            self._pages[idx], self._pages[idx - 1] = self._pages[idx - 1], self._pages[idx]
            self._refresh()
            self._page_list.setCurrentRow(idx - 1)

    def _move_down(self):
        sel = self._page_list.selectedIndexes()
        if sel and (idx := sel[0].row()) < len(self._pages) - 1:
            self._pages[idx], self._pages[idx + 1] = self._pages[idx + 1], self._pages[idx]
            self._refresh()
            self._page_list.setCurrentRow(idx + 1)

    def _build_pdf(self, output_path: str):
        result = fitz.open()
        for pd in self._pages:
            src = fitz.open(pd["source"])
            result.insert_pdf(src, from_page=pd["page_num"], to_page=pd["page_num"])
            src.close()
        result.save(output_path)
        result.close()

    def _save_pdf(self):
        if not self._pages:
            QMessageBox.warning(self, "Warning", "No pages to save.")
            return
        if self._current_pdf:
            self._build_pdf(self._current_pdf)
            QMessageBox.information(self, "Saved", f"PDF saved to:\n{self._current_pdf}")
        else:
            self._save_pdf_as()

    def _save_pdf_as(self):
        if not self._pages:
            QMessageBox.warning(self, "Warning", "No pages to save.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF As", "", "PDF Files (*.pdf)")
        if not path:
            return
        if not path.endswith(".pdf"):
            path += ".pdf"
        self._build_pdf(path)
        self._current_pdf = path
        QMessageBox.information(self, "Saved", f"PDF saved to:\n{path}")


# ─────────────────────────────────────────────
#  Tab 2: Merge
# ─────────────────────────────────────────────

class _MergeTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Select multiple PDF files to merge into one."))

        # File list
        self._file_list = QListWidget()
        layout.addWidget(self._file_list, stretch=1)

        # Buttons
        btn_row = QHBoxLayout()

        add_btn = QPushButton(" Add PDFs")
        add_btn.setIcon(icon("add_file"))
        add_btn.setIconSize(QSize(18, 18))
        add_btn.setToolTip("Add PDF files to merge list")
        add_btn.clicked.connect(self._add_files)
        btn_row.addWidget(add_btn)

        up_btn = QPushButton()
        up_btn.setObjectName("textIconButton")
        up_btn.setIcon(icon("move_up"))
        up_btn.setIconSize(QSize(20, 20))
        up_btn.setToolTip("Move selected file up")
        up_btn.clicked.connect(self._move_up)
        btn_row.addWidget(up_btn)

        down_btn = QPushButton()
        down_btn.setObjectName("textIconButton")
        down_btn.setIcon(icon("move_down"))
        down_btn.setIconSize(QSize(20, 20))
        down_btn.setToolTip("Move selected file down")
        down_btn.clicked.connect(self._move_down)
        btn_row.addWidget(down_btn)

        remove_btn = QPushButton()
        remove_btn.setObjectName("textIconButton")
        remove_btn.setIcon(icon("delete"))
        remove_btn.setIconSize(QSize(18, 18))
        remove_btn.setToolTip("Remove selected file")
        remove_btn.clicked.connect(self._remove_selected)
        btn_row.addWidget(remove_btn)

        btn_row.addStretch()

        merge_btn = QPushButton(" Merge")
        merge_btn.setIcon(icon("convert", "#1e1e2e"))
        merge_btn.setIconSize(QSize(18, 18))
        merge_btn.setToolTip("Merge all PDFs into one file")
        merge_btn.clicked.connect(self._merge)
        btn_row.addWidget(merge_btn)

        layout.addLayout(btn_row)

        self._files: list[str] = []

    def _add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDFs", "", "PDF Files (*.pdf)")
        for f in files:
            if f not in self._files:
                self._files.append(f)
                self._file_list.addItem(Path(f).name)

    def _move_up(self):
        row = self._file_list.currentRow()
        if row > 0:
            self._files[row], self._files[row - 1] = self._files[row - 1], self._files[row]
            item = self._file_list.takeItem(row)
            self._file_list.insertItem(row - 1, item)
            self._file_list.setCurrentRow(row - 1)

    def _move_down(self):
        row = self._file_list.currentRow()
        if 0 <= row < len(self._files) - 1:
            self._files[row], self._files[row + 1] = self._files[row + 1], self._files[row]
            item = self._file_list.takeItem(row)
            self._file_list.insertItem(row + 1, item)
            self._file_list.setCurrentRow(row + 1)

    def _remove_selected(self):
        row = self._file_list.currentRow()
        if 0 <= row < len(self._files):
            self._files.pop(row)
            self._file_list.takeItem(row)

    def _merge(self):
        if len(self._files) < 2:
            QMessageBox.warning(self, "Warning", "Add at least 2 PDF files to merge.")
            return

        output, _ = QFileDialog.getSaveFileName(self, "Save Merged PDF", "", "PDF Files (*.pdf)")
        if not output:
            return
        if not output.endswith(".pdf"):
            output += ".pdf"

        try:
            result = fitz.open()
            for f in self._files:
                src = fitz.open(f)
                result.insert_pdf(src)
                src.close()
            result.save(output)
            result.close()
            QMessageBox.information(self, "Done", f"Merged {len(self._files)} PDFs into:\n{output}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Merge failed:\n{e}")


# ─────────────────────────────────────────────
#  Tab 3: Split
# ─────────────────────────────────────────────

class _SplitTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Split a PDF into individual pages or page ranges."))

        # Input file
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("PDF File:"))
        self._file_label = QLabel("No file selected")
        input_row.addWidget(self._file_label, stretch=1)

        browse_btn = QPushButton()
        browse_btn.setObjectName("textIconButton")
        browse_btn.setIcon(icon("folder_open"))
        browse_btn.setIconSize(QSize(18, 18))
        browse_btn.setToolTip("Select PDF to split")
        browse_btn.clicked.connect(self._browse_file)
        input_row.addWidget(browse_btn)
        layout.addLayout(input_row)

        # Info
        self._info_label = QLabel("")
        layout.addWidget(self._info_label)

        # Mode selection
        mode_group = QGroupBox("Split Mode")
        mode_layout = QVBoxLayout(mode_group)

        # Single pages
        single_row = QHBoxLayout()
        self._split_all_btn = QPushButton(" Split into single pages")
        self._split_all_btn.setIcon(icon("convert", "#1e1e2e"))
        self._split_all_btn.setIconSize(QSize(18, 18))
        self._split_all_btn.setToolTip("Save each page as a separate PDF")
        self._split_all_btn.clicked.connect(self._split_all)
        single_row.addWidget(self._split_all_btn)
        single_row.addStretch()
        mode_layout.addLayout(single_row)

        # Range
        range_row = QHBoxLayout()
        range_row.addWidget(QLabel("Extract pages:"))
        self._from_spin = QSpinBox()
        self._from_spin.setMinimum(1)
        self._from_spin.setMaximum(1)
        range_row.addWidget(self._from_spin)
        range_row.addWidget(QLabel("to"))
        self._to_spin = QSpinBox()
        self._to_spin.setMinimum(1)
        self._to_spin.setMaximum(1)
        range_row.addWidget(self._to_spin)

        extract_btn = QPushButton(" Extract")
        extract_btn.setIcon(icon("convert", "#1e1e2e"))
        extract_btn.setIconSize(QSize(18, 18))
        extract_btn.setToolTip("Extract selected page range to a new PDF")
        extract_btn.clicked.connect(self._extract_range)
        range_row.addWidget(extract_btn)
        range_row.addStretch()
        mode_layout.addLayout(range_row)

        layout.addWidget(mode_group)
        layout.addStretch()

        self._input_path: str | None = None
        self._page_count = 0

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if not path:
            return
        self._input_path = path
        self._file_label.setText(Path(path).name)

        doc = fitz.open(path)
        self._page_count = len(doc)
        doc.close()

        self._info_label.setText(f"{self._page_count} pages")
        self._from_spin.setMaximum(self._page_count)
        self._to_spin.setMaximum(self._page_count)
        self._to_spin.setValue(self._page_count)

    def _split_all(self):
        if not self._input_path:
            QMessageBox.warning(self, "Warning", "Select a PDF first.")
            return

        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir:
            return

        try:
            doc = fitz.open(self._input_path)
            stem = Path(self._input_path).stem
            for i in range(len(doc)):
                page_doc = fitz.open()
                page_doc.insert_pdf(doc, from_page=i, to_page=i)
                out = Path(output_dir) / f"{stem}_page_{i + 1}.pdf"
                page_doc.save(str(out))
                page_doc.close()
            doc.close()
            QMessageBox.information(self, "Done",
                                    f"Split into {self._page_count} files in:\n{output_dir}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Split failed:\n{e}")

    def _extract_range(self):
        if not self._input_path:
            QMessageBox.warning(self, "Warning", "Select a PDF first.")
            return

        from_page = self._from_spin.value() - 1
        to_page = self._to_spin.value() - 1

        if from_page > to_page:
            QMessageBox.warning(self, "Warning", "'From' must be <= 'To'.")
            return

        output, _ = QFileDialog.getSaveFileName(self, "Save Extracted Pages", "", "PDF Files (*.pdf)")
        if not output:
            return
        if not output.endswith(".pdf"):
            output += ".pdf"

        try:
            doc = fitz.open(self._input_path)
            result = fitz.open()
            result.insert_pdf(doc, from_page=from_page, to_page=to_page)
            result.save(output)
            result.close()
            doc.close()
            count = to_page - from_page + 1
            QMessageBox.information(self, "Done", f"Extracted {count} page(s) to:\n{output}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Extract failed:\n{e}")


# ─────────────────────────────────────────────
#  Main Dialog (unified)
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
#  Tab 4: Rotate
# ─────────────────────────────────────────────

class _RotateTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Rotate pages of a PDF file."))

        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("PDF File:"))
        self._file_label = QLabel("No file selected")
        input_row.addWidget(self._file_label, stretch=1)
        browse_btn = QPushButton()
        browse_btn.setObjectName("textIconButton")
        browse_btn.setIcon(icon("folder_open"))
        browse_btn.setIconSize(QSize(18, 18))
        browse_btn.setToolTip("Select PDF")
        browse_btn.clicked.connect(self._browse)
        input_row.addWidget(browse_btn)
        layout.addLayout(input_row)

        self._info_label = QLabel("")
        layout.addWidget(self._info_label)

        opts = QGroupBox("Rotation")
        opts_layout = QVBoxLayout(opts)

        angle_row = QHBoxLayout()
        angle_row.addWidget(QLabel("Angle:"))
        self._angle_combo = QComboBox()
        self._angle_combo.addItems(["90", "180", "270"])
        angle_row.addWidget(self._angle_combo)
        angle_row.addStretch()
        opts_layout.addLayout(angle_row)

        pages_row = QHBoxLayout()
        pages_row.addWidget(QLabel("Pages:"))
        self._pages_combo = QComboBox()
        self._pages_combo.addItems(["All pages", "Only odd pages", "Only even pages", "Custom range"])
        pages_row.addWidget(self._pages_combo)
        self._range_input = QLineEdit()
        self._range_input.setPlaceholderText("e.g. 1,3,5-8")
        self._range_input.setEnabled(False)
        self._pages_combo.currentTextChanged.connect(
            lambda t: self._range_input.setEnabled(t == "Custom range"))
        pages_row.addWidget(self._range_input)
        opts_layout.addLayout(pages_row)

        layout.addWidget(opts)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        rotate_btn = QPushButton(" Rotate & Save")
        rotate_btn.setIcon(icon("convert", "#1e1e2e"))
        rotate_btn.setIconSize(QSize(18, 18))
        rotate_btn.setToolTip("Rotate pages and save")
        rotate_btn.clicked.connect(self._rotate)
        btn_row.addWidget(rotate_btn)
        layout.addLayout(btn_row)
        layout.addStretch()

        self._input_path: str | None = None
        self._page_count = 0

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if not path:
            return
        self._input_path = path
        self._file_label.setText(Path(path).name)
        doc = fitz.open(path)
        self._page_count = len(doc)
        doc.close()
        self._info_label.setText(f"{self._page_count} pages")

    def _get_page_indices(self) -> list[int]:
        mode = self._pages_combo.currentText()
        if mode == "All pages":
            return list(range(self._page_count))
        elif mode == "Only odd pages":
            return list(range(0, self._page_count, 2))
        elif mode == "Only even pages":
            return list(range(1, self._page_count, 2))
        else:
            indices = []
            for part in self._range_input.text().split(","):
                part = part.strip()
                if "-" in part:
                    a, b = part.split("-", 1)
                    indices.extend(range(int(a) - 1, int(b)))
                elif part.isdigit():
                    indices.append(int(part) - 1)
            return [i for i in indices if 0 <= i < self._page_count]

    def _rotate(self):
        if not self._input_path:
            QMessageBox.warning(self, "Warning", "Select a PDF first.")
            return
        output, _ = QFileDialog.getSaveFileName(self, "Save Rotated PDF", "", "PDF Files (*.pdf)")
        if not output:
            return
        if not output.endswith(".pdf"):
            output += ".pdf"
        try:
            angle = int(self._angle_combo.currentText())
            doc = fitz.open(self._input_path)
            for idx in self._get_page_indices():
                doc[idx].set_rotation((doc[idx].rotation + angle) % 360)
            doc.save(output)
            doc.close()
            QMessageBox.information(self, "Done", f"Rotated PDF saved to:\n{output}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Rotation failed:\n{e}")


# ─────────────────────────────────────────────
#  Tab 5: Extract Images
# ─────────────────────────────────────────────

class _ExtractImagesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Extract all images from a PDF file."))

        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("PDF File:"))
        self._file_label = QLabel("No file selected")
        input_row.addWidget(self._file_label, stretch=1)
        browse_btn = QPushButton()
        browse_btn.setObjectName("textIconButton")
        browse_btn.setIcon(icon("folder_open"))
        browse_btn.setIconSize(QSize(18, 18))
        browse_btn.setToolTip("Select PDF")
        browse_btn.clicked.connect(self._browse)
        input_row.addWidget(browse_btn)
        layout.addLayout(input_row)

        self._info_label = QLabel("")
        layout.addWidget(self._info_label)

        fmt_row = QHBoxLayout()
        fmt_row.addWidget(QLabel("Save as:"))
        self._format_combo = QComboBox()
        self._format_combo.addItems(["png", "jpg"])
        fmt_row.addWidget(self._format_combo)
        fmt_row.addStretch()
        layout.addLayout(fmt_row)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        extract_btn = QPushButton(" Extract Images")
        extract_btn.setIcon(icon("convert", "#1e1e2e"))
        extract_btn.setIconSize(QSize(18, 18))
        extract_btn.setToolTip("Extract all images to a folder")
        extract_btn.clicked.connect(self._extract)
        btn_row.addWidget(extract_btn)
        layout.addLayout(btn_row)
        layout.addStretch()

        self._input_path: str | None = None

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if not path:
            return
        self._input_path = path
        self._file_label.setText(Path(path).name)
        doc = fitz.open(path)
        img_count = sum(len(page.get_images(full=True)) for page in doc)
        doc.close()
        self._info_label.setText(f"Found {img_count} image(s)")

    def _extract(self):
        if not self._input_path:
            QMessageBox.warning(self, "Warning", "Select a PDF first.")
            return
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir:
            return
        try:
            doc = fitz.open(self._input_path)
            fmt = self._format_combo.currentText()
            count = 0
            for page_num, page in enumerate(doc):
                for img_idx, img_info in enumerate(page.get_images(full=True)):
                    xref = img_info[0]
                    pix = fitz.Pixmap(doc, xref)
                    if pix.n - pix.alpha > 3:
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    out = Path(output_dir) / f"page{page_num + 1}_img{img_idx + 1}.{fmt}"
                    pix.save(str(out))
                    count += 1
            doc.close()
            QMessageBox.information(self, "Done", f"Extracted {count} image(s) to:\n{output_dir}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Extraction failed:\n{e}")


# ─────────────────────────────────────────────
#  Tab 6: Images to PDF
# ─────────────────────────────────────────────

class _ImagesToPdfTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Combine multiple images into a single PDF."))

        self._file_list = QListWidget()
        layout.addWidget(self._file_list, stretch=1)

        btn_row = QHBoxLayout()
        add_btn = QPushButton(" Add Images")
        add_btn.setIcon(icon("add_file"))
        add_btn.setIconSize(QSize(18, 18))
        add_btn.setToolTip("Add image files")
        add_btn.clicked.connect(self._add_images)
        btn_row.addWidget(add_btn)

        up_btn = QPushButton()
        up_btn.setObjectName("textIconButton")
        up_btn.setIcon(icon("move_up"))
        up_btn.setIconSize(QSize(20, 20))
        up_btn.setToolTip("Move up")
        up_btn.clicked.connect(self._move_up)
        btn_row.addWidget(up_btn)

        down_btn = QPushButton()
        down_btn.setObjectName("textIconButton")
        down_btn.setIcon(icon("move_down"))
        down_btn.setIconSize(QSize(20, 20))
        down_btn.setToolTip("Move down")
        down_btn.clicked.connect(self._move_down)
        btn_row.addWidget(down_btn)

        remove_btn = QPushButton()
        remove_btn.setObjectName("textIconButton")
        remove_btn.setIcon(icon("delete"))
        remove_btn.setIconSize(QSize(18, 18))
        remove_btn.setToolTip("Remove selected")
        remove_btn.clicked.connect(self._remove)
        btn_row.addWidget(remove_btn)

        btn_row.addStretch()

        create_btn = QPushButton(" Create PDF")
        create_btn.setIcon(icon("convert", "#1e1e2e"))
        create_btn.setIconSize(QSize(18, 18))
        create_btn.setToolTip("Create PDF from images")
        create_btn.clicked.connect(self._create_pdf)
        btn_row.addWidget(create_btn)
        layout.addLayout(btn_row)

        self._files: list[str] = []

    def _add_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.webp *.gif)")
        for f in files:
            if f not in self._files:
                self._files.append(f)
                self._file_list.addItem(Path(f).name)

    def _move_up(self):
        row = self._file_list.currentRow()
        if row > 0:
            self._files[row], self._files[row - 1] = self._files[row - 1], self._files[row]
            item = self._file_list.takeItem(row)
            self._file_list.insertItem(row - 1, item)
            self._file_list.setCurrentRow(row - 1)

    def _move_down(self):
        row = self._file_list.currentRow()
        if 0 <= row < len(self._files) - 1:
            self._files[row], self._files[row + 1] = self._files[row + 1], self._files[row]
            item = self._file_list.takeItem(row)
            self._file_list.insertItem(row + 1, item)
            self._file_list.setCurrentRow(row + 1)

    def _remove(self):
        row = self._file_list.currentRow()
        if 0 <= row < len(self._files):
            self._files.pop(row)
            self._file_list.takeItem(row)

    def _create_pdf(self):
        if not self._files:
            QMessageBox.warning(self, "Warning", "Add images first.")
            return
        output, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if not output:
            return
        if not output.endswith(".pdf"):
            output += ".pdf"
        try:
            doc = fitz.open()
            for img_path in self._files:
                img_doc = fitz.open(img_path)
                pdfbytes = img_doc.convert_to_pdf()
                img_pdf = fitz.open("pdf", pdfbytes)
                doc.insert_pdf(img_pdf)
                img_doc.close()
                img_pdf.close()
            doc.save(output)
            doc.close()
            QMessageBox.information(self, "Done",
                                    f"Created PDF with {len(self._files)} page(s):\n{output}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed:\n{e}")


# ─────────────────────────────────────────────
#  Tab 7: Compress
# ─────────────────────────────────────────────

class _CompressTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Compress a PDF to reduce file size."))

        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("PDF File:"))
        self._file_label = QLabel("No file selected")
        input_row.addWidget(self._file_label, stretch=1)
        self._size_label = QLabel("")
        input_row.addWidget(self._size_label)
        browse_btn = QPushButton()
        browse_btn.setObjectName("textIconButton")
        browse_btn.setIcon(icon("folder_open"))
        browse_btn.setIconSize(QSize(18, 18))
        browse_btn.setToolTip("Select PDF")
        browse_btn.clicked.connect(self._browse)
        input_row.addWidget(browse_btn)
        layout.addLayout(input_row)

        opts = QGroupBox("Compression Options")
        opts_layout = QVBoxLayout(opts)

        q_row = QHBoxLayout()
        q_row.addWidget(QLabel("Image quality:"))
        self._quality_spin = QSpinBox()
        self._quality_spin.setRange(10, 100)
        self._quality_spin.setValue(60)
        self._quality_spin.setToolTip("Lower = smaller file, less quality")
        q_row.addWidget(self._quality_spin)
        q_row.addWidget(QLabel("%"))
        q_row.addStretch()
        opts_layout.addLayout(q_row)

        self._garbage_check = QCheckBox("Clean unused objects (garbage collection)")
        self._garbage_check.setChecked(True)
        opts_layout.addWidget(self._garbage_check)

        self._deflate_check = QCheckBox("Deflate streams")
        self._deflate_check.setChecked(True)
        opts_layout.addWidget(self._deflate_check)

        layout.addWidget(opts)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        compress_btn = QPushButton(" Compress & Save")
        compress_btn.setIcon(icon("convert", "#1e1e2e"))
        compress_btn.setIconSize(QSize(18, 18))
        compress_btn.setToolTip("Compress and save PDF")
        compress_btn.clicked.connect(self._compress)
        btn_row.addWidget(compress_btn)
        layout.addLayout(btn_row)

        self._result_label = QLabel("")
        layout.addWidget(self._result_label)
        layout.addStretch()

        self._input_path: str | None = None

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if not path:
            return
        self._input_path = path
        self._file_label.setText(Path(path).name)
        size = Path(path).stat().st_size
        self._size_label.setText(f"({size / 1024:.0f} KB)")

    def _compress(self):
        if not self._input_path:
            QMessageBox.warning(self, "Warning", "Select a PDF first.")
            return
        output, _ = QFileDialog.getSaveFileName(self, "Save Compressed PDF", "", "PDF Files (*.pdf)")
        if not output:
            return
        if not output.endswith(".pdf"):
            output += ".pdf"
        try:
            doc = fitz.open(self._input_path)
            original_size = Path(self._input_path).stat().st_size

            # Recompress images
            quality = self._quality_spin.value()
            for page in doc:
                for img_info in page.get_images(full=True):
                    xref = img_info[0]
                    try:
                        pix = fitz.Pixmap(doc, xref)
                        if pix.n - pix.alpha > 3:
                            pix = fitz.Pixmap(fitz.csRGB, pix)
                        img_bytes = pix.tobytes(output="jpeg", jpg_quality=quality)
                        doc.update_stream(xref, img_bytes)
                    except Exception:
                        continue

            garbage = 4 if self._garbage_check.isChecked() else 0
            deflate = self._deflate_check.isChecked()
            doc.save(output, garbage=garbage, deflate=deflate, clean=True)
            doc.close()

            new_size = Path(output).stat().st_size
            ratio = (1 - new_size / original_size) * 100 if original_size > 0 else 0
            self._result_label.setText(
                f"Original: {original_size / 1024:.0f} KB  |  "
                f"Compressed: {new_size / 1024:.0f} KB  |  "
                f"Saved: {ratio:.1f}%"
            )
            QMessageBox.information(self, "Done", f"Compressed PDF saved to:\n{output}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Compression failed:\n{e}")


# ─────────────────────────────────────────────
#  Tab 8: Password
# ─────────────────────────────────────────────

class _PasswordTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Add or remove password protection from a PDF."))

        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("PDF File:"))
        self._file_label = QLabel("No file selected")
        input_row.addWidget(self._file_label, stretch=1)
        browse_btn = QPushButton()
        browse_btn.setObjectName("textIconButton")
        browse_btn.setIcon(icon("folder_open"))
        browse_btn.setIconSize(QSize(18, 18))
        browse_btn.setToolTip("Select PDF")
        browse_btn.clicked.connect(self._browse)
        input_row.addWidget(browse_btn)
        layout.addLayout(input_row)

        # Existing password (for encrypted PDFs)
        existing_row = QHBoxLayout()
        existing_row.addWidget(QLabel("Current password (if any):"))
        self._existing_pw = QLineEdit()
        self._existing_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self._existing_pw.setPlaceholderText("Leave empty if not encrypted")
        existing_row.addWidget(self._existing_pw)
        layout.addLayout(existing_row)

        # Add password group
        add_group = QGroupBox("Encrypt PDF")
        add_layout = QVBoxLayout(add_group)
        pw_row = QHBoxLayout()
        pw_row.addWidget(QLabel("New password:"))
        self._new_pw = QLineEdit()
        self._new_pw.setEchoMode(QLineEdit.EchoMode.Password)
        pw_row.addWidget(self._new_pw)
        add_layout.addLayout(pw_row)

        encrypt_btn = QPushButton(" Encrypt & Save")
        encrypt_btn.setIcon(icon("convert", "#1e1e2e"))
        encrypt_btn.setIconSize(QSize(18, 18))
        encrypt_btn.setToolTip("Encrypt PDF with password")
        encrypt_btn.clicked.connect(self._encrypt)
        add_layout.addWidget(encrypt_btn)
        layout.addWidget(add_group)

        # Remove password group
        remove_group = QGroupBox("Decrypt PDF")
        remove_layout = QVBoxLayout(remove_group)
        remove_layout.addWidget(QLabel("Remove encryption (requires current password above)."))
        decrypt_btn = QPushButton(" Decrypt & Save")
        decrypt_btn.setIcon(icon("convert", "#1e1e2e"))
        decrypt_btn.setIconSize(QSize(18, 18))
        decrypt_btn.setToolTip("Remove password protection")
        decrypt_btn.clicked.connect(self._decrypt)
        remove_layout.addWidget(decrypt_btn)
        layout.addWidget(remove_group)

        layout.addStretch()
        self._input_path: str | None = None

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if path:
            self._input_path = path
            self._file_label.setText(Path(path).name)

    def _encrypt(self):
        if not self._input_path:
            QMessageBox.warning(self, "Warning", "Select a PDF first.")
            return
        pw = self._new_pw.text()
        if not pw:
            QMessageBox.warning(self, "Warning", "Enter a password.")
            return
        output, _ = QFileDialog.getSaveFileName(self, "Save Encrypted PDF", "", "PDF Files (*.pdf)")
        if not output:
            return
        if not output.endswith(".pdf"):
            output += ".pdf"
        try:
            existing = self._existing_pw.text() or None
            doc = fitz.open(self._input_path)
            if existing and doc.is_encrypted:
                doc.authenticate(existing)
            perm = fitz.PDF_PERM_ACCESSIBILITY | fitz.PDF_PERM_PRINT
            doc.save(output, encryption=fitz.PDF_ENCRYPT_AES_256,
                     user_pw=pw, owner_pw=pw, permissions=perm)
            doc.close()
            QMessageBox.information(self, "Done", f"Encrypted PDF saved to:\n{output}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Encryption failed:\n{e}")

    def _decrypt(self):
        if not self._input_path:
            QMessageBox.warning(self, "Warning", "Select a PDF first.")
            return
        existing = self._existing_pw.text()
        if not existing:
            QMessageBox.warning(self, "Warning", "Enter the current password.")
            return
        output, _ = QFileDialog.getSaveFileName(self, "Save Decrypted PDF", "", "PDF Files (*.pdf)")
        if not output:
            return
        if not output.endswith(".pdf"):
            output += ".pdf"
        try:
            doc = fitz.open(self._input_path)
            if not doc.authenticate(existing):
                QMessageBox.critical(self, "Error", "Wrong password.")
                doc.close()
                return
            doc.save(output, encryption=fitz.PDF_ENCRYPT_NONE)
            doc.close()
            QMessageBox.information(self, "Done", f"Decrypted PDF saved to:\n{output}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Decryption failed:\n{e}")


# ─────────────────────────────────────────────
#  Tab 9: Page Numbers
# ─────────────────────────────────────────────

class _PageNumbersTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Add page numbers to a PDF."))

        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("PDF File:"))
        self._file_label = QLabel("No file selected")
        input_row.addWidget(self._file_label, stretch=1)
        browse_btn = QPushButton()
        browse_btn.setObjectName("textIconButton")
        browse_btn.setIcon(icon("folder_open"))
        browse_btn.setIconSize(QSize(18, 18))
        browse_btn.setToolTip("Select PDF")
        browse_btn.clicked.connect(self._browse)
        input_row.addWidget(browse_btn)
        layout.addLayout(input_row)

        opts = QGroupBox("Options")
        opts_layout = QVBoxLayout(opts)

        pos_row = QHBoxLayout()
        pos_row.addWidget(QLabel("Position:"))
        self._pos_combo = QComboBox()
        self._pos_combo.addItems(["Bottom center", "Bottom right", "Bottom left",
                                   "Top center", "Top right", "Top left"])
        pos_row.addWidget(self._pos_combo)
        pos_row.addStretch()
        opts_layout.addLayout(pos_row)

        fmt_row = QHBoxLayout()
        fmt_row.addWidget(QLabel("Format:"))
        self._fmt_combo = QComboBox()
        self._fmt_combo.addItems(["1", "Page 1", "- 1 -", "1 / {total}", "Page 1 of {total}"])
        fmt_row.addWidget(self._fmt_combo)
        fmt_row.addStretch()

        fmt_row.addWidget(QLabel("Font size:"))
        self._size_spin = QSpinBox()
        self._size_spin.setRange(6, 36)
        self._size_spin.setValue(10)
        fmt_row.addWidget(self._size_spin)
        opts_layout.addLayout(fmt_row)

        start_row = QHBoxLayout()
        start_row.addWidget(QLabel("Start from page:"))
        self._start_spin = QSpinBox()
        self._start_spin.setMinimum(1)
        self._start_spin.setValue(1)
        start_row.addWidget(self._start_spin)
        start_row.addStretch()
        opts_layout.addLayout(start_row)

        layout.addWidget(opts)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        apply_btn = QPushButton(" Add Page Numbers")
        apply_btn.setIcon(icon("convert", "#1e1e2e"))
        apply_btn.setIconSize(QSize(18, 18))
        apply_btn.setToolTip("Add page numbers and save")
        apply_btn.clicked.connect(self._apply)
        btn_row.addWidget(apply_btn)
        layout.addLayout(btn_row)
        layout.addStretch()

        self._input_path: str | None = None

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if path:
            self._input_path = path
            self._file_label.setText(Path(path).name)

    def _apply(self):
        if not self._input_path:
            QMessageBox.warning(self, "Warning", "Select a PDF first.")
            return
        output, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if not output:
            return
        if not output.endswith(".pdf"):
            output += ".pdf"
        try:
            doc = fitz.open(self._input_path)
            total = len(doc)
            font_size = self._size_spin.value()
            start_page = self._start_spin.value() - 1
            fmt_template = self._fmt_combo.currentText()
            pos_name = self._pos_combo.currentText()

            for i in range(start_page, total):
                page = doc[i]
                rect = page.rect
                num = i - start_page + 1
                text = fmt_template.replace("1", str(num)).replace("{total}", str(total - start_page))

                # Calculate position
                if "Bottom" in pos_name:
                    y = rect.height - 30
                else:
                    y = 20 + font_size
                if "center" in pos_name:
                    x = rect.width / 2
                    align = fitz.TEXT_ALIGN_CENTER
                elif "right" in pos_name:
                    x = rect.width - 40
                    align = fitz.TEXT_ALIGN_RIGHT
                else:
                    x = 40
                    align = fitz.TEXT_ALIGN_LEFT

                tw = fitz.TextWriter(page.rect)
                tw.append((x, y), text, fontsize=font_size)
                tw.write_text(page)

            doc.save(output)
            doc.close()
            QMessageBox.information(self, "Done", f"Page numbers added:\n{output}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed:\n{e}")


# ─────────────────────────────────────────────
#  Main Dialog (unified)
# ─────────────────────────────────────────────

class PDFEditorDialog(QDialog):
    pdf_saved = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PDF Tools")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)

        tabs = QTabWidget()
        tabs.addTab(_PageEditorTab(), "Editor")
        tabs.addTab(_MergeTab(), "Merge")
        tabs.addTab(_SplitTab(), "Split")
        tabs.addTab(_RotateTab(), "Rotate")
        tabs.addTab(_ExtractImagesTab(), "Images")
        tabs.addTab(_ImagesToPdfTab(), "IMG to PDF")
        tabs.addTab(_CompressTab(), "Compress")
        tabs.addTab(_PasswordTab(), "Password")
        tabs.addTab(_PageNumbersTab(), "Page Numbers")
        layout.addWidget(tabs)
