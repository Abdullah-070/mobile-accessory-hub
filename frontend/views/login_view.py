"""
=============================================================================
Login View
=============================================================================
This module provides the login screen for user authentication.

Features:
    - Username and password input
    - Password visibility toggle
    - Remember me option
    - Login validation with bcrypt
    - Role-based access determination
    - Error message display

The login process:
    1. User enters username and password
    2. System validates against EMPLOYEE table
    3. Password is verified using bcrypt hash
    4. On success, user role is loaded and dashboard is shown
    5. On failure, error message is displayed

=============================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QFrame, QSpacerItem, QSizePolicy,
    QMessageBox, QDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap, QIcon

from repositories.employee_repository import EmployeeRepository, Employee


class LoginView(QWidget):
    """
    Login screen widget for user authentication.
    
    Signals:
        login_successful: Emitted when login succeeds, passes Employee object
        
    Usage:
        login = LoginView()
        login.login_successful.connect(on_login_success)
        login.show()
    """
    
    # Signal emitted when login is successful
    # Passes the authenticated Employee object
    login_successful = Signal(object)
    
    def __init__(self, parent=None):
        """
        Initialize the login view.
        
        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        
        # Store the currently logged-in user
        self.current_user: Employee = None
        
        # Set up the UI
        self._setup_ui()
        
        # Connect signals
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the user interface components."""
        
        # Set window properties
        self.setWindowTitle("Login - Mobile Accessory Inventory")
        self.setMinimumSize(400, 500)
        self.setMaximumSize(500, 600)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        # Add stretch to center vertically
        main_layout.addStretch(1)
        
        # =====================================================================
        # HEADER SECTION
        # =====================================================================
        
        # Logo/Icon placeholder
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setText("📱")  # Placeholder emoji
        self.logo_label.setStyleSheet("font-size: 48pt;")
        main_layout.addWidget(self.logo_label)
        
        # Title
        self.title_label = QLabel("Mobile Accessory")
        self.title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #1976D2;")
        main_layout.addWidget(self.title_label)
        
        # Subtitle
        self.subtitle_label = QLabel("Inventory Management System")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet("color: #757575; font-size: 11pt;")
        main_layout.addWidget(self.subtitle_label)
        
        # Spacer
        main_layout.addSpacing(30)
        
        # =====================================================================
        # LOGIN FORM
        # =====================================================================
        
        # Form container with card-like styling
        form_container = QFrame()
        form_container.setProperty("class", "card")
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(15)
        
        # Username field
        username_label = QLabel("Username")
        username_label.setProperty("class", "field-label")
        form_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(45)
        form_layout.addWidget(self.username_input)
        
        # Password field
        password_label = QLabel("Password")
        password_label.setProperty("class", "field-label")
        form_layout.addWidget(password_label)
        
        # Password input with visibility toggle
        password_container = QHBoxLayout()
        password_container.setSpacing(0)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(45)
        password_container.addWidget(self.password_input)
        
        # Toggle password visibility button
        self.toggle_password_btn = QPushButton("👁")
        self.toggle_password_btn.setProperty("class", "icon")
        self.toggle_password_btn.setMaximumWidth(45)
        self.toggle_password_btn.setMinimumHeight(45)
        self.toggle_password_btn.setCheckable(True)
        self.toggle_password_btn.setToolTip("Show/Hide Password")
        password_container.addWidget(self.toggle_password_btn)
        
        form_layout.addLayout(password_container)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox("Remember me")
        form_layout.addWidget(self.remember_checkbox)
        
        # Error message label (hidden by default)
        self.error_label = QLabel()
        self.error_label.setProperty("class", "error")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        form_layout.addWidget(self.error_label)
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setMinimumHeight(50)
        self.login_button.setCursor(Qt.PointingHandCursor)
        form_layout.addWidget(self.login_button)
        
        # Forgot password link
        self.forgot_password_btn = QPushButton("Forgot Password?")
        self.forgot_password_btn.setProperty("class", "link")
        self.forgot_password_btn.setFlat(True)
        self.forgot_password_btn.setCursor(Qt.PointingHandCursor)
        self.forgot_password_btn.setStyleSheet(
            "border: none; color: #2196F3; text-decoration: underline; font-size: 9pt;"
        )
        
        # Sign up link
        self.signup_btn = QPushButton("Create Account")
        self.signup_btn.setProperty("class", "link")
        self.signup_btn.setFlat(True)
        self.signup_btn.setCursor(Qt.PointingHandCursor)
        self.signup_btn.setStyleSheet(
            "border: none; color: #4CAF50; text-decoration: underline; font-size: 9pt; font-weight: bold;"
        )
        
        # Links layout
        links_layout = QHBoxLayout()
        links_layout.addWidget(self.forgot_password_btn)
        links_layout.addStretch()
        links_layout.addWidget(self.signup_btn)
        form_layout.addLayout(links_layout)
        
        main_layout.addWidget(form_container)
        
        # Add stretch to center vertically
        main_layout.addStretch(1)
        
        # =====================================================================
        # FOOTER
        # =====================================================================
        
        footer_label = QLabel("© 2025 Mobile Accessory Inventory System")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: #9E9E9E; font-size: 9pt;")
        main_layout.addWidget(footer_label)
    
    def _connect_signals(self):
        """Connect UI signals to their handler methods."""
        
        # Login button click
        self.login_button.clicked.connect(self._on_login_clicked)
        
        # Enter key in password field triggers login
        self.password_input.returnPressed.connect(self._on_login_clicked)
        
        # Enter key in username field moves to password
        self.username_input.returnPressed.connect(self.password_input.setFocus)
        
        # Toggle password visibility
        self.toggle_password_btn.toggled.connect(self._toggle_password_visibility)
        
        # Forgot password
        self.forgot_password_btn.clicked.connect(self._on_forgot_password)
        
        # Sign up
        self.signup_btn.clicked.connect(self._on_signup_clicked)
    
    def _toggle_password_visibility(self, checked: bool):
        """
        Toggle password field visibility.
        
        Args:
            checked: True to show password, False to hide
        """
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_btn.setText("🔒")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_btn.setText("👁")
    
    def _on_login_clicked(self):
        """Handle login button click."""
        
        # Get input values
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validate inputs
        if not username:
            self._show_error("Please enter your username")
            self.username_input.setFocus()
            return
        
        if not password:
            self._show_error("Please enter your password")
            self.password_input.setFocus()
            return
        
        # Disable login button during authentication
        self.login_button.setEnabled(False)
        self.login_button.setText("Logging in...")
        
        try:
            # Attempt authentication
            success, employee, message = EmployeeRepository.authenticate(username, password)
            
            if success:
                # Store the logged-in user
                self.current_user = employee
                
                # Clear the form
                self._clear_form()
                
                # Hide any error message
                self.error_label.hide()
                
                # Emit success signal with the employee object
                self.login_successful.emit(employee)
            else:
                # Show error message
                self._show_error(message)
                self.password_input.clear()
                self.password_input.setFocus()
        
        except Exception as e:
            # Handle unexpected errors
            self._show_error(f"Login error: {str(e)}")
        
        finally:
            # Re-enable login button
            self.login_button.setEnabled(True)
            self.login_button.setText("Login")
    
    def _on_forgot_password(self):
        """Handle forgot password click."""
        
        QMessageBox.information(
            self,
            "Forgot Password",
            "Please contact your system administrator to reset your password.\n\n"
            "Admin Contact: admin@store.com",
            QMessageBox.Ok
        )
    
    def _on_signup_clicked(self):
        """Handle sign up button click - show customer registration dialog."""
        from views.signup_view import SignupDialog
        
        dialog = SignupDialog(self)
        if dialog.exec() == QDialog.Accepted:
            QMessageBox.information(
                self,
                "Registration Successful",
                "Your account has been created successfully!\n"
                "You can now login with your credentials.",
                QMessageBox.Ok
            )
    
    def _show_error(self, message: str):
        """
        Display an error message.
        
        Args:
            message: Error message to display
        """
        self.error_label.setText(message)
        self.error_label.show()
    
    def _clear_form(self):
        """Clear all form inputs."""
        self.username_input.clear()
        self.password_input.clear()
        self.remember_checkbox.setChecked(False)
        self.error_label.hide()
    
    def set_focus_username(self):
        """Set focus to the username input field."""
        self.username_input.setFocus()


# =============================================================================
# MODULE TEST
# =============================================================================

if __name__ == "__main__":
    """Test the login view when running this module directly."""
    
    import sys
    from PySide6.QtWidgets import QApplication
    
    # Create application
    app = QApplication(sys.argv)
    
    # Load stylesheet
    try:
        with open("styles/theme.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Stylesheet not found, using default styling")
    
    # Create and show login view
    login = LoginView()
    
    def on_login_success(employee):
        print(f"Login successful! Welcome, {employee.employee_name}")
        print(f"Role: {employee.role}")
    
    login.login_successful.connect(on_login_success)
    login.show()
    
    # Run application
    sys.exit(app.exec())
