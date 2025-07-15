#!/usr/bin/env python3
"""
EXIF Data Manager - UI Module
"""

import sys
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QTreeWidget,
    QTreeWidgetItem, QFileDialog, QMessageBox, QProgressBar, QCheckBox,
    QScrollArea, QFrame, QSplitter, QGroupBox, QGridLayout, QComboBox,
    QSpinBox, QDoubleSpinBox, QDateTimeEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QThread, Signal, QDateTime, QTimer
from PySide6.QtGui import QPixmap, QFont, QIcon, QAction

from PIL import Image, ExifTags
from PIL.ExifTags import TAGS, GPSTAGS
import piexif
import json
import shutil
from datetime import datetime


class EXIFProcessor(QThread):
    """Background thread for processing EXIF data"""
    progress = Signal(int)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, image_path: str, operation: str, exif_data: dict = None):
        super().__init__()
        self.image_path = image_path
        self.operation = operation
        self.exif_data = exif_data

    def run(self):
        try:
            if self.operation == "extract":
                result = self.extract_exif()
            elif self.operation == "edit":
                result = self.edit_exif()
            elif self.operation == "delete":
                result = self.delete_exif()
            else:
                raise ValueError(f"Unknown operation: {self.operation}")

            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

    def extract_exif(self) -> dict:
        """Extract EXIF data from image"""
        try:
            image = Image.open(self.image_path)
            exif_data = {}

            if hasattr(image, '_getexif') and image._getexif():
                exif = image._getexif()
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)

                    # Handle GPS data specially
                    if tag == 'GPSInfo':
                        gps_data = {}
                        for gps_tag_id, gps_value in value.items():
                            gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                            gps_data[gps_tag] = gps_value
                        exif_data[tag] = gps_data
                    else:
                        exif_data[tag] = value

            return exif_data
        except Exception as e:
            raise Exception(f"Failed to extract EXIF data: {str(e)}")

    def edit_exif(self) -> dict:
        """Edit EXIF data in image"""
        try:
            # Load existing EXIF data
            exif_dict = piexif.load(self.image_path)

            # Update with new data
            for key, value in self.exif_data.items():
                if key in exif_dict:
                    exif_dict[key].update(value)
                else:
                    exif_dict[key] = value

            # Save the modified EXIF data
            exif_bytes = piexif.dump(exif_dict)

            # Create backup if needed
            backup_path = self.image_path + ".backup"
            shutil.copy2(self.image_path, backup_path)

            # Write modified EXIF data
            piexif.insert(exif_bytes, self.image_path)

            return {"status": "success", "message": "EXIF data updated successfully"}
        except Exception as e:
            raise Exception(f"Failed to edit EXIF data: {str(e)}")

    def delete_exif(self) -> dict:
        """Delete EXIF data from image"""
        try:
            # Create backup if needed
            backup_path = self.image_path + ".backup"
            shutil.copy2(self.image_path, backup_path)

            # Remove EXIF data
            piexif.remove(self.image_path)

            return {"status": "success", "message": "EXIF data deleted successfully"}
        except Exception as e:
            raise Exception(f"Failed to delete EXIF data: {str(e)}")


class BatchProcessor(QThread):
    """Background thread for batch processing"""
    progress = Signal(int)
    file_processed = Signal(str, str)  # filename, status
    finished = Signal()
    error = Signal(str)

    def __init__(self, file_list: List[str], operation: str, exif_data: dict = None, preserve_original: bool = True):
        super().__init__()
        self.file_list = file_list
        self.operation = operation
        self.exif_data = exif_data
        self.preserve_original = preserve_original

    def run(self):
        try:
            total_files = len(self.file_list)

            for i, file_path in enumerate(self.file_list):
                try:
                    if self.preserve_original:
                        # Create a copy with _modified suffix
                        base_path = Path(file_path)
                        new_path = base_path.parent / f"{base_path.stem}_modified{base_path.suffix}"
                        shutil.copy2(file_path, new_path)
                        working_path = str(new_path)
                    else:
                        working_path = file_path

                    # Process the file
                    processor = EXIFProcessor(working_path, self.operation, self.exif_data)
                    processor.run()

                    self.file_processed.emit(os.path.basename(file_path), "Success")

                except Exception as e:
                    self.file_processed.emit(os.path.basename(file_path), f"Error: {str(e)}")

                # Update progress
                progress = int((i + 1) / total_files * 100)
                self.progress.emit(progress)

            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))


class EXIFManager(QMainWindow):
    """Main EXIF Manager Application"""

    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.current_exif_data = {}
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("EXIF Data Manager")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create tab widget
        self.tab_widget = QTabWidget()
        central_widget.setLayout(QVBoxLayout())
        central_widget.layout().addWidget(self.tab_widget)

        # Create tabs
        self.create_single_image_tab()
        self.create_batch_processing_tab()

        # Create menu bar
        self.create_menu_bar()

        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        open_action = QAction('Open Image', self)
        open_action.triggered.connect(self.open_single_image)
        file_menu.addAction(open_action)

        open_batch_action = QAction('Open Images for Batch Processing', self)
        open_batch_action.triggered.connect(self.open_batch_images)
        file_menu.addAction(open_batch_action)

        file_menu.addSeparator()

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def create_single_image_tab(self):
        """Create the single image processing tab"""
        single_tab = QWidget()
        self.tab_widget.addTab(single_tab, "Single Image")

        # Main layout
        main_layout = QHBoxLayout(single_tab)

        # Left side - Image preview and controls
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # File selection
        file_group = QGroupBox("Image Selection")
        file_layout = QVBoxLayout(file_group)

        self.file_path_label = QLabel("No image selected")
        self.file_path_label.setWordWrap(True)

        select_button = QPushButton("Select Image")
        select_button.clicked.connect(self.open_single_image)

        file_layout.addWidget(self.file_path_label)
        file_layout.addWidget(select_button)

        # Image preview
        preview_group = QGroupBox("Image Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(300, 300)
        self.image_label.setStyleSheet("border: 1px solid gray;")
        self.image_label.setText("No image selected")

        preview_layout.addWidget(self.image_label)

        # Action buttons
        action_group = QGroupBox("Actions")
        action_layout = QVBoxLayout(action_group)

        extract_button = QPushButton("Extract EXIF Data")
        extract_button.clicked.connect(self.extract_exif)

        self.preserve_original_cb = QCheckBox("Preserve original file")
        self.preserve_original_cb.setChecked(True)

        save_exif_button = QPushButton("Save EXIF Changes")
        save_exif_button.clicked.connect(self.save_exif_changes)

        delete_exif_button = QPushButton("Delete All EXIF Data")
        delete_exif_button.clicked.connect(self.delete_all_exif)

        action_layout.addWidget(extract_button)
        action_layout.addWidget(self.preserve_original_cb)
        action_layout.addWidget(save_exif_button)
        action_layout.addWidget(delete_exif_button)

        # Add to left layout
        left_layout.addWidget(file_group)
        left_layout.addWidget(preview_group)
        left_layout.addWidget(action_group)
        left_layout.addStretch()

        # Right side - EXIF data display and editing
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # EXIF data display
        exif_group = QGroupBox("EXIF Data")
        exif_layout = QVBoxLayout(exif_group)

        # Search/filter
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_line_edit = QLineEdit()
        self.search_line_edit.textChanged.connect(self.filter_exif_data)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_line_edit)

        # EXIF data table
        self.exif_table = QTableWidget()
        self.exif_table.setColumnCount(3)
        self.exif_table.setHorizontalHeaderLabels(["Tag", "Value", "Type"])
        self.exif_table.horizontalHeader().setStretchLastSection(True)
        self.exif_table.itemChanged.connect(self.on_exif_item_changed)

        exif_layout.addLayout(search_layout)
        exif_layout.addWidget(self.exif_table)

        right_layout.addWidget(exif_group)

        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        main_layout.addWidget(splitter)

    def create_batch_processing_tab(self):
        """Create the batch processing tab"""
        batch_tab = QWidget()
        self.tab_widget.addTab(batch_tab, "Batch Processing")

        # Main layout
        main_layout = QVBoxLayout(batch_tab)

        # File selection
        file_group = QGroupBox("Image Selection")
        file_layout = QVBoxLayout(file_group)

        file_buttons_layout = QHBoxLayout()
        add_files_button = QPushButton("Add Images")
        add_files_button.clicked.connect(self.open_batch_images)

        clear_files_button = QPushButton("Clear List")
        clear_files_button.clicked.connect(self.clear_batch_files)

        file_buttons_layout.addWidget(add_files_button)
        file_buttons_layout.addWidget(clear_files_button)
        file_buttons_layout.addStretch()

        # File list
        self.batch_file_list = QListWidget()
        self.batch_file_list.setMaximumHeight(200)

        file_layout.addLayout(file_buttons_layout)
        file_layout.addWidget(self.batch_file_list)

        # Batch operations
        operations_group = QGroupBox("Batch Operations")
        operations_layout = QVBoxLayout(operations_group)

        # Operation selection
        operation_layout = QHBoxLayout()
        operation_label = QLabel("Operation:")
        self.operation_combo = QComboBox()
        self.operation_combo.addItems(["Delete All EXIF Data", "Apply EXIF Template"])
        operation_layout.addWidget(operation_label)
        operation_layout.addWidget(self.operation_combo)
        operation_layout.addStretch()

        # Preserve original option
        self.batch_preserve_original_cb = QCheckBox("Preserve original files (create copies)")
        self.batch_preserve_original_cb.setChecked(True)

        # Process button
        process_button = QPushButton("Process Images")
        process_button.clicked.connect(self.process_batch_images)

        operations_layout.addLayout(operation_layout)
        operations_layout.addWidget(self.batch_preserve_original_cb)
        operations_layout.addWidget(process_button)

        # Progress
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)

        self.batch_progress_bar = QProgressBar()
        self.batch_status_list = QListWidget()
        self.batch_status_list.setMaximumHeight(200)

        progress_layout.addWidget(self.batch_progress_bar)
        progress_layout.addWidget(self.batch_status_list)

        # Add to main layout
        main_layout.addWidget(file_group)
        main_layout.addWidget(operations_group)
        main_layout.addWidget(progress_group)

    def open_single_image(self):
        """Open a single image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Image Files (*.jpg *.jpeg *.png *.tiff *.bmp);;All Files (*)"
        )

        if file_path:
            self.current_image_path = file_path
            self.file_path_label.setText(f"Selected: {os.path.basename(file_path)}")
            self.load_image_preview(file_path)
            self.status_bar.showMessage(f"Loaded: {os.path.basename(file_path)}")

    def load_image_preview(self, image_path: str):
        """Load and display image preview"""
        try:
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        except Exception as e:
            self.image_label.setText(f"Error loading image: {str(e)}")

    def extract_exif(self):
        """Extract EXIF data from current image"""
        if not self.current_image_path:
            QMessageBox.warning(self, "Warning", "Please select an image first.")
            return

        self.status_bar.showMessage("Extracting EXIF data...")

        # Create and start processor thread
        self.processor = EXIFProcessor(self.current_image_path, "extract")
        self.processor.finished.connect(self.on_exif_extracted)
        self.processor.error.connect(self.on_processor_error)
        self.processor.start()

    def on_exif_extracted(self, exif_data: dict):
        """Handle extracted EXIF data"""
        self.current_exif_data = exif_data
        self.populate_exif_table(exif_data)
        self.status_bar.showMessage(f"EXIF data extracted ({len(exif_data)} tags)")

    def populate_exif_table(self, exif_data: dict):
        """Populate the EXIF data table"""
        self.exif_table.setRowCount(len(exif_data))

        # Common EXIF tags to highlight
        common_tags = [
            'Make', 'Model', 'DateTime', 'DateTimeOriginal', 'DateTimeDigitized',
            'ExposureTime', 'FNumber', 'ISOSpeedRatings', 'FocalLength',
            'Flash', 'WhiteBalance', 'GPSInfo', 'Orientation', 'XResolution', 'YResolution'
        ]

        row = 0
        for tag, value in exif_data.items():
            # Tag name
            tag_item = QTableWidgetItem(str(tag))
            if tag in common_tags:
                font = QFont()
                font.setBold(True)
                tag_item.setFont(font)

            # Value
            if isinstance(value, dict):
                value_str = json.dumps(value, indent=2)
            else:
                value_str = str(value)

            value_item = QTableWidgetItem(value_str)

            # Type
            type_item = QTableWidgetItem(type(value).__name__)

            self.exif_table.setItem(row, 0, tag_item)
            self.exif_table.setItem(row, 1, value_item)
            self.exif_table.setItem(row, 2, type_item)

            row += 1

        # Resize columns to content
        self.exif_table.resizeColumnsToContents()

    def filter_exif_data(self, text: str):
        """Filter EXIF data table based on search text"""
        for row in range(self.exif_table.rowCount()):
            tag_item = self.exif_table.item(row, 0)
            value_item = self.exif_table.item(row, 1)

            if tag_item and value_item:
                tag_text = tag_item.text().lower()
                value_text = value_item.text().lower()
                search_text = text.lower()

                if search_text in tag_text or search_text in value_text:
                    self.exif_table.setRowHidden(row, False)
                else:
                    self.exif_table.setRowHidden(row, True)

    def on_exif_item_changed(self, item):
        """Handle EXIF table item changes"""
        if item.column() == 1:  # Value column
            row = item.row()
            tag_item = self.exif_table.item(row, 0)

            if tag_item:
                tag = tag_item.text()
                new_value = item.text()

                # Update the current EXIF data
                try:
                    # Try to parse the value as JSON first (for complex values)
                    if new_value.startswith('{') or new_value.startswith('['):
                        self.current_exif_data[tag] = json.loads(new_value)
                    else:
                        self.current_exif_data[tag] = new_value
                except json.JSONDecodeError:
                    self.current_exif_data[tag] = new_value

    def save_exif_changes(self):
        """Save changes to EXIF data"""
        if not self.current_image_path:
            QMessageBox.warning(self, "Warning", "Please select an image first.")
            return

        if not self.current_exif_data:
            QMessageBox.warning(self, "Warning", "No EXIF data to save.")
            return

        # Ask for confirmation
        reply = QMessageBox.question(
            self, "Confirm",
            "This will modify the EXIF data. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.status_bar.showMessage("Saving EXIF changes...")

            # Create backup if preserve original is checked
            if self.preserve_original_cb.isChecked():
                backup_path = self.current_image_path + ".backup"
                shutil.copy2(self.current_image_path, backup_path)

            # Process the changes
            self.processor = EXIFProcessor(self.current_image_path, "edit", self.current_exif_data)
            self.processor.finished.connect(self.on_exif_saved)
            self.processor.error.connect(self.on_processor_error)
            self.processor.start()

    def on_exif_saved(self, result: dict):
        """Handle EXIF save result"""
        self.status_bar.showMessage("EXIF data saved successfully")
        QMessageBox.information(self, "Success", result.get("message", "EXIF data saved"))

    def delete_all_exif(self):
        """Delete all EXIF data from current image"""
        if not self.current_image_path:
            QMessageBox.warning(self, "Warning", "Please select an image first.")
            return

        # Ask for confirmation
        reply = QMessageBox.question(
            self, "Confirm",
            "This will permanently delete all EXIF data. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.status_bar.showMessage("Deleting EXIF data...")

            # Create backup if preserve original is checked
            if self.preserve_original_cb.isChecked():
                backup_path = self.current_image_path + ".backup"
                shutil.copy2(self.current_image_path, backup_path)

            # Delete EXIF data
            self.processor = EXIFProcessor(self.current_image_path, "delete")
            self.processor.finished.connect(self.on_exif_deleted)
            self.processor.error.connect(self.on_processor_error)
            self.processor.start()

    def on_exif_deleted(self, result: dict):
        """Handle EXIF deletion result"""
        self.status_bar.showMessage("EXIF data deleted successfully")
        QMessageBox.information(self, "Success", result.get("message", "EXIF data deleted"))

        # Clear the table
        self.exif_table.setRowCount(0)
        self.current_exif_data = {}

    def on_processor_error(self, error_msg: str):
        """Handle processor errors"""
        self.status_bar.showMessage("Error occurred")
        QMessageBox.critical(self, "Error", error_msg)

    def open_batch_images(self):
        """Open multiple images for batch processing"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "",
            "Image Files (*.jpg *.jpeg *.png *.tiff *.bmp);;All Files (*)"
        )

        if file_paths:
            for file_path in file_paths:
                item = QListWidgetItem(os.path.basename(file_path))
                item.setData(Qt.UserRole, file_path)
                self.batch_file_list.addItem(item)

            self.status_bar.showMessage(f"Added {len(file_paths)} images to batch list")

    def clear_batch_files(self):
        """Clear the batch file list"""
        self.batch_file_list.clear()
        self.batch_status_list.clear()
        self.batch_progress_bar.setValue(0)
        self.status_bar.showMessage("Batch list cleared")

    def process_batch_images(self):
        """Process images in batch"""
        if self.batch_file_list.count() == 0:
            QMessageBox.warning(self, "Warning", "Please add images to process.")
            return

        # Get file paths
        file_paths = []
        for i in range(self.batch_file_list.count()):
            item = self.batch_file_list.item(i)
            file_paths.append(item.data(Qt.UserRole))

        # Get operation
        operation = self.operation_combo.currentText()

        if operation == "Delete All EXIF Data":
            # Ask for confirmation
            reply = QMessageBox.question(
                self, "Confirm",
                f"This will delete EXIF data from {len(file_paths)} images. Continue?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.batch_status_list.clear()
                self.batch_progress_bar.setValue(0)

                # Start batch processor
                self.batch_processor = BatchProcessor(
                    file_paths,
                    "delete",
                    preserve_original=self.batch_preserve_original_cb.isChecked()
                )
                self.batch_processor.progress.connect(self.batch_progress_bar.setValue)
                self.batch_processor.file_processed.connect(self.on_batch_file_processed)
                self.batch_processor.finished.connect(self.on_batch_finished)
                self.batch_processor.error.connect(self.on_batch_error)
                self.batch_processor.start()

                self.status_bar.showMessage("Processing batch...")

    def on_batch_file_processed(self, filename: str, status: str):
        """Handle individual file processing in batch"""
        item = QListWidgetItem(f"{filename}: {status}")
        self.batch_status_list.addItem(item)

    def on_batch_finished(self):
        """Handle batch processing completion"""
        self.status_bar.showMessage("Batch processing completed")
        QMessageBox.information(self, "Success", "Batch processing completed successfully!")

    def on_batch_error(self, error_msg: str):
        """Handle batch processing errors"""
        self.status_bar.showMessage("Batch processing error")
        QMessageBox.critical(self, "Batch Error", error_msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EXIFManager()
    window.show()
    sys.exit(app.exec())