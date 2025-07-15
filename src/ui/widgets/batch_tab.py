#!/usr/bin/env python3
"""
Batch Processing Tab Widget
"""
import os
from typing import List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton,
    QListWidget, QComboBox, QCheckBox, QProgressBar, QLabel, QListWidgetItem
)
from PySide6.QtCore import Qt

class BatchProcessingTab(QWidget):
    """UI for the Batch Processing tab."""
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components for this tab."""
        main_layout = QVBoxLayout(self)

        # File selection group
        file_group = QGroupBox("Image Selection")
        file_layout = QVBoxLayout(file_group)
        
        file_buttons_layout = QHBoxLayout()
        self.add_files_button = QPushButton("Add Images")
        self.clear_files_button = QPushButton("Clear List")
        file_buttons_layout.addWidget(self.add_files_button)
        file_buttons_layout.addWidget(self.clear_files_button)
        file_buttons_layout.addStretch()

        self.batch_file_list = QListWidget()
        self.batch_file_list.setSelectionMode(QListWidget.ExtendedSelection)

        file_layout.addLayout(file_buttons_layout)
        file_layout.addWidget(self.batch_file_list)

        # Operations group
        operations_group = QGroupBox("Batch Operations")
        operations_layout = QVBoxLayout(operations_group)

        operation_layout = QHBoxLayout()
        operation_label = QLabel("Operation:")
        self.operation_combo = QComboBox()
        self.operation_combo.addItems(["Delete All EXIF Data"]) # Add more later
        operation_layout.addWidget(operation_label)
        operation_layout.addWidget(self.operation_combo)
        operation_layout.addStretch()

        self.batch_preserve_original_cb = QCheckBox("Preserve original files (create copies)")
        self.batch_preserve_original_cb.setChecked(True)

        self.process_button = QPushButton("Start Batch Process")
        
        operations_layout.addLayout(operation_layout)
        operations_layout.addWidget(self.batch_preserve_original_cb)
        operations_layout.addWidget(self.process_button)

        # Progress group
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        self.batch_progress_bar = QProgressBar()
        self.batch_status_list = QListWidget()
        progress_layout.addWidget(self.batch_progress_bar)
        progress_layout.addWidget(self.batch_status_list)

        main_layout.addWidget(file_group)
        main_layout.addWidget(operations_group)
        main_layout.addWidget(progress_group)

    def add_files(self, file_paths: List[str]):
        """Add a list of file paths to the file list widget."""
        for path in file_paths:
            # Avoid adding duplicates
            if not self.batch_file_list.findItems(os.path.basename(path), Qt.MatchExactly):
                item = QListWidgetItem(os.path.basename(path))
                item.setData(Qt.UserRole, path) # Store full path in user data
                self.batch_file_list.addItem(item)
    
    def get_file_list(self) -> List[str]:
        """Return a list of full file paths from the list widget."""
        paths = []
        for i in range(self.batch_file_list.count()):
            item = self.batch_file_list.item(i)
            paths.append(item.data(Qt.UserRole))
        return paths

    def clear_file_list(self):
        """Clear all items from the file list."""
        self.batch_file_list.clear()

    def reset_progress(self):
        """Reset the progress bar and status list."""
        self.batch_progress_bar.setValue(0)
        self.batch_status_list.clear()
