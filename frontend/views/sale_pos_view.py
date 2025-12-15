"""
=============================================================================
Point of Sale (POS) View
=============================================================================
This module provides the sales entry screen with a fast, cashier-friendly UI.

Features:
    - Quick product search by barcode or name
    - Large product tiles with big buttons
    - Shopping cart display
    - Quantity adjustment with +/- buttons
    - Real-time total calculation
    - Customer selection
    - Payment processing
    - Keyboard shortcuts for speed
    - Receipt preview

Keyboard Shortcuts:
    - F1: Focus search/barcode input
    - F2: Checkout
    - F3: Clear cart
    - Enter: Add product (when in search)
    - +/-: Adjust quantity of selected item
    - Delete: Remove selected item
    - Escape: Cancel sale

=============================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QSpinBox,
    QFrame, QMessageBox, QGroupBox, QScrollArea, QHeaderView, QDialog,
    QDialogButtonBox, QDoubleSpinBox, QFormLayout, QSizePolicy, QTextEdit
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from PySide6.QtPrintSupport import QPrinter, QPrintDialog

from dataclasses import dataclass
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

from repositories.product_repository import ProductRepository, Product
from repositories.customer_repository import CustomerRepository
from repositories.inventory_repository import InventoryRepository
from repositories.sale_repository import SaleRepository
from repositories.employee_repository import Employee
from utils import format_currency


class ReceiptDialog(QDialog):
    """Dialog showing a printable receipt/slip for the customer."""
    
    def __init__(self, invoice_no: str, customer_name: str, employee_name: str,
                 cart_items: list, subtotal: float, tax: float, total: float,
                 payment_method: str, amount_received: float, change: float, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("🧾 Receipt")
        self.setMinimumSize(500, 650)
        self.setMaximumWidth(450)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Receipt content in a text widget for easy printing
        self.receipt_text = QTextEdit()
        self.receipt_text.setReadOnly(True)
        self.receipt_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 11pt;
                background-color: white;
                border: 1px solid #ddd;
                padding: 15px;
            }
        """)
        
        # Build receipt content
        receipt_content = self._build_receipt(
            invoice_no, customer_name, employee_name,
            cart_items, subtotal, tax, total,
            payment_method, amount_received, change
        )
        self.receipt_text.setHtml(receipt_content)
        layout.addWidget(self.receipt_text)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        print_btn = QPushButton("🖨️ Print Receipt")
        print_btn.setMinimumHeight(40)
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        print_btn.clicked.connect(self._print_receipt)
        btn_layout.addWidget(print_btn)
        
        close_btn = QPushButton("✓ Done")
        close_btn.setMinimumHeight(40)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #43A047; }
        """)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def _build_receipt(self, invoice_no, customer_name, employee_name,
                       cart_items, subtotal, tax, total,
                       payment_method, amount_received, change) -> str:
        """Build the HTML content for the receipt."""
        
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        # Header
        html = """
        <div style="text-align: center; font-family: 'Courier New', monospace;">
            <h2 style="margin: 5px 0;">MOBILE ACCESSORY STORE</h2>
            <p style="margin: 2px 0; font-size: 10pt;">Your one-stop shop for mobile accessories</p>
            <p style="margin: 2px 0; font-size: 9pt;">Tel: 0300-1234567</p>
            <hr style="border: 1px dashed #000;">
        </div>
        """
        
        # Invoice info
        html += f"""
        <table style="width: 100%; font-size: 10pt;">
            <tr><td><b>Invoice #:</b></td><td style="text-align: right;">{invoice_no}</td></tr>
            <tr><td><b>Date:</b></td><td style="text-align: right;">{date_str}</td></tr>
            <tr><td><b>Time:</b></td><td style="text-align: right;">{time_str}</td></tr>
            <tr><td><b>Cashier:</b></td><td style="text-align: right;">{employee_name or 'Staff'}</td></tr>
            <tr><td><b>Customer:</b></td><td style="text-align: right;">{customer_name or 'Walk-in'}</td></tr>
        </table>
        <hr style="border: 1px dashed #000;">
        """
        
        # Items
        html += """
        <table style="width: 100%; font-size: 10pt;">
            <tr style="border-bottom: 1px solid #000;">
                <th style="text-align: left;">Item</th>
                <th style="text-align: center;">Qty</th>
                <th style="text-align: right;">Price</th>
                <th style="text-align: right;">Total</th>
            </tr>
        """
        
        for item in cart_items:
            # Truncate long names
            name = item.product_name[:20] + "..." if len(item.product_name) > 20 else item.product_name
            html += f"""
            <tr>
                <td style="text-align: left;">{name}</td>
                <td style="text-align: center;">{item.quantity}</td>
                <td style="text-align: right;">{item.unit_price:.2f}</td>
                <td style="text-align: right;">{item.total_price:.2f}</td>
            </tr>
            """
        
        html += "</table>"
        html += '<hr style="border: 1px dashed #000;">'
        
        # Totals
        html += f"""
        <table style="width: 100%; font-size: 10pt;">
            <tr><td>Subtotal:</td><td style="text-align: right;">Rs. {subtotal:,.2f}</td></tr>
            <tr><td>Tax (8%):</td><td style="text-align: right;">Rs. {tax:,.2f}</td></tr>
            <tr style="font-weight: bold; font-size: 12pt;">
                <td>TOTAL:</td><td style="text-align: right;">Rs. {total:,.2f}</td>
            </tr>
        </table>
        <hr style="border: 1px dashed #000;">
        """
        
        # Payment info
        html += f"""
        <table style="width: 100%; font-size: 10pt;">
            <tr><td>Payment Method:</td><td style="text-align: right;">{payment_method}</td></tr>
            <tr><td>Amount Received:</td><td style="text-align: right;">Rs. {amount_received:,.2f}</td></tr>
            <tr style="font-weight: bold;"><td>Change:</td><td style="text-align: right;">Rs. {change:,.2f}</td></tr>
        </table>
        <hr style="border: 1px dashed #000;">
        """
        
        # Footer
        html += """
        <div style="text-align: center; font-size: 9pt; margin-top: 10px;">
            <p style="margin: 5px 0;">Thank you for shopping with us!</p>
            <p style="margin: 5px 0;">Please keep this receipt for returns.</p>
            <p style="margin: 5px 0;">*** Have a nice day! ***</p>
        </div>
        """
        
        return html
    
    def _print_receipt(self):
        """Print the receipt."""
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec() == QDialog.Accepted:
            self.receipt_text.print_(printer)
            QMessageBox.information(self, "Printed", "Receipt sent to printer!")


@dataclass
class CartItem:
    """Represents an item in the shopping cart."""
    product_id: int
    product_code: str  # Added for stored procedure
    product_name: str
    sku: str
    barcode: str
    unit_price: float
    quantity: int
    available_stock: int
    
    @property
    def total_price(self) -> float:
        return self.unit_price * self.quantity


class ProductSearchResultWidget(QPushButton):
    """A clickable widget showing product search results."""
    
    def __init__(self, product: Product, available_stock: int, parent=None):
        super().__init__(parent)
        
        self.product = product
        self.available_stock = available_stock
        
        self.setProperty("class", "tile")
        self.setMinimumSize(160, 90)
        self.setMaximumSize(180, 100)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        # Product name
        name_label = QLabel(product.product_name)
        name_font = QFont()
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        # Price and stock
        info_label = QLabel(
            f"{format_currency(product.price)} | Stock: {available_stock}"
        )
        info_label.setStyleSheet("color: #757575;")
        layout.addWidget(info_label)


class CustomerInfoDialog(QDialog):
    """Dialog for entering customer name and phone number at checkout."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Customer Information")
        self.setMinimumWidth(550)
        self.setModal(True)
        
        self.customer_id = None
        self.customer_name = None
        self.is_existing_customer = False
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QLabel("👤 Customer Information")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1976D2;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Info text
        info = QLabel("Enter customer details for the bill.\nIf phone number exists, existing customer will be used.")
        info.setStyleSheet("font-size: 12px; color: #666;")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        # Form
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        # Phone number input
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("e.g., 03001234567")
        self.phone_input.setMinimumHeight(45)
        self.phone_input.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 10px;
                border: 2px solid #ccc;
                border-radius: 8px;
            }
            QLineEdit:focus {
                border: 2px solid #1976D2;
            }
        """)
        self.phone_input.textChanged.connect(self._check_phone)
        form_layout.addRow("📱 Phone Number:", self.phone_input)
        
        # Customer name input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Customer's full name")
        self.name_input.setMinimumHeight(45)
        self.name_input.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 10px;
                border: 2px solid #ccc;
                border-radius: 8px;
            }
            QLineEdit:focus {
                border: 2px solid #1976D2;
            }
        """)
        form_layout.addRow("👤 Customer Name:", self.name_input)
        
        layout.addWidget(form_frame)
        
        # Status label (shows if customer exists)
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumHeight(40)
        self.status_label.setStyleSheet("font-size: 13px; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        # Walk-in button
        walkin_btn = QPushButton("🚶 Walk-in Customer")
        walkin_btn.setMinimumHeight(50)
        walkin_btn.setCursor(Qt.PointingHandCursor)
        walkin_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-weight: bold;
                font-size: 13px;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #F57C00; }
        """)
        walkin_btn.clicked.connect(self._use_walkin)
        btn_layout.addWidget(walkin_btn)
        
        # Continue button
        self.continue_btn = QPushButton("✓ Continue to Checkout")
        self.continue_btn.setMinimumHeight(50)
        self.continue_btn.setCursor(Qt.PointingHandCursor)
        self.continue_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #388E3C; }
            QPushButton:disabled { background-color: #BDBDBD; }
        """)
        self.continue_btn.clicked.connect(self._continue)
        btn_layout.addWidget(self.continue_btn)
        
        layout.addLayout(btn_layout)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #616161; }
        """)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
        
        # Focus on phone input
        self.phone_input.setFocus()
    
    def _check_phone(self, phone_text: str):
        """Check if phone number exists in database."""
        if len(phone_text) >= 10:
            # Check for existing customer
            existing = CustomerRepository.get_by_phone(phone_text)
            if existing:
                self.is_existing_customer = True
                self.customer_id = existing.customer_id
                self.name_input.setText(existing.customer_name)
                self.name_input.setEnabled(False)
                self.status_label.setText(f"✅ Existing Customer Found: {existing.customer_name} ({existing.customer_id})")
                self.status_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #2E7D32; background-color: #E8F5E9; padding: 10px; border-radius: 5px;")
            else:
                self.is_existing_customer = False
                self.customer_id = None
                self.name_input.setEnabled(True)
                if self.name_input.text() == "" or not self.name_input.isEnabled():
                    self.name_input.clear()
                self.status_label.setText("🆕 New Customer - Please enter name")
                self.status_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #1976D2; background-color: #E3F2FD; padding: 10px; border-radius: 5px;")
        else:
            self.status_label.setText("")
            self.name_input.setEnabled(True)
            self.is_existing_customer = False
    
    def _use_walkin(self):
        """Use walk-in customer."""
        self.customer_id = 'C000'
        self.customer_name = 'Walk-in Customer'
        self.is_existing_customer = True
        self.accept()
    
    def _continue(self):
        """Validate and continue to checkout."""
        phone = self.phone_input.text().strip()
        name = self.name_input.text().strip()
        
        if not phone:
            QMessageBox.warning(self, "Required", "Please enter a phone number or use Walk-in Customer.")
            return
        
        if not self.is_existing_customer and not name:
            QMessageBox.warning(self, "Required", "Please enter the customer's name.")
            return
        
        if self.is_existing_customer:
            # Use existing customer
            self.customer_name = name
        else:
            # Create new customer
            success, msg, new_id = CustomerRepository.create_customer(
                customer_name=name,
                phone=phone
            )
            if success:
                self.customer_id = new_id
                self.customer_name = name
                QMessageBox.information(
                    self, "Customer Created",
                    f"New customer created:\n\nID: {new_id}\nName: {name}\nPhone: {phone}"
                )
            else:
                QMessageBox.critical(self, "Error", f"Failed to create customer: {msg}")
                return
        
        self.accept()
    
    def get_customer_info(self) -> dict:
        """Return the customer information."""
        return {
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'is_existing': self.is_existing_customer
        }


class CheckoutDialog(QDialog):
    """Dialog for completing a sale with payment information."""
    
    def __init__(self, total_amount: float, customer_name: str, cart_items: list = None, parent=None):
        super().__init__(parent)
        from PySide6.QtWidgets import QScrollArea
        
        self.setWindowTitle("Checkout - Complete Sale")
        self.setMinimumSize(550, 600)
        self.resize(600, 700)
        self.setModal(True)
        
        # Outer layout for dialog
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: white; }")
        
        # Content widget inside scroll
        content = QWidget()
        content.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(content)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # ===== HEADER =====
        header = QLabel("CHECKOUT")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #1976D2; background: white;")
        header.setAlignment(Qt.AlignCenter)
        header.setFixedHeight(40)
        layout.addWidget(header)
        
        # ===== CUSTOMER =====
        cust_frame = QFrame()
        cust_frame.setStyleSheet("QFrame { background-color: #E3F2FD; border-radius: 5px; }")
        cust_frame.setFixedHeight(40)
        cust_lay = QHBoxLayout(cust_frame)
        cust_lay.setContentsMargins(12, 8, 12, 8)
        cust_lbl = QLabel("Customer:")
        cust_lbl.setStyleSheet("font-weight: bold; background: transparent;")
        cust_lay.addWidget(cust_lbl)
        cust_val = QLabel(customer_name or "Walk-in Customer")
        cust_val.setStyleSheet("font-weight: bold; color: #1565C0; font-size: 13px; background: transparent;")
        cust_lay.addWidget(cust_val)
        cust_lay.addStretch()
        layout.addWidget(cust_frame)
        
        # ===== ORDER ITEMS =====
        items_header = QLabel("ORDER ITEMS")
        items_header.setStyleSheet("font-weight: bold; font-size: 11px; color: #666; background: white; margin-top: 8px;")
        layout.addWidget(items_header)
        
        # Create table for items
        tbl = QTableWidget()
        tbl.setColumnCount(4)
        tbl.setHorizontalHeaderLabels(["Product", "Qty", "Price", "Total"])
        tbl.verticalHeader().setVisible(False)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl.setSelectionMode(QTableWidget.NoSelection)
        tbl.setAlternatingRowColors(True)
        tbl.setStyleSheet("""
            QTableWidget { 
                background-color: white; 
                border: 1px solid #E0E0E0; 
                gridline-color: #EEEEEE;
            }
            QTableWidget::item { padding: 5px; }
            QHeaderView::section { 
                background-color: #F5F5F5; 
                font-weight: bold; 
                border: none;
                border-bottom: 1px solid #E0E0E0;
                padding: 6px;
            }
        """)
        
        # Set column sizes
        h = tbl.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.Stretch)
        h.setSectionResizeMode(1, QHeaderView.Fixed)
        h.setSectionResizeMode(2, QHeaderView.Fixed)
        h.setSectionResizeMode(3, QHeaderView.Fixed)
        tbl.setColumnWidth(1, 45)
        tbl.setColumnWidth(2, 75)
        tbl.setColumnWidth(3, 75)
        
        # Populate table
        if cart_items and len(cart_items) > 0:
            tbl.setRowCount(len(cart_items))
            for r, item in enumerate(cart_items):
                # Product name
                name_item = QTableWidgetItem(item.product_name)
                tbl.setItem(r, 0, name_item)
                # Quantity
                qty_item = QTableWidgetItem(str(item.quantity))
                qty_item.setTextAlignment(Qt.AlignCenter)
                tbl.setItem(r, 1, qty_item)
                # Price
                price_item = QTableWidgetItem(format_currency(item.unit_price))
                price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                tbl.setItem(r, 2, price_item)
                # Total
                total_item = QTableWidgetItem(format_currency(item.total_price))
                total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                tbl.setItem(r, 3, total_item)
                tbl.setRowHeight(r, 30)
            
            # Set table height - show up to 5 rows, then scroll
            visible_rows = min(len(cart_items), 5)
            tbl.setMinimumHeight(30 * visible_rows + 35)
            tbl.setMaximumHeight(30 * 5 + 35)
        else:
            tbl.setRowCount(0)
            tbl.setFixedHeight(65)
        
        layout.addWidget(tbl)
        
        # Items count
        if cart_items:
            total_qty = sum(i.quantity for i in cart_items)
            count_lbl = QLabel(f"Total Items: {total_qty}")
            count_lbl.setAlignment(Qt.AlignRight)
            count_lbl.setStyleSheet("font-weight: bold; color: #666; background: white;")
            layout.addWidget(count_lbl)
        
        # ===== PAYMENT DETAILS =====
        pay_header = QLabel("PAYMENT DETAILS")
        pay_header.setStyleSheet("font-weight: bold; font-size: 11px; color: #666; background: white; margin-top: 10px;")
        layout.addWidget(pay_header)
        
        pay_frame = QFrame()
        pay_frame.setStyleSheet("QFrame { background-color: #FAFAFA; border: 1px solid #E0E0E0; border-radius: 5px; }")
        pay_grid = QGridLayout(pay_frame)
        pay_grid.setSpacing(8)
        pay_grid.setContentsMargins(15, 12, 15, 12)
        pay_grid.setColumnMinimumWidth(0, 130)
        pay_grid.setColumnMinimumWidth(1, 150)
        
        subtotal = sum(item.total_price for item in cart_items) if cart_items else total_amount / 1.08
        tax = subtotal * 0.08
        
        # Subtotal row
        pay_grid.addWidget(QLabel("Subtotal:"), 0, 0)
        sub_val = QLabel(format_currency(subtotal))
        sub_val.setAlignment(Qt.AlignRight)
        pay_grid.addWidget(sub_val, 0, 1)
        
        # Tax row
        pay_grid.addWidget(QLabel("Tax (8%):"), 1, 0)
        tax_val = QLabel(format_currency(tax))
        tax_val.setAlignment(Qt.AlignRight)
        pay_grid.addWidget(tax_val, 1, 1)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(2)
        sep.setStyleSheet("background-color: #BDBDBD;")
        pay_grid.addWidget(sep, 2, 0, 1, 2)
        
        # Total row - BIG
        total_lbl = QLabel("TOTAL:")
        total_lbl.setStyleSheet("font-size: 15px; font-weight: bold;")
        pay_grid.addWidget(total_lbl, 3, 0)
        total_val = QLabel(format_currency(total_amount))
        total_val.setStyleSheet("font-size: 18px; font-weight: bold; color: #2E7D32;")
        total_val.setAlignment(Qt.AlignRight)
        pay_grid.addWidget(total_val, 3, 1)
        
        # Payment method
        method_lbl = QLabel("Payment Method:")
        method_lbl.setStyleSheet("font-weight: bold; margin-top: 5px;")
        pay_grid.addWidget(method_lbl, 4, 0)
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems(["Cash", "Credit Card", "Debit Card", "Mobile Payment"])
        self.payment_method_combo.setFixedHeight(30)
        pay_grid.addWidget(self.payment_method_combo, 4, 1)
        
        # Amount received
        recv_lbl = QLabel("Amount Received:")
        recv_lbl.setStyleSheet("font-weight: bold;")
        pay_grid.addWidget(recv_lbl, 5, 0)
        self.amount_received_input = QDoubleSpinBox()
        self.amount_received_input.setRange(0, 999999.99)
        self.amount_received_input.setDecimals(2)
        self.amount_received_input.setPrefix("Rs. ")
        self.amount_received_input.setValue(total_amount)
        self.amount_received_input.setFixedHeight(32)
        self.amount_received_input.setStyleSheet("font-size: 13px; font-weight: bold;")
        self.amount_received_input.valueChanged.connect(self._update_change)
        pay_grid.addWidget(self.amount_received_input, 5, 1)
        
        # Change
        chg_lbl = QLabel("Change:")
        chg_lbl.setStyleSheet("font-weight: bold;")
        pay_grid.addWidget(chg_lbl, 6, 0)
        self.change_label = QLabel("Rs. 0.00")
        self.change_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #2E7D32;")
        self.change_label.setAlignment(Qt.AlignRight)
        pay_grid.addWidget(self.change_label, 6, 1)
        
        layout.addWidget(pay_frame)
        layout.addStretch()
        
        scroll.setWidget(content)
        outer_layout.addWidget(scroll)
        
        # ===== BUTTONS (outside scroll) =====
        btn_frame = QFrame()
        btn_frame.setStyleSheet("QFrame { background-color: #F5F5F5; border-top: 1px solid #E0E0E0; }")
        btn_frame.setFixedHeight(65)
        btn_lay = QHBoxLayout(btn_frame)
        btn_lay.setContentsMargins(20, 10, 20, 10)
        btn_lay.setSpacing(15)
        
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setFixedSize(120, 42)
        btn_cancel.setStyleSheet("""
            QPushButton { background-color: #E53935; color: white; font-weight: bold; font-size: 12px; border-radius: 5px; border: none; }
            QPushButton:hover { background-color: #C62828; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_lay.addWidget(btn_cancel)
        
        btn_complete = QPushButton("Complete Sale")
        btn_complete.setFixedHeight(42)
        btn_complete.setStyleSheet("""
            QPushButton { background-color: #43A047; color: white; font-weight: bold; font-size: 14px; border-radius: 5px; border: none; }
            QPushButton:hover { background-color: #2E7D32; }
        """)
        btn_complete.clicked.connect(self.accept)
        btn_lay.addWidget(btn_complete, stretch=2)
        
        outer_layout.addWidget(btn_frame)
        
        self.total_amount = total_amount
        self._update_change()
    
    def _update_change(self):
        """Update the change amount display."""
        received = self.amount_received_input.value()
        change = received - self.total_amount
        self.change_label.setText(f"Rs. {max(0, change):,.2f}")
        
        if change < 0:
            self.change_label.setStyleSheet("color: red; font-weight: bold; font-size: 14pt;")
        else:
            self.change_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 14pt;")
    
    def get_payment_info(self) -> dict:
        """Get the payment information entered by the user."""
        return {
            "method": self.payment_method_combo.currentText(),
            "amount_received": self.amount_received_input.value(),
            "change": max(0, self.amount_received_input.value() - self.total_amount)
        }


class TaxSelectionDialog(QDialog):
    """Dialog for selecting tax rate with preset options."""
    
    def __init__(self, current_rate: float = 0, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Tax Rate")
        self.setMinimumWidth(450)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Select Tax Rate")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Preset tax rates - HARDCODED VALUES ONLY
        presets_group = QGroupBox("Tax Options")
        presets_layout = QVBoxLayout(presets_group)
        
        self.tax_buttons = []
        preset_rates = [
            ("No Tax (0%)", 0),
            ("GST Tax (16%)", 16),
            ("Sale Tax (17%)", 17),
        ]
        
        for label, rate in preset_rates:
            btn = QPushButton(label)
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #E3F2FD;
                    border: 1px solid #2196F3;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 13px;
                    color: #1565C0;
                }
                QPushButton:hover { background-color: #BBDEFB; }
            """)
            btn.clicked.connect(lambda _, r=rate: self._select_rate(r))
            presets_layout.addWidget(btn)
            self.tax_buttons.append(btn)
        
        layout.addWidget(presets_group)
        
        # Custom rate
        custom_group = QGroupBox("Custom Tax Rate")
        custom_layout = QHBoxLayout(custom_group)
        
        custom_layout.addWidget(QLabel("Rate:"))
        self.custom_rate = QDoubleSpinBox()
        self.custom_rate.setRange(0, 100)
        self.custom_rate.setDecimals(1)
        self.custom_rate.setSuffix(" %")
        self.custom_rate.setValue(current_rate)
        self.custom_rate.setMinimumHeight(35)
        self.custom_rate.setMinimumWidth(100)
        custom_layout.addWidget(self.custom_rate)
        
        apply_custom = QPushButton("Apply")
        apply_custom.setMinimumHeight(35)
        apply_custom.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                padding: 0 20px;
            }
            QPushButton:hover { background-color: #43A047; }
        """)
        apply_custom.clicked.connect(self._apply_custom)
        custom_layout.addWidget(apply_custom)
        
        layout.addWidget(custom_group)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #616161; }
        """)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
        
        self.selected_rate = current_rate
    
    def _select_rate(self, rate: float):
        self.selected_rate = rate
        self.accept()
    
    def _apply_custom(self):
        self.selected_rate = self.custom_rate.value()
        self.accept()
    
    def get_rate(self) -> float:
        return self.selected_rate


class DiscountSelectionDialog(QDialog):
    """Dialog for selecting discount with preset options and all-day option."""
    
    def __init__(self, subtotal: float = 0, current_discount: float = 0, allday_active: bool = False, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Apply Discount")
        self.setMinimumWidth(550)
        self.setMinimumHeight(400)
        self.setMaximumHeight(600)
        self.setModal(True)
        self.subtotal = subtotal
        self.current_discount = current_discount
        self.remove_all_discounts = False
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title (outside scroll area)
        title = QLabel("Apply Discount")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Subtotal display
        subtotal_lbl = QLabel(f"Subtotal: Rs. {subtotal:,.2f}")
        subtotal_lbl.setStyleSheet("font-size: 15px; color: #666;")
        subtotal_lbl.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtotal_lbl)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 12px;
                background: #f0f0f0;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #bbb;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #999;
            }
        """)
        
        # Content widget inside scroll
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(5, 5, 5, 5)
        
        # Show current discount if any OR all-day discount active
        if current_discount > 0 or allday_active:
            current_box = QFrame()
            current_box.setStyleSheet("""
                QFrame {
                    background-color: #FFF3E0;
                    border: 2px solid #FF9800;
                    border-radius: 10px;
                }
            """)
            current_layout = QVBoxLayout(current_box)
            current_layout.setContentsMargins(15, 15, 15, 15)
            current_layout.setSpacing(10)
            
            if current_discount > 0:
                current_info = QLabel(f"🏷️ Current Discount: Rs. {current_discount:,.2f}")
                current_info.setStyleSheet("font-size: 16px; font-weight: bold; color: #E65100;")
                current_info.setAlignment(Qt.AlignCenter)
                current_layout.addWidget(current_info)
            
            if allday_active:
                allday_info = QLabel("📅 All-Day Discount is ACTIVE")
                allday_info.setStyleSheet("font-size: 14px; font-weight: bold; color: #2E7D32;")
                allday_info.setAlignment(Qt.AlignCenter)
                current_layout.addWidget(allday_info)
            
            # Remove All Discounts button
            remove_all_btn = QPushButton("🚫 REMOVE ALL DISCOUNTS")
            remove_all_btn.setMinimumHeight(50)
            remove_all_btn.setCursor(Qt.PointingHandCursor)
            remove_all_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 10px;
                }
                QPushButton:hover { background-color: #d32f2f; }
            """)
            remove_all_btn.clicked.connect(self._remove_all_discounts)
            current_layout.addWidget(remove_all_btn)
            
            content_layout.addWidget(current_box)
        
        # Percentage discounts
        pct_group = QGroupBox("Percentage Discount")
        pct_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                font-size: 14px;
                padding-top: 15px;
            }
        """)
        pct_layout = QGridLayout(pct_group)
        pct_layout.setSpacing(12)
        pct_layout.setContentsMargins(10, 20, 10, 10)
        
        pct_rates = [5, 10, 15, 20, 25, 30]
        for i, pct in enumerate(pct_rates):
            discount_amt = subtotal * pct / 100
            btn = QPushButton()
            btn.setMinimumHeight(80)
            btn.setMinimumWidth(130)
            btn.setCursor(Qt.PointingHandCursor)
            
            # Two-line text
            btn.setText(f"{pct}%\nRs. {discount_amt:,.0f}")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFF3E0;
                    border: 2px solid #FF9800;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 16px;
                    color: #E65100;
                    padding: 10px;
                }
                QPushButton:hover { 
                    background-color: #FFE0B2; 
                    border: 3px solid #E65100;
                }
            """)
            btn.clicked.connect(lambda _, d=discount_amt: self._select_discount(d))
            pct_layout.addWidget(btn, i // 3, i % 3)
        
        content_layout.addWidget(pct_group)
        
        # Fixed amount discount
        fixed_group = QGroupBox("Fixed Amount Discount")
        fixed_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                font-size: 14px;
                padding-top: 15px;
            }
        """)
        fixed_layout = QHBoxLayout(fixed_group)
        fixed_layout.setSpacing(12)
        fixed_layout.setContentsMargins(15, 25, 15, 15)
        
        amount_label = QLabel("Amount:")
        amount_label.setStyleSheet("font-weight: normal; font-size: 14px;")
        fixed_layout.addWidget(amount_label)
        
        self.fixed_amount = QDoubleSpinBox()
        self.fixed_amount.setRange(0, 999999)
        self.fixed_amount.setDecimals(2)
        self.fixed_amount.setPrefix("Rs. ")
        self.fixed_amount.setValue(current_discount)
        self.fixed_amount.setMinimumHeight(45)
        self.fixed_amount.setMinimumWidth(160)
        self.fixed_amount.setStyleSheet("""
            QDoubleSpinBox {
                font-size: 15px;
                padding: 8px;
                border: 2px solid #ccc;
                border-radius: 8px;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #FF9800;
            }
        """)
        fixed_layout.addWidget(self.fixed_amount)
        
        apply_fixed = QPushButton("Apply")
        apply_fixed.setMinimumHeight(45)
        apply_fixed.setMinimumWidth(100)
        apply_fixed.setCursor(Qt.PointingHandCursor)
        apply_fixed.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                padding: 0 25px;
            }
            QPushButton:hover { background-color: #F57C00; }
        """)
        apply_fixed.clicked.connect(self._apply_fixed)
        fixed_layout.addWidget(apply_fixed)
        
        content_layout.addWidget(fixed_group)
        
        # All-day discount option
        allday_group = QGroupBox("All-Day Discount")
        allday_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                font-size: 14px;
                padding-top: 15px;
            }
        """)
        allday_layout = QVBoxLayout(allday_group)
        allday_layout.setContentsMargins(10, 20, 10, 10)
        
        allday_info = QLabel("Apply a percentage discount to all sales today:")
        allday_info.setStyleSheet("color: #666; font-weight: normal; font-size: 13px;")
        allday_layout.addWidget(allday_info)
        
        allday_btn_layout = QHBoxLayout()
        allday_btn_layout.setSpacing(10)
        for pct in [10, 15, 20, 25]:
            btn = QPushButton(f"{pct}%\nAll Day")
            btn.setMinimumHeight(55)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #E8F5E9;
                    border: 2px solid #4CAF50;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 13px;
                    color: #2E7D32;
                }
                QPushButton:hover { 
                    background-color: #C8E6C9; 
                    border: 3px solid #2E7D32;
                }
            """)
            btn.clicked.connect(lambda _, p=pct: self._set_allday_discount(p))
            allday_btn_layout.addWidget(btn)
        
        allday_layout.addLayout(allday_btn_layout)
        content_layout.addWidget(allday_group)
        
        # Add stretch at bottom
        content_layout.addStretch()
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)  # stretch factor 1
        
        # Bottom buttons (outside scroll area)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(50)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #616161; }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(btn_layout)
        
        self.selected_discount = current_discount
        self.all_day_percentage = None
    
    def _remove_all_discounts(self):
        """Remove all discounts including all-day discount."""
        self.selected_discount = 0
        self.all_day_percentage = 0  # Signal to remove all-day discount
        self.remove_all_discounts = True
        self.accept()
    
    def _select_discount(self, amount: float):
        self.selected_discount = amount
        self.accept()
    
    def _apply_fixed(self):
        self.selected_discount = self.fixed_amount.value()
        self.accept()
    
    def _set_allday_discount(self, percentage: int):
        self.all_day_percentage = percentage
        self.selected_discount = self.subtotal * percentage / 100
        reply = QMessageBox.question(
            self, "All-Day Discount",
            f"Apply {percentage}% discount to ALL sales for the rest of today?\n\n"
            f"This will automatically apply {percentage}% discount to every sale.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.accept()
    
    def get_discount(self) -> float:
        return self.selected_discount
    
    def get_allday_percentage(self) -> Optional[int]:
        return self.all_day_percentage
    
    def should_remove_all(self) -> bool:
        return self.remove_all_discounts


class SalePOSView(QWidget):
    """
    Point of Sale widget for creating sales.
    
    Signals:
        sale_completed: Emitted when a sale is successfully completed
        navigate_back: Emitted when user wants to go back
    """
    
    # Signals
    sale_completed = Signal(str)  # invoice_no
    navigate_back = Signal()
    
    def __init__(self, current_user: Employee = None, parent=None):
        """
        Initialize the POS view.
        
        Args:
            current_user: Currently logged-in employee
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.current_user = current_user
        
        # Cart data
        self.cart_items: List[CartItem] = []
        
        # Product cache for search
        self.products: List[Product] = []
        self.inventory_map = {}  # product_id -> Inventory
        
        # Customer
        self.selected_customer_id = None
        
        # Set up UI
        self._setup_ui()
        
        # Connect signals
        self._connect_signals()
        
        # Set up shortcuts
        self._setup_shortcuts()
        
        # Load initial data
        self.refresh_data()
        
        # Focus search input
        QTimer.singleShot(100, self.search_input.setFocus)
    
    def _setup_ui(self):
        """Set up the user interface components."""
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # =====================================================================
        # LEFT PANEL - Product Search and Results
        # =====================================================================
        
        left_panel = QFrame()
        left_panel.setProperty("class", "card")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        
        # Search header
        search_header = QHBoxLayout()
        
        title_label = QLabel("🛒 Point of Sale")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        search_header.addWidget(title_label)
        
        search_header.addStretch()
        
        # Back button
        self.back_button = QPushButton("← Back")
        self.back_button.setProperty("class", "secondary")
        self.back_button.clicked.connect(self.navigate_back.emit)
        search_header.addWidget(self.back_button)
        
        left_layout.addLayout(search_header)
        
        # Search input (large, prominent)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "🔍 Scan barcode or search product... (F1)"
        )
        self.search_input.setMinimumHeight(50)
        search_font = QFont()
        search_font.setPointSize(14)
        self.search_input.setFont(search_font)
        self.search_input.setStyleSheet(
            "font-size: 14pt; padding: 10px; border: 2px solid #2196F3; border-radius: 8px;"
        )
        left_layout.addWidget(self.search_input)
        
        # Search results grid (scrollable)
        results_scroll = QScrollArea()
        results_scroll.setWidgetResizable(True)
        results_scroll.setFrameShape(QFrame.NoFrame)
        
        self.results_container = QWidget()
        self.results_layout = QGridLayout(self.results_container)
        self.results_layout.setSpacing(10)
        self.results_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        results_scroll.setWidget(self.results_container)
        left_layout.addWidget(results_scroll)
        
        # Quick action buttons at bottom
        quick_actions = QHBoxLayout()
        
        self.clear_search_btn = QPushButton("Clear Search")
        self.clear_search_btn.setProperty("class", "secondary")
        quick_actions.addWidget(self.clear_search_btn)
        
        quick_actions.addStretch()
        
        left_layout.addLayout(quick_actions)
        
        main_layout.addWidget(left_panel, stretch=2)
        
        # =====================================================================
        # RIGHT PANEL - Shopping Cart
        # =====================================================================
        
        right_panel = QFrame()
        right_panel.setProperty("class", "card")
        right_panel.setMinimumWidth(550)  # Ensure minimum width for cart
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)
        
        # Cart header
        cart_header = QHBoxLayout()
        
        cart_title = QLabel("🛍️ Shopping Cart")
        cart_title_font = QFont()
        cart_title_font.setPointSize(14)
        cart_title_font.setBold(True)
        cart_title.setFont(cart_title_font)
        cart_header.addWidget(cart_title)
        
        cart_header.addStretch()
        
        # Clear cart button
        self.clear_cart_btn = QPushButton("Clear (F3)")
        self.clear_cart_btn.setProperty("class", "danger")
        cart_header.addWidget(self.clear_cart_btn)
        
        right_layout.addLayout(cart_header)
        
        # Customer selection
        customer_layout = QHBoxLayout()
        customer_layout.addWidget(QLabel("Customer:"))
        
        self.customer_combo = QComboBox()
        self.customer_combo.setMinimumHeight(35)
        self.customer_combo.addItem("Walk-in Customer", None)
        customer_layout.addWidget(self.customer_combo, stretch=1)
        
        right_layout.addLayout(customer_layout)
        
        # Cart table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels([
            "Product", "Price", "Qty", "Total", "Actions"
        ])
        self.cart_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.cart_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.cart_table.verticalHeader().setVisible(False)
        
        header = self.cart_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.cart_table.setColumnWidth(0, 180)  # Product column - fixed width
        self.cart_table.setColumnWidth(2, 70)   # Quantity column
        self.cart_table.setColumnWidth(4, 100)  # Actions column
        
        right_layout.addWidget(self.cart_table)
        
        # Totals section
        totals_frame = QFrame()
        totals_frame.setStyleSheet(
            "background-color: #f5f5f5; border-radius: 8px; padding: 10px;"
        )
        totals_layout = QGridLayout(totals_frame)
        totals_layout.setSpacing(10)
        
        # All-day discount indicator (hidden by default)
        self.allday_discount_pct = None  # Stores all-day discount percentage
        self.allday_label = QLabel("")
        self.allday_label.setStyleSheet("color: #2E7D32; font-weight: bold; font-size: 11px;")
        self.allday_label.setAlignment(Qt.AlignCenter)
        self.allday_label.hide()
        totals_layout.addWidget(self.allday_label, 0, 0, 1, 2)
        
        # Subtotal
        totals_layout.addWidget(QLabel("Subtotal:"), 1, 0)
        self.subtotal_label = QLabel("Rs. 0.00")
        self.subtotal_label.setAlignment(Qt.AlignRight)
        self.subtotal_label.setStyleSheet("font-size: 13px;")
        totals_layout.addWidget(self.subtotal_label, 1, 1)
        
        # Discount button (opens dialog)
        self.discount_btn = QPushButton("🏷️ Add Discount")
        self.discount_btn.setMinimumHeight(38)
        self.discount_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-weight: bold;
                font-size: 12px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover { background-color: #F57C00; }
        """)
        self.discount_btn.clicked.connect(self._open_discount_dialog)
        totals_layout.addWidget(self.discount_btn, 2, 0)
        
        self.discount_label = QLabel("Rs. 0.00")
        self.discount_label.setAlignment(Qt.AlignRight)
        self.discount_label.setStyleSheet("font-size: 13px; color: #E65100; font-weight: bold;")
        totals_layout.addWidget(self.discount_label, 2, 1)
        
        # Hidden discount value storage
        self.current_discount = 0.0
        
        # Tax button (opens dialog)
        self.tax_btn = QPushButton("📋 Set Tax Rate")
        self.tax_btn.setMinimumHeight(38)
        self.tax_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                font-size: 12px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        self.tax_btn.clicked.connect(self._open_tax_dialog)
        totals_layout.addWidget(self.tax_btn, 3, 0)
        
        self.tax_label = QLabel("0% (Rs. 0.00)")
        self.tax_label.setAlignment(Qt.AlignRight)
        self.tax_label.setStyleSheet("font-size: 13px; color: #1565C0; font-weight: bold;")
        totals_layout.addWidget(self.tax_label, 3, 1)
        
        # Hidden tax rate storage
        self.current_tax_rate = 0.0
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #ccc;")
        totals_layout.addWidget(separator, 4, 0, 1, 2)
        
        # Total
        total_text_label = QLabel("TOTAL:")
        total_text_font = QFont()
        total_text_font.setPointSize(14)
        total_text_font.setBold(True)
        total_text_label.setFont(total_text_font)
        totals_layout.addWidget(total_text_label, 5, 0)
        
        self.total_label = QLabel("Rs. 0.00")
        self.total_label.setAlignment(Qt.AlignRight)
        total_label_font = QFont()
        total_label_font.setPointSize(18)
        total_label_font.setBold(True)
        self.total_label.setFont(total_label_font)
        self.total_label.setStyleSheet("color: #4CAF50;")
        totals_layout.addWidget(self.total_label, 5, 1)
        
        right_layout.addWidget(totals_frame)
        
        # Checkout button (large and prominent)
        self.checkout_btn = QPushButton("💳 CHECKOUT (F2)")
        self.checkout_btn.setMinimumHeight(60)
        checkout_font = QFont()
        checkout_font.setPointSize(14)
        checkout_font.setBold(True)
        self.checkout_btn.setFont(checkout_font)
        self.checkout_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #43A047;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        self.checkout_btn.setEnabled(False)
        right_layout.addWidget(self.checkout_btn)
        
        main_layout.addWidget(right_panel, stretch=3)
    
    def _connect_signals(self):
        """Connect UI signals to handler methods."""
        
        # Search
        self.search_input.textChanged.connect(self._on_search_changed)
        self.search_input.returnPressed.connect(self._on_search_enter)
        self.clear_search_btn.clicked.connect(self._clear_search)
        
        # Cart
        self.clear_cart_btn.clicked.connect(self._clear_cart)
        self.checkout_btn.clicked.connect(self._checkout)
    
    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        
        # F1: Focus search
        shortcut_search = QShortcut(QKeySequence("F1"), self)
        shortcut_search.activated.connect(self.search_input.setFocus)
        
        # F2: Checkout
        shortcut_checkout = QShortcut(QKeySequence("F2"), self)
        shortcut_checkout.activated.connect(self._checkout)
        
        # F3: Clear cart
        shortcut_clear = QShortcut(QKeySequence("F3"), self)
        shortcut_clear.activated.connect(self._clear_cart)
        
        # Escape: Cancel/clear
        shortcut_escape = QShortcut(QKeySequence("Escape"), self)
        shortcut_escape.activated.connect(self._on_escape)
    
    def refresh_data(self):
        """Refresh product and customer data."""
        
        try:
            # Load products
            self.products = ProductRepository.get_all()
            
            # Load inventory for stock info - use product_code as key
            inventory_items = InventoryRepository.get_all()
            self.inventory_map = {item.product_code: item for item in inventory_items}
            
            # Load customers (exclude C000 walk-in as we add it manually)
            customers = CustomerRepository.get_all(include_walkin=False)
            
            self.customer_combo.clear()
            self.customer_combo.addItem("Walk-in Customer", None)
            for customer in customers:
                self.customer_combo.addItem(
                    customer.customer_name,
                    customer.customer_id
                )
            
            # Show all products initially
            self._display_search_results(self.products)
        
        except Exception as e:
            QMessageBox.warning(
                self, "Warning",
                f"Failed to load data: {str(e)}",
                QMessageBox.Ok
            )
    
    def _on_search_changed(self, text: str):
        """Handle search text change with debounce."""
        
        search_text = text.strip().lower()
        
        if not search_text:
            self._display_search_results(self.products)
            return
        
        # Filter products
        filtered = [
            p for p in self.products
            if (p.product_name and search_text in p.product_name.lower()) or
               (p.barcode and search_text in p.barcode.lower()) or
               (p.sku and search_text in p.sku.lower())
        ]
        
        self._display_search_results(filtered)
    
    def _on_search_enter(self):
        """Handle Enter key in search field."""
        
        search_text = self.search_input.text().strip()
        
        if not search_text:
            return
        
        # Try to find exact barcode match
        for product in self.products:
            if product.barcode and product.barcode == search_text:
                self._add_to_cart(product)
                self.search_input.clear()
                return
        
        # If only one result, add it
        search_lower = search_text.lower()
        matches = [
            p for p in self.products
            if (p.product_name and search_lower in p.product_name.lower()) or
               (p.barcode and search_lower in p.barcode.lower()) or
               (p.sku and search_lower in p.sku.lower())
        ]
        
        if len(matches) == 1:
            self._add_to_cart(matches[0])
            self.search_input.clear()
    
    def _clear_search(self):
        """Clear the search input."""
        self.search_input.clear()
        self.search_input.setFocus()
    
    def _display_search_results(self, products: List[Product]):
        """
        Display product search results as tiles.
        
        Args:
            products: List of products to display
        """
        # Clear existing results
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not products:
            no_results = QLabel("No products found")
            no_results.setStyleSheet("color: #757575; font-size: 12pt;")
            no_results.setAlignment(Qt.AlignCenter)
            self.results_layout.addWidget(no_results, 0, 0)
            return
        
        # Display products in a grid (2 columns)
        columns = 2
        for i, product in enumerate(products[:30]):  # Limit to 30 results
            row = i // columns
            col = i % columns
            
            # Get stock info - use product_code as key
            inventory = self.inventory_map.get(product.product_code)
            stock = inventory.current_stock if inventory else 0
            
            tile = ProductSearchResultWidget(product, stock)
            tile.clicked.connect(lambda checked, p=product: self._add_to_cart(p))
            
            self.results_layout.addWidget(tile, row, col)
    
    def _add_to_cart(self, product: Product):
        """
        Add a product to the cart or increase quantity if already in cart.
        
        Args:
            product: Product to add
        """
        # Check stock - use product_code as key
        inventory = self.inventory_map.get(product.product_code)
        available_stock = inventory.current_stock if inventory else 0
        
        # Check if product already in cart - use product_code for matching
        for item in self.cart_items:
            if item.product_code == product.product_code:
                # Check if we can add more
                if item.quantity >= available_stock:
                    QMessageBox.warning(
                        self, "Out of Stock",
                        f"Cannot add more {product.product_name}.\n"
                        f"Only {available_stock} available.",
                        QMessageBox.Ok
                    )
                    return
                
                item.quantity += 1
                self._refresh_cart_display()
                return
        
        # Check if we have stock
        if available_stock <= 0:
            QMessageBox.warning(
                self, "Out of Stock",
                f"{product.product_name} is out of stock.",
                QMessageBox.Ok
            )
            return
        
        # Add new item to cart
        cart_item = CartItem(
            product_id=product.product_id,
            product_code=product.product_code,  # Store product_code for sale
            product_name=product.product_name,
            sku=product.sku or "",
            barcode=product.barcode or "",
            unit_price=float(product.price) if product.price else 0.0,
            quantity=1,
            available_stock=available_stock
        )
        
        print(f"[DEBUG] Adding to cart: {product.product_name}, price={product.price}, unit_price={cart_item.unit_price}")
        
        self.cart_items.append(cart_item)
        self._refresh_cart_display()
    
    def _refresh_cart_display(self):
        """Refresh the cart table display."""
        from PySide6.QtWidgets import QToolButton
        
        self.cart_table.setRowCount(len(self.cart_items))
        
        for row, item in enumerate(self.cart_items):
            # Product name
            name_item = QTableWidgetItem(item.product_name)
            self.cart_table.setItem(row, 0, name_item)
            
            # Unit price
            price_item = QTableWidgetItem(format_currency(item.unit_price))
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.cart_table.setItem(row, 1, price_item)
            
            # Quantity display only (no buttons here)
            qty_item = QTableWidgetItem(str(item.quantity))
            qty_item.setTextAlignment(Qt.AlignCenter)
            self.cart_table.setItem(row, 2, qty_item)
            
            # Total
            total_item = QTableWidgetItem(format_currency(item.total_price))
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.cart_table.setItem(row, 3, total_item)
            
            # Actions column with +, -, Delete buttons using QToolButton
            actions_widget = QWidget()
            actions_widget.setStyleSheet("background: transparent;")
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(1, 1, 1, 1)
            actions_layout.setSpacing(2)
            actions_layout.setAlignment(Qt.AlignCenter)
            
            # Minus button
            minus_btn = QToolButton()
            minus_btn.setText("−")
            minus_btn.setFixedSize(25, 28)
            minus_btn.setStyleSheet("""
                QToolButton {
                    background-color: #ffcdd2;
                    color: #b71c1c;
                    font-size: 18px;
                    font-weight: bold;
                    border: 1px solid #e57373;
                    border-radius: 2px;
                    padding: 0px;
                    margin: 0px;
                }
                QToolButton:hover { background-color: #ef9a9a; }
            """)
            minus_btn.clicked.connect(lambda _, r=row: self._decrease_quantity(r))
            actions_layout.addWidget(minus_btn)
            
            # Plus button
            plus_btn = QToolButton()
            plus_btn.setText("+")
            plus_btn.setFixedSize(25, 28)
            plus_btn.setStyleSheet("""
                QToolButton {
                    background-color: #c8e6c9;
                    color: #1b5e20;
                    font-size: 18px;
                    font-weight: bold;
                    border: 1px solid #81c784;
                    border-radius: 2px;
                    padding: 0px;
                    margin: 0px;
                }
                QToolButton:hover { background-color: #a5d6a7; }
            """)
            plus_btn.clicked.connect(lambda _, r=row: self._increase_quantity(r))
            actions_layout.addWidget(plus_btn)
            
            # Delete button
            del_btn = QToolButton()
            del_btn.setText("✕")
            del_btn.setFixedSize(25, 28)
            del_btn.setStyleSheet("""
                QToolButton {
                    background-color: #ffebee;
                    color: #d32f2f;
                    font-size: 16px;
                    font-weight: bold;
                    border: 1px solid #d32f2f;
                    border-radius: 2px;
                    padding: 0px;
                    margin: 0px;
                }
                QToolButton:hover { background-color: #ffcdd2; }
            """)
            del_btn.clicked.connect(lambda _, r=row: self._remove_from_cart(r))
            actions_layout.addWidget(del_btn)
            
            self.cart_table.setCellWidget(row, 4, actions_widget)
            self.cart_table.setRowHeight(row, 60)
        
        # Update totals
        self._update_totals()
    
    def _increase_quantity(self, row: int):
        """Increase quantity of item at given row."""
        if row < len(self.cart_items):
            item = self.cart_items[row]
            if item.quantity < item.available_stock:
                item.quantity += 1
                self._refresh_cart_display()
            else:
                QMessageBox.warning(
                    self, "Stock Limit",
                    f"Only {item.available_stock} available.",
                    QMessageBox.Ok
                )
    
    def _decrease_quantity(self, row: int):
        """Decrease quantity of item at given row."""
        if row < len(self.cart_items):
            item = self.cart_items[row]
            if item.quantity > 1:
                item.quantity -= 1
                self._refresh_cart_display()
            else:
                self._remove_from_cart(row)
    
    def _remove_from_cart(self, row: int):
        """Remove item at given row from cart."""
        if row < len(self.cart_items):
            del self.cart_items[row]
            self._refresh_cart_display()
    
    def _open_discount_dialog(self):
        """Open the discount selection dialog."""
        subtotal = sum(item.total_price for item in self.cart_items)
        allday_active = self.allday_discount_pct is not None
        dialog = DiscountSelectionDialog(subtotal, self.current_discount, allday_active, self)
        
        if dialog.exec() == QDialog.Accepted:
            # Check if user wants to remove all discounts
            if dialog.should_remove_all():
                self.current_discount = 0
                self.allday_discount_pct = None
                self.allday_label.hide()
            else:
                self.current_discount = dialog.get_discount()
                
                # Check for all-day discount
                allday_pct = dialog.get_allday_percentage()
                if allday_pct is not None:
                    if allday_pct == 0:
                        # Remove all-day discount
                        self.allday_discount_pct = None
                        self.allday_label.hide()
                    else:
                        self.allday_discount_pct = allday_pct
                        self.allday_label.setText(f"🏷️ All-Day Discount Active: {allday_pct}% off all sales!")
                        self.allday_label.show()
            
            self._update_totals()
    
    def _open_tax_dialog(self):
        """Open the tax rate selection dialog."""
        dialog = TaxSelectionDialog(self.current_tax_rate, self)
        
        if dialog.exec() == QDialog.Accepted:
            self.current_tax_rate = dialog.get_rate()
            self._update_totals()
    
    def _update_totals(self):
        """Update the totals display with adjustable tax and discount."""
        
        subtotal = sum(item.total_price for item in self.cart_items)
        
        # Apply all-day discount if active
        if self.allday_discount_pct is not None and self.current_discount == 0:
            self.current_discount = subtotal * self.allday_discount_pct / 100
        
        # Get discount value
        discount = self.current_discount
        
        # Get tax rate (as percentage)
        tax_rate = self.current_tax_rate / 100.0
        
        # Calculate: apply discount first, then tax
        after_discount = subtotal - discount
        if after_discount < 0:
            after_discount = 0
        
        tax = after_discount * tax_rate
        total = after_discount + tax
        
        # Update labels
        self.subtotal_label.setText(format_currency(subtotal))
        self.discount_label.setText(f"-{format_currency(discount)}" if discount > 0 else "Rs. 0.00")
        self.tax_label.setText(f"{self.current_tax_rate}% ({format_currency(tax)})")
        self.total_label.setText(format_currency(total))
        
        # Update button text to show current values
        if discount > 0:
            self.discount_btn.setText(f"🏷️ Discount: -{format_currency(discount)}")
            self.discount_btn.setStyleSheet("""
                QPushButton {
                    background-color: #E65100;
                    color: white;
                    font-weight: bold;
                    font-size: 11px;
                    border-radius: 5px;
                    border: none;
                }
                QPushButton:hover { background-color: #BF360C; }
            """)
        else:
            self.discount_btn.setText("🏷️ Add Discount")
            self.discount_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    font-weight: bold;
                    font-size: 12px;
                    border-radius: 5px;
                    border: none;
                }
                QPushButton:hover { background-color: #F57C00; }
            """)
        
        if self.current_tax_rate > 0:
            self.tax_btn.setText(f"📋 Tax: {self.current_tax_rate}%")
        else:
            self.tax_btn.setText("📋 Set Tax Rate")
        
        # Enable/disable checkout button
        cart_has_items = len(self.cart_items) > 0
        self.checkout_btn.setEnabled(cart_has_items)
        print(f"[DEBUG] _update_totals: cart_items={len(self.cart_items)}, checkout enabled={cart_has_items}")
    
    def _clear_cart(self):
        """Clear all items from the cart."""
        
        if not self.cart_items:
            return
        
        reply = QMessageBox.question(
            self, "Clear Cart",
            "Are you sure you want to clear all items from the cart?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.cart_items.clear()
            self._refresh_cart_display()
    
    def _on_escape(self):
        """Handle Escape key press."""
        if self.search_input.text():
            self._clear_search()
        elif self.cart_items:
            self._clear_cart()
    
    def _checkout(self):
        """Process the checkout."""
        print(f"[DEBUG] _checkout called, cart_items count: {len(self.cart_items)}")
        print(f"[DEBUG] checkout_btn enabled: {self.checkout_btn.isEnabled()}")
        
        if not self.cart_items:
            QMessageBox.warning(
                self, "Empty Cart",
                "Please add items to the cart before checkout.",
                QMessageBox.Ok
            )
            return
        
        # Step 1: Get customer information
        customer_dialog = CustomerInfoDialog(self)
        if customer_dialog.exec() != QDialog.Accepted:
            return  # User cancelled
        
        customer_info = customer_dialog.get_customer_info()
        customer_id = customer_info['customer_id']
        customer_name = customer_info['customer_name']
        
        # Calculate total using adjustable values
        subtotal = sum(item.total_price for item in self.cart_items)
        discount = self.current_discount
        tax_rate = self.current_tax_rate / 100.0
        
        after_discount = max(0, subtotal - discount)
        tax = after_discount * tax_rate
        total = after_discount + tax
        
        # Step 2: Show checkout dialog with cart items
        dialog = CheckoutDialog(total, customer_name, self.cart_items, self)
        
        if dialog.exec() == QDialog.Accepted:
            payment_info = dialog.get_payment_info()
            
            try:
                # Generate invoice number
                invoice_no = SaleRepository.get_next_id()
                
                # Prepare sale details - use product_code stored in cart item
                sale_details = [
                    {
                        "Product_Code": item.product_code,
                        "Quantity": item.quantity,
                        "Unit_Price": item.unit_price
                    }
                    for item in self.cart_items
                ]
                
                # Get employee ID
                employee_id = self.current_user.employee_id if self.current_user else 'EMP001'
                
                # Use 'C000' for walk-in customers (when customer_id is None)
                actual_customer_id = customer_id if customer_id else 'C000'
                
                # Use the discount from the POS input
                sale_discount = discount
                
                # Create sale using stored procedure
                result = SaleRepository.create_sale(
                    invoice_no=invoice_no,
                    customer_id=actual_customer_id,
                    employee_id=employee_id,
                    discount=sale_discount,
                    details=sale_details
                )
                
                if result.success:
                    # Get employee name for receipt
                    employee_name = self.current_user.employee_name if self.current_user else "Staff"
                    
                    # Store cart items for receipt before clearing
                    receipt_items = list(self.cart_items)
                    
                    # Clear cart and reset current discount (but keep all-day discount)
                    self.cart_items.clear()
                    self.current_discount = 0  # Reset discount for next sale
                    self._refresh_cart_display()
                    self.refresh_data()
                    
                    # Show receipt dialog
                    receipt_dialog = ReceiptDialog(
                        invoice_no=result.created_key,
                        customer_name=customer_name,
                        employee_name=employee_name,
                        cart_items=receipt_items,
                        subtotal=subtotal,
                        tax=tax,
                        total=total,
                        payment_method=payment_info['method'],
                        amount_received=payment_info['amount_received'],
                        change=payment_info['change'],
                        parent=self
                    )
                    receipt_dialog.exec()
                    
                    # Emit signal
                    self.sale_completed.emit(result.created_key)
                else:
                    QMessageBox.warning(
                        self, "Error",
                        f"Failed to create sale.\n\n{result.error_message}",
                        QMessageBox.Ok
                    )
            
            except Exception as e:
                QMessageBox.critical(
                    self, "Error",
                    f"Failed to process sale: {str(e)}",
                    QMessageBox.Ok
                )


# =============================================================================
# MODULE TEST
# =============================================================================

if __name__ == "__main__":
    """Test the POS view when running this module directly."""
    
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
    
    # Create mock employee
    mock_employee = Employee(
        employee_id=1,
        employee_name="Test Cashier",
        username="cashier",
        password_hash="",
        role="Employee",
        phone_number="555-0101",
        email="cashier@store.com"
    )
    
    # Create and show view
    view = SalePOSView(current_user=mock_employee)
    
    def on_sale_completed(sale_id):
        print(f"Sale completed: #{sale_id}")
    
    view.sale_completed.connect(on_sale_completed)
    view.show()
    
    # Run application
    sys.exit(app.exec())
