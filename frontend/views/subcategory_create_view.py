# COPILOT_MODIFIED: true  # 2025-12-07T19:30:00Z
"""
Subcategory Creation Dialog
Admin-only modal for creating new product subcategories.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QLabel, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt
from repositories.category_repository import CategoryRepository
from repositories.subcategory_repository import SubcategoryRepository


class SubcategoryCreateView(QDialog):
    """Dialog for creating a new subcategory."""
    
    def __init__(self, category_id=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Subcategory")
        self.setMinimumWidth(550)
        self.category_id = category_id
        self.new_subcategory_id = None
        self._setup_ui()
        self._load_categories()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Create New Subcategory")
        header.setStyleSheet("font-size: 14pt; font-weight: bold; color: #4CAF50;")
        layout.addWidget(header)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Parent Category
        self.category_combo = QComboBox()
        self.category_combo.setMinimumHeight(35)
        form_layout.addRow("Parent Category *:", self.category_combo)
        
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
        button_layout = QVBoxLayout()
        
        self.save_btn = QPushButton("Create Subcategory")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.clicked.connect(self._on_save)
        button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.name_input.setFocus()
    
    def _load_categories(self):
        try:
            categories = CategoryRepository.get_all_categories()
            self.category_combo.clear()
            self.category_combo.addItem("Select Category...", None)
            
            for category in categories:
                cat_name = category.category_name if hasattr(category, 'category_name') else category.cat_name
                cat_id = category.category_id if hasattr(category, 'category_id') else category.cat_id
                self.category_combo.addItem(cat_name, cat_id)
            
            # Pre-select if category_id provided
            if self.category_id:
                index = self.category_combo.findData(self.category_id)
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to load categories: {str(e)}")
    
    def _on_save(self):
        category_id = self.category_combo.currentData()
        name = self.name_input.text().strip()
        description = self.desc_input.toPlainText().strip() or None
        
        if not category_id:
            QMessageBox.warning(self, "Validation Error", "Please select a parent category.")
            return
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Subcategory name is required.")
            self.name_input.setFocus()
            return
        
        try:
            success, message, subcat_id = SubcategoryRepository.create_subcategory(
                category_id, name, description
            )
            
            if success:
                self.new_subcategory_id = subcat_id
                QMessageBox.information(self, "Success", message)
                self.accept()
            else:
                QMessageBox.warning(self, "Error", message)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create subcategory: {str(e)}")
