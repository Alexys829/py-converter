from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
)

from pyconverter.core.history import ConversionHistory


class HistoryDialog(QDialog):
    def __init__(self, history: ConversionHistory, parent=None):
        super().__init__(parent)
        self._history = history
        self.setWindowTitle("Conversion History")
        self.setMinimumSize(800, 500)

        layout = QVBoxLayout(self)

        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels([
            "Date/Time", "Input", "Output", "Converter", "Status", "Error"
        ])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        layout.addWidget(self._table, stretch=1)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        clear_btn = QPushButton("Clear History")
        clear_btn.setObjectName("cancelButton")
        clear_btn.setToolTip("Delete all conversion history")
        clear_btn.clicked.connect(self._clear_history)
        btn_layout.addWidget(clear_btn)

        close_btn = QPushButton("Close")
        close_btn.setToolTip("Close this dialog")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        self._load_data()

    def _load_data(self):
        entries = self._history.get_entries(limit=100)
        self._table.setRowCount(len(entries))

        for row, entry in enumerate(entries):
            # Timestamp
            ts = entry.timestamp[:19].replace("T", " ")
            self._table.setItem(row, 0, QTableWidgetItem(ts))

            # Input (just filename)
            from pathlib import Path
            in_name = Path(entry.input_path).name
            self._table.setItem(row, 1, QTableWidgetItem(in_name))

            # Output format
            out_name = Path(entry.output_path).name
            self._table.setItem(row, 2, QTableWidgetItem(out_name))

            # Converter
            self._table.setItem(row, 3, QTableWidgetItem(entry.converter))

            # Status
            status = "OK" if entry.success else "FAILED"
            item = QTableWidgetItem(status)
            if entry.success:
                item.setForeground(Qt.GlobalColor.green)
            else:
                item.setForeground(Qt.GlobalColor.red)
            self._table.setItem(row, 4, item)

            # Error
            self._table.setItem(row, 5, QTableWidgetItem(entry.error or ""))

    def _clear_history(self):
        reply = QMessageBox.question(
            self, "Clear History",
            "Are you sure you want to clear the conversion history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._history.clear()
            self._table.setRowCount(0)
