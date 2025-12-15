# COPILOT_MODIFIED: true  # 2025-12-09T16:30:00Z
"""
=============================================================================
Employee View
=============================================================================
This module provides the employee management screen (Admin only).

Features:
    - View all employees
    - Search by name, username, or email
    - Add new employee with password
    - Edit employee (update password optional)
    - Role assignment (Admin/Employee)
    - Delete employee (with confirmation)

=============================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
    QAbstractItemView, QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QKeySequence, QShortcut

from repositories.employee_repository import EmployeeRepository, Employee
from utils import is_valid_email
import error_reporter


class EmployeeFormDialog(QDialog):
    """Dialog for adding/editing an employee."""
    
    def __init__(self, employee: Employee = None, parent=None):
        super().__init__(parent)
        
        self.employee = employee
        self.is_edit = employee is not None
        
        self.setWindowTitle("Edit Employee" if self.is_edit else "Add Employee")
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
        self.name_input.setPlaceholderText("Full name (required)")
        form_layout.addRow("Name *:", self.name_input)
        
        # Username (required)
        self.username_input = QLineEdit()
        self.username_input.setMinimumHeight(35)
        self.username_input.setPlaceholderText("Login username (required)")
        if self.is_edit:
            self.username_input.setEnabled(False)  # Cannot change username
        form_layout.addRow("Username *:", self.username_input)
        
        # Password
        password_label = "New Password:" if self.is_edit else "Password *:"
        self.password_input = QLineEdit()
        self.password_input.setMinimumHeight(35)
        self.password_input.setEchoMode(QLineEdit.Password)
        placeholder = "Leave blank to keep current" if self.is_edit else "Password (required)"
        self.password_input.setPlaceholderText(placeholder)
        form_layout.addRow(password_label, self.password_input)
        
        # Confirm Password
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setMinimumHeight(35)
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setPlaceholderText("Confirm password")
        form_layout.addRow("Confirm:", self.confirm_password_input)
        
        # Role
        self.role_combo = QComboBox()
        self.role_combo.setMinimumHeight(35)
        self.role_combo.addItems(["Employee", "Admin"])
        form_layout.addRow("Role *:", self.role_combo)
        
        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setMinimumHeight(35)
        self.phone_input.setPlaceholderText("e.g., 555-1234")
        form_layout.addRow("Phone:", self.phone_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setMinimumHeight(35)
        self.email_input.setPlaceholderText("e.g., employee@store.com")
        form_layout.addRow("Email:", self.email_input)
        
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
        """Populate form with existing employee data."""
        if self.employee:
            self.name_input.setText(self.employee.employee_name or "")
            self.username_input.setText(self.employee.username or "")
            
            # Set role
            role_index = self.role_combo.findText(self.employee.role or "Employee")
            if role_index >= 0:
                self.role_combo.setCurrentIndex(role_index)
            
            self.phone_input.setText(self.employee.phone or "")
            self.email_input.setText(self.employee.email or "")
    
    def _on_accept(self):
        """Validate and accept the dialog."""
        
        # Validate name
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Employee name is required.")
            self.name_input.setFocus()
            return
        
        # Validate username
        username = self.username_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Validation Error", "Username is required.")
            self.username_input.setFocus()
            return
        
        # Validate password
        password = self.password_input.text()
        confirm = self.confirm_password_input.text()
        
        if not self.is_edit and not password:
            QMessageBox.warning(self, "Validation Error", "Password is required.")
            self.password_input.setFocus()
            return
        
        if password and password != confirm:
            QMessageBox.warning(self, "Validation Error", "Passwords do not match.")
            self.confirm_password_input.setFocus()
            return
        
        if password and len(password) < 6:
            QMessageBox.warning(self, "Validation Error", "Password must be at least 6 characters.")
            self.password_input.setFocus()
            return
        
        # Validate email if provided
        email = self.email_input.text().strip()
        if email and not is_valid_email(email):
            QMessageBox.warning(self, "Validation Error", "Please enter a valid email address.")
            self.email_input.setFocus()
            return
        
        self.accept()
    
    def get_employee(self) -> Employee:
        """Get the employee object from form data."""
        return Employee(
            employee_id=self.employee.employee_id if self.employee else None,
            employee_name=self.name_input.text().strip(),
            username=self.username_input.text().strip(),
            password_hash=self.employee.password_hash if self.employee else "",
            role=self.role_combo.currentText(),
            phone=self.phone_input.text().strip() or None,
            email=self.email_input.text().strip() or None
        )
    
    def get_password(self) -> str:
        """Get the password (empty string if not changed)."""
        return self.password_input.text()


class EmployeeView(QWidget):
    """
    Widget for managing employees (Admin only).
    
    Signals:
        navigate_back: Go back to previous view
    """
    
    navigate_back = Signal()
    
    def __init__(self, current_user: Employee = None, parent=None):
        """Initialize the employee view."""
        super().__init__(parent)
        
        self.current_user = current_user
        self.employees = []
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
        
        title_label = QLabel("👤 Employee Management")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.add_button = QPushButton("+ Add Employee")
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
        self.search_input.setPlaceholderText("Search by name, username, or email...")
        self.search_input.setMinimumWidth(300)
        self.search_input.setClearButtonEnabled(True)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addStretch()
        
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.setProperty("class", "secondary")
        filter_layout.addWidget(self.refresh_button)
        
        main_layout.addWidget(filter_frame)
        
        # Employee table
        self.employee_table = QTableWidget()
        self.employee_table.setColumnCount(6)
        self.employee_table.setHorizontalHeaderLabels([
            "ID", "Name", "Username", "Role", "Email", "Actions"
        ])
        
        self.employee_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.employee_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.employee_table.setAlternatingRowColors(True)
        self.employee_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.employee_table.setSortingEnabled(True)
        self.employee_table.verticalHeader().setVisible(False)
        self.employee_table.verticalHeader().setDefaultSectionSize(60)
        self.employee_table.setWordWrap(False)
        
        header = self.employee_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.employee_table.setColumnWidth(5, 200)
        
        main_layout.addWidget(self.employee_table)
        
        # Footer
        footer_layout = QHBoxLayout()
        self.status_label = QLabel("0 employees")
        self.status_label.setStyleSheet("color: #757575;")
        footer_layout.addWidget(self.status_label)
        footer_layout.addStretch()
        main_layout.addLayout(footer_layout)
    
    def _connect_signals(self):
        """Connect UI signals."""
        self.add_button.clicked.connect(self._add_employee)
        self.search_input.textChanged.connect(self._on_search_changed)
        self.refresh_button.clicked.connect(self.refresh_data)
        self.employee_table.doubleClicked.connect(self._edit_selected_employee)
    
    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self._add_employee)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.search_input.setFocus)
        QShortcut(QKeySequence("F5"), self).activated.connect(self.refresh_data)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self._delete_selected_employee)
    
    def refresh_data(self):
        """Refresh employee data from database."""
        try:
            self.employees = EmployeeRepository.get_all()
            self._apply_filter()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load employees: {str(e)}")
    
    def load_employees(self):
        """Alias for refresh_data - load all employees and refresh table."""
        self.refresh_data()
    
    def _on_search_changed(self, text: str):
        """Handle search text change."""
        self.search_text = text.strip().lower()
        self._apply_filter()
    
    def _apply_filter(self):
        """Apply search filter and update table."""
        filtered = self.employees
        
        if self.search_text:
            filtered = [
                e for e in filtered
                if (e.employee_name and self.search_text in e.employee_name.lower()) or
                   (e.username and self.search_text in e.username.lower()) or
                   (e.email and self.search_text in e.email.lower())
            ]
        
        self._populate_table(filtered)
        self.status_label.setText(f"{len(filtered)} of {len(self.employees)} employees")
    
    def _populate_table(self, employees):
        """Populate the table with employee data."""
        # Disable sorting during update to prevent issues
        self.employee_table.setSortingEnabled(False)
        
        # Clear existing rows
        self.employee_table.clearContents()
        self.employee_table.setRowCount(0)
        self.employee_table.setRowCount(len(employees))
        
        for row, emp in enumerate(employees):
            id_item = QTableWidgetItem(str(emp.employee_id))
            id_item.setData(Qt.UserRole, emp.employee_id)
            self.employee_table.setItem(row, 0, id_item)
            
            self.employee_table.setItem(row, 1, QTableWidgetItem(emp.employee_name or ""))
            self.employee_table.setItem(row, 2, QTableWidgetItem(emp.username or ""))
            
            # Role with color coding
            role_item = QTableWidgetItem(emp.role or "")
            if emp.role and emp.role.lower() == "admin":
                role_item.setForeground(Qt.darkGreen)
                font = QFont()
                font.setBold(True)
                role_item.setFont(font)
            self.employee_table.setItem(row, 3, role_item)
            
            self.employee_table.setItem(row, 4, QTableWidgetItem(emp.email or ""))
            
            self._add_action_buttons(row, emp)
        
        # Re-enable sorting after population
        self.employee_table.setSortingEnabled(True)
    
    def _add_action_buttons(self, row: int, employee: Employee):
        """Add action buttons to table row."""
        # Create container widget with horizontal layout
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
        edit_btn.setToolTip("Edit employee")
        edit_btn.setAccessibleName(f"edit_employee_btn_{employee.employee_id}")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(lambda _, eid=employee.employee_id: self._on_edit_employee(eid))
        actions_layout.addWidget(edit_btn)
        
        # Delete button - check if can delete
        can_delete = (
            self.current_user is None or 
            employee.employee_id != self.current_user.employee_id
        )
        
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
            QPushButton:disabled {
                border-color: #BDBDBD;
                color: #BDBDBD;
            }
        """)
        delete_btn.setToolTip("Delete employee")
        delete_btn.setAccessibleName(f"delete_employee_btn_{employee.employee_id}")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setEnabled(can_delete)
        delete_btn.clicked.connect(lambda _, eid=employee.employee_id: self._on_delete_employee(eid))
        actions_layout.addWidget(delete_btn)
        
        # Set the widget in the table cell
        self.employee_table.setCellWidget(row, 5, actions_widget)
    
    def _add_employee(self):
        """Show dialog to add a new employee (admin only)."""
        dialog = EmployeeFormDialog(parent=self)
        
        if dialog.exec() == QDialog.Accepted:
            employee_data = dialog.get_employee()
            password = dialog.get_password()
            
            if not password:
                QMessageBox.warning(self, "Error", "Password is required for new employees.")
                return
            
            try:
                # Use create_employee method (admin-only operation)
                success, message = EmployeeRepository.create_employee(
                    employee_name=employee_data.employee_name,
                    phone=employee_data.phone,
                    email=employee_data.email,
                    position=employee_data.position,
                    salary=employee_data.salary,
                    username=employee_data.username,
                    password=password,
                    role=employee_data.role
                )
                
                if success:
                    QMessageBox.information(self, "Success", "Employee created successfully.")
                    self.load_employees()  # Refresh the table
                else:
                    QMessageBox.warning(self, "Error", message)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create employee: {str(e)}")
    
    def _on_edit_employee(self, employee_id: str):
        """Open edit dialog for employee by ID."""
        # Find employee by ID
        employee = None
        for emp in self.employees:
            if emp.employee_id == employee_id:
                employee = emp
                break
        
        if not employee:
            QMessageBox.warning(self, "Error", f"Employee {employee_id} not found.")
            return
        
        dialog = EmployeeFormDialog(employee=employee, parent=self)
        
        if dialog.exec() == QDialog.Accepted:
            updated_employee = dialog.get_employee()
            password = dialog.get_password()
            
            try:
                success, message = EmployeeRepository.update(
                    employee_id=updated_employee.employee_id,
                    employee_name=updated_employee.employee_name,
                    phone=updated_employee.phone,
                    email=updated_employee.email,
                    position=updated_employee.position,
                    salary=updated_employee.salary,
                    username=updated_employee.username,
                    role=updated_employee.role
                )
                
                # Update password if provided
                if password and success:
                    pwd_success, pwd_message = EmployeeRepository.change_password(
                        updated_employee.employee_id, 
                        password
                    )
                    if not pwd_success:
                        QMessageBox.warning(self, "Warning", f"Employee updated but password change failed: {pwd_message}")
                
                if success:
                    QMessageBox.information(self, "Success", "Employee updated successfully.")
                    self.load_employees()  # Refresh the table
                else:
                    QMessageBox.warning(self, "Error", message)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update employee: {str(e)}")
    
    def _edit_employee(self, employee: Employee):
        """Show dialog to edit an employee (backward compatibility method)."""
        self._on_edit_employee(employee.employee_id)
    
    def _edit_selected_employee(self):
        """Edit the currently selected employee."""
        row = self.employee_table.currentRow()
        if row >= 0:
            emp_id = self.employee_table.item(row, 0).data(Qt.UserRole)
            self._on_edit_employee(emp_id)
    
    def _on_delete_employee(self, employee_id: str):
        """Delete an employee by ID after confirmation."""
        # Find employee by ID
        employee = None
        for emp in self.employees:
            if emp.employee_id == employee_id:
                employee = emp
                break
        
        if not employee:
            QMessageBox.warning(self, "Error", f"Employee {employee_id} not found.")
            return
        
        # Prevent self-deletion
        if self.current_user and employee.employee_id == self.current_user.employee_id:
            QMessageBox.warning(self, "Error", "You cannot delete your own account.")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete employee '{employee.employee_name}'?\n\n"
            "This will permanently remove their login access.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success, message = EmployeeRepository.delete_employee(employee_id)
                if success:
                    QMessageBox.information(self, "Success", message)
                    self.load_employees()  # Refresh the table
                else:
                    QMessageBox.warning(self, "Error", message)
            except Exception as exc:
                error_reporter.report_error("Delete failed", exc, parent=self)
                self.load_employees()  # Refresh table even on error
    
    def _delete_employee(self, employee: Employee):
        """Delete an employee after confirmation (backward compatibility method)."""
        self._on_delete_employee(employee.employee_id)
    
    def _delete_selected_employee(self):
        """Delete the currently selected employee."""
        row = self.employee_table.currentRow()
        if row >= 0:
            emp_id = self.employee_table.item(row, 0).data(Qt.UserRole)
            self._on_delete_employee(emp_id)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    try:
        with open("styles/theme.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass
    
    view = EmployeeView()
    view.show()
    sys.exit(app.exec())
