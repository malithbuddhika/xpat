"""Reusable Qt widgets for the XPAT Worker Automation Tool."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QFrame, QLabel, QPlainTextEdit


class DragDropFrame(QFrame):
    """A frame that accepts a dragged file and emits a signal."""

    fileDropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if not urls:
            return
        path = urls[0].toLocalFile()
        if path:
            self.fileDropped.emit(path)


class LogConsole(QPlainTextEdit):
    """Simple read-only console for status logs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setPlaceholderText("Logs will appear here...")

    def append(self, message: str) -> None:
        self.appendPlainText(message)


class ClickableLabel(QLabel):
    """A label that can emit a clicked signal."""

    clicked = Signal()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)


class ImagePreview(QLabel):
    """A placeholder for showing worker photo previews."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setText("No photo selected")
        self.setStyleSheet("border: 1px solid #888; background: #121212; color: #fff; padding: 10px;")

    def set_image(self, pixmap):
        if pixmap:
            self.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.setText("No photo available")
