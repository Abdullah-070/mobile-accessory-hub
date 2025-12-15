"""
=============================================================================
Category and Subcategory Quick-Add Dialogs
=============================================================================
Purpose: Admin-only dialogs for quickly creating categories/subcategories
from the Product Add/Edit form.

Why Created: Allows admins to add missing categories on-the-fly without
navigating away from product form.
=============================================================================
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QLabel, QDialogButtonBox, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt
from repositories.category_repository import CategoryRepository
from repositories.subcategory_repository import SubcategoryRepository


class AddCategoryDialog(QDialog):
    """Dialog for adding a new category."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Category")
        self.setMinimumWidth(500)
        self.new_category_id = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Create New Category")
        header.setStyleSheet("font-size: 14pt; font-weight: bold; color: #1976D2;")
        layout.addWidget(header)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Category Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Audio, Cables, etc.")
        self.name_input.setMinimumHeight(35)
        form_layout.addRow("Category Name *:", self.name_input)
        
        # Description
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Optional description")
        self.desc_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.desc_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._on_save)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Focus on name input
        self.name_input.setFocus()
    
    def _on_save(self):
        name = self.name_input.text().strip()
        description = self.desc_input.toPlainText().strip() or None
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Category name is required.")
            self.name_input.setFocus()
            return
        
        # Create category
        success, message, cat_id = CategoryRepository.create_category(name, description)
        
        if success:
            self.new_category_id = cat_id
            QMessageBox.information(self, "Success", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", message)


class AddSubcategoryDialog(QDialog):
    """Dialog for adding a new subcategory."""
    
    def __init__(self, category_id: str, parent=None):
        super().__init__(parent)
        self.category_id = category_id
        self.setWindowTitle("Add Subcategory")
        self.setMinimumWidth(500)
        self.new_subcategory_id = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Create New Subcategory")
        header.setStyleSheet("font-size: 14pt; font-weight: bold; color: #4CAF50;")
        layout.addWidget(header)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Subcategory Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Phone Cases, Earphones, etc.")
        self.name_input.setMinimumHeight(35)
        form_layout.addRow("Subcategory Name *:", self.name_input)
        
        # Description
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Optional description")
        self.desc_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.desc_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._on_save)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Focus on name input
        self.name_input.setFocus()
    
    def _on_save(self):
        name = self.name_input.text().strip()
        description = self.desc_input.toPlainText().strip() or None
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Subcategory name is required.")
            self.name_input.setFocus()
            return
        
        if not self.category_id:
            QMessageBox.warning(self, "Error", "Please select a category first.")
            return
        
        # Create subcategory
        success, message, subcat_id = SubcategoryRepository.create_subcategory(
            self.category_id, name, description
        )
        
        if success:
            self.new_subcategory_id = subcat_id
            QMessageBox.information(self, "Success", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", message)
