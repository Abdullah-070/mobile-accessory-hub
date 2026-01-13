"""
=============================================================================
Customer View
=============================================================================
This module provides the customer management screen.

Features:
    - View all customers
    - Search by name, phone, or email
    - Add new customer
    - Edit existing customer
    - Delete customer (with confirmation)

=============================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
    QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QKeySequence, QShortcut

from repositories.customer_repository import CustomerRepository, Customer
from utils import is_valid_email, is_valid_phone


class CustomerFormDialog(QDialog):
    """Dialog for adding/editing a customer."""
    
    def __init__(self, customer: Customer = None, parent=None):
        super().__init__(parent)
        
        self.customer = customer
        self.is_edit = customer is not None
        
        self.setWindowTitle("Edit Customer" if self.is_edit else "Add Customer")
        self.setMinimumWidth(550)
        self.setModal(True)
        
        self._setup_ui()
        
        if self.is_edit:
            self._populate_form()
    
    def _setup_ui(self):
        """Set up the dialog UI."""
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Name (required)
        self.name_input = QLineEdit()
        self.name_input.setMinimumHeight(35)
        self.name_input.setPlaceholderText("Customer name (required)")
        form_layout.addRow("Name *:", self.name_input)
        
        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setMinimumHeight(35)
        self.phone_input.setPlaceholderText("e.g., 555-1234")
        form_layout.addRow("Phone:", self.phone_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setMinimumHeight(35)
        self.email_input.setPlaceholderText("e.g., customer@email.com")
        form_layout.addRow("Email:", self.email_input)
        
        # Address
        self.address_input = QLineEdit()
        self.address_input.setMinimumHeight(35)
        self.address_input.setPlaceholderText("Street address")
        form_layout.addRow("Address:", self.address_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        
        ok_btn = button_box.button(QDialogButtonBox.Ok)
        ok_btn.setText("Save")
        ok_btn.setMinimumHeight(40)
        
        layout.addWidget(button_box)
    
    def _populate_form(self):
        """Populate form with existing customer data."""
        if self.customer:
            self.name_input.setText(self.customer.customer_name or "")
            self.phone_input.setText(self.customer.phone_number or "")
            self.email_input.setText(self.customer.email or "")
            self.address_input.setText(self.customer.address or "")
    
    def _on_accept(self):
        """Validate and accept the dialog."""
        
        # Validate required fields
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(
                self, "Validation Error",
                "Customer name is required.",
                QMessageBox.Ok
            )
            self.name_input.setFocus()
            return
        
        # Validate email if provided
        email = self.email_input.text().strip()
        if email and not is_valid_email(email):
            QMessageBox.warning(
                self, "Validation Error",
                "Please enter a valid email address.",
                QMessageBox.Ok
            )
            self.email_input.setFocus()
            return
        
        self.accept()
    
    def get_customer(self) -> Customer:
        """Get the customer object from form data."""
        return Customer(
            customer_id=self.customer.customer_id if self.customer else None,
            customer_name=self.name_input.text().strip(),
            phone_number=self.phone_input.text().strip() or None,
            email=self.email_input.text().strip() or None,
            address=self.address_input.text().strip() or None
        )


class CustomerView(QWidget):
    """
    Widget for managing customers.
    
    Signals:
        navigate_back: Go back to previous view
    """
    
    navigate_back = Signal()
    
    def __init__(self, parent=None):
        """Initialize the customer view."""
        super().__init__(parent)
        
        # Data
        self.customers = []
        self.search_text = ""
        
        # Set up UI
        self._setup_ui()
        
        # Connect signals
        self._connect_signals()
        
        # Set up shortcuts
        self._setup_shortcuts()
        
        # Load data
        self.refresh_data()
    
    def _setup_ui(self):
        """Set up the user interface components."""
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # =====================================================================
        # HEADER
        # =====================================================================
        
        header_layout = QHBoxLayout()
        
        title_label = QLabel("👥 Customer Management")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Add button
        self.add_button = QPushButton("+ Add Customer")
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.setMinimumHeight(40)
        header_layout.addWidget(self.add_button)
        
        main_layout.addLayout(header_layout)
        
        # =====================================================================
        # FILTER BAR
        # =====================================================================
        
        filter_frame = QFrame()
        filter_frame.setProperty("class", "card")
        filter_layout = QHBoxLayout(filter_frame)
        
        search_label = QLabel("Search:")
        filter_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, phone, or email...")
        self.search_input.setMinimumWidth(300)
        self.search_input.setClearButtonEnabled(True)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addStretch()
        
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.setProperty("class", "secondary")
        filter_layout.addWidget(self.refresh_button)
        
        main_layout.addWidget(filter_frame)
        
        # =====================================================================
        # CUSTOMER TABLE
        # =====================================================================
        
        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(6)
        self.customer_table.setHorizontalHeaderLabels([
            "ID", "Name", "Phone", "Email", "Address", "Actions"
        ])
        
        self.customer_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.customer_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.customer_table.setAlternatingRowColors(True)
        self.customer_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.customer_table.setSortingEnabled(True)
        self.customer_table.verticalHeader().setVisible(False)
        self.customer_table.verticalHeader().setDefaultSectionSize(100)
        
        header = self.customer_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.customer_table.setColumnWidth(5, 200)
        
        main_layout.addWidget(self.customer_table)
        
        # =====================================================================
        # FOOTER
        # =====================================================================
        
        footer_layout = QHBoxLayout()
        
        self.status_label = QLabel("0 customers")
        self.status_label.setStyleSheet("color: #757575;")
        footer_layout.addWidget(self.status_label)
        
        footer_layout.addStretch()
        
        main_layout.addLayout(footer_layout)
    
    def _connect_signals(self):
        """Connect UI signals."""
        
        self.add_button.clicked.connect(self._add_customer)
        self.search_input.textChanged.connect(self._on_search_changed)
        self.refresh_button.clicked.connect(self.refresh_data)
        self.customer_table.doubleClicked.connect(self._edit_selected_customer)
    
    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        
        shortcut_add = QShortcut(QKeySequence("Ctrl+N"), self)
        shortcut_add.activated.connect(self._add_customer)
        
        shortcut_search = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut_search.activated.connect(self.search_input.setFocus)
        
        shortcut_refresh = QShortcut(QKeySequence("F5"), self)
        shortcut_refresh.activated.connect(self.refresh_data)
        
        shortcut_delete = QShortcut(QKeySequence("Delete"), self)
        shortcut_delete.activated.connect(self._delete_selected_customer)
    
    def refresh_data(self):
        """Refresh customer data from database."""
        
        try:
            # Exclude walk-in customer (C000) from display
            self.customers = CustomerRepository.get_all(include_walkin=False)
            self._apply_filter()
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Failed to load customers: {str(e)}",
                QMessageBox.Ok
            )
    
    def _on_search_changed(self, text: str):
        """Handle search text change."""
        self.search_text = text.strip().lower()
        self._apply_filter()
    
    def _apply_filter(self):
        """Apply search filter and update table."""
        
        filtered = self.customers
        
        if self.search_text:
            filtered = [
                c for c in filtered
                if (c.customer_name and self.search_text in c.customer_name.lower()) or
                   (c.phone_number and self.search_text in c.phone_number.lower()) or
                   (c.email and self.search_text in c.email.lower())
            ]
        
        self._populate_table(filtered)
        self.status_label.setText(f"{len(filtered)} of {len(self.customers)} customers")
    
    def _populate_table(self, customers):
        """Populate the table with customer data."""
        
        self.customer_table.setRowCount(len(customers))
        
        for row, customer in enumerate(customers):
            # ID
            id_item = QTableWidgetItem(str(customer.customer_id))
            id_item.setData(Qt.UserRole, customer.customer_id)
            self.customer_table.setItem(row, 0, id_item)
            
            # Name
            self.customer_table.setItem(row, 1, QTableWidgetItem(customer.customer_name or ""))
            
            # Phone
            self.customer_table.setItem(row, 2, QTableWidgetItem(customer.phone_number or ""))
            
            # Email
            self.customer_table.setItem(row, 3, QTableWidgetItem(customer.email or ""))
            
            # Address
            self.customer_table.setItem(row, 4, QTableWidgetItem(customer.address or ""))
            
            # Actions
            self._add_action_buttons(row, customer)
    
    def _add_action_buttons(self, row: int, customer: Customer):
        """Add action buttons to table row."""
        
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(5, 5, 5, 5)
        actions_layout.setSpacing(8)
        
        # Edit button with blue border and text
        edit_btn = QPushButton("Edit")
        edit_btn.setFixedWidth(70)
        edit_btn.setFixedHeight(40)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid #2196F3;
                color: #2196F3;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E3F2FD;
            }
            QPushButton:pressed {
                background-color: #BBDEFB;
            }
        """)
        edit_btn.setToolTip("Edit customer")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(lambda: self._edit_customer(customer))
        actions_layout.addWidget(edit_btn)
        
        # Delete button with red border and text
        delete_btn = QPushButton("Delete")
        delete_btn.setFixedWidth(85)
        delete_btn.setFixedHeight(40)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid #F44336;
                color: #F44336;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFEBEE;
            }
            QPushButton:pressed {
                background-color: #FFCDD2;
            }
        """)
        delete_btn.setToolTip("Delete customer")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(lambda: self._delete_customer(customer))
        actions_layout.addWidget(delete_btn)
        
        self.customer_table.setCellWidget(row, 5, actions_widget)
    
    def _add_customer(self):
        """Show dialog to add a new customer."""
        
        dialog = CustomerFormDialog(parent=self)
        
        if dialog.exec() == QDialog.Accepted:
            customer = dialog.get_customer()
            
            try:
                new_id = CustomerRepository.create(customer)
                
                if new_id:
                    QMessageBox.information(
                        self, "Success",
                        f"Customer '{customer.customer_name}' created successfully.",
                        QMessageBox.Ok
                    )
                    self.refresh_data()
                else:
                    QMessageBox.warning(
                        self, "Error",
                        "Failed to create customer.",
                        QMessageBox.Ok
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error",
                    f"Failed to create customer: {str(e)}",
                    QMessageBox.Ok
                )
    
    def _edit_customer(self, customer: Customer):
        """Show dialog to edit a customer."""
        
        dialog = CustomerFormDialog(customer=customer, parent=self)
        
        if dialog.exec() == QDialog.Accepted:
            updated_customer = dialog.get_customer()
            
            try:
                success = CustomerRepository.update(updated_customer)
                
                if success:
                    QMessageBox.information(
                        self, "Success",
                        "Customer updated successfully.",
                        QMessageBox.Ok
                    )
                    self.refresh_data()
                else:
                    QMessageBox.warning(
                        self, "Error",
                        "Failed to update customer.",
                        QMessageBox.Ok
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error",
                    f"Failed to update customer: {str(e)}",
                    QMessageBox.Ok
                )
    
    def _edit_selected_customer(self):
        """Edit the currently selected customer."""
        row = self.customer_table.currentRow()
        if row >= 0:
            customer_id = self.customer_table.item(row, 0).data(Qt.UserRole)
            for customer in self.customers:
                if customer.customer_id == customer_id:
                    self._edit_customer(customer)
                    break
    
    def _delete_customer(self, customer: Customer):
        """Delete a customer after confirmation."""
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{customer.customer_name}'?\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = CustomerRepository.delete(customer.customer_id)
                
                if success:
                    QMessageBox.information(
                        self, "Success",
                        "Customer deleted successfully.",
                        QMessageBox.Ok
                    )
                    self.refresh_data()
                else:
                    QMessageBox.warning(
                        self, "Error",
                        "Failed to delete customer. They may have related sales records.",
                        QMessageBox.Ok
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error",
                    f"Failed to delete customer: {str(e)}",
                    QMessageBox.Ok
                )
    
    def _delete_selected_customer(self):
        """Delete the currently selected customer."""
        row = self.customer_table.currentRow()
        if row >= 0:
            customer_id = self.customer_table.item(row, 0).data(Qt.UserRole)
            for customer in self.customers:
                if customer.customer_id == customer_id:
                    self._delete_customer(customer)
                    break


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
    
    view = CustomerView()
    view.show()
    
    sys.exit(app.exec())
