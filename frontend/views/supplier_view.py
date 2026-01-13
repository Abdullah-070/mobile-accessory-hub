"""
=============================================================================
Supplier View
=============================================================================
This module provides the supplier management screen.

Features:
    - View all suppliers
    - Search by name, phone, or email
    - Add new supplier
    - Edit existing supplier
    - Delete supplier (with confirmation)

=============================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
    QAbstractItemView, QTextEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QKeySequence, QShortcut

from repositories.supplier_repository import SupplierRepository, Supplier
from utils import is_valid_email


class SupplierFormDialog(QDialog):
    """Dialog for adding/editing a supplier."""
    
    def __init__(self, supplier: Supplier = None, parent=None):
        super().__init__(parent)
        
        self.supplier = supplier
        self.is_edit = supplier is not None
        
        self.setWindowTitle("Edit Supplier" if self.is_edit else "Add Supplier")
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
        self.name_input.setPlaceholderText("Supplier name (required)")
        form_layout.addRow("Name *:", self.name_input)
        
        # Contact Person
        self.contact_input = QLineEdit()
        self.contact_input.setMinimumHeight(35)
        self.contact_input.setPlaceholderText("Contact person name")
        form_layout.addRow("Contact:", self.contact_input)
        
        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setMinimumHeight(35)
        self.phone_input.setPlaceholderText("e.g., 555-1234")
        form_layout.addRow("Phone:", self.phone_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setMinimumHeight(35)
        self.email_input.setPlaceholderText("e.g., supplier@company.com")
        form_layout.addRow("Email:", self.email_input)
        
        # Address
        self.address_input = QTextEdit()
        self.address_input.setMinimumHeight(60)
        self.address_input.setMaximumHeight(80)
        self.address_input.setPlaceholderText("Full address")
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
        """Populate form with existing supplier data."""
        if self.supplier:
            self.name_input.setText(self.supplier.supplier_name or "")
            self.contact_input.setText(self.supplier.contact_name or "")
            self.phone_input.setText(self.supplier.phone_number or "")
            self.email_input.setText(self.supplier.email or "")
            self.address_input.setPlainText(self.supplier.address or "")
    
    def _on_accept(self):
        """Validate and accept the dialog."""
        
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(
                self, "Validation Error",
                "Supplier name is required.",
                QMessageBox.Ok
            )
            self.name_input.setFocus()
            return
        
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
    
    def get_supplier(self) -> Supplier:
        """Get the supplier object from form data."""
        return Supplier(
            supplier_id=self.supplier.supplier_id if self.supplier else None,
            supplier_name=self.name_input.text().strip(),
            contact_person=self.contact_input.text().strip() or None,
            phone=self.phone_input.text().strip() or None,
            email=self.email_input.text().strip() or None,
            address=self.address_input.toPlainText().strip() or None
        )


class SupplierView(QWidget):
    """
    Widget for managing suppliers.
    
    Signals:
        navigate_back: Go back to previous view
    """
    
    navigate_back = Signal()
    
    def __init__(self, parent=None):
        """Initialize the supplier view."""
        super().__init__(parent)
        
        self.suppliers = []
        self.search_text = ""
        
        self._setup_ui()
        self._connect_signals()
        self._setup_shortcuts()
        self.refresh_data()
    
    def _setup_ui(self):
        """Set up the user interface components."""
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🏭 Supplier Management")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.add_button = QPushButton("+ Add Supplier")
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.setMinimumHeight(40)
        header_layout.addWidget(self.add_button)
        
        main_layout.addLayout(header_layout)
        
        # Filter bar
        filter_frame = QFrame()
        filter_frame.setProperty("class", "card")
        filter_layout = QHBoxLayout(filter_frame)
        
        filter_layout.addWidget(QLabel("Search:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, contact, or email...")
        self.search_input.setMinimumWidth(300)
        self.search_input.setClearButtonEnabled(True)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addStretch()
        
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.setProperty("class", "secondary")
        filter_layout.addWidget(self.refresh_button)
        
        main_layout.addWidget(filter_frame)
        
        # Supplier table
        self.supplier_table = QTableWidget()
        self.supplier_table.setColumnCount(7)
        self.supplier_table.setHorizontalHeaderLabels([
            "ID", "Name", "Contact", "Phone", "Email", "Address", "Actions"
        ])
        
        self.supplier_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.supplier_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.supplier_table.setAlternatingRowColors(True)
        self.supplier_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.supplier_table.setSortingEnabled(True)
        self.supplier_table.verticalHeader().setVisible(False)
        self.supplier_table.verticalHeader().setDefaultSectionSize(100)
        
        header = self.supplier_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        self.supplier_table.setColumnWidth(6, 200)
        
        main_layout.addWidget(self.supplier_table)
        
        # Footer
        footer_layout = QHBoxLayout()
        self.status_label = QLabel("0 suppliers")
        self.status_label.setStyleSheet("color: #757575;")
        footer_layout.addWidget(self.status_label)
        footer_layout.addStretch()
        main_layout.addLayout(footer_layout)
    
    def _connect_signals(self):
        """Connect UI signals."""
        self.add_button.clicked.connect(self._add_supplier)
        self.search_input.textChanged.connect(self._on_search_changed)
        self.refresh_button.clicked.connect(self.refresh_data)
        self.supplier_table.doubleClicked.connect(self._edit_selected_supplier)
    
    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self._add_supplier)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.search_input.setFocus)
        QShortcut(QKeySequence("F5"), self).activated.connect(self.refresh_data)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self._delete_selected_supplier)
    
    def refresh_data(self):
        """Refresh supplier data from database."""
        try:
            self.suppliers = SupplierRepository.get_all()
            self._apply_filter()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load suppliers: {str(e)}")
    
    def _on_search_changed(self, text: str):
        """Handle search text change."""
        self.search_text = text.strip().lower()
        self._apply_filter()
    
    def _apply_filter(self):
        """Apply search filter and update table."""
        filtered = self.suppliers
        
        if self.search_text:
            filtered = [
                s for s in filtered
                if (s.supplier_name and self.search_text in s.supplier_name.lower()) or
                   (s.contact_name and self.search_text in s.contact_name.lower()) or
                   (s.email and self.search_text in s.email.lower())
            ]
        
        self._populate_table(filtered)
        self.status_label.setText(f"{len(filtered)} of {len(self.suppliers)} suppliers")
    
    def _populate_table(self, suppliers):
        """Populate the table with supplier data."""
        self.supplier_table.setRowCount(len(suppliers))
        
        for row, supplier in enumerate(suppliers):
            id_item = QTableWidgetItem(str(supplier.supplier_id))
            id_item.setData(Qt.UserRole, supplier.supplier_id)
            self.supplier_table.setItem(row, 0, id_item)
            
            self.supplier_table.setItem(row, 1, QTableWidgetItem(supplier.supplier_name or ""))
            self.supplier_table.setItem(row, 2, QTableWidgetItem(supplier.contact_name or ""))
            self.supplier_table.setItem(row, 3, QTableWidgetItem(supplier.phone_number or ""))
            self.supplier_table.setItem(row, 4, QTableWidgetItem(supplier.email or ""))
            self.supplier_table.setItem(row, 5, QTableWidgetItem(supplier.address or ""))
            
            self._add_action_buttons(row, supplier)
    
    def _add_action_buttons(self, row: int, supplier: Supplier):
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
        edit_btn.setToolTip("Edit supplier")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(lambda: self._edit_supplier(supplier))
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
        delete_btn.setToolTip("Delete supplier")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(lambda: self._delete_supplier(supplier))
        actions_layout.addWidget(delete_btn)
        
        self.supplier_table.setCellWidget(row, 6, actions_widget)
        self.supplier_table.setCellWidget(row, 6, actions_widget)
    
    def _add_supplier(self):
        """Show dialog to add a new supplier."""
        dialog = SupplierFormDialog(parent=self)
        
        if dialog.exec() == QDialog.Accepted:
            supplier = dialog.get_supplier()
            try:
                # Generate supplier ID
                supplier_id = SupplierRepository.get_next_id()
                
                success = SupplierRepository.create(
                    supplier_id=supplier_id,
                    supplier_name=supplier.supplier_name,
                    contact_person=supplier.contact_person,
                    phone=supplier.phone,
                    email=supplier.email,
                    address=supplier.address
                )
                if success:
                    QMessageBox.information(self, "Success", f"Supplier '{supplier.supplier_name}' created.")
                    self.refresh_data()
                else:
                    QMessageBox.warning(self, "Error", "Failed to create supplier.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create supplier: {str(e)}")
    
    def _edit_supplier(self, supplier: Supplier):
        """Show dialog to edit a supplier."""
        dialog = SupplierFormDialog(supplier=supplier, parent=self)
        
        if dialog.exec() == QDialog.Accepted:
            updated_supplier = dialog.get_supplier()
            try:
                success = SupplierRepository.update(
                    supplier_id=supplier.supplier_id,
                    supplier_name=updated_supplier.supplier_name,
                    contact_person=updated_supplier.contact_person,
                    phone=updated_supplier.phone,
                    email=updated_supplier.email,
                    address=updated_supplier.address
                )
                if success:
                    QMessageBox.information(self, "Success", "Supplier updated successfully.")
                    self.refresh_data()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update supplier.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update supplier: {str(e)}")
    
    def _edit_selected_supplier(self):
        """Edit the currently selected supplier."""
        row = self.supplier_table.currentRow()
        if row >= 0:
            supplier_id = self.supplier_table.item(row, 0).data(Qt.UserRole)
            for supplier in self.suppliers:
                if supplier.supplier_id == supplier_id:
                    self._edit_supplier(supplier)
                    break
    
    def _delete_supplier(self, supplier: Supplier):
        """Delete a supplier after confirmation."""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{supplier.supplier_name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = SupplierRepository.delete(supplier.supplier_id)
                if success:
                    QMessageBox.information(self, "Success", "Supplier deleted.")
                    self.refresh_data()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete. May have related records.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete supplier: {str(e)}")
    
    def _delete_selected_supplier(self):
        """Delete the currently selected supplier."""
        row = self.supplier_table.currentRow()
        if row >= 0:
            supplier_id = self.supplier_table.item(row, 0).data(Qt.UserRole)
            for supplier in self.suppliers:
                if supplier.supplier_id == supplier_id:
                    self._delete_supplier(supplier)
                    break


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    try:
        with open("styles/theme.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass
    
    view = SupplierView()
    view.show()
    sys.exit(app.exec())
