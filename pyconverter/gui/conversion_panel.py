from PySide6.QtCore import Signal, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QLineEdit, QGroupBox,
    QPushButton, QFileDialog,
)

from pyconverter.core.base_converter import ConversionOption
from pyconverter.core.registry import ConverterRegistry
from pyconverter.gui.icons import icon


class ConversionPanel(QWidget):
    convert_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._input_format: str | None = None
        self._option_widgets: dict[str, QWidget] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Format selection row
        fmt_layout = QHBoxLayout()
        fmt_layout.addWidget(QLabel("Output Format:"))

        self._format_combo = QComboBox()
        self._format_combo.setMinimumWidth(120)
        self._format_combo.currentTextChanged.connect(self._on_format_changed)
        fmt_layout.addWidget(self._format_combo)

        fmt_layout.addSpacing(20)
        fmt_layout.addWidget(QLabel("Output Dir:"))

        self._output_dir_label = QLabel("Same as input")
        self._output_dir_label.setMinimumWidth(150)
        fmt_layout.addWidget(self._output_dir_label, stretch=1)

        self._browse_dir_btn = QPushButton()
        self._browse_dir_btn.setObjectName("textIconButton")
        self._browse_dir_btn.setIcon(icon("folder_open"))
        self._browse_dir_btn.setIconSize(QSize(18, 18))
        self._browse_dir_btn.setToolTip("Change output directory")
        self._browse_dir_btn.clicked.connect(self._browse_output_dir)
        fmt_layout.addWidget(self._browse_dir_btn)

        layout.addLayout(fmt_layout)

        # Options group
        self._options_group = QGroupBox("Conversion Options")
        self._options_layout = QVBoxLayout(self._options_group)
        layout.addWidget(self._options_group)

        self._output_dir: str | None = None

    @property
    def output_dir(self) -> str | None:
        return self._output_dir

    @property
    def selected_format(self) -> str:
        return self._format_combo.currentText()

    def set_input_format(self, fmt: str) -> None:
        self._input_format = fmt.lower().lstrip(".")
        self._format_combo.blockSignals(True)
        self._format_combo.clear()

        # Handle format aliases (jpg/jpeg, tif/tiff, yml/yaml)
        aliases = {
            "jpg": ["jpg", "jpeg"], "jpeg": ["jpg", "jpeg"],
            "tif": ["tif", "tiff"], "tiff": ["tif", "tiff"],
            "yml": ["yml", "yaml"], "yaml": ["yml", "yaml"],
        }
        input_variants = aliases.get(self._input_format, [self._input_format])

        all_outputs: set[str] = set()
        for variant in input_variants:
            all_outputs.update(ConverterRegistry.get_output_formats(variant))

        # Remove input format and its aliases from output list
        exclude = set(input_variants)
        formats = sorted(f for f in all_outputs if f not in exclude)

        self._format_combo.addItems(formats)
        self._format_combo.blockSignals(False)
        if formats:
            self._on_format_changed(formats[0])

    def _on_format_changed(self, output_format: str) -> None:
        if not self._input_format or not output_format:
            return

        # Clear previous options
        self._clear_options()

        try:
            converter = ConverterRegistry.find_converter(self._input_format, output_format)
        except Exception:
            return

        options = converter.get_options(self._input_format, output_format)
        for opt in options:
            widget = self._create_option_widget(opt)
            if widget:
                row = QHBoxLayout()
                row.addWidget(QLabel(opt.label))
                row.addWidget(widget)
                self._options_layout.addLayout(row)
                self._option_widgets[opt.name] = widget

    def _create_option_widget(self, opt: ConversionOption) -> QWidget | None:
        if opt.type == "int":
            w = QSpinBox()
            w.setValue(int(opt.default))
            if opt.min_val is not None:
                w.setMinimum(int(opt.min_val))
            if opt.max_val is not None:
                w.setMaximum(int(opt.max_val))
            return w
        elif opt.type == "float":
            w = QDoubleSpinBox()
            w.setValue(float(opt.default))
            if opt.min_val is not None:
                w.setMinimum(opt.min_val)
            if opt.max_val is not None:
                w.setMaximum(opt.max_val)
            return w
        elif opt.type == "bool":
            w = QCheckBox()
            w.setChecked(bool(opt.default))
            return w
        elif opt.type == "choice":
            w = QComboBox()
            if opt.choices:
                w.addItems([str(c) for c in opt.choices])
            if opt.default:
                w.setCurrentText(str(opt.default))
            return w
        elif opt.type == "str":
            w = QLineEdit()
            w.setText(str(opt.default) if opt.default else "")
            return w
        return None

    def get_options(self) -> dict:
        result = {}
        for name, widget in self._option_widgets.items():
            if isinstance(widget, QSpinBox):
                result[name] = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                result[name] = widget.value()
            elif isinstance(widget, QCheckBox):
                result[name] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                result[name] = widget.currentText()
            elif isinstance(widget, QLineEdit):
                result[name] = widget.text()
        return result

    def _clear_options(self):
        self._option_widgets.clear()
        while self._options_layout.count():
            item = self._options_layout.takeAt(0)
            if item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
            elif item.widget():
                item.widget().deleteLater()

    def _browse_output_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if d:
            self._output_dir = d
            # Show last part of path
            display = d if len(d) < 40 else "..." + d[-37:]
            self._output_dir_label.setText(display)
