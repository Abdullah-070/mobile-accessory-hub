"""
=============================================================================
Product List View
=============================================================================
This module provides the product listing screen with filtering and search.

Features:
    - Tabular display of all products
    - Search by name, barcode, or SKU
    - Filter by category and subcategory
    - Pagination for large datasets
    - Add, Edit, Delete actions
    - Double-click to edit
    - Keyboard shortcuts

=============================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QMessageBox, QSpacerItem, QSizePolicy,
    QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QKeySequence, QShortcut

from repositories.product_repository import ProductRepository, Product
from repositories.category_repository import CategoryRepository
from repositories.subcategory_repository import SubcategoryRepository
from utils import format_currency


class ProductListView(QWidget):
    """
    Widget for displaying and managing the product list.
    
    Signals:
        add_product_requested: User wants to add a new product
        edit_product_requested: User wants to edit a product (passes product_code)
        view_product_requested: User wants to view product details
    """
    
    # Signals
    add_product_requested = Signal()
    edit_product_requested = Signal(str)  # product_code
    view_product_requested = Signal(str)  # product_code
    
    def __init__(self, parent=None):
        """
        Initialize the product list view.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Data
        self.products = []
        self.categories = []
        self.subcategories = []
        self.filtered_subcategories = []
        
        # Current filter values
        self.search_text = ""
        self.selected_category_id = None
        self.selected_subcategory_id = None
        
        # Set up UI
        self._setup_ui()
        
        # Connect signals
        self._connect_signals()
        
        # Set up keyboard shortcuts
        self._setup_shortcuts()
        
        # Load initial data
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
        
        # Title
        title_label = QLabel("Products")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Add button
        self.add_button = QPushButton("+ Add Product")
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
        filter_layout.setSpacing(15)
        
        # Search input
        search_label = QLabel("Search:")
        filter_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, barcode, or SKU...")
        self.search_input.setMinimumWidth(250)
        self.search_input.setClearButtonEnabled(True)
        filter_layout.addWidget(self.search_input)
        
        # Category filter
        category_label = QLabel("Category:")
        filter_layout.addWidget(category_label)
        
        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(150)
        self.category_combo.addItem("All Categories", None)
        filter_layout.addWidget(self.category_combo)
        
        # Subcategory filter
        subcategory_label = QLabel("Subcategory:")
        filter_layout.addWidget(subcategory_label)
        
        self.subcategory_combo = QComboBox()
        self.subcategory_combo.setMinimumWidth(150)
        self.subcategory_combo.addItem("All Subcategories", None)
        filter_layout.addWidget(self.subcategory_combo)
        
        # Clear filters button
        self.clear_filters_button = QPushButton("Clear")
        self.clear_filters_button.setProperty("class", "secondary")
        filter_layout.addWidget(self.clear_filters_button)
        
        filter_layout.addStretch()
        
        main_layout.addWidget(filter_frame)
        
        # =====================================================================
        # PRODUCT TABLE
        # =====================================================================
        
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(8)
        self.product_table.setHorizontalHeaderLabels([
            "Code", "Name", "Brand", "Description", "Category", "Subcategory", "Price", "Actions"
        ])
        
        # Table settings
        self.product_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.product_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.product_table.setAlternatingRowColors(True)
        self.product_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.product_table.setSortingEnabled(True)
        self.product_table.verticalHeader().setVisible(False)
        self.product_table.verticalHeader().setDefaultSectionSize(60)
        
        # Column widths
        header = self.product_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # SKU
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Barcode
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Category
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Subcategory
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Price
        header.setSectionResizeMode(7, QHeaderView.Fixed)             # Actions
        self.product_table.setColumnWidth(7, 200)
        
        main_layout.addWidget(self.product_table)
        
        # =====================================================================
        # FOOTER (Status and Pagination)
        # =====================================================================
        
        footer_layout = QHBoxLayout()
        
        # Record count
        self.status_label = QLabel("0 products")
        self.status_label.setStyleSheet("color: #757575;")
        footer_layout.addWidget(self.status_label)
        
        footer_layout.addStretch()
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setProperty("class", "secondary")
        footer_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(footer_layout)
    
    def _connect_signals(self):
        """Connect UI signals to handler methods."""
        
        # Add button
        self.add_button.clicked.connect(self.add_product_requested.emit)
        
        # Search input
        self.search_input.textChanged.connect(self._on_search_changed)
        
        # Category filter
        self.category_combo.currentIndexChanged.connect(self._on_category_changed)
        
        # Subcategory filter
        self.subcategory_combo.currentIndexChanged.connect(self._on_subcategory_changed)
        
        # Clear filters
        self.clear_filters_button.clicked.connect(self._clear_filters)
        
        # Table double-click
        self.product_table.doubleClicked.connect(self._on_row_double_clicked)
        
        # Refresh button
        self.refresh_button.clicked.connect(self.refresh_data)
    
    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        
        # Ctrl+N: Add new product
        shortcut_add = QShortcut(QKeySequence("Ctrl+N"), self)
        shortcut_add.activated.connect(self.add_product_requested.emit)
        
        # Ctrl+F: Focus search
        shortcut_search = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut_search.activated.connect(self.search_input.setFocus)
        
        # F5: Refresh
        shortcut_refresh = QShortcut(QKeySequence("F5"), self)
        shortcut_refresh.activated.connect(self.refresh_data)
        
        # Delete: Delete selected
        shortcut_delete = QShortcut(QKeySequence("Delete"), self)
        shortcut_delete.activated.connect(self._delete_selected_product)
        
        # Enter: Edit selected
        shortcut_edit = QShortcut(QKeySequence("Return"), self)
        shortcut_edit.activated.connect(self._edit_selected_product)
    
    def refresh_data(self):
        """Refresh all data from the database."""
        
        try:
            # Load categories
            self._load_categories()
            
            # Load products
            self._load_products()
        
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Failed to load data: {str(e)}",
                QMessageBox.Ok
            )
    
    def _load_categories(self):
        """Load categories into the filter dropdown."""
        
        try:
            self.categories = CategoryRepository.get_all()
            
            # Remember current selection
            current_id = self.category_combo.currentData()
            
            # Update combo box
            self.category_combo.blockSignals(True)
            self.category_combo.clear()
            self.category_combo.addItem("All Categories", None)
            
            for category in self.categories:
                self.category_combo.addItem(
                    category.cat_name,
                    category.cat_id
                )
            
            # Restore selection
            if current_id is not None:
                index = self.category_combo.findData(current_id)
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
            
            self.category_combo.blockSignals(False)
            
            # Load all subcategories
            self.subcategories = SubcategoryRepository.get_all()
            self._update_subcategory_filter()
        
        except Exception as e:
            print(f"Error loading categories: {e}")
    
    def _update_subcategory_filter(self):
        """Update subcategory dropdown based on selected category."""
        
        current_id = self.subcategory_combo.currentData()
        
        self.subcategory_combo.blockSignals(True)
        self.subcategory_combo.clear()
        self.subcategory_combo.addItem("All Subcategories", None)
        
        # Filter subcategories by selected category
        if self.selected_category_id is not None:
            self.filtered_subcategories = [
                s for s in self.subcategories
                if s.cat_id == self.selected_category_id
            ]
        else:
            self.filtered_subcategories = self.subcategories
        
        for subcategory in self.filtered_subcategories:
            self.subcategory_combo.addItem(
                subcategory.subcat_name,
                subcategory.subcat_id
            )
        
        # Restore selection if still valid
        if current_id is not None:
            index = self.subcategory_combo.findData(current_id)
            if index >= 0:
                self.subcategory_combo.setCurrentIndex(index)
        
        self.subcategory_combo.blockSignals(False)
    
    def _load_products(self):
        """Load products into the table with current filters applied."""
        
        try:
            # Get all products
            all_products = ProductRepository.get_all()
            
            # Apply filters
            self.products = self._apply_filters(all_products)
            
            # Update table
            self._populate_table()
            
            # Update status
            self.status_label.setText(
                f"{len(self.products)} of {len(all_products)} products"
            )
        
        except Exception as e:
            print(f"Error loading products: {e}")
    
    def _apply_filters(self, products):
        """
        Apply search and category filters to the product list.
        
        Args:
            products: List of Product objects
            
        Returns:
            Filtered list of Product objects
        """
        filtered = products
        
        # Search filter
        if self.search_text:
            search_lower = self.search_text.lower()
            filtered = [
                p for p in filtered
                if (p.product_name and search_lower in p.product_name.lower()) or
                   (p.brand and search_lower in p.brand.lower()) or
                   (p.product_code and search_lower in p.product_code.lower())
            ]
        
        # Category filter
        if self.selected_category_id is not None:
            # Need to check subcategory's category
            category_subcategory_ids = {
                s.subcat_id for s in self.subcategories
                if s.cat_id == self.selected_category_id
            }
            filtered = [
                p for p in filtered
                if p.subcat_id in category_subcategory_ids
            ]
        
        # Subcategory filter
        if self.selected_subcategory_id is not None:
            filtered = [
                p for p in filtered
                if p.subcat_id == self.selected_subcategory_id
            ]
        
        return filtered
    
    def _populate_table(self):
        """Populate the table with current product data."""
        
        self.product_table.setRowCount(len(self.products))
        
        # Create lookup dictionaries
        subcategory_map = {s.subcat_id: s for s in self.subcategories}
        category_map = {c.cat_id: c for c in self.categories}
        
        for row, product in enumerate(self.products):
            # Product Code
            id_item = QTableWidgetItem(str(product.product_code))
            id_item.setData(Qt.UserRole, product.product_code)
            self.product_table.setItem(row, 0, id_item)
            
            # Name
            name_item = QTableWidgetItem(product.product_name or "")
            self.product_table.setItem(row, 1, name_item)
            
            # Brand
            brand_item = QTableWidgetItem(product.brand or "")
            self.product_table.setItem(row, 2, brand_item)
            
            # Description
            desc_item = QTableWidgetItem(product.description or "")
            self.product_table.setItem(row, 3, desc_item)
            
            # Category (via subcategory)
            subcategory = subcategory_map.get(product.subcat_id)
            category_name = ""
            subcategory_name = ""
            if subcategory:
                subcategory_name = subcategory.subcat_name or ""
                category = category_map.get(subcategory.cat_id)
                if category:
                    category_name = category.cat_name or ""
            
            category_item = QTableWidgetItem(category_name)
            self.product_table.setItem(row, 4, category_item)
            
            # Subcategory
            subcategory_item = QTableWidgetItem(subcategory_name)
            self.product_table.setItem(row, 5, subcategory_item)
            
            # Price
            price_item = QTableWidgetItem(
                format_currency(product.retail_price) if product.retail_price else "Rs. 0.00"
            )
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.product_table.setItem(row, 6, price_item)
            
            # Actions
            self._add_action_buttons(row, product.product_code)
    
    def _add_action_buttons(self, row: int, product_code: str):
        """
        Add edit and delete buttons to a table row.
        
        Args:
            row: Table row index
            product_code: Product code for the row
        """
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
        edit_btn.setToolTip("Edit product")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(lambda: self.edit_product_requested.emit(product_code))
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
        delete_btn.setToolTip("Delete product")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(lambda: self._delete_product(product_code))
        actions_layout.addWidget(delete_btn)
        
        self.product_table.setCellWidget(row, 7, actions_widget)
    
    def _on_search_changed(self, text: str):
        """Handle search text change."""
        self.search_text = text.strip()
        self._load_products()
    
    def _on_category_changed(self, index: int):
        """Handle category selection change."""
        self.selected_category_id = self.category_combo.currentData()
        self._update_subcategory_filter()
        self._load_products()
    
    def _on_subcategory_changed(self, index: int):
        """Handle subcategory selection change."""
        self.selected_subcategory_id = self.subcategory_combo.currentData()
        self._load_products()
    
    def _clear_filters(self):
        """Clear all filters and reset the view."""
        self.search_input.clear()
        self.category_combo.setCurrentIndex(0)
        self.subcategory_combo.setCurrentIndex(0)
        self.search_text = ""
        self.selected_category_id = None
        self.selected_subcategory_id = None
        self._load_products()
    
    def _on_row_double_clicked(self, index):
        """Handle table row double-click."""
        row = index.row()
        product_id = self.product_table.item(row, 0).data(Qt.UserRole)
        if product_id:
            self.edit_product_requested.emit(product_id)
    
    def _edit_selected_product(self):
        """Edit the currently selected product."""
        selected_row = self.product_table.currentRow()
        if selected_row >= 0:
            product_id = self.product_table.item(selected_row, 0).data(Qt.UserRole)
            if product_id:
                self.edit_product_requested.emit(product_id)
    
    def _delete_selected_product(self):
        """Delete the currently selected product."""
        selected_row = self.product_table.currentRow()
        if selected_row >= 0:
            product_id = self.product_table.item(selected_row, 0).data(Qt.UserRole)
            if product_id:
                self._delete_product(product_id)
    
    def _delete_product(self, product_id: int):
        """
        Delete a product after confirmation.
        
        Args:
            product_id: ID of the product to delete
        """
        # Find product name for confirmation message
        product_name = "this product"
        for product in self.products:
            if product.product_code == product_id:
                product_name = product.product_name
                break
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{product_name}'?\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success, message = ProductRepository.delete(product_id)
                
                if success:
                    QMessageBox.information(
                        self, "Success",
                        message,
                        QMessageBox.Ok
                    )
                    self.refresh_data()
                else:
                    QMessageBox.warning(
                        self, "Error",
                        message,
                        QMessageBox.Ok
                    )
            
            except Exception as e:
                QMessageBox.critical(
                    self, "Error",
                    f"Failed to delete product: {str(e)}",
                    QMessageBox.Ok
                )


# =============================================================================
# MODULE TEST
# =============================================================================

if __name__ == "__main__":
    """Test the product list view when running this module directly."""
    
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
    
    # Create and show view
    view = ProductListView()
    
    def on_add():
        print("Add product requested")
    
    def on_edit(product_id):
        print(f"Edit product requested: {product_id}")
    
    view.add_product_requested.connect(on_add)
    view.edit_product_requested.connect(on_edit)
    
    view.show()
    
    # Run application
    sys.exit(app.exec())
