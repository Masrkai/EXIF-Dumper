#!/usr/bin/env python3
"""
Main Application Window
"""
import os
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QMessageBox, QFileDialog, QListWidgetItem
)
from PySide6.QtCore import QThread, Signal, Qt

from ..processing.exif_processor import EXIFProcessor
from ..processing.batch_processor import BatchProcessor
from .widgets.single_image_tab import SingleImageTab
from .widgets.batch_tab import BatchProcessingTab

class Worker(QThread):
    """Generic worker thread to run functions in the background."""
    finished = Signal(object)
    error = Signal(str)
    progress = Signal(int, int, str, str) # current, total, filename, status

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            # If the function is from BatchProcessor, pass the progress signal
            if isinstance(self.func.__self__, BatchProcessor):
                self.kwargs['progress_callback'] = lambda cur, tot, fname, stat: self.progress.emit(cur, tot, fname, stat)
            
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    """The main application window."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EXIF Data Manager")
        self.setGeometry(100, 100, 1200, 800)
        self.current_image_path = None
        self.worker = None

        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        """Initialize the main UI components."""
        self.tab_widget = QTabWidget()
        self.single_image_tab = SingleImageTab()
        self.batch_tab = BatchProcessingTab()
        self.tab_widget.addTab(self.single_image_tab, "Single Image")
        self.tab_widget.addTab(self.batch_tab, "Batch Processing")
        self.setCentralWidget(self.tab_widget)
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

    def connect_signals(self):
        """Connect signals from widgets to slots in the main window."""
        # Single Image Tab Signals
        self.single_image_tab.select_button.clicked.connect(self.open_single_image)
        self.single_image_tab.extract_button.clicked.connect(self.extract_exif)
        self.single_image_tab.save_exif_button.clicked.connect(self.save_exif_changes)
        self.single_image_tab.delete_exif_button.clicked.connect(self.delete_all_exif)

        # Batch Processing Tab Signals
        self.batch_tab.add_files_button.clicked.connect(self.open_batch_images)
        self.batch_tab.clear_files_button.clicked.connect(self.batch_tab.clear_file_list)
        self.batch_tab.process_button.clicked.connect(self.process_batch_images)

    def on_processor_error(self, error_msg: str):
        """Handle errors from the worker thread."""
        self.status_bar.showMessage("An error occurred.")
        QMessageBox.critical(self, "Error", error_msg)

    # --- Single Image Slots ---
    def open_single_image(self):
        """Open a file dialog to select a single image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Image Files (*.jpg *.jpeg *.png *.tiff *.bmp);;All Files (*)"
        )
        if file_path:
            self.current_image_path = file_path
            self.single_image_tab.set_image_preview(file_path)
            self.status_bar.showMessage(f"Loaded: {os.path.basename(file_path)}")
            self.extract_exif() # Automatically extract data on load

    def extract_exif(self):
        """Extract EXIF data from the current image."""
        if not self.current_image_path:
            QMessageBox.warning(self, "Warning", "Please select an image first.")
            return
        self.status_bar.showMessage("Extracting EXIF data...")
        processor = EXIFProcessor(self.current_image_path)
        self.worker = Worker(processor.extract)
        self.worker.finished.connect(self.on_exif_extracted)
        self.worker.error.connect(self.on_processor_error)
        self.worker.start()

    def on_exif_extracted(self, exif_data: dict):
        """Slot to handle the result of EXIF extraction."""
        self.single_image_tab.populate_exif_table(exif_data)
        self.status_bar.showMessage(f"EXIF data extracted ({len(exif_data)} tags found).")

    def save_exif_changes(self):
        """Save modified EXIF data back to the file."""
        if not self.current_image_path:
            QMessageBox.warning(self, "Warning", "No image selected.")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Save", "Are you sure you want to save these changes?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.No:
            return

        self.status_bar.showMessage("Saving EXIF data...")
        edited_data = self.single_image_tab.get_edited_data()
        preserve = self.single_image_tab.preserve_original_cb.isChecked()
        
        processor = EXIFProcessor(self.current_image_path)
        self.worker = Worker(processor.edit, edited_data, preserve_original=preserve)
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.error.connect(self.on_processor_error)
        self.worker.start()

    def delete_all_exif(self):
        """Delete all EXIF data from the current image."""
        if not self.current_image_path:
            QMessageBox.warning(self, "Warning", "No image selected.")
            return

        reply = QMessageBox.question(
            self, "Confirm Delete", "This will permanently remove all EXIF data. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.No:
            return
            
        self.status_bar.showMessage("Deleting EXIF data...")
        preserve = self.single_image_tab.preserve_original_cb.isChecked()
        processor = EXIFProcessor(self.current_image_path)
        self.worker = Worker(processor.delete, preserve_original=preserve)
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.error.connect(self.on_processor_error)
        self.worker.start()

    def on_operation_finished(self, result: dict):
        """Handle successful save/delete operations."""
        message = result.get("message", "Operation completed successfully.")
        self.status_bar.showMessage(message)
        QMessageBox.information(self, "Success", message)
        # Refresh the data
        self.extract_exif()

    # --- Batch Processing Slots ---
    def open_batch_images(self):
        """Open a file dialog to select multiple images for batch processing."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Images for Batch Processing", "",
            "Image Files (*.jpg *.jpeg *.png *.tiff *.bmp);;All Files (*)"
        )
        if file_paths:
            self.batch_tab.add_files(file_paths)
            self.status_bar.showMessage(f"Added {len(file_paths)} images to batch list.")

    def process_batch_images(self):
        """Start the batch processing job."""
        file_list = self.batch_tab.get_file_list()
        if not file_list:
            QMessageBox.warning(self, "Warning", "No images in the batch list.")
            return

        operation_text = self.batch_tab.operation_combo.currentText()
        if "Delete" in operation_text:
            operation = "delete"
        else: # Add more operations here later
            QMessageBox.warning(self, "Warning", "Selected operation is not yet implemented.")
            return

        reply = QMessageBox.question(
            self, "Confirm Batch Process", f"This will perform '{operation}' on {len(file_list)} images. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.No:
            return
        
        self.status_bar.showMessage("Starting batch processing...")
        self.batch_tab.reset_progress()
        preserve = self.batch_tab.batch_preserve_original_cb.isChecked()

        batch_processor = BatchProcessor(file_list, operation, preserve)
        self.worker = Worker(batch_processor.run)
        self.worker.progress.connect(self.on_batch_progress)
        self.worker.finished.connect(self.on_batch_finished)
        self.worker.error.connect(self.on_processor_error)
        self.worker.start()

    def on_batch_progress(self, current: int, total: int, filename: str, status: str):
        """Update the UI during batch processing."""
        progress_percent = int((current / total) * 100)
        self.batch_tab.batch_progress_bar.setValue(progress_percent)
        self.batch_tab.batch_status_list.addItem(f"({current}/{total}) {filename}: {status}")
        self.batch_tab.batch_status_list.scrollToBottom()

    def on_batch_finished(self, result):
        """Handle the completion of the batch job."""
        self.status_bar.showMessage("Batch processing finished.")
        QMessageBox.information(self, "Batch Complete", "The batch operation has finished.")
