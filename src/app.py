#!/usr/bin/env python3
"""
Application runner
"""
import sys
from PySide6.QtWidgets import QApplication
from .ui.main_window import MainWindow

def run():
    app = QApplication(sys.argv)
    app.setApplicationName("EXIF Data Manager")
    app.setOrganizationName("ImageTools")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())