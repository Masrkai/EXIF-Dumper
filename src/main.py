#!/usr/bin/env python3
"""
EXIF Data Manager - Main Application Entry Point
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'UI'))

from PySide6.QtWidgets import QApplication
from UI import EXIFManager

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("EXIF Data Manager")
    app.setOrganizationName("ImageTools")
    
    window = EXIFManager()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()