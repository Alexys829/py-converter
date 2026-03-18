import sys

from PySide6.QtWidgets import QApplication

from pyconverter.gui.theme import ThemeManager
from pyconverter.gui.main_window import MainWindow


def run_gui():
    # Ensure converters are registered
    import pyconverter.converters  # noqa: F401

    app = QApplication(sys.argv)
    app.setApplicationName("PyConverter")

    theme_manager = ThemeManager()
    theme_manager.apply(app)

    window = MainWindow(theme_manager)
    window.show()

    sys.exit(app.exec())
