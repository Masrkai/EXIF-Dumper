#!/usr/bin/env python3
"""
EXIF Data Manager - Main Application Entry Point
"""
import os
import sys

# Add src to the Python path
sys.path.append(os.path.dirname(__file__))

from src.app import run

if __name__ == "__main__":
    run()