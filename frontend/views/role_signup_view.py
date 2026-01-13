"""
=============================================================================
Role Signup View
=============================================================================
Signup screen for Admin or Employee.
- Admin signup requires ADMIN_SETUP_CODE from config.ini
- Employee signup creates pending request in data/pending_employees.json
  (Admin must approve before employee can login)
Uses passlib bcrypt for password hashing.
=============================================================================
"""

import os
import json
import configparser
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from passlib.hash import pbkdf2_sha256
from repositories.employee_repository import EmployeeRepository, Employee


# Pending employees file path
PENDING_FILE = Path(__file__).parent.parent / "data" / "pending_employees.json"


def load_pending_employees() -> list:
    """Load pending employee requests from JSON file."""
    if PENDING_FILE.exists():
        try:
            with open(PENDING_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []


def save_pending_employees(pending: list):
    """Save pending employee requests to JSON file."""
    PENDING_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PENDING_FILE, 'w') as f:
        json.dump(pending, f, indent=2, default=str)


def get_admin_setup_code() -> str:
    """Get admin setup code from config.ini."""
    config = configparser.ConfigParser()
    config_path = Path(__file__).parent.parent / "config.ini"
    if config_path.exists():
        config.read(config_path)
        return config.get('security', 'admin_setup_code', fallback='ADMIN2024')
    return 'ADMIN2024'


class RoleSignupView(QWidget):
    """
    Signup view for Admin or Employee.
    
    Signals:
        signup_successful: Emitted on successful signup
        back_requested: User wants to go back
    """
    
    signup_successful = Signal(str)  # message
    back_requested = Signal()
    
    def __init__(self, role: str, parent=None):
        """
        Initialize signup view.
        
        Args:
            role: 'Admin' or 'Employee'
        """
        super().__init__(parent)
        self.role = role
        self.color = "#1976D2" if role == "Admin" else "#4CAF50"
        self.icon = "👨‍💼" if role == "Admin" else "👤"
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        self.setWindowTitle(f"{self.role} Sign Up")
        self.setMinimumSize(480, 650)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        
        # Header
        icon_label = QLabel(self.icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 40pt;")
        main_layout.addWidget(icon_label)
        
        title = QLabel(f"{self.role} Sign Up")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {self.color};")
        main_layout.addWidget(title)
        
        # Info label
        if self.role == "Admin":
            info_text = "Admin registration requires setup code"
        else:
            info_text = "Employee signup requires admin approval"
        info_label = QLabel(info_text)
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #757575; font-size: 10pt;")
        main_layout.addWidget(info_label)
        
        main_layout.addSpacing(20)
        
        # Form
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        # Full Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full Name *")
        self.name_input.setMinimumHeight(42)
        form_layout.addWidget(self.name_input)
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username *")
        self.username_input.setMinimumHeight(42)
        form_layout.addWidget(self.username_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setMinimumHeight(42)
        form_layout.addWidget(self.email_input)
        
        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone")
        self.phone_input.setMinimumHeight(42)
        form_layout.addWidget(self.phone_input)
        
        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password *")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(42)
        form_layout.addWidget(self.password_input)
        
        # Confirm Password
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirm Password *")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setMinimumHeight(42)
        form_layout.addWidget(self.confirm_input)
        
        # Admin setup code (only for Admin)
        if self.role == "Admin":
            self.code_input = QLineEdit()
            self.code_input.setPlaceholderText("Admin Setup Code *")
            self.code_input.setEchoMode(QLineEdit.Password)
            self.code_input.setMinimumHeight(42)
            form_layout.addWidget(self.code_input)
        
        # Error label
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #F44336; font-size: 10pt;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        form_layout.addWidget(self.error_label)
        
        # Signup button
        self.signup_btn = QPushButton("Create Account")
        self.signup_btn.setMinimumHeight(48)
        self.signup_btn.setCursor(Qt.PointingHandCursor)
        self.signup_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self.color};
                border: 2px solid {self.color};
                border-radius: 6px;
                font-size: 11pt;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {self.color}15; }}
            QPushButton:disabled {{ background-color: #BDBDBD; }}
        """)
        form_layout.addWidget(self.signup_btn)
        
        main_layout.addWidget(form_frame)
        
        main_layout.addSpacing(15)
        
        # Back button
        self.back_btn = QPushButton("← Back to Role Selection")
        self.back_btn.setFlat(True)
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self.color};
                border: 2px solid {self.color};
                border-radius: 6px;
                font-size: 12pt;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {self.color}15; }}
            QPushButton:disabled {{ background-color: #BDBDBD; }}
        """)
        main_layout.addWidget(self.back_btn, alignment=Qt.AlignCenter)
    
    def _connect_signals(self):
        self.signup_btn.clicked.connect(self._on_signup)
        self.back_btn.clicked.connect(self.back_requested.emit)
        self.confirm_input.returnPressed.connect(self._on_signup)
    
    def _on_signup(self):
        name = self.name_input.text().strip()
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        # Validate
        if not name:
            self._show_error("Full name is required")
            return
        if not username:
            self._show_error("Username is required")
            return
        if len(username) < 3:
            self._show_error("Username must be at least 3 characters")
            return
        if not password:
            self._show_error("Password is required")
            return
        if len(password) < 6:
            self._show_error("Password must be at least 6 characters")
            return
        if password != confirm:
            self._show_error("Passwords do not match")
            return
        
        # Admin: verify setup code
        if self.role == "Admin":
            code = self.code_input.text().strip()
            if code != get_admin_setup_code():
                self._show_error("Invalid admin setup code")
                return
        
        self.signup_btn.setEnabled(False)
        self.signup_btn.setText("Creating...")
        
        try:
            # Check if username exists
            existing = EmployeeRepository.get_by_username(username)
            if existing:
                self._show_error("Username already exists")
                return
            
            # Hash password (pbkdf2_sha256 has no length limit)
            password_hash = pbkdf2_sha256.hash(password)
            
            if self.role == "Admin":
                # Create admin directly
                employee = Employee(
                    employee_id=None,
                    employee_name=name,
                    username=username,
                    password_hash=password_hash,
                    role="Admin",
                    email=email or None,
                    phone=phone or None
                )
                new_id = EmployeeRepository.create_from_signup(employee)
                if new_id:
                    self.signup_successful.emit("Admin account created! You can now login.")
                else:
                    self._show_error("Failed to create account")
            else:
                # Employee: save to pending file
                pending = load_pending_employees()
                pending.append({
                    'name': name,
                    'username': username,
                    'email': email,
                    'phone': phone,
                    'password_hash': password_hash,
                    'requested_at': datetime.now().isoformat(),
                    'status': 'pending'
                })
                save_pending_employees(pending)
                self.signup_successful.emit(
                    "Signup request submitted!\n"
                    "Please wait for admin approval before logging in."
                )
        
        except Exception as e:
            self._show_error(f"Signup error: {str(e)}")
        finally:
            self.signup_btn.setEnabled(True)
            self.signup_btn.setText("Create Account")
    
    def _show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.show()
        self.signup_btn.setEnabled(True)
        self.signup_btn.setText("Create Account")
    
    def clear_form(self):
        self.name_input.clear()
        self.username_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        self.password_input.clear()
        self.confirm_input.clear()
        if self.role == "Admin":
            self.code_input.clear()
        self.error_label.hide()
