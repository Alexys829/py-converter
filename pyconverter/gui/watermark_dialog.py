from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QSpinBox, QDoubleSpinBox, QFileDialog,
    QGroupBox, QMessageBox, QComboBox,
)


class WatermarkDialog(QDialog):
    """Dialog for adding watermark to images or PDFs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Watermark")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Input file
        input_group = QGroupBox("Input")
        input_layout = QHBoxLayout(input_group)
        self._input_label = QLabel("No file selected")
        input_layout.addWidget(self._input_label, stretch=1)
        input_btn = QPushButton("Select File...")
        input_btn.setToolTip("Select image or PDF to watermark")
        input_btn.clicked.connect(self._select_input)
        input_layout.addWidget(input_btn)
        layout.addWidget(input_group)

        # Watermark settings
        settings_group = QGroupBox("Watermark Settings")
        settings_layout = QVBoxLayout(settings_group)

        # Text
        text_row = QHBoxLayout()
        text_row.addWidget(QLabel("Text:"))
        self._text_input = QLineEdit()
        self._text_input.setPlaceholderText("Enter watermark text...")
        text_row.addWidget(self._text_input, stretch=1)
        settings_layout.addLayout(text_row)

        # Options row
        opts_row = QHBoxLayout()

        opts_row.addWidget(QLabel("Font Size:"))
        self._font_size_spin = QSpinBox()
        self._font_size_spin.setRange(10, 200)
        self._font_size_spin.setValue(50)
        opts_row.addWidget(self._font_size_spin)

        opts_row.addWidget(QLabel("Opacity:"))
        self._opacity_spin = QDoubleSpinBox()
        self._opacity_spin.setRange(0.05, 1.0)
        self._opacity_spin.setSingleStep(0.05)
        self._opacity_spin.setValue(0.3)
        opts_row.addWidget(self._opacity_spin)

        opts_row.addWidget(QLabel("Rotation:"))
        self._rotation_spin = QSpinBox()
        self._rotation_spin.setRange(-180, 180)
        self._rotation_spin.setValue(45)
        opts_row.addWidget(self._rotation_spin)

        settings_layout.addLayout(opts_row)

        # Position for images
        pos_row = QHBoxLayout()
        pos_row.addWidget(QLabel("Position (images):"))
        self._position_combo = QComboBox()
        self._position_combo.addItems(["center", "top-left", "top-right", "bottom-left", "bottom-right"])
        pos_row.addWidget(self._position_combo)
        pos_row.addStretch()
        settings_layout.addLayout(pos_row)

        layout.addWidget(settings_group)

        # Apply button
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        apply_btn = QPushButton("Apply Watermark")
        apply_btn.setToolTip("Apply watermark and save to new file")
        apply_btn.clicked.connect(self._apply)
        btn_row.addWidget(apply_btn)

        layout.addLayout(btn_row)

        self._input_path: Path | None = None

    def _select_input(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "",
            "Supported Files (*.pdf *.png *.jpg *.jpeg *.webp *.bmp *.tiff)"
        )
        if path:
            self._input_path = Path(path)
            self._input_label.setText(self._input_path.name)

    def _apply(self):
        if not self._input_path:
            QMessageBox.warning(self, "Warning", "Select a file first.")
            return

        text = self._text_input.text().strip()
        if not text:
            QMessageBox.warning(self, "Warning", "Enter watermark text.")
            return

        ext = self._input_path.suffix.lower()
        output_path = self._input_path.parent / f"{self._input_path.stem}_watermarked{ext}"

        try:
            if ext == ".pdf":
                self._watermark_pdf(output_path, text)
            elif ext in (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"):
                self._watermark_image(output_path, text)
            else:
                QMessageBox.warning(self, "Warning", f"Unsupported format: {ext}")
                return
            QMessageBox.information(self, "Done", f"Watermarked file saved to:\n{output_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply watermark:\n{e}")

    def _watermark_pdf(self, output_path: Path, text: str):
        from pyconverter.converters.pdf_tools import add_watermark
        add_watermark(
            self._input_path, output_path, text,
            opacity=self._opacity_spin.value(),
            font_size=self._font_size_spin.value(),
            rotation=self._rotation_spin.value(),
        )

    def _watermark_image(self, output_path: Path, text: str):
        from PIL import Image, ImageDraw, ImageFont

        img = Image.open(self._input_path).convert("RGBA")
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        font_size = self._font_size_spin.value()
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except (OSError, IOError):
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        position = self._position_combo.currentText()
        w, h = img.size
        padding = 20
        positions = {
            "center": ((w - text_w) // 2, (h - text_h) // 2),
            "top-left": (padding, padding),
            "top-right": (w - text_w - padding, padding),
            "bottom-left": (padding, h - text_h - padding),
            "bottom-right": (w - text_w - padding, h - text_h - padding),
        }
        pos = positions.get(position, positions["center"])

        alpha = int(self._opacity_spin.value() * 255)
        draw.text(pos, text, fill=(255, 255, 255, alpha), font=font)

        result = Image.alpha_composite(img, overlay).convert("RGB")
        result.save(output_path)
