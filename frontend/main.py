"""
=============================================================================
Mobile Accessory Inventory Management System
=============================================================================

Main entry point for the desktop application.

This application provides a complete inventory management solution for
mobile accessory retail stores with features including:

    - User authentication with role-based access
    - Product catalog management
    - Inventory tracking with low-stock alerts
    - Point of Sale (POS) interface
    - Customer and supplier management
    - Purchase order processing
    - Sales reporting

Requirements:
    - Python 3.10+
    - PySide6
    - pyodbc
    - passlib[bcrypt]
    - SQL Server with MobileAccessoryInventory database

Usage:
    python main.py

Author: Mobile Accessory Inventory Team
Version: 1.0.0

=============================================================================
"""

import sys
import os
import ctypes

# Add the frontend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Windows App User Model ID for proper taskbar icon display
# This ensures the custom icon appears in the taskbar instead of Python icon
try:
    myappid = 'mobileaccessory.inventory.system.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass  # Non-Windows or older Windows version

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon

from views.main_window import MainWindow


def load_stylesheet(app: QApplication) -> bool:
    """
    Load the application stylesheet.
    
    Args:
        app: QApplication instance
        
    Returns:
        True if stylesheet loaded successfully, False otherwise
    """
    stylesheet_path = os.path.join(
        os.path.dirname(__file__),
        "styles",
        "theme.qss"
    )
    
    try:
        with open(stylesheet_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
        return True
    except FileNotFoundError:
        print(f"Warning: Stylesheet not found at {stylesheet_path}")
        return False
    except Exception as e:
        print(f"Warning: Failed to load stylesheet: {e}")
        return False


def setup_application() -> QApplication:
    """
    Create and configure the application instance.
    
    Returns:
        Configured QApplication instance
    """
    # Enable high DPI scaling (important for modern displays)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Mobile Accessory Inventory")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Mobile Accessory Store")
    app.setOrganizationDomain("mobileaccessory.local")
    
    # Set default font
    font = QFont()
    font.setFamily("Segoe UI")  # Windows default
    font.setPointSize(10)
    app.setFont(font)
    
    
    # Set application icon for taskbar and shortcuts
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "app_icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Load stylesheet
    load_stylesheet(app)
    
    return app


def check_database_connection() -> bool:
    """
    Verify database connection is working.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        from db import get_connection
        
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False


def show_database_error(app: QApplication):
    """
    Show a database connection error dialog.
    
    Args:
        app: QApplication instance
    """
    QMessageBox.critical(
        None,
        "Database Connection Error",
        "Failed to connect to the database.\n\n"
        "Please check the following:\n"
        "1. SQL Server is running\n"
        "2. Database 'MobileAccessoryInventory' exists\n"
        "3. Connection settings in config.ini are correct\n"
        "4. ODBC Driver 18 for SQL Server is installed\n\n"
        "See the README.md file for setup instructions.",
        QMessageBox.Ok
    )


def main():
    """Main entry point for the application."""
    
    print("=" * 60)
    print("Mobile Accessory Inventory Management System")
    print("=" * 60)
    print("Starting application...")
    
    # Create application
    app = setup_application()
    
    # Check database connection
    print("Checking database connection...")
    if not check_database_connection():
        show_database_error(app)
        sys.exit(1)
    
    print("Database connection successful!")
    
    # Create main window
    print("Loading main window...")
    main_window = MainWindow()
    main_window.show()
    
    print("Application ready!")
    print("=" * 60)
    
    # Run application event loop
    exit_code = app.exec()
    
    print("Application closed.")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
