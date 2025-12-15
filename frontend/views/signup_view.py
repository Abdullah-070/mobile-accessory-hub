"""
=============================================================================
Sign Up View
=============================================================================
This module provides customer registration functionality.

Created to add Sign Up flow for new customers. Employee creation is 
restricted to Admin users only.

Features:
    - Customer registration form
    - Input validation
    - Database insertion via CustomerRepository

=============================================================================
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QDialogButtonBox, QMessageBox,
    QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from repositories.customer_repository import CustomerRepository, Customer
from utils import is_valid_email, is_valid_phone


class SignupDialog(QDialog):
    """
    Dialog for customer self-registration.
    
    Note: Employee creation is NOT allowed here - only Admin can create employees.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Create Account")
        self.setMinimumWidth(500)
        self.setMaximumWidth(500)
        self.setModal(True)
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the dialog UI."""
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_label = QLabel("📝 Customer Registration")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("color: #1976D2;")
        layout.addWidget(header_label)
        
        subtitle = QLabel("Create your customer account to track purchases")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #757575; font-size: 9pt;")
        layout.addWidget(subtitle)
        
        # Form container
        form_frame = QFrame()
        form_frame.setProperty("class", "card")
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(15, 15, 15, 15)
        
        # Name (required)
        self.name_input = QLineEdit()
        self.name_input.setMinimumHeight(40)
        self.name_input.setPlaceholderText("Enter your full name (required)")
        form_layout.addRow("Full Name *:", self.name_input)
        
        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setMinimumHeight(40)
        self.phone_input.setPlaceholderText("e.g., 555-123-4567")
        form_layout.addRow("Phone:", self.phone_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setMinimumHeight(40)
        self.email_input.setPlaceholderText("e.g., you@email.com")
        form_layout.addRow("Email:", self.email_input)
        
        # Address
        self.address_input = QLineEdit()
        self.address_input.setMinimumHeight(40)
        self.address_input.setPlaceholderText("Street address (optional)")
        form_layout.addRow("Address:", self.address_input)
        
        # City
        self.city_input = QLineEdit()
        self.city_input.setMinimumHeight(40)
        self.city_input.setPlaceholderText("City (optional)")
        form_layout.addRow("City:", self.city_input)
        
        layout.addWidget(form_frame)
        
        # Error label
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #F44336; font-size: 9pt;")
        self.error_label.setWordWrap(True)
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.hide()
        layout.addWidget(self.error_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setProperty("class", "secondary")
        self.cancel_btn.setMinimumHeight(45)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        button_layout.addWidget(self.cancel_btn)
        
        self.register_btn = QPushButton("Create Account")
        self.register_btn.setProperty("class", "success")
        self.register_btn.setMinimumHeight(45)
        self.register_btn.setCursor(Qt.PointingHandCursor)
        button_layout.addWidget(self.register_btn)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect UI signals."""
        self.cancel_btn.clicked.connect(self.reject)
        self.register_btn.clicked.connect(self._on_register)
        self.name_input.returnPressed.connect(self.phone_input.setFocus)
        self.phone_input.returnPressed.connect(self.email_input.setFocus)
        self.email_input.returnPressed.connect(self.address_input.setFocus)
        self.address_input.returnPressed.connect(self.city_input.setFocus)
        self.city_input.returnPressed.connect(self._on_register)
    
    def _on_register(self):
        """Handle registration button click."""
        
        # Validate required fields
        name = self.name_input.text().strip()
        if not name:
            self._show_error("Please enter your full name.")
            self.name_input.setFocus()
            return
        
        if len(name) < 2:
            self._show_error("Name must be at least 2 characters.")
            self.name_input.setFocus()
            return
        
        # Validate email if provided
        email = self.email_input.text().strip()
        if email and not is_valid_email(email):
            self._show_error("Please enter a valid email address.")
            self.email_input.setFocus()
            return
        
        # Validate phone if provided
        phone = self.phone_input.text().strip()
        if phone and not is_valid_phone(phone):
            self._show_error("Please enter a valid phone number.")
            self.phone_input.setFocus()
            return
        
        # Disable button during processing
        self.register_btn.setEnabled(False)
        self.register_btn.setText("Creating...")
        
        try:
            # Create customer object
            customer = Customer(
                customer_id=None,  # Will be generated
                customer_name=name,
                phone=phone or None,
                email=email or None,
                address=self.address_input.text().strip() or None,
                city=self.city_input.text().strip() or None
            )
            
            # Insert into database
            new_id = CustomerRepository.create(customer)
            
            if new_id:
                self.accept()
            else:
                self._show_error("Failed to create account. Please try again.")
        
        except Exception as e:
            self._show_error(f"Registration error: {str(e)}")
        
        finally:
            self.register_btn.setEnabled(True)
            self.register_btn.setText("Create Account")
    
    def _show_error(self, message: str):
        """Display an error message."""
        self.error_label.setText(message)
        self.error_label.show()


# =============================================================================
# MODULE TEST
# =============================================================================

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    try:
        with open("styles/theme.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass
    
    dialog = SignupDialog()
    dialog.show()
    
    sys.exit(app.exec())
