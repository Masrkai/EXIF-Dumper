#!/usr/bin/env python3
"""
Single Image Tab Widget
"""
import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QCheckBox, QSplitter, QTableWidget, QTableWidgetItem,
    QLineEdit, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont

def _exif_value_to_str(value):
    """Safely converts any EXIF value to a displayable string."""
    if isinstance(value, bytes):
        # Decode bytes, replacing errors
        return value.decode('utf-8', errors='replace')
    if isinstance(value, dict):
        # For dictionaries (like GPSInfo), serialize with a custom handler
        def json_serializer(obj):
            if isinstance(obj, bytes):
                return obj.decode('utf-8', errors='replace')
            # Handle IFDRational and other non-standard types by converting to string
            return str(obj)
        return json.dumps(value, indent=2, default=json_serializer)
    # For IFDRational, numbers, and anything else, its string representation is best
    return str(value)


class SingleImageTab(QWidget):
    """UI for the Single Image Processing tab."""
    def __init__(self):
        super().__init__()
        self.current_exif_data = {}
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components for this tab."""
        main_layout = QHBoxLayout(self)

        # --- Left Side ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # File selection group
        file_group = QGroupBox("Image Selection")
        file_layout = QVBoxLayout(file_group)
        self.file_path_label = QLabel("No image selected")
        self.file_path_label.setWordWrap(True)
        self.select_button = QPushButton("Select Image")
        file_layout.addWidget(self.file_path_label)
        file_layout.addWidget(self.select_button)

        # Image preview group
        preview_group = QGroupBox("Image Preview")
        preview_layout = QVBoxLayout(preview_group)
        self.image_label = QLabel("Image Preview")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(300, 300)
        self.image_label.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        preview_layout.addWidget(self.image_label)

        # Actions group
        action_group = QGroupBox("Actions")
        action_layout = QVBoxLayout(action_group)
        self.extract_button = QPushButton("Extract EXIF Data")
        self.preserve_original_cb = QCheckBox("Preserve original file (creates a backup)")
        self.preserve_original_cb.setChecked(True)
        self.save_exif_button = QPushButton("Save EXIF Changes")
        self.delete_exif_button = QPushButton("Delete All EXIF Data")
        action_layout.addWidget(self.extract_button)
        action_layout.addWidget(self.preserve_original_cb)
        action_layout.addWidget(self.save_exif_button)
        action_layout.addWidget(self.delete_exif_button)

        left_layout.addWidget(file_group)
        left_layout.addWidget(preview_group)
        left_layout.addWidget(action_group)
        left_layout.addStretch()

        # --- Right Side ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        exif_group = QGroupBox("EXIF Data")
        exif_layout = QVBoxLayout(exif_group)

        # Search/filter
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_line_edit = QLineEdit()
        self.search_line_edit.setPlaceholderText("Filter by tag or value...")
        self.search_line_edit.textChanged.connect(self.filter_exif_data)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_line_edit)

        # EXIF data table
        self.exif_table = QTableWidget()
        self.exif_table.setColumnCount(3)
        self.exif_table.setHorizontalHeaderLabels(["Tag", "Value", "Type"])
        self.exif_table.horizontalHeader().setStretchLastSection(True)
        self.exif_table.setSortingEnabled(True)

        exif_layout.addLayout(search_layout)
        exif_layout.addWidget(self.exif_table)
        right_layout.addWidget(exif_group)

        # --- Splitter ---
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        main_layout.addWidget(splitter)

    def set_image_preview(self, image_path: str):
        """Load and display the image preview."""
        self.file_path_label.setText(f"Selected: {os.path.basename(image_path)}")
        try:
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        except Exception as e:
            self.image_label.setText(f"Error loading preview:\n{e}")

    def populate_exif_table(self, exif_data: dict):
        """Populate the EXIF data table."""
        self.current_exif_data = exif_data
        self.exif_table.setSortingEnabled(False) # Disable sorting during population
        self.exif_table.setRowCount(0) # Clear table
        self.exif_table.setRowCount(len(exif_data))

        common_tags = [
            'Make', 'Model', 'DateTime', 'DateTimeOriginal', 'DateTimeDigitized',
            'ExposureTime', 'FNumber', 'ISOSpeedRatings', 'FocalLength',
            'Flash', 'WhiteBalance', 'GPSInfo', 'Orientation'
        ]

        row = 0
        for tag, value in exif_data.items():
            tag_item = QTableWidgetItem(str(tag))
            tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable) # Make tag non-editable
            
            if tag in common_tags:
                font = QFont()
                font.setBold(True)
                tag_item.setFont(font)

            # Use the new helper function to safely convert any value to a string
            value_str = _exif_value_to_str(value)
            value_item = QTableWidgetItem(value_str)
            
            type_item = QTableWidgetItem(type(value).__name__)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable) # Make type non-editable

            self.exif_table.setItem(row, 0, tag_item)
            self.exif_table.setItem(row, 1, value_item)
            self.exif_table.setItem(row, 2, type_item)
            row += 1

        self.exif_table.resizeColumnsToContents()
        self.exif_table.setSortingEnabled(True)

    def filter_exif_data(self, text: str):
        """Filter the EXIF table based on search text."""
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

    def get_edited_data(self) -> dict:
        """Reads the current state of the table to get edited data."""
        # This is a simplified approach. A more robust solution would track
        # actual changes. For now, we rebuild the data from the table.
        edited_data = {}
        for row in range(self.exif_table.rowCount()):
            tag = self.exif_table.item(row, 0).text()
            value_str = self.exif_table.item(row, 1).text()
            original_value = self.current_exif_data.get(tag)

            # Try to convert back to original type
            try:
                if isinstance(original_value, int):
                    edited_data[tag] = int(value_str)
                elif isinstance(original_value, float):
                    edited_data[tag] = float(value_str)
                elif isinstance(original_value, dict):
                     edited_data[tag] = json.loads(value_str)
                else:
                    edited_data[tag] = value_str
            except (ValueError, json.JSONDecodeError):
                edited_data[tag] = value_str # Keep as string if conversion fails
        
        return edited_data
