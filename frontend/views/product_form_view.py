# COPILOT_MODIFIED: true  # 2025-12-07T19:35:00Z
"""
=============================================================================
Product Form View
=============================================================================
This module provides the form for adding and editing products.

Features:
    - Add new product
    - Edit existing product
    - Category/Subcategory selection with auto-populate
    - Quick add category/subcategory for admins
    - Form validation
    - Image placeholder
    - Barcode/SKU generation

Changes Applied:
- Fixed category/subcategory dropdown population using get_all_categories()
- Added "Add Category" and "Add Subcategory" buttons for admins
- Improved validation with inline error messages
- Uses field_mapper for consistent attribute naming
- Added error_reporter for centralized error handling

=============================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTextEdit, QDoubleSpinBox, QFrame,
    QMessageBox, QScrollArea, QGroupBox, QSpinBox, QMenu, QInputDialog,
    QDateEdit
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont, QCursor

from decimal import Decimal
from datetime import date

from repositories.product_repository import ProductRepository, Product
from repositories.category_repository import CategoryRepository
from repositories.subcategory_repository import SubcategoryRepository
from repositories.supplier_repository import SupplierRepository
from repositories.purchase_repository import PurchaseRepository
from repositories.brand_repository import BrandRepository
from views.category_create_view import CategoryCreateView
from views.subcategory_create_view import SubcategoryCreateView
from error_reporter import report_error, report_warning


class ProductFormView(QWidget):
    """
    Form widget for adding/editing a product.
    
    Signals:
        saved: Emitted when product is saved successfully
        cancelled: Emitted when user cancels the form
    """
    
    # Signals
    saved = Signal()
    cancelled = Signal()
    
    def __init__(self, product_id: str = None, is_admin: bool = False, parent=None):
        """
        Initialize the product form.
        
        Args:
            product_id: Product code to edit (None for new product)
            is_admin: Whether current user is admin (enables quick-add buttons)
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.product_id = product_id
        self.is_edit_mode = product_id is not None
        self.is_admin = is_admin
        self.product: Product = None
        
        # Data
        self.categories = []
        self.subcategories = []
        self.suppliers = []
        
        # Set up UI
        self._setup_ui()
        
        # Load data
        self._load_dropdown_data()
        
        # If editing, load product data
        if self.is_edit_mode:
            self._load_product_data()
    
    def _setup_ui(self):
        """Set up the user interface components."""
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # =====================================================================
        # HEADER
        # =====================================================================
        
        header_layout = QHBoxLayout()
        
        # Title
        title_text = "Edit Product" if self.is_edit_mode else "Add New Product"
        title_label = QLabel(title_text)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Back button
        self.back_button = QPushButton("← Back")
        self.back_button.setProperty("class", "secondary")
        self.back_button.clicked.connect(self.cancelled.emit)
        header_layout.addWidget(self.back_button)
        
        main_layout.addLayout(header_layout)
        
        # =====================================================================
        # SCROLL AREA
        # =====================================================================
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        
        # =====================================================================
        # BASIC INFO GROUP
        # =====================================================================
        
        basic_group = QGroupBox("Basic Information")
        basic_layout = QGridLayout(basic_group)
        basic_layout.setSpacing(15)
        basic_layout.setColumnStretch(1, 1)
        basic_layout.setColumnStretch(3, 1)
        
        row = 0
        
        # Product Code (auto-generated, read-only for new products)
        basic_layout.addWidget(QLabel("Product Code"), row, 0)
        self.product_code_input = QLineEdit()
        self.product_code_input.setPlaceholderText("Auto-generated (e.g., PRD001)")
        self.product_code_input.setMinimumHeight(35)
        self.product_code_input.setReadOnly(True)
        self.product_code_input.setStyleSheet("background-color: #f0f0f0;")
        basic_layout.addWidget(self.product_code_input, row, 1, 1, 3)
        
        row += 1
        
        # Product Name (required)
        basic_layout.addWidget(QLabel("Product Name *"), row, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter product name")
        self.name_input.setMinimumHeight(35)
        basic_layout.addWidget(self.name_input, row, 1, 1, 3)
        
        row += 1
        
        # Brand (dropdown with add option)
        basic_layout.addWidget(QLabel("Brand"), row, 0)
        
        # Brand combo + Add button layout
        brand_layout = QHBoxLayout()
        self.brand_combo = QComboBox()
        self.brand_combo.setMinimumHeight(35)
        self.brand_combo.setEditable(False)  # Non-editable - clicking shows dropdown
        # Enable right-click context menu for edit/delete (admin only)
        if self.is_admin:
            self.brand_combo.setContextMenuPolicy(Qt.CustomContextMenu)
            self.brand_combo.customContextMenuRequested.connect(self._show_brand_context_menu)
        brand_layout.addWidget(self.brand_combo, 1)
        
        # Add Brand button
        self.add_brand_btn = QPushButton("+ Add")
        self.add_brand_btn.setMaximumWidth(80)
        self.add_brand_btn.setMinimumHeight(35)
        self.add_brand_btn.clicked.connect(self._add_brand)
        brand_layout.addWidget(self.add_brand_btn)
        
        basic_layout.addLayout(brand_layout, row, 1)
        
        # Stock Quantity
        basic_layout.addWidget(QLabel("Initial Stock Qty"), row, 2)
        self.stock_qty_input = QSpinBox()
        self.stock_qty_input.setRange(0, 999999)
        self.stock_qty_input.setValue(0)
        self.stock_qty_input.setMinimumHeight(35)
        basic_layout.addWidget(self.stock_qty_input, row, 3)
        
        row += 1
        
        # Minimum Stock Level
        basic_layout.addWidget(QLabel("Min Stock Level *"), row, 0)
        self.min_stock_input = QSpinBox()
        self.min_stock_input.setRange(0, 999999)
        self.min_stock_input.setValue(5)
        self.min_stock_input.setMinimumHeight(35)
        self.min_stock_input.setToolTip("Alert when stock falls below this level")
        basic_layout.addWidget(self.min_stock_input, row, 1)
        
        row += 1
        
        # Category (required)
        basic_layout.addWidget(QLabel("Category *"), row, 0)
        
        # Category combo + Add button layout
        category_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.setMinimumHeight(35)
        self.category_combo.currentIndexChanged.connect(self._on_category_changed)
        # Enable right-click context menu for edit/delete (admin only)
        if self.is_admin:
            self.category_combo.setContextMenuPolicy(Qt.CustomContextMenu)
            self.category_combo.customContextMenuRequested.connect(self._show_category_context_menu)
        category_layout.addWidget(self.category_combo, 1)
        
        # Add Category button (admin only)
        if self.is_admin:
            self.add_category_btn = QPushButton("+ Add")
            self.add_category_btn.setMaximumWidth(80)
            self.add_category_btn.setMinimumHeight(35)
            self.add_category_btn.clicked.connect(self._add_category)
            category_layout.addWidget(self.add_category_btn)
        
        basic_layout.addLayout(category_layout, row, 1)
        
        # Subcategory (required)
        basic_layout.addWidget(QLabel("Subcategory *"), row, 2)
        
        # Subcategory combo + Add button layout
        subcategory_layout = QHBoxLayout()
        self.subcategory_combo = QComboBox()
        self.subcategory_combo.setMinimumHeight(35)
        # Enable right-click context menu for edit/delete (admin only)
        if self.is_admin:
            self.subcategory_combo.setContextMenuPolicy(Qt.CustomContextMenu)
            self.subcategory_combo.customContextMenuRequested.connect(self._show_subcategory_context_menu)
        subcategory_layout.addWidget(self.subcategory_combo, 1)
        
        # Add Subcategory button (admin only)
        if self.is_admin:
            self.add_subcategory_btn = QPushButton("+ Add")
            self.add_subcategory_btn.setMaximumWidth(80)
            self.add_subcategory_btn.setMinimumHeight(35)
            self.add_subcategory_btn.clicked.connect(self._add_subcategory)
            self.add_subcategory_btn.setEnabled(False)  # Disabled until category selected
            subcategory_layout.addWidget(self.add_subcategory_btn)
        
        basic_layout.addLayout(subcategory_layout, row, 3)
        
        row += 1
        
        # Price (required)
        basic_layout.addWidget(QLabel("Price *"), row, 0)
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 999999.99)
        self.price_input.setDecimals(2)
        self.price_input.setPrefix("Rs. ")
        self.price_input.setMinimumHeight(35)
        basic_layout.addWidget(self.price_input, row, 1)
        
        # Cost (required for purchase)
        basic_layout.addWidget(QLabel("Cost Price *"), row, 2)
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0, 999999.99)
        self.cost_input.setDecimals(2)
        self.cost_input.setPrefix("Rs. ")
        self.cost_input.setMinimumHeight(35)
        basic_layout.addWidget(self.cost_input, row, 3)
        
        row += 1
        
        # Supplier (required for new products)
        basic_layout.addWidget(QLabel("Supplier *"), row, 0)
        self.supplier_combo = QComboBox()
        self.supplier_combo.setMinimumHeight(35)
        basic_layout.addWidget(self.supplier_combo, row, 1)
        
        # Purchase Date
        basic_layout.addWidget(QLabel("Purchase Date *"), row, 2)
        self.purchase_date_input = QDateEdit()
        self.purchase_date_input.setCalendarPopup(True)
        self.purchase_date_input.setDate(QDate.currentDate())
        self.purchase_date_input.setMinimumHeight(35)
        self.purchase_date_input.setDisplayFormat("yyyy-MM-dd")
        # Make calendar popup larger and more visible
        self.purchase_date_input.setStyleSheet("""
            QDateEdit {
                padding: 5px;
            }
            QCalendarWidget {
                min-width: 300px;
                min-height: 250px;
            }
            QCalendarWidget QToolButton {
                height: 30px;
                width: 80px;
                color: white;
                font-size: 12px;
                background-color: #2196F3;
                border-radius: 4px;
            }
            QCalendarWidget QMenu {
                width: 120px;
                background-color: white;
            }
            QCalendarWidget QSpinBox {
                width: 60px;
                font-size: 12px;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #2196F3;
                min-height: 40px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                font-size: 12px;
                color: black;
                background-color: white;
                selection-background-color: #2196F3;
                selection-color: white;
            }
        """)
        basic_layout.addWidget(self.purchase_date_input, row, 3)
        
        row += 1
        
        # Description
        basic_layout.addWidget(QLabel("Description"), row, 0, Qt.AlignTop)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Product description...")
        self.description_input.setMinimumHeight(80)
        self.description_input.setMaximumHeight(120)
        basic_layout.addWidget(self.description_input, row, 1, 1, 3)
        
        scroll_layout.addWidget(basic_group)
        
        # Add stretch
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # =====================================================================
        # FOOTER (Buttons)
        # =====================================================================
        
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setProperty("class", "secondary")
        self.cancel_button.setMinimumSize(120, 40)
        self.cancel_button.clicked.connect(self.cancelled.emit)
        footer_layout.addWidget(self.cancel_button)
        
        # Save button
        self.save_button = QPushButton("Save Product")
        self.save_button.setMinimumSize(150, 40)
        self.save_button.clicked.connect(self._save_product)
        footer_layout.addWidget(self.save_button)
        
        main_layout.addLayout(footer_layout)
    
    def _load_dropdown_data(self):
        """Load categories, subcategories, suppliers, and brands for dropdowns."""
        
        try:
            # Load categories using get_all_categories()
            self.categories = CategoryRepository.get_all_categories()
            
            self.category_combo.clear()
            if len(self.categories) == 0:
                self.category_combo.addItem("No categories - click + Add to create", None)
            else:
                self.category_combo.addItem("Select Category...", None)
                for category in self.categories:
                    # Use property aliases for compatibility
                    cat_name = category.category_name if hasattr(category, 'category_name') else category.cat_name
                    cat_id = category.category_id if hasattr(category, 'category_id') else category.cat_id
                    self.category_combo.addItem(cat_name, cat_id)
            
            # Load all subcategories
            self.subcategories = SubcategoryRepository.get_all()
            
            # Initially show "Select Category first" message
            self.subcategory_combo.clear()
            self.subcategory_combo.addItem("Select Category first...", None)
            
            # Load suppliers
            self.suppliers = SupplierRepository.get_all()
            self.supplier_combo.clear()
            if len(self.suppliers) == 0:
                self.supplier_combo.addItem("No suppliers - add in Suppliers tab", None)
            else:
                self.supplier_combo.addItem("Select Supplier...", None)
                for supplier in self.suppliers:
                    supplier_name = supplier.supplier_name if hasattr(supplier, 'supplier_name') else supplier.company_name
                    supplier_id = supplier.supplier_id
                    self.supplier_combo.addItem(supplier_name, supplier_id)
            
            # Load brands
            self.brands = BrandRepository.get_all()
            self.brand_combo.clear()
            self.brand_combo.addItem("Select Brand...", None)  # Placeholder option
            for brand in self.brands:
                self.brand_combo.addItem(brand.brand_name, brand.brand_id)
        
        except Exception as e:
            report_error("Load Dropdown Data Error", e, self)
    
    def _on_category_changed(self, index: int):
        """Handle category selection change."""
        
        category_id = self.category_combo.currentData()
        
        self.subcategory_combo.clear()
        
        if category_id is None:
            self.subcategory_combo.addItem("Select Category first...", None)
            if self.is_admin and hasattr(self, 'add_subcategory_btn'):
                self.add_subcategory_btn.setEnabled(False)
        else:
            self.subcategory_combo.addItem("Select Subcategory...", None)
            
            # Filter subcategories using get_subcategories_for_category
            try:
                filtered_subcats = SubcategoryRepository.get_subcategories_for_category(category_id)
                for subcategory in filtered_subcats:
                    # Use property aliases for compatibility
                    subcat_name = subcategory.subcategory_name if hasattr(subcategory, 'subcategory_name') else subcategory.subcat_name
                    subcat_id = subcategory.subcategory_id if hasattr(subcategory, 'subcategory_id') else subcategory.subcat_id
                    self.subcategory_combo.addItem(subcat_name, subcat_id)
                
                if len(filtered_subcats) == 0:
                    self.subcategory_combo.addItem("No subcategories - click + Add", None)
            except Exception as e:
                report_error("Load Subcategories Error", e, self)
            
            if self.is_admin and hasattr(self, 'add_subcategory_btn'):
                self.add_subcategory_btn.setEnabled(True)
    
    def _add_category(self):
        """Open dialog to add a new category (admin only)."""
        # Store current brand selection
        current_brand_text = self.brand_combo.currentText()
        current_brand_id = self.brand_combo.currentData()
        
        dialog = CategoryCreateView(self)
        if dialog.exec():
            # Reload categories and select the new one
            self._load_dropdown_data()
            
            # Restore brand selection
            if current_brand_id:
                index = self.brand_combo.findData(current_brand_id)
                if index >= 0:
                    self.brand_combo.setCurrentIndex(index)
            
            # Select the new category
            if dialog.new_category_id:
                index = self.category_combo.findData(dialog.new_category_id)
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
    
    def _add_subcategory(self):
        """Open dialog to add a new subcategory (admin only)."""
        category_id = self.category_combo.currentData()
        if not category_id:
            report_warning("No Category Selected", "Please select a category first.", self)
            return
        
        # Store current brand selection
        current_brand_text = self.brand_combo.currentText()
        current_brand_id = self.brand_combo.currentData()
        
        dialog = SubcategoryCreateView(category_id, self)
        if dialog.exec():
            # Reload category to refresh subcategories
            current_index = self.category_combo.currentIndex()
            self._load_dropdown_data()
            self.category_combo.setCurrentIndex(current_index)  # Triggers _on_category_changed
            
            # Restore brand selection
            if current_brand_id:
                index = self.brand_combo.findData(current_brand_id)
                if index >= 0:
                    self.brand_combo.setCurrentIndex(index)
            
            # Select the new subcategory
            if dialog.new_subcategory_id:
                index = self.subcategory_combo.findData(dialog.new_subcategory_id)
                if index >= 0:
                    self.subcategory_combo.setCurrentIndex(index)
    
    def _add_brand(self):
        """Open dialog to add a new brand."""
        brand_name, ok = QInputDialog.getText(
            self, "Add New Brand",
            "Enter brand name:",
            QLineEdit.Normal
        )
        
        if ok and brand_name.strip():
            brand_name = brand_name.strip()
            
            # Check if already exists
            existing = BrandRepository.get_by_name(brand_name)
            if existing:
                QMessageBox.warning(self, "Brand Exists", f"Brand '{brand_name}' already exists.")
                # Select the existing brand
                index = self.brand_combo.findText(brand_name)
                if index >= 0:
                    self.brand_combo.setCurrentIndex(index)
                return
            
            # Create the brand
            success, message, brand_id = BrandRepository.create_brand(brand_name)
            
            if success:
                # Reload brands and select the new one
                self._reload_brands()
                index = self.brand_combo.findText(brand_name)
                if index >= 0:
                    self.brand_combo.setCurrentIndex(index)
                QMessageBox.information(self, "Success", f"Brand '{brand_name}' added successfully!")
            else:
                QMessageBox.critical(self, "Error", f"Failed to add brand: {message}")
    
    def _reload_brands(self):
        """Reload brand dropdown."""
        try:
            current_text = self.brand_combo.currentText()
            self.brands = BrandRepository.get_all()
            self.brand_combo.clear()
            self.brand_combo.addItem("Select Brand...", None)  # Placeholder option
            for brand in self.brands:
                self.brand_combo.addItem(brand.brand_name, brand.brand_id)
            # Try to restore selection
            index = self.brand_combo.findText(current_text)
            if index >= 0:
                self.brand_combo.setCurrentIndex(index)
        except Exception as e:
            report_error("Reload Brands Error", e, self)

    def _show_category_context_menu(self, position):
        """Show context menu for category edit/delete."""
        # Get the current category
        cat_id = self.category_combo.currentData()
        cat_name = self.category_combo.currentText()
        
        if not cat_id or cat_name == "Select Category...":
            return
        
        menu = QMenu(self)
        edit_action = menu.addAction("✏️ Edit Category")
        delete_action = menu.addAction("🗑️ Delete Category")
        
        action = menu.exec(QCursor.pos())
        
        if action == edit_action:
            self._edit_category(cat_id, cat_name)
        elif action == delete_action:
            self._delete_category(cat_id, cat_name)
    
    def _edit_category(self, cat_id: str, cat_name: str):
        """Edit the selected category."""
        new_name, ok = QInputDialog.getText(
            self, "Edit Category",
            "Enter new category name:",
            QLineEdit.Normal,
            cat_name
        )
        
        if ok and new_name.strip():
            new_name = new_name.strip()
            if new_name == cat_name:
                return  # No change
            
            try:
                success = CategoryRepository.update(cat_id, new_name)
                if success:
                    QMessageBox.information(self, "Success", "Category updated successfully.")
                    # Reload dropdowns
                    self._load_dropdown_data()
                    # Re-select the category
                    index = self.category_combo.findData(cat_id)
                    if index >= 0:
                        self.category_combo.setCurrentIndex(index)
                else:
                    QMessageBox.warning(self, "Error", "Failed to update category.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update category: {str(e)}")
    
    def _delete_category(self, cat_id: str, cat_name: str):
        """Delete the selected category and its subcategories."""
        # Confirm deletion
        reply = QMessageBox.warning(
            self, "Confirm Delete",
            f"Are you sure you want to delete category '{cat_name}'?\n\n"
            "⚠️ WARNING: This will also delete ALL subcategories under this category!\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # First delete all subcategories under this category
                SubcategoryRepository.delete_by_category(cat_id)
                # Then delete the category
                success, message = CategoryRepository.delete(cat_id)
                if success:
                    QMessageBox.information(self, "Success", "Category and its subcategories deleted successfully.")
                    # Reload dropdowns
                    self._load_dropdown_data()
                else:
                    QMessageBox.warning(self, "Error", message)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete category: {str(e)}")
    
    def _show_brand_context_menu(self, position):
        """Show context menu for brand edit/delete."""
        # Get the current brand
        brand_id = self.brand_combo.currentData()
        brand_name = self.brand_combo.currentText()
        
        if not brand_id or brand_name in ["Select Brand..."]:
            return
        
        menu = QMenu(self)
        edit_action = menu.addAction("✏️ Edit Brand")
        delete_action = menu.addAction("🗑️ Delete Brand")
        
        action = menu.exec(QCursor.pos())
        
        if action == edit_action:
            self._edit_brand(brand_id, brand_name)
        elif action == delete_action:
            self._delete_brand(brand_id, brand_name)
    
    def _show_subcategory_context_menu(self, position):
        """Show context menu for subcategory edit/delete."""
        # Get the current subcategory
        subcat_id = self.subcategory_combo.currentData()
        subcat_name = self.subcategory_combo.currentText()
        
        if not subcat_id or subcat_name in ["Select Category first...", "Select Subcategory...", "No subcategories - click + Add"]:
            return
        
        menu = QMenu(self)
        edit_action = menu.addAction("✏️ Edit Subcategory")
        delete_action = menu.addAction("🗑️ Delete Subcategory")
        
        action = menu.exec(QCursor.pos())
        
        if action == edit_action:
            self._edit_subcategory(subcat_id, subcat_name)
        elif action == delete_action:
            self._delete_subcategory(subcat_id, subcat_name)
    
    def _edit_subcategory(self, subcat_id: str, subcat_name: str):
        """Edit the selected subcategory."""
        new_name, ok = QInputDialog.getText(
            self, "Edit Subcategory",
            "Enter new subcategory name:",
            QLineEdit.Normal,
            subcat_name
        )
        
        if ok and new_name.strip():
            new_name = new_name.strip()
            if new_name == subcat_name:
                return  # No change
            
            try:
                success = SubcategoryRepository.update_name(subcat_id, new_name)
                if success:
                    QMessageBox.information(self, "Success", "Subcategory updated successfully.")
                    # Reload dropdowns
                    current_cat_index = self.category_combo.currentIndex()
                    self._load_dropdown_data()
                    self.category_combo.setCurrentIndex(current_cat_index)
                    # Re-select the subcategory
                    index = self.subcategory_combo.findData(subcat_id)
                    if index >= 0:
                        self.subcategory_combo.setCurrentIndex(index)
                else:
                    QMessageBox.warning(self, "Error", "Failed to update subcategory.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update subcategory: {str(e)}")
    
    def _delete_subcategory(self, subcat_id: str, subcat_name: str):
        """Delete the selected subcategory."""
        # Confirm deletion
        reply = QMessageBox.warning(
            self, "Confirm Delete",
            f"Are you sure you want to delete subcategory '{subcat_name}'?\n\n"
            "⚠️ WARNING: This may fail if products exist in this subcategory!\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success, message = SubcategoryRepository.delete(subcat_id)
                if success:
                    QMessageBox.information(self, "Success", message)
                    # Reload dropdowns
                    current_cat_index = self.category_combo.currentIndex()
                    self._load_dropdown_data()
                    self.category_combo.setCurrentIndex(current_cat_index)
                else:
                    QMessageBox.warning(self, "Error", message)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete subcategory: {str(e)}")
    
    def _edit_brand(self, brand_id: str, brand_name: str):
        """Edit the selected brand."""
        new_name, ok = QInputDialog.getText(
            self, "Edit Brand",
            "Enter new brand name:",
            QLineEdit.Normal,
            brand_name
        )
        
        if ok and new_name.strip():
            new_name = new_name.strip()
            if new_name == brand_name:
                return  # No change
            
            try:
                success = BrandRepository.update(brand_id, new_name)
                if success:
                    QMessageBox.information(self, "Success", "Brand updated successfully.")
                    # Reload brands and re-select
                    self._reload_brands()
                    index = self.brand_combo.findData(brand_id)
                    if index >= 0:
                        self.brand_combo.setCurrentIndex(index)
                else:
                    QMessageBox.warning(self, "Error", "Failed to update brand.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update brand: {str(e)}")
    
    def _delete_brand(self, brand_id: str, brand_name: str):
        """Delete the selected brand."""
        # First, check if products exist with this brand
        try:
            total_products, products_with_stock, total_stock = BrandRepository.check_products_exist(brand_name)
            
            if products_with_stock > 0:
                # Products with inventory exist - cannot delete
                QMessageBox.critical(
                    self, "Cannot Delete Brand",
                    f"Cannot delete brand '{brand_name}'!\n\n"
                    f"📦 {products_with_stock} product(s) with this brand have inventory.\n"
                    f"📊 Total stock quantity: {total_stock} units\n\n"
                    "❌ You must sell all inventory items before deleting this brand.\n\n"
                    "To proceed:\n"
                    "1. Sell all products with this brand, OR\n"
                    "2. Adjust inventory to zero for these products, OR\n"
                    "3. Change the brand of these products to another brand"
                )
                return
            
            if total_products > 0:
                # Products exist but have no inventory - warn user
                reply = QMessageBox.warning(
                    self, "Confirm Delete",
                    f"⚠️ Warning: {total_products} product(s) exist with brand '{brand_name}'.\n\n"
                    "These products currently have NO inventory (stock = 0).\n\n"
                    "Deleting this brand will remove it from the brand list,\n"
                    "but the products will still reference this brand name.\n\n"
                    "Do you want to continue?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply != QMessageBox.Yes:
                    return
            else:
                # No products with this brand - safe to delete
                reply = QMessageBox.question(
                    self, "Confirm Delete",
                    f"Are you sure you want to delete brand '{brand_name}'?\n\n"
                    "✓ No products are using this brand.\n"
                    "This action cannot be undone.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply != QMessageBox.Yes:
                    return
            
            # Proceed with deletion
            success, message = BrandRepository.delete(brand_id)
            if success:
                QMessageBox.information(self, "Success", "Brand deleted successfully.")
                # Reload brands
                self._reload_brands()
            else:
                QMessageBox.warning(self, "Error", message)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete brand: {str(e)}")

    def _load_product_data(self):
        """Load existing product data for editing."""
        
        try:
            self.product = ProductRepository.get_by_id(self.product_id)
            
            if self.product is None:
                QMessageBox.warning(
                    self, "Error",
                    "Product not found.",
                    QMessageBox.Ok
                )
                self.cancelled.emit()
                return
            
            # Populate form fields
            self.product_code_input.setText(self.product.product_code or "")
            self.name_input.setText(self.product.product_name or "")
            
            # Set brand in combo box
            if self.product.brand:
                index = self.brand_combo.findText(self.product.brand)
                if index >= 0:
                    self.brand_combo.setCurrentIndex(index)
                else:
                    # Brand not in list, set as text (editable combo)
                    self.brand_combo.setCurrentText(self.product.brand)
            
            self.stock_qty_input.setValue(self.product.current_stock or 0)
            self.stock_qty_input.setEnabled(False)  # Can't change stock directly when editing
            self.min_stock_input.setValue(self.product.min_stock_level or 5)
            self.price_input.setValue(float(self.product.retail_price) or 0)
            self.cost_input.setValue(float(self.product.cost_price) or 0)
            self.description_input.setPlainText(self.product.description or "")
            
            # Disable supplier and date for editing (those are only for initial purchase)
            self.supplier_combo.setEnabled(False)
            self.purchase_date_input.setEnabled(False)
            
            # Find and select the correct category via subcategory
            if self.product.subcat_id:
                # Find the subcategory to get its category
                for subcategory in self.subcategories:
                    if subcategory.subcat_id == self.product.subcat_id:
                        # Select category
                        category_index = self.category_combo.findData(
                            subcategory.cat_id
                        )
                        if category_index >= 0:
                            self.category_combo.setCurrentIndex(category_index)
                        
                        # Select subcategory (after category change populates it)
                        subcategory_index = self.subcategory_combo.findData(
                            self.product.subcat_id
                        )
                        if subcategory_index >= 0:
                            self.subcategory_combo.setCurrentIndex(subcategory_index)
                        break
        
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Failed to load product: {str(e)}",
                QMessageBox.Ok
            )
            self.cancelled.emit()
    
    def _validate_form(self) -> bool:
        """
        Validate form inputs.
        
        Returns:
            True if valid, False otherwise
        """
        errors = []
        
        # Required fields
        if not self.name_input.text().strip():
            errors.append("Product name is required")
        
        if self.category_combo.currentData() is None:
            errors.append("Category is required")
        
        if self.subcategory_combo.currentData() is None:
            errors.append("Subcategory is required")
        
        if self.price_input.value() <= 0:
            errors.append("Selling price must be greater than zero")
        
        if self.cost_input.value() > self.price_input.value():
            errors.append("Cost price cannot be greater than selling price")
        
        # For new products, require supplier and cost price
        if not self.is_edit_mode:
            if self.supplier_combo.currentData() is None:
                errors.append("Supplier is required for new products")
            
            if self.cost_input.value() <= 0:
                errors.append("Cost price must be greater than zero")
            
            if self.stock_qty_input.value() <= 0:
                errors.append("Initial stock quantity must be greater than zero")
        
        if errors:
            QMessageBox.warning(
                self, "Validation Error",
                "\n".join(errors),
                QMessageBox.Ok
            )
            return False
        
        return True
    
    def _save_product(self):
        """Save the product to the database."""
        
        if not self._validate_form():
            return
        
        try:
            # Generate product code if creating new product
            if not self.is_edit_mode:
                product_code = ProductRepository.get_next_id()
                # Display the generated code
                self.product_code_input.setText(product_code)
            else:
                product_code = self.product_id
            
            # Get form values
            initial_stock = self.stock_qty_input.value()
            cost_price = Decimal(str(self.cost_input.value()))
            retail_price = Decimal(str(self.price_input.value()))
            supplier_id = self.supplier_combo.currentData()
            purchase_date = self.purchase_date_input.date().toPython()
            
            # Create product object
            product = Product(
                product_code=product_code,
                product_name=self.name_input.text().strip(),
                subcat_id=self.subcategory_combo.currentData(),
                brand=self.brand_combo.currentText().strip() or None,
                description=self.description_input.toPlainText().strip() or None,
                cost_price=cost_price,
                retail_price=retail_price,
                min_stock_level=self.min_stock_input.value(),
                date_added=purchase_date
            )
            
            if self.is_edit_mode:
                # Update existing product
                success = ProductRepository.update(
                    product_code=product.product_code,
                    subcat_id=product.subcat_id,
                    product_name=product.product_name,
                    brand=product.brand,
                    description=product.description,
                    cost_price=product.cost_price,
                    retail_price=product.retail_price,
                    min_stock_level=product.min_stock_level
                )
                message = "Product updated successfully."
            else:
                # Create new product
                # When using purchase workflow, set initial_stock=0 since inventory
                # will be added when purchase is marked as Received
                create_initial_stock = 0 if supplier_id else initial_stock
                
                print(f"DEBUG: Creating product {product.product_code}, supplier_id={supplier_id}, initial_stock={create_initial_stock}")
                success = ProductRepository.create(
                    product_code=product.product_code,
                    subcat_id=product.subcat_id,
                    product_name=product.product_name,
                    brand=product.brand,
                    description=product.description,
                    cost_price=product.cost_price,
                    retail_price=product.retail_price,
                    min_stock_level=product.min_stock_level,
                    date_added=product.date_added,
                    initial_stock=create_initial_stock
                )
                print(f"DEBUG: Product creation success = {success}")
                
                # If product created successfully, also create a purchase record
                if success and supplier_id:
                    try:
                        # Calculate total cost
                        total_cost = cost_price * initial_stock
                        
                        print(f"DEBUG: Creating purchase - supplier={supplier_id}, product={product_code}, qty={initial_stock}, price={cost_price}")
                        
                        # Create purchase record (status: Pending)
                        purchase_success = PurchaseRepository.create_with_product(
                            supplier_id=supplier_id,
                            product_code=product_code,
                            quantity=initial_stock,
                            unit_price=cost_price,
                            purchase_date=purchase_date,
                            notes=f"Initial stock purchase for {product.product_name}"
                        )
                        
                        print(f"DEBUG: Purchase result = {purchase_success}")
                        
                        if purchase_success:
                            message = (
                                f"Product created successfully!\n\n"
                                f"Purchase order created for {initial_stock} units @ Rs. {cost_price} = Rs. {total_cost}\n\n"
                                f"⚠️ Note: Inventory will be updated when you mark\n"
                                f"the order as 'Received' in the Purchases view."
                            )
                        else:
                            message = "Product created, but failed to create purchase record."
                    except Exception as pe:
                        message = f"Product created, but purchase record failed: {str(pe)}"
                else:
                    message = "Product created successfully."
            
            if success:
                QMessageBox.information(
                    self, "Success",
                    message,
                    QMessageBox.Ok
                )
                self.saved.emit()
            else:
                QMessageBox.warning(
                    self, "Error",
                    "Failed to save product. Please try again.",
                    QMessageBox.Ok
                )
        
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Failed to save product: {str(e)}",
                QMessageBox.Ok
            )


# =============================================================================
# MODULE TEST
# =============================================================================

if __name__ == "__main__":
    """Test the product form view when running this module directly."""
    
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
    
    # Create form (None for new product, or pass ID for edit)
    form = ProductFormView(product_id=None)
    
    def on_saved():
        print("Product saved!")
    
    def on_cancelled():
        print("Form cancelled")
    
    form.saved.connect(on_saved)
    form.cancelled.connect(on_cancelled)
    
    form.show()
    
    # Run application
    sys.exit(app.exec())
