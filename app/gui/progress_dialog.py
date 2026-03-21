"""Progress dialog shown during verification."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QGridLayout, QLabel, QProgressBar, QPushButton


class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Verification Progress")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QGridLayout(self)

        self.progress = QProgressBar(self)
        self.progress.setMinimum(0)
        self.progress.setValue(0)

        self.label_total = QLabel("Total: 0")
        self.label_completed = QLabel("Completed: 0")
        self.label_errors = QLabel("Errors: 0")
        self.label_speed = QLabel("Speed: 0/sec")

        self.button_close = QPushButton("Close")
        self.button_close.clicked.connect(self.accept)

        layout.addWidget(self.progress, 0, 0, 1, 2)
        layout.addWidget(self.label_total, 1, 0)
        layout.addWidget(self.label_completed, 1, 1)
        layout.addWidget(self.label_errors, 2, 0)
        layout.addWidget(self.label_speed, 2, 1)
        layout.addWidget(self.button_close, 3, 1)

    def update_stats(self, total: int, completed: int, errors: int, speed: float) -> None:
        self.progress.setMaximum(total)
        self.progress.setValue(completed)
        self.label_total.setText(f"Total: {total}")
        self.label_completed.setText(f"Completed: {completed}")
        self.label_errors.setText(f"Errors: {errors}")
        self.label_speed.setText(f"Speed: {speed:.1f}/sec")
