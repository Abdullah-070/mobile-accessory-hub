# COPILOT_MODIFIED: true  # 2025-12-09T10:30:00Z
"""
=============================================================================
Role Login View
=============================================================================
Login screen for Admin or Employee based on selected role.
Enforces role-based authentication:
- Admin login only accepts accounts with role='Admin'
- Employee login only accepts accounts with role='Employee'
Uses passlib pbkdf2_sha256 for password verification.
=============================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from repositories.employee_repository import EmployeeRepository


class RoleLoginView(QWidget):
    """
    Login view for a specific role (Admin or Employee).
    
    Signals:
        login_successful: Emitted with Employee object on success
        back_requested: User wants to go back to role selection
    """
    
    login_successful = Signal(object)
    back_requested = Signal()
    
    def __init__(self, role: str, parent=None):
        """
        Initialize login view.
        
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
        self.setWindowTitle(f"{self.role} Login")
        self.setMinimumSize(450, 500)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        main_layout.addStretch(1)
        
        # Header
        icon_label = QLabel(self.icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48pt;")
        main_layout.addWidget(icon_label)
        
        title = QLabel(f"{self.role} Login")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {self.color};")
        main_layout.addWidget(title)
        
        main_layout.addSpacing(30)
        
        # Form
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)
        
        # Username
        username_label = QLabel("Username")
        username_label.setStyleSheet("font-weight: bold; color: #424242;")
        form_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(45)
        form_layout.addWidget(self.username_input)
        
        # Password
        password_label = QLabel("Password")
        password_label.setStyleSheet("font-weight: bold; color: #424242;")
        form_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(45)
        form_layout.addWidget(self.password_input)
        
        # Remember me
        self.remember_cb = QCheckBox("Remember me")
        form_layout.addWidget(self.remember_cb)
        
        # Error label
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #F44336; font-size: 10pt;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        form_layout.addWidget(self.error_label)
        
        # Login button
        self.login_btn = QPushButton("Login")
        self.login_btn.setMinimumHeight(50)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12pt;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {self.color}DD; }}
            QPushButton:disabled {{ background-color: #BDBDBD; }}
        """)
        form_layout.addWidget(self.login_btn)
        
        main_layout.addWidget(form_frame)
        
        main_layout.addSpacing(20)
        
        # Back button
        self.back_btn = QPushButton("← Back to Role Selection")
        self.back_btn.setFlat(True)
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.setStyleSheet(f"color: {self.color}; font-size: 10pt;")
        main_layout.addWidget(self.back_btn, alignment=Qt.AlignCenter)
        
        main_layout.addStretch(1)
    
    def _connect_signals(self):
        self.login_btn.clicked.connect(self._on_login)
        self.back_btn.clicked.connect(self.back_requested.emit)
        self.password_input.returnPressed.connect(self._on_login)
        self.username_input.returnPressed.connect(self.password_input.setFocus)
    
    def _on_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username:
            self._show_error("Please enter your username")
            return
        if not password:
            self._show_error("Please enter your password")
            return
        
        self.login_btn.setEnabled(False)
        self.login_btn.setText("Logging in...")
        
        try:
            success, employee, message = EmployeeRepository.authenticate(username, password)
            
            if success:
                # Enforce role matches selected login type
                if employee.role.lower() != self.role.lower():
                    if self.role == "Employee" and employee.role == "Admin":
                        self._show_error("Use Admin Login for admin accounts")
                    elif self.role == "Admin" and employee.role == "Employee":
                        self._show_error("Use Employee Login for employee accounts")
                    else:
                        self._show_error(f"This account is not registered as {self.role}")
                    return
                
                self.error_label.hide()
                self.login_successful.emit(employee)
            else:
                self._show_error(message or "Invalid credentials")
        except Exception as e:
            self._show_error(f"Login error: {str(e)}")
        finally:
            self.login_btn.setEnabled(True)
            self.login_btn.setText("Login")
    
    def _show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.show()
    
    def clear_form(self):
        self.username_input.clear()
        self.password_input.clear()
        self.error_label.hide()
