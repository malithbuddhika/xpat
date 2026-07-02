"""Main application window for XPAT Worker Automation Tool."""

from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Event
from typing import Dict, List, Optional

import requests
from loguru import logger
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QAction, QIcon, QPixmap, QColor, QBrush
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

from ..data.excel_reader import load_workers_from_excel
from ..data.excel_writer import export_to_excel
from ..services.xpat_client import XpatClient
from ..utils.config import APP_NAME, MAX_WORKERS
from ..utils.logger import get_logger, setup_logger
from .progress_dialog import ProgressDialog
from .widgets import DragDropFrame, ImagePreview, LogConsole


class MainWindow(QMainWindow):
    # Signal to safely update GUI from worker thread
    worker_result_ready = Signal(object)
    photo_result_ready = Signal(object)
    
    def __init__(self) -> None:
        super().__init__()
        setup_logger()
        self._logger = get_logger()
        self._logger.info("Starting %s", APP_NAME)

        self.client = XpatClient()
        self.executor: Optional[ThreadPoolExecutor] = None
        self.photo_executor: Optional[ThreadPoolExecutor] = None
        self.stop_event: Optional[Event] = None

        self._workers: List = []
        self._worker_index: Dict[str, int] = {}
        self._stats = {"total": 0, "completed": 0, "errors": 0}
        self._start_time = 0.0

        self._setup_ui()
        
        # Connect signal for thread-safe GUI updates
        self.worker_result_ready.connect(self._on_worker_result)
        self.photo_result_ready.connect(self._on_photo_result)

    def _setup_ui(self) -> None:
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(1100, 700)

        # Prefer SVG icon if available (better for scaling).
        icon_path = Path(__file__).resolve().parents[2] / "assets" / "icon.svg"
        if not icon_path.exists():
            icon_path = icon_path.with_suffix(".png")
        self.setWindowIcon(QIcon(str(icon_path)))

        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        layout.addLayout(self._create_top_bar())
        layout.addLayout(self._create_table_section())
        layout.addLayout(self._create_bottom_bar())

        self._apply_dark_mode(True)
        self._attach_log_handler()

    def _create_top_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()

        self.load_button = QPushButton("Load Excel")
        self.load_button.clicked.connect(self._on_load_excel)
        bar.addWidget(self.load_button)

        self.start_button = QPushButton("Start Verification")
        self.start_button.clicked.connect(self._on_start)
        self.start_button.setEnabled(False)
        bar.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Process")
        self.stop_button.clicked.connect(self._on_stop)
        self.stop_button.setEnabled(False)
        bar.addWidget(self.stop_button)

        self.export_button = QPushButton("Export Updated Excel")
        self.export_button.clicked.connect(self._on_export)
        self.export_button.setEnabled(False)
        bar.addWidget(self.export_button)

        self.clear_cache_button = QPushButton("Clear Cache")
        self.clear_cache_button.clicked.connect(self._on_clear_cache)
        bar.addWidget(self.clear_cache_button)

        dark_mode_action = QAction("Toggle Dark Mode", self)
        dark_mode_action.setCheckable(True)
        dark_mode_action.setChecked(True)
        dark_mode_action.triggered.connect(self._apply_dark_mode)
        self.menuBar().addAction(dark_mode_action)

        # Drag and drop area
        drop_frame = DragDropFrame(self)
        drop_label = QLabel("Drag & drop an Excel file here")
        drop_label.setAlignment(Qt.AlignCenter)  # type: ignore
        drop_layout = QVBoxLayout()
        drop_layout.addWidget(drop_label)
        drop_frame.setLayout(drop_layout)
        drop_frame.fileDropped.connect(self._on_file_dropped)
        drop_frame.setFixedHeight(80)
        bar.addWidget(drop_frame, stretch=1)

        return bar

    def _create_table_section(self) -> QVBoxLayout:
        section = QVBoxLayout()

        self.table = QTableWidget(0, 7, self)
        self.table.setHorizontalHeaderLabels([
            "Work Permit",
            "Passport",
            "Worker Name",
            "Company",
            "Status",
            "Permit Expiry",
            "Verification Time",
        ])
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setMinimumWidth(800)
        self.table.setMinimumHeight(350)
        self.table.setWordWrap(False)
        self.table.cellClicked.connect(self._on_cell_clicked)
        section.addWidget(self.table)

        self.photo_preview = ImagePreview(self)
        self.photo_preview.setFixedHeight(180)
        section.addWidget(self.photo_preview)

        return section

    def _create_bottom_bar(self) -> QVBoxLayout:
        section = QVBoxLayout()

        self.progress_bar = QLabel("Progress: 0/0")
        section.addWidget(self.progress_bar)

        self.log_console = LogConsole(self)
        self.log_console.setFixedHeight(160)
        section.addWidget(self.log_console)

        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("Total: 0 | Completed: 0 | Errors: 0 | Speed: 0/sec")
        stats_layout.addWidget(self.stats_label)
        section.addLayout(stats_layout)

        return section

    def _attach_log_handler(self) -> None:
        def _append_log(message: str) -> None:
            self.log_console.append(message)

        logger.add(_append_log, level="INFO", enqueue=True)

    def _apply_dark_mode(self, enabled: bool) -> None:
        if enabled:
            self.setStyleSheet(
                "QWidget { background: #121212; color: #ffffff; } "
                "QTableWidget { gridline-color: #444; color: #ffffff; background: #121212; } "
                "QHeaderView::section { background: #1f1f1f; color: #ffffff; } "
                "QPushButton { background: #1f1f1f; color: #ffffff; border: 1px solid #333; padding: 6px; } "
                "QPushButton:hover { background: #2a2a2a; } "
                "QLabel, QLineEdit, QPlainTextEdit, QTextEdit, QComboBox, QMenu, QMenuBar, QStatusBar { color: #ffffff; } "
                "QTableWidget::item { color: #ffffff; background: transparent; } "
                "QScrollBar, QScrollBar::handle { background: #333; color: #ffffff; }"
            )
        else:
            self.setStyleSheet("")

    def _update_stats(self) -> None:
        total = self._stats["total"]
        completed = self._stats["completed"]
        errors = self._stats["errors"]
        elapsed = max(1.0, time.time() - self._start_time)
        speed = completed / elapsed
        self.stats_label.setText(
            f"Total: {total} | Completed: {completed} | Errors: {errors} | Speed: {speed:.1f}/sec"
        )
        self.progress_bar.setText(f"Progress: {completed}/{total}")

    def _load_workers_to_table(self, workers: List) -> None:
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(workers))
        self._worker_index.clear()

        default_text_brush = QBrush(QColor(240, 240, 240))
        red_font_brush = QBrush(QColor(255, 0, 0))  # Red color for NO DATA

        for i, worker in enumerate(workers):
            # Work Permit Number (with red styling if NO DATA)
            permit_item = QTableWidgetItem(worker.work_permit_number)
            permit_item.setForeground(default_text_brush)
            if worker.missing_data and worker.work_permit_number == "NO DATA":
                permit_item.setForeground(red_font_brush)
                font = permit_item.font()
                font.setBold(True)
                permit_item.setFont(font)
            self.table.setItem(i, 0, permit_item)

            # Passport Number (with red styling if NO DATA)
            passport_item = QTableWidgetItem(worker.passport_number)
            passport_item.setForeground(default_text_brush)
            if worker.missing_data and worker.passport_number == "NO DATA":
                passport_item.setForeground(red_font_brush)
                font = passport_item.font()
                font.setBold(True)
                passport_item.setFont(font)
            self.table.setItem(i, 1, passport_item)
            self._logger.info(f"Row {i + 1} passport={worker.passport_number}")

            name_item = QTableWidgetItem(worker.worker_name or "")
            name_item.setForeground(default_text_brush)
            self.table.setItem(i, 2, name_item)
            company_item = QTableWidgetItem(worker.company or "")
            company_item.setForeground(default_text_brush)
            self.table.setItem(i, 3, company_item)
            status_item = QTableWidgetItem(worker.status or "")
            status_item.setForeground(default_text_brush)
            self.table.setItem(i, 4, status_item)
            permit_valid_item = QTableWidgetItem(worker.permit_valid_till or "")
            permit_valid_item.setForeground(default_text_brush)
            self.table.setItem(i, 5, permit_valid_item)
            verification_time_item = QTableWidgetItem(worker.verification_time or "")
            verification_time_item.setForeground(default_text_brush)
            self.table.setItem(i, 6, verification_time_item)
            self._worker_index[worker.work_permit_number.strip().upper()] = i

        # Re-enable sorting once the table is fully populated.
        self.table.setSortingEnabled(True)
        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(0, max(self.table.columnWidth(0), 140))
        self.table.setColumnWidth(1, max(self.table.columnWidth(1), 140))
        self.table.scrollToTop()

    def _on_load_excel(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Excel file",
            os.getcwd(),
            "Excel Files (*.xlsx *.xls)",
        )
        if not path:
            return
        self._load_from_file(path)

    def _on_file_dropped(self, file_path: str) -> None:
        if not file_path.lower().endswith((".xlsx", ".xls")):
            QMessageBox.warning(self, "Invalid File", "Please drop an Excel file (.xlsx or .xls).")
            return
        self._load_from_file(file_path)

    def _load_from_file(self, file_path: str) -> None:
        try:
            df, workers = load_workers_from_excel(file_path)
        except Exception as exc:
            QMessageBox.critical(self, "Failed to load", str(exc))
            return

        self._excel_df = df
        self._workers = workers
        self._stats = {"total": len(workers), "completed": 0, "errors": 0}
        self._load_workers_to_table(workers)
        self.start_button.setEnabled(bool(workers))
        self.export_button.setEnabled(False)
        
        # Check for missing data and show warning
        missing_data_count = sum(1 for w in workers if w.missing_data)
        if missing_data_count > 0:
            self.log_console.append(
                f"⚠️ WARNING: {missing_data_count} row(s) with missing PassportNumber or WorkPermitNumber detected!"
            )
            self.log_console.append(f"These rows are marked as 'NO DATA' in red and will be skipped during verification.")
            QMessageBox.warning(
                self,
                "Missing Data Detected",
                f"{missing_data_count} row(s) have empty PassportNumber or WorkPermitNumber.\n\n"
                "These rows are marked as 'NO DATA' in red and will be:\n"
                "• Skipped during verification\n"
                "• Exported with 'NO DATA' in red in the Excel file"
            )
        
        self.log_console.append(f"Loaded {len(workers)} workers from {file_path}")
        self._update_stats()

    def _on_start(self) -> None:
        if not self._workers:
            return

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.export_button.setEnabled(False)
        self.stop_event = Event()

        self._stats.update({"completed": 0, "errors": 0})
        self._start_time = time.time()

        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        self._future_to_permit = {}

        # Count and skip workers with missing data
        valid_workers = [w for w in self._workers if not w.missing_data]
        skipped_count = len(self._workers) - len(valid_workers)
        
        if skipped_count > 0:
            self.log_console.append(f"Skipping {skipped_count} row(s) with missing data (NO DATA)")
        
        self._stats["total"] = len(valid_workers)
        
        for worker in valid_workers:
            future = self.executor.submit(
                self.client.verify_worker,
                worker.work_permit_number,
                worker.passport_number,
                self.stop_event,
            )
            self._future_to_permit[future] = worker.work_permit_number

        self.log_console.append(f"Starting verification for {len(valid_workers)} worker(s)...")
        QTimer.singleShot(100, self._process_futures)

    def _process_futures(self) -> None:
        if not self.executor:
            return

        for future in list(self._future_to_permit.keys()):
            if future.done():
                permit = self._future_to_permit.pop(future)
                try:
                    worker = future.result()
                    self._apply_worker_result(worker)
                except Exception as exc:
                    self._logger.exception("Exception while processing result for %s", permit)
                    self._stats["errors"] += 1
                    self.log_console.append(f"Error processing {permit}: {exc}")
                    self._update_stats()

        if self._future_to_permit and not (self.stop_event and self.stop_event.is_set()):
            QTimer.singleShot(200, self._process_futures)
        else:
            self._on_finish()

    def _apply_worker_result(self, worker) -> None:
        """Emit signal to update GUI from worker thread (thread-safe)."""
        self.worker_result_ready.emit(worker)

    def _find_row_for_permit(self, permit: str) -> Optional[int]:
        if not permit:
            return None
        items = self.table.findItems(permit, Qt.MatchExactly)
        for item in items:
            if item.column() == 0:
                return item.row()
        return None

    @Slot(object)
    def _on_worker_result(self, worker) -> None:
        """Handle worker result update on main thread (thread-safe)."""
        key = worker.work_permit_number.strip().upper()
        idx = self._find_row_for_permit(key)
        if idx is None:
            idx = self._worker_index.get(key)
        if idx is None:
            return

        self.table.setItem(idx, 2, QTableWidgetItem(worker.worker_name or ""))
        self.table.setItem(idx, 3, QTableWidgetItem(worker.company or ""))
        self.table.setItem(idx, 4, QTableWidgetItem(worker.status or ""))
        self.table.setItem(idx, 5, QTableWidgetItem(worker.permit_valid_till or ""))
        self.table.setItem(idx, 6, QTableWidgetItem(worker.verification_time or ""))

        self._stats["completed"] += 1
        if worker.error:
            self._stats["errors"] += 1
            self.log_console.append(f"ERROR {worker.work_permit_number}: {worker.error}")
        else:
            self.log_console.append(f"Verified {worker.work_permit_number} -> {worker.status}")

        # Store the updated worker back into our list
        for i, w in enumerate(self._workers):
            if w.work_permit_number.strip().upper() == key:
                self._workers[i] = worker
                break
        
        self._update_stats()

    def _on_finish(self) -> None:
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.export_button.setEnabled(True)
        if self.executor:
            self.executor.shutdown(wait=False)
            self.executor = None

        self.log_console.append("Verification process completed.")

    def _on_stop(self) -> None:
        if self.stop_event:
            self.stop_event.set()
        self.stop_button.setEnabled(False)
        self.log_console.append("Stopping verification...")

    def _on_export(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export results",
            os.path.join(os.getcwd(), "xpat_results.xlsx"),
            "Excel (*.xlsx);;CSV (*.csv)",
        )
        if not path:
            return
        try:
            export_to_excel(self._excel_df, self._workers, path)
            QMessageBox.information(self, "Exported", f"Results exported to {path}")
        except Exception as exc:
            QMessageBox.critical(self, "Export failed", str(exc))

    def _on_clear_cache(self) -> None:
        reply = QMessageBox.question(
            self,
            "Clear Cache",
            "Clear all cached worker data? This will force fresh verification on next run.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.client.cache.clear_cache()
            self.log_console.append("✓ Cache cleared successfully. Next verification will fetch fresh data.")
            QMessageBox.information(self, "Cache Cleared", "All cached data has been cleared.")

    @Slot(int, int)
    def _on_cell_clicked(self, row: int, _col: int) -> None:
        permit_item = self.table.item(row, 0)
        if not permit_item:
            return
        permit = permit_item.text().strip().upper()
        worker = next((w for w in self._workers if w.work_permit_number.strip().upper() == permit), None)
        if not worker or not worker.photo_url:
            self.photo_preview.setText("No photo available")
            return

        # Fetch image in background and update
        self.photo_preview.setText("Loading photo...")
        if self.photo_executor is None:
            self.photo_executor = ThreadPoolExecutor(max_workers=1)
        future = self.photo_executor.submit(self._fetch_photo, worker.photo_url)
        future.add_done_callback(self._on_photo_fetch_done)

    def _fetch_photo(self, url: str) -> tuple[Optional[QPixmap], str]:
        try:
            session = self.client.session_manager.get_session()
            resp = session.get(url, timeout=10)
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "")
            if not content_type.lower().startswith("image"):
                return None, f"Unsupported content type: {content_type}"
            pixmap = QPixmap()
            if not pixmap.loadFromData(resp.content):
                return None, "Failed to decode image"
            return pixmap, ""
        except Exception as exc:
            return None, str(exc)

    def _on_photo_fetch_done(self, future) -> None:
        try:
            result = future.result()
        except Exception as exc:
            result = (None, str(exc))
        self.photo_result_ready.emit(result)

    @Slot(object)
    def _on_photo_result(self, result: tuple[Optional[QPixmap], str]) -> None:
        pixmap, error = result
        if pixmap:
            self.photo_preview.set_image(pixmap)
        else:
            self.photo_preview.setText(f"Failed to load photo: {error}")

    def closeEvent(self, event) -> None:
        """Handle app close event - clean up resources."""
        # Stop any running verification process 
        if self.stop_event:
            self.stop_event.set()
        
        # Shutdown executors properly
        if self.executor:
            self.executor.shutdown(wait=False)
            self.executor = None
        if self.photo_executor:
            self.photo_executor.shutdown(wait=False)
            self.photo_executor = None
        
        self._logger.info("Closing %s", APP_NAME)
        event.accept()


def main() -> None:
    import sys
    import os
    import subprocess
    from pathlib import Path
    
    # Create a lock file to prevent multiple instances
    try:
        lock_dir = Path(os.path.expanduser("~/.xpat_worker_tool"))
        lock_dir.mkdir(exist_ok=True, parents=True)
        lock_file = lock_dir / "app.lock"
        
        # Check if lock file exists and if process is running
        if lock_file.exists():
            try:
                with open(lock_file, 'r') as f:
                    old_pid = int(f.read().strip())
                # Check if old process still exists
                result = subprocess.run(['ps', '-p', str(old_pid)], capture_output=True)
                if result.returncode == 0:
                    # Process still running, exit silently
                    return
            except (ValueError, OSError):
                pass
            # Lock file is stale or unreadable, remove it
            try:
                lock_file.unlink()
            except OSError:
                pass
        
        # Create lock file with current PID
        try:
            with open(lock_file, 'w') as f:
                f.write(str(os.getpid()))
        except OSError:
            pass
        
        # Check if an application instance already exists
        app = QApplication.instance()
        if app is None:
            # Create a new application instance
            app = QApplication(sys.argv)
        
        win = MainWindow()
        win.show()
        sys.exit(app.exec())
    except Exception as e:
        # Fallback: just try to start the app even if lock fails
        app = QApplication.instance() or QApplication(sys.argv)
        win = MainWindow()
        win.show()
        sys.exit(app.exec())
