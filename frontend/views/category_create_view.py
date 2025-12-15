# COPILOT_MODIFIED: true  # 2025-12-07T19:30:00Z
"""
Category Creation Dialog
Admin-only modal for creating new product categories.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QLabel, QMessageBox
)
from PySide6.QtCore import Qt
from repositories.category_repository import CategoryRepository


class CategoryCreateView(QDialog):
    """Dialog for creating a new category."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Category")
        self.setMinimumWidth(450)
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
        button_layout = QVBoxLayout()
        
        self.save_btn = QPushButton("Create Category")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.clicked.connect(self._on_save)
        button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.name_input.setFocus()
    
    def _on_save(self):
        name = self.name_input.text().strip()
        description = self.desc_input.toPlainText().strip() or None
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Category name is required.")
            self.name_input.setFocus()
            return
        
        try:
            success, message, cat_id = CategoryRepository.create_category(name, description)
            
            if success:
                self.new_category_id = cat_id
                QMessageBox.information(self, "Success", message)
                self.accept()
            else:
                QMessageBox.warning(self, "Error", message)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create category: {str(e)}")
