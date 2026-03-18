from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

DARK_STYLE = """
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: "Segoe UI", "Roboto", "Noto Sans", sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #1e1e2e;
}

/* ── Menu ── */

QMenuBar {
    background-color: #181825;
    color: #cdd6f4;
    border-bottom: 1px solid #313244;
    padding: 2px;
}

QMenuBar::item {
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #313244;
}

QMenu {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #45475a;
}

/* ── Buttons ── */

QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 20px;
    padding: 8px 20px;
    font-weight: bold;
    min-height: 32px;
}

QPushButton:hover {
    background-color: #74c7ec;
}

QPushButton:pressed {
    background-color: #89dceb;
}

QPushButton:disabled {
    background-color: #45475a;
    color: #6c7086;
}

QPushButton#cancelButton {
    background-color: #f38ba8;
    color: #1e1e2e;
}

QPushButton#cancelButton:hover {
    background-color: #eba0ac;
}

QPushButton#iconButton {
    background-color: #313244;
    color: #cdd6f4;
    border-radius: 18px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    padding: 0;
}

QPushButton#iconButton:hover {
    background-color: #45475a;
}

QPushButton#textIconButton {
    background-color: #313244;
    color: #cdd6f4;
    border-radius: 18px;
    padding: 6px 16px;
    min-height: 32px;
    font-weight: normal;
}

QPushButton#textIconButton:hover {
    background-color: #45475a;
}

QPushButton#dangerIconButton {
    background-color: transparent;
    color: #f38ba8;
    border: 1px solid #f38ba8;
    border-radius: 14px;
    min-width: 28px;
    max-width: 28px;
    min-height: 28px;
    max-height: 28px;
    padding: 0;
}

QPushButton#dangerIconButton:hover {
    background-color: #f38ba8;
    color: #1e1e2e;
}

/* ── Inputs ── */

QComboBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 2px solid transparent;
    border-bottom: 2px solid #45475a;
    border-radius: 8px;
    padding: 8px 12px;
}

QComboBox:hover {
    border-bottom-color: #89b4fa;
}

QComboBox:focus {
    border-color: #89b4fa;
}

QComboBox QAbstractItemView {
    background-color: #313244;
    color: #cdd6f4;
    selection-background-color: #45475a;
    border-radius: 8px;
    padding: 4px;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QSpinBox, QDoubleSpinBox, QLineEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 2px solid transparent;
    border-bottom: 2px solid #45475a;
    border-radius: 8px;
    padding: 8px;
}

QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus {
    border-color: #89b4fa;
}

/* ── Progress ── */

QProgressBar {
    background-color: #313244;
    border: none;
    border-radius: 6px;
    text-align: center;
    color: #cdd6f4;
    height: 12px;
    font-size: 10px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #89b4fa, stop:1 #a6e3a1);
    border-radius: 6px;
}

/* ── List ── */

QListWidget {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 12px;
    padding: 4px;
    outline: none;
}

QListWidget::item {
    padding: 4px;
    border-radius: 8px;
}

QListWidget::item:selected {
    background-color: #313244;
}

/* ── Labels ── */

QLabel#dropLabel {
    color: #6c7086;
    font-size: 15px;
}

QLabel#titleLabel {
    font-size: 20px;
    font-weight: bold;
    color: #89b4fa;
}

/* ── StatusBar ── */

QStatusBar {
    background-color: #181825;
    color: #a6adc8;
    border-top: 1px solid #313244;
    font-size: 12px;
}

/* ── GroupBox ── */

QGroupBox {
    border: 1px solid #313244;
    border-radius: 12px;
    margin-top: 14px;
    padding: 16px 8px 8px 8px;
}

QGroupBox::title {
    color: #89b4fa;
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
    font-weight: bold;
}

/* ── CheckBox ── */

QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid #45475a;
    background-color: transparent;
}

QCheckBox::indicator:hover {
    border-color: #89b4fa;
}

QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}

/* ── Tabs ── */

QTabWidget::pane {
    border: 1px solid #313244;
    border-radius: 8px;
    background-color: #1e1e2e;
}

QTabBar::tab {
    background-color: #181825;
    color: #6c7086;
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #1e1e2e;
    color: #89b4fa;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background-color: #313244;
    color: #cdd6f4;
}

/* ── Table ── */

QTableWidget {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 8px;
    gridline-color: #313244;
}

QHeaderView::section {
    background-color: #313244;
    color: #cdd6f4;
    padding: 8px;
    border: none;
    font-weight: bold;
}

/* ── ScrollBar ── */

QScrollBar:vertical {
    background-color: transparent;
    width: 8px;
    border: none;
    margin: 4px 0;
}

QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 4px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background-color: #585b70;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: transparent;
    height: 8px;
    border: none;
    margin: 0 4px;
}

QScrollBar::handle:horizontal {
    background-color: #45475a;
    border-radius: 4px;
    min-width: 24px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* ── TextBrowser ── */

QTextBrowser {
    background-color: #181825;
    color: #cdd6f4;
    border: none;
    padding: 8px;
}

/* ── PlainTextEdit ── */

QPlainTextEdit {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 8px;
}
"""

LIGHT_STYLE = """
QWidget {
    background-color: #eff1f5;
    color: #4c4f69;
    font-family: "Segoe UI", "Roboto", "Noto Sans", sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #eff1f5;
}

/* ── Menu ── */

QMenuBar {
    background-color: #e6e9ef;
    color: #4c4f69;
    border-bottom: 1px solid #ccd0da;
    padding: 2px;
}

QMenuBar::item {
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #ccd0da;
}

QMenu {
    background-color: #eff1f5;
    border: 1px solid #ccd0da;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #dce0e8;
}

/* ── Buttons ── */

QPushButton {
    background-color: #1e66f5;
    color: #eff1f5;
    border: none;
    border-radius: 20px;
    padding: 8px 20px;
    font-weight: bold;
    min-height: 32px;
}

QPushButton:hover {
    background-color: #2a7de1;
}

QPushButton:pressed {
    background-color: #3592d3;
}

QPushButton:disabled {
    background-color: #ccd0da;
    color: #9ca0b0;
}

QPushButton#cancelButton {
    background-color: #d20f39;
    color: #eff1f5;
}

QPushButton#cancelButton:hover {
    background-color: #e34068;
}

QPushButton#iconButton {
    background-color: #dce0e8;
    color: #4c4f69;
    border-radius: 18px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    padding: 0;
}

QPushButton#iconButton:hover {
    background-color: #ccd0da;
}

QPushButton#textIconButton {
    background-color: #dce0e8;
    color: #4c4f69;
    border-radius: 18px;
    padding: 6px 16px;
    min-height: 32px;
    font-weight: normal;
}

QPushButton#textIconButton:hover {
    background-color: #ccd0da;
}

QPushButton#dangerIconButton {
    background-color: transparent;
    color: #d20f39;
    border: 1px solid #d20f39;
    border-radius: 14px;
    min-width: 28px;
    max-width: 28px;
    min-height: 28px;
    max-height: 28px;
    padding: 0;
}

QPushButton#dangerIconButton:hover {
    background-color: #d20f39;
    color: #eff1f5;
}

/* ── Inputs ── */

QComboBox {
    background-color: #e6e9ef;
    color: #4c4f69;
    border: 2px solid transparent;
    border-bottom: 2px solid #ccd0da;
    border-radius: 8px;
    padding: 8px 12px;
}

QComboBox:hover {
    border-bottom-color: #1e66f5;
}

QComboBox:focus {
    border-color: #1e66f5;
}

QComboBox QAbstractItemView {
    background-color: #e6e9ef;
    color: #4c4f69;
    selection-background-color: #ccd0da;
    border-radius: 8px;
    padding: 4px;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QSpinBox, QDoubleSpinBox, QLineEdit {
    background-color: #e6e9ef;
    color: #4c4f69;
    border: 2px solid transparent;
    border-bottom: 2px solid #ccd0da;
    border-radius: 8px;
    padding: 8px;
}

QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus {
    border-color: #1e66f5;
}

/* ── Progress ── */

QProgressBar {
    background-color: #ccd0da;
    border: none;
    border-radius: 6px;
    text-align: center;
    color: #4c4f69;
    height: 12px;
    font-size: 10px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1e66f5, stop:1 #40a02b);
    border-radius: 6px;
}

/* ── List ── */

QListWidget {
    background-color: #e6e9ef;
    color: #4c4f69;
    border: 1px solid #ccd0da;
    border-radius: 12px;
    padding: 4px;
    outline: none;
}

QListWidget::item {
    padding: 4px;
    border-radius: 8px;
}

QListWidget::item:selected {
    background-color: #ccd0da;
}

/* ── Labels ── */

QLabel#dropLabel {
    color: #9ca0b0;
    font-size: 15px;
}

QLabel#titleLabel {
    font-size: 20px;
    font-weight: bold;
    color: #1e66f5;
}

/* ── StatusBar ── */

QStatusBar {
    background-color: #e6e9ef;
    color: #6c6f85;
    border-top: 1px solid #ccd0da;
    font-size: 12px;
}

/* ── GroupBox ── */

QGroupBox {
    border: 1px solid #ccd0da;
    border-radius: 12px;
    margin-top: 14px;
    padding: 16px 8px 8px 8px;
}

QGroupBox::title {
    color: #1e66f5;
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
    font-weight: bold;
}

/* ── CheckBox ── */

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid #ccd0da;
    background-color: transparent;
}

QCheckBox::indicator:hover {
    border-color: #1e66f5;
}

QCheckBox::indicator:checked {
    background-color: #1e66f5;
    border-color: #1e66f5;
}

/* ── Tabs ── */

QTabWidget::pane {
    border: 1px solid #ccd0da;
    border-radius: 8px;
    background-color: #eff1f5;
}

QTabBar::tab {
    background-color: #e6e9ef;
    color: #9ca0b0;
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #eff1f5;
    color: #1e66f5;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background-color: #ccd0da;
    color: #4c4f69;
}

/* ── Table ── */

QTableWidget {
    background-color: #e6e9ef;
    color: #4c4f69;
    border: 1px solid #ccd0da;
    border-radius: 8px;
    gridline-color: #ccd0da;
}

QHeaderView::section {
    background-color: #dce0e8;
    color: #4c4f69;
    padding: 8px;
    border: none;
    font-weight: bold;
}

/* ── ScrollBar ── */

QScrollBar:vertical {
    background-color: transparent;
    width: 8px;
    border: none;
    margin: 4px 0;
}

QScrollBar::handle:vertical {
    background-color: #ccd0da;
    border-radius: 4px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background-color: #bcc0cc;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: transparent;
    height: 8px;
    border: none;
    margin: 0 4px;
}

QScrollBar::handle:horizontal {
    background-color: #ccd0da;
    border-radius: 4px;
    min-width: 24px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* ── TextBrowser ── */

QTextBrowser {
    background-color: #e6e9ef;
    color: #4c4f69;
    border: none;
    padding: 8px;
}

/* ── PlainTextEdit ── */

QPlainTextEdit {
    background-color: #e6e9ef;
    color: #4c4f69;
    border: 1px solid #ccd0da;
    border-radius: 8px;
    padding: 8px;
}
"""


class ThemeManager:
    DARK = "dark"
    LIGHT = "light"

    # Icon colors per theme
    ICON_COLORS = {
        DARK: "#cdd6f4",
        LIGHT: "#4c4f69",
    }

    def __init__(self):
        self._settings = QSettings("PyConverter", "PyConverter")
        self._current = self._settings.value("theme", self.DARK)

    @property
    def current(self) -> str:
        return self._current

    @property
    def icon_color(self) -> str:
        return self.ICON_COLORS.get(self._current, "#cdd6f4")

    def apply(self, app: QApplication) -> None:
        if self._current == self.DARK:
            app.setStyleSheet(DARK_STYLE)
        else:
            app.setStyleSheet(LIGHT_STYLE)

    def toggle(self, app: QApplication) -> str:
        self._current = self.LIGHT if self._current == self.DARK else self.DARK
        self._settings.setValue("theme", self._current)
        self.apply(app)
        return self._current

    def set_theme(self, theme: str, app: QApplication) -> None:
        self._current = theme
        self._settings.setValue("theme", self._current)
        self.apply(app)
