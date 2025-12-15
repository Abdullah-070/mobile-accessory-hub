"""
=============================================================================
Inventory View
=============================================================================
This module provides the inventory management screen.

Features:
    - View all inventory levels
    - Filter by low stock
    - Search by product name
    - Quick adjustment of stock levels
    - Reorder level management
    - Buy Stock - place purchase orders for low stock items

=============================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox, QCheckBox, QSpinBox, QDialog,
    QFormLayout, QDialogButtonBox, QAbstractItemView, QComboBox,
    QDoubleSpinBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QBrush, QKeySequence, QShortcut
from typing import Optional, Dict, Any

from repositories.inventory_repository import InventoryRepository, InventoryItem
from repositories.supplier_repository import SupplierRepository
from repositories.purchase_repository import PurchaseRepository
import db


class AdjustStockDialog(QDialog):
    """Dialog for adjusting inventory stock levels."""
    
    def __init__(self, product_name: str, current_qty: int, min_stock: int, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Adjust Stock")
        self.setMinimumWidth(350)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Product info
        info_label = QLabel(f"<b>{product_name}</b>")
        layout.addWidget(info_label)
        
        # Form
        form_layout = QFormLayout()
        
        # Current quantity (read-only)
        current_label = QLabel(str(current_qty))
        form_layout.addRow("Current Stock:", current_label)
        
        # New quantity
        self.new_qty_spin = QSpinBox()
        self.new_qty_spin.setRange(0, 999999)
        self.new_qty_spin.setValue(current_qty)
        self.new_qty_spin.setMinimumHeight(35)
        form_layout.addRow("New Stock:", self.new_qty_spin)
        
        # Min stock level (read-only info)
        min_label = QLabel(str(min_stock))
        form_layout.addRow("Min Stock Level:", min_label)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_new_quantity(self) -> int:
        """Get the entered new quantity."""
        return self.new_qty_spin.value()


class BuyStockDialog(QDialog):
    """Dialog for placing a purchase order to restock inventory."""
    
    def __init__(self, product_code: str, product_name: str, current_stock: int, 
                 original_cost_price: float, last_purchase_info: Optional[Dict[str, Any]] = None,
                 parent=None):
        super().__init__(parent)
        
        self.product_code = product_code
        self.product_name = product_name
        # Convert to float to avoid Decimal issues
        self.original_cost_price = float(original_cost_price) if original_cost_price else 0.0
        self.last_purchase_info = last_purchase_info
        
        self.setWindowTitle("🛒 Buy Stock")
        self.setFixedWidth(400)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Product Info Header (compact)
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #E3F2FD; padding: 8px; border-radius: 5px;")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(2)
        info_layout.setContentsMargins(8, 8, 8, 8)
        
        title_label = QLabel(f"<b>📦 {product_name}</b>")
        info_layout.addWidget(title_label)
        
        details_label = QLabel(f"Code: {product_code} | Stock: <b style='color:#FF9800;'>{current_stock}</b>")
        info_layout.addWidget(details_label)
        
        layout.addWidget(info_frame)
        
        # Form layout for compact display
        form_frame = QFrame()
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(8)
        
        # Quantity
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 999999)
        self.quantity_spin.setValue(10)
        self.quantity_spin.setMinimumHeight(30)
        self.quantity_spin.valueChanged.connect(self._update_total)
        form_layout.addRow("Quantity:", self.quantity_spin)
        
        # Cost Price
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0.01, 9999999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setValue(self.original_cost_price)
        self.price_spin.setPrefix("Rs. ")
        self.price_spin.setMinimumHeight(30)
        self.price_spin.valueChanged.connect(self._update_total)
        form_layout.addRow("Cost Price:", self.price_spin)
        
        # Supplier dropdown
        self.supplier_combo = QComboBox()
        self.supplier_combo.setMinimumHeight(30)
        self._load_suppliers()
        
        # Pre-select last supplier if available
        if last_purchase_info and last_purchase_info.get('Supplier_ID'):
            last_sup_id = last_purchase_info['Supplier_ID']
            for i in range(self.supplier_combo.count()):
                if self.supplier_combo.itemData(i) == last_sup_id:
                    self.supplier_combo.setCurrentIndex(i)
                    break
        
        form_layout.addRow("Supplier:", self.supplier_combo)
        
        layout.addWidget(form_frame)
        
        # Total display
        self.total_label = QLabel()
        self.total_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #4CAF50; padding: 5px;")
        self.total_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.total_label)
        
        self._update_total()
        
        # Note
        note_label = QLabel("<i>Note: Inventory updates when order is marked 'Received'</i>")
        note_label.setStyleSheet("color: #666; font-size: 8pt;")
        note_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(note_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(35)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        self.place_order_btn = QPushButton("🛒 Place Order")
        self.place_order_btn.setMinimumHeight(35)
        self.place_order_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.place_order_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.place_order_btn)
        
        layout.addLayout(button_layout)
    
    def _load_suppliers(self):
        """Load suppliers into combo box."""
        try:
            suppliers = SupplierRepository.get_all()
            for supplier in suppliers:
                self.supplier_combo.addItem(
                    f"{supplier.supplier_name} ({supplier.supplier_id})",
                    supplier.supplier_id
                )
        except Exception as e:
            print(f"Error loading suppliers: {e}")
    
    def _update_total(self):
        """Update the total amount label."""
        quantity = self.quantity_spin.value()
        unit_price = self.price_spin.value()
        total = quantity * unit_price
        self.total_label.setText(f"Total: Rs. {total:,.2f}")
    
    def get_quantity(self) -> int:
        """Get the order quantity."""
        return self.quantity_spin.value()
    
    def get_unit_price(self) -> float:
        """Get the unit price."""
        return self.price_spin.value()
    
    def get_supplier_id(self) -> str:
        """Get the selected supplier ID."""
        return self.supplier_combo.currentData()


class InventoryView(QWidget):
    """
    Widget for managing inventory levels.
    
    Signals:
        navigate_back: Go back to previous view
    """
    
    navigate_back = Signal()
    
    def __init__(self, parent=None):
        """Initialize the inventory view."""
        super().__init__(parent)
        
        # Data
        self.inventory_items = []
        
        # Filter state
        self.show_low_stock_only = False
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
        
        # Title
        title_label = QLabel("📊 Inventory Management")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # =====================================================================
        # FILTER BAR
        # =====================================================================
        
        filter_frame = QFrame()
        filter_frame.setProperty("class", "card")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setSpacing(15)
        
        # Search
        search_label = QLabel("Search:")
        filter_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by product name...")
        self.search_input.setMinimumWidth(250)
        self.search_input.setClearButtonEnabled(True)
        filter_layout.addWidget(self.search_input)
        
        # Low stock filter
        self.low_stock_checkbox = QCheckBox("Show Low Stock Only")
        self.low_stock_checkbox.setStyleSheet("font-weight: bold; color: #FF5722;")
        filter_layout.addWidget(self.low_stock_checkbox)
        
        filter_layout.addStretch()
        
        # Refresh button
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.setProperty("class", "secondary")
        filter_layout.addWidget(self.refresh_button)
        
        main_layout.addWidget(filter_frame)
        
        # =====================================================================
        # STATS ROW
        # =====================================================================
        
        stats_layout = QHBoxLayout()
        
        # Total products
        self.total_products_label = QLabel("Total Products: 0")
        self.total_products_label.setStyleSheet("font-size: 11pt;")
        stats_layout.addWidget(self.total_products_label)
        
        stats_layout.addSpacing(30)
        
        # Low stock count
        self.low_stock_label = QLabel("⚠️ Low Stock: 0")
        self.low_stock_label.setStyleSheet("font-size: 11pt; color: #FF5722; font-weight: bold;")
        stats_layout.addWidget(self.low_stock_label)
        
        stats_layout.addSpacing(30)
        
        # Out of stock count
        self.out_of_stock_label = QLabel("❌ Out of Stock: 0")
        self.out_of_stock_label.setStyleSheet("font-size: 11pt; color: #F44336; font-weight: bold;")
        stats_layout.addWidget(self.out_of_stock_label)
        
        stats_layout.addStretch()
        
        main_layout.addLayout(stats_layout)
        
        # =====================================================================
        # INVENTORY TABLE
        # =====================================================================
        
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(7)
        self.inventory_table.setHorizontalHeaderLabels([
            "Product Code", "Product Name", "Brand", "In Stock",
            "Min Level", "Status", "Actions"
        ])
        
        # Table settings
        self.inventory_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.inventory_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.inventory_table.setAlternatingRowColors(True)
        self.inventory_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.inventory_table.setSortingEnabled(True)
        self.inventory_table.verticalHeader().setVisible(False)
        self.inventory_table.verticalHeader().setDefaultSectionSize(60)
        
        # Column widths
        header = self.inventory_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        self.inventory_table.setColumnWidth(6, 130)  # Wider for Buy Stock button
        
        main_layout.addWidget(self.inventory_table)
        
        # =====================================================================
        # FOOTER
        # =====================================================================
        
        footer_layout = QHBoxLayout()
        
        self.status_label = QLabel("0 items")
        self.status_label.setStyleSheet("color: #757575;")
        footer_layout.addWidget(self.status_label)
        
        footer_layout.addStretch()
        
        main_layout.addLayout(footer_layout)
    
    def _connect_signals(self):
        """Connect UI signals."""
        
        self.search_input.textChanged.connect(self._on_search_changed)
        self.low_stock_checkbox.toggled.connect(self._on_low_stock_filter_changed)
        self.refresh_button.clicked.connect(self.refresh_data)
    
    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        
        # F5: Refresh
        shortcut_refresh = QShortcut(QKeySequence("F5"), self)
        shortcut_refresh.activated.connect(self.refresh_data)
        
        # Ctrl+F: Focus search
        shortcut_search = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut_search.activated.connect(self.search_input.setFocus)
    
    def refresh_data(self):
        """Refresh inventory data from database."""
        
        try:
            # Load inventory with product details
            self.inventory_items = InventoryRepository.get_all()
            
            # Apply filters and display
            self._apply_filters()
        
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Failed to load inventory: {str(e)}",
                QMessageBox.Ok
            )
    
    def _on_search_changed(self, text: str):
        """Handle search text change."""
        self.search_text = text.strip().lower()
        self._apply_filters()
    
    def _on_low_stock_filter_changed(self, checked: bool):
        """Handle low stock filter change."""
        self.show_low_stock_only = checked
        self._apply_filters()
    
    def _apply_filters(self):
        """Apply current filters and update the table."""
        
        filtered = self.inventory_items
        
        # Apply low stock filter
        if self.show_low_stock_only:
            filtered = [item for item in filtered if item.is_low_stock]
        
        # Apply search filter
        if self.search_text:
            filtered = [
                item for item in filtered
                if self._item_matches_search(item)
            ]
        
        # Update table
        self._populate_table(filtered)
        
        # Update stats
        self._update_stats()
    
    def _item_matches_search(self, item: InventoryItem) -> bool:
        """Check if inventory item matches search text."""
        return (
            (item.product_name and self.search_text in item.product_name.lower()) or
            (item.product_code and self.search_text in item.product_code.lower()) or
            (item.brand and self.search_text in item.brand.lower())
        )
    
    def _populate_table(self, items):
        """Populate the table with inventory items."""
        
        self.inventory_table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            # Product Code
            code_item = QTableWidgetItem(item.product_code)
            code_item.setData(Qt.UserRole, item.product_code)
            self.inventory_table.setItem(row, 0, code_item)
            
            # Product Name
            name_item = QTableWidgetItem(item.product_name or "")
            self.inventory_table.setItem(row, 1, name_item)
            
            # Brand
            brand_item = QTableWidgetItem(item.brand or "")
            self.inventory_table.setItem(row, 2, brand_item)
            
            # In Stock
            qty_item = QTableWidgetItem(str(item.current_stock))
            qty_item.setTextAlignment(Qt.AlignCenter)
            
            # Color code based on stock level
            min_level = item.min_stock_level or 0
            if item.current_stock == 0:
                qty_item.setForeground(QBrush(QColor("#F44336")))
                qty_item.setFont(self._get_bold_font())
            elif item.current_stock <= min_level:
                qty_item.setForeground(QBrush(QColor("#FF5722")))
                qty_item.setFont(self._get_bold_font())
            
            self.inventory_table.setItem(row, 3, qty_item)
            
            # Min Stock Level
            min_item = QTableWidgetItem(str(min_level))
            min_item.setTextAlignment(Qt.AlignCenter)
            self.inventory_table.setItem(row, 4, min_item)
            
            # Status
            if item.current_stock == 0:
                status = "❌ Out of Stock"
                status_color = "#F44336"
            elif item.is_low_stock:
                status = "⚠️ Low Stock"
                status_color = "#FF5722"
            else:
                status = "✅ In Stock"
                status_color = "#4CAF50"
            
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QBrush(QColor(status_color)))
            status_item.setFont(self._get_bold_font())
            self.inventory_table.setItem(row, 5, status_item)
            
            # Actions
            self._add_action_button(row, item)
        
        # Update status
        self.status_label.setText(f"{len(items)} items shown")
    
    def _get_bold_font(self) -> QFont:
        """Get a bold font."""
        font = QFont()
        font.setBold(True)
        return font
    
    def _add_action_button(self, row: int, item: InventoryItem):
        """Add action button to table row."""
        
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(5, 5, 5, 5)
        actions_layout.setSpacing(5)
        
        # Buy Stock button
        buy_btn = QPushButton("🛒 Buy Stock")
        buy_btn.setMinimumHeight(30)
        buy_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold; padding: 5px 10px;"
        )
        buy_btn.setCursor(Qt.PointingHandCursor)
        buy_btn.clicked.connect(lambda checked, i=item: self._buy_stock(i))
        actions_layout.addWidget(buy_btn)
        
        self.inventory_table.setCellWidget(row, 6, actions_widget)
    
    def _buy_stock(self, item: InventoryItem):
        """Show dialog to place a purchase order for stock."""
        product_code = item.product_code
        product_name = item.product_name or product_code
        current_stock = item.current_stock
        cost_price = float(item.cost_price) if item.cost_price else 0.0
        
        # Get last purchase info for this product
        last_purchase_info = None
        try:
            rows = db.call_procedure_with_result('usp_GetLastPurchaseForProduct', (product_code,))
            if rows:
                row = rows[0]
                last_purchase_info = {
                    'Supplier_ID': row.Supplier_ID,
                    'Supplier_Name': row.Supplier_Name,
                    'Last_Cost_Price': float(row.Last_Cost_Price),
                    'Last_Quantity': row.Last_Quantity,
                    'Last_Purchase_Date': row.Last_Purchase_Date
                }
        except Exception as e:
            print(f"Error getting last purchase info: {e}")
        
        # Show the Buy Stock dialog
        dialog = BuyStockDialog(
            product_code=product_code,
            product_name=product_name,
            current_stock=current_stock,
            original_cost_price=cost_price,
            last_purchase_info=last_purchase_info,
            parent=self
        )
        
        if dialog.exec() == QDialog.Accepted:
            # Get values from dialog
            quantity = dialog.get_quantity()
            unit_price = dialog.get_unit_price()
            supplier_id = dialog.get_supplier_id()
            
            if not supplier_id:
                QMessageBox.warning(
                    self, "Error",
                    "Please select a supplier.",
                    QMessageBox.Ok
                )
                return
            
            try:
                # Generate purchase number
                purchase_no = PurchaseRepository.get_next_id()
                
                # Create purchase order note
                notes = f"Stock reorder for {product_name}"
                
                # Call stored procedure to create purchase order
                result = db.call_procedure_with_result('usp_CreatePurchaseOrder', (
                    purchase_no,
                    supplier_id,
                    product_code,
                    quantity,
                    unit_price,
                    notes
                ), commit=True)
                
                if result:
                    QMessageBox.information(
                        self, "Purchase Order Created",
                        f"✅ Purchase order <b>{purchase_no}</b> has been created successfully!\n\n"
                        f"Quantity: {quantity}\n"
                        f"Unit Price: Rs. {unit_price:.2f}\n"
                        f"Total: Rs. {quantity * unit_price:,.2f}\n\n"
                        f"<b>Important:</b> The inventory will be updated when you mark "
                        f"this order as 'Received' in the Purchases tab.",
                        QMessageBox.Ok
                    )
                    self.refresh_data()
                else:
                    QMessageBox.warning(
                        self, "Error",
                        "Failed to create purchase order.",
                        QMessageBox.Ok
                    )
            
            except Exception as e:
                print(f"DEBUG: Exception: {e}")
                QMessageBox.critical(
                    self, "Error",
                    f"Failed to create purchase order: {str(e)}",
                    QMessageBox.Ok
                )
    
    def _adjust_stock(self, item: InventoryItem):
        """Show dialog to adjust stock level."""
        
        product_name = item.product_name or item.product_code
        min_level = item.min_stock_level or 0
        
        dialog = AdjustStockDialog(
            product_name,
            item.current_stock,
            min_level,
            self
        )
        
        if dialog.exec() == QDialog.Accepted:
            new_qty = dialog.get_new_quantity()
            
            try:
                success = InventoryRepository.update_stock(item.product_code, new_qty)
                
                if success:
                    QMessageBox.information(
                        self, "Success",
                        "Inventory updated successfully.",
                        QMessageBox.Ok
                    )
                    self.refresh_data()
                else:
                    QMessageBox.warning(
                        self, "Error",
                        "Failed to update inventory.",
                        QMessageBox.Ok
                    )
            
            except Exception as e:
                QMessageBox.critical(
                    self, "Error",
                    f"Failed to update inventory: {str(e)}",
                    QMessageBox.Ok
                )
    
    def _update_stats(self):
        """Update the stats labels."""
        
        total = len(self.inventory_items)
        low_stock = sum(1 for item in self.inventory_items if item.is_low_stock and item.current_stock > 0)
        out_of_stock = sum(1 for item in self.inventory_items if item.current_stock == 0)
        
        self.total_products_label.setText(f"Total Products: {total}")
        self.low_stock_label.setText(f"⚠️ Low Stock: {low_stock}")
        self.out_of_stock_label.setText(f"❌ Out of Stock: {out_of_stock}")


# =============================================================================
# MODULE TEST
# =============================================================================

if __name__ == "__main__":
    """Test the inventory view when running this module directly."""
    
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    try:
        with open("styles/theme.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass
    
    view = InventoryView()
    view.show()
    
    sys.exit(app.exec())
