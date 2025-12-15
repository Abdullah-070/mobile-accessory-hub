"""
=============================================================================
Error Reporter Utility
=============================================================================
Purpose: Centralized error handling and logging to prevent multiple popups.
Logs full tracebacks to logs/app_errors.log and shows user-friendly error dialogs.

Why Changed: Replaces scattered try/except blocks with consistent error reporting.
=============================================================================
"""

import os
import traceback
from datetime import datetime
from typing import Optional
from PySide6.QtWidgets import QMessageBox, QTextEdit, QVBoxLayout, QDialog, QPushButton


def ensure_logs_dir():
    """Ensure logs directory exists."""
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir


def log_error(title: str, exc: Exception):
    """Log error to file with full traceback."""
    logs_dir = ensure_logs_dir()
    log_file = os.path.join(logs_dir, 'app_errors.log')
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    error_msg = f"\n{'='*60}\n"
    error_msg += f"[{timestamp}] {title}\n"
    error_msg += f"{'='*60}\n"
    error_msg += f"{traceback.format_exc()}\n"
    
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(error_msg)
    except Exception as e:
        print(f"Failed to write to log file: {e}")


def report_error(title: str, exc: Exception, parent=None):
    """
    Report error to user with expandable details.
    
    Args:
        title: Error dialog title
        exc: Exception object
        parent: Parent widget for dialog
    """
    log_error(title, exc)
    
    # Create error dialog
    dialog = QMessageBox(parent)
    dialog.setIcon(QMessageBox.Critical)
    dialog.setWindowTitle(title)
    dialog.setText(f"An error occurred: {str(exc)}")
    dialog.setInformativeText("Check logs/app_errors.log for details.")
    dialog.setDetailedText(traceback.format_exc())
    dialog.setStandardButtons(QMessageBox.Ok)
    dialog.exec()


def report_warning(title: str, message: str, parent=None):
    """Show warning message to user."""
    QMessageBox.warning(parent, title, message)


def report_info(title: str, message: str, parent=None):
    """Show information message to user."""
    QMessageBox.information(parent, title, message)
