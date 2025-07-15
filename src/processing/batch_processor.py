#!/usr/bin/env python3
"""
Batch Processor for multiple image operations
"""
import os
import shutil
from pathlib import Path
from typing import List, Callable
from .exif_processor import EXIFProcessor

class BatchProcessor:
    """Processes a batch of images."""

    def __init__(self, file_paths: List[str], operation: str, preserve_original: bool, exif_data: dict = None):
        self.file_paths = file_paths
        self.operation = operation
        self.preserve_original = preserve_original
        self.exif_data = exif_data

    def run(self, progress_callback: Callable):
        """Executes the batch operation."""
        total_files = len(self.file_paths)
        for i, file_path in enumerate(self.file_paths):
            status = "Success"
            try:
                if self.preserve_original:
                    base_path = Path(file_path)
                    new_path = base_path.parent / f"{base_path.stem}_modified{base_path.suffix}"
                    shutil.copy2(file_path, new_path)
                    working_path = str(new_path)
                else:
                    working_path = file_path

                processor = EXIFProcessor(working_path)
                if self.operation == 'delete':
                    processor.delete(preserve_original=False) # Already handled
                elif self.operation == 'edit':
                    processor.edit(self.exif_data, preserve_original=False)

            except Exception as e:
                status = f"Error: {e}"
            
            progress_callback(i + 1, total_files, os.path.basename(file_path), status)