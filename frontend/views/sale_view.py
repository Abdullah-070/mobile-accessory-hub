"""
=============================================================================
Sale View
=============================================================================
Displays all sales with filtering, daily/monthly totals, and details.

Features:
    - List all sales with customer, date, amount
    - Filter by date range (day/month/custom)
    - Show daily/monthly sales totals
    - View sale details
    - Track revenue and employee performance

=============================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QFrame, QHeaderView, QMessageBox,
    QDateEdit, QGroupBox, QGridLayout, QDialog, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont, QColor

from decimal import Decimal
from datetime import date, datetime, timedelta
from typing import List, Optional

from repositories.sale_repository import SaleRepository, Sale
from repositories.employee_repository import EmployeeRepository
from utils import format_currency


class SaleDetailDialog(QDialog):
    """Dialog to show sale/invoice details."""
    
    def __init__(self, sale: Sale, parent=None):
        super().__init__(parent)
        self.sale = sale
        self.setWindowTitle(f"Sale Details - {sale.invoice_no}")
        self.setMinimumSize(700, 600)
        self.resize(650, 550)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header info
        header_group = QGroupBox("Invoice Information")
        header_layout = QGridLayout(header_group)
        
        header_layout.addWidget(QLabel("Invoice No:"), 0, 0)
        invoice_label = QLabel(f"<b>{self.sale.invoice_no}</b>")
        invoice_label.setStyleSheet("color: #2196F3; font-size: 14pt;")
        header_layout.addWidget(invoice_label, 0, 1)
        
        header_layout.addWidget(QLabel("Customer:"), 0, 2)
        header_layout.addWidget(QLabel(f"<b>{self.sale.customer_name or self.sale.customer_id}</b>"), 0, 3)
        
        header_layout.addWidget(QLabel("Date:"), 1, 0)
        header_layout.addWidget(QLabel(f"<b>{self.sale.sale_date}</b>"), 1, 1)
        
        header_layout.addWidget(QLabel("Time:"), 1, 2)
        header_layout.addWidget(QLabel(f"<b>{self.sale.sale_time}</b>"), 1, 3)
        
        header_layout.addWidget(QLabel("Employee:"), 2, 0)
        header_layout.addWidget(QLabel(f"<b>{self.sale.employee_name or self.sale.employee_id}</b>"), 2, 1)
        
        layout.addWidget(header_group)
        
        # Items table
        items_group = QGroupBox("Items Sold")
        items_layout = QVBoxLayout(items_group)
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels([
            "Product Code", "Product Name", "Quantity", "Unit Price", "Line Total"
        ])
        # Set maximum height to enable scrolling for many items
        self.items_table.setMaximumHeight(300)
        self.items_table.setMinimumHeight(150)
        
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.items_table.setAlternatingRowColors(True)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.items_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.items_table.setFocusPolicy(Qt.NoFocus)
        self.items_table.verticalHeader().setVisible(False)
        
        # Load details
        if self.sale.details:
            self.items_table.setRowCount(len(self.sale.details))
            for row, detail in enumerate(self.sale.details):
                self.items_table.setItem(row, 0, QTableWidgetItem(detail.product_code))
                self.items_table.setItem(row, 1, QTableWidgetItem(detail.product_name or detail.product_code))
                
                qty_item = QTableWidgetItem(str(detail.quantity))
                qty_item.setTextAlignment(Qt.AlignCenter)
                self.items_table.setItem(row, 2, qty_item)
                
                price_item = QTableWidgetItem(format_currency(detail.unit_price))
                price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.items_table.setItem(row, 3, price_item)
                
                total_item = QTableWidgetItem(format_currency(detail.line_total))
                total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.items_table.setItem(row, 4, total_item)
        
        items_layout.addWidget(self.items_table)
        layout.addWidget(items_group)
        
        # Totals
        totals_group = QGroupBox("Payment Summary")
        totals_layout = QGridLayout(totals_group)
        
        totals_layout.addWidget(QLabel("Subtotal:"), 0, 0)
        subtotal_label = QLabel(format_currency(self.sale.total_amount))
        subtotal_label.setAlignment(Qt.AlignRight)
        totals_layout.addWidget(subtotal_label, 0, 1)
        
        totals_layout.addWidget(QLabel("Discount:"), 1, 0)
        discount_label = QLabel(f"-{format_currency(self.sale.discount)}")
        discount_label.setAlignment(Qt.AlignRight)
        discount_label.setStyleSheet("color: #f44336;")
        totals_layout.addWidget(discount_label, 1, 1)
        
        totals_layout.addWidget(QLabel("Net Total:"), 2, 0)
        net_label = QLabel(format_currency(self.sale.net_amount))
        net_label.setAlignment(Qt.AlignRight)
        net_font = QFont()
        net_font.setPointSize(16)
        net_font.setBold(True)
        net_label.setFont(net_font)
        net_label.setStyleSheet("color: #4CAF50;")
        totals_layout.addWidget(net_label, 2, 1)
        
        layout.addWidget(totals_group)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setMinimumHeight(40)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class SaleView(QWidget):
    """
    Widget displaying sales history with filtering and details.
    
    Signals:
        navigate_back: Emitted when user wants to go back
    """
    
    navigate_back = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
        self.refresh_data()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("📊 Sales Report")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Back button
        self.back_btn = QPushButton("← Back")
        self.back_btn.setProperty("class", "secondary")
        self.back_btn.clicked.connect(self.navigate_back.emit)
        header_layout.addWidget(self.back_btn)
        
        layout.addLayout(header_layout)
        
        # Filter section
        filter_frame = QFrame()
        filter_frame.setProperty("class", "card")
        filter_layout = QHBoxLayout(filter_frame)
        
        # Date range filter
        filter_layout.addWidget(QLabel("Period:"))
        
        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "Today",
            "Last 7 Days",
            "This Month",
            "Last Month",
            "Custom Range"
        ])
        self.period_combo.setMinimumWidth(180)
        filter_layout.addWidget(self.period_combo)
        
        # Custom date range
        filter_layout.addWidget(QLabel("From:"))
        self.from_date = QDateEdit()
        self.from_date.setDate(QDate.currentDate().addDays(-30))
        self.from_date.setCalendarPopup(False)
        self.from_date.setMinimumWidth(110)
        self.from_date.setMinimumHeight(32)
        self.from_date.setDisplayFormat("dd/MM/yyyy")
        filter_layout.addWidget(self.from_date)
        
        # Calendar button for from date
        self.from_cal_btn = QPushButton("📅")
        self.from_cal_btn.setFixedSize(36, 32)
        self.from_cal_btn.setCursor(Qt.PointingHandCursor)
        self.from_cal_btn.setToolTip("Open Calendar")
        self.from_cal_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        self.from_cal_btn.clicked.connect(lambda: self._show_calendar(self.from_date))
        filter_layout.addWidget(self.from_cal_btn)
        
        filter_layout.addWidget(QLabel("To:"))
        self.to_date = QDateEdit()
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setCalendarPopup(False)
        self.to_date.setMinimumWidth(110)
        self.to_date.setMinimumHeight(32)
        self.to_date.setDisplayFormat("dd/MM/yyyy")
        filter_layout.addWidget(self.to_date)
        
        # Calendar button for to date
        self.to_cal_btn = QPushButton("📅")
        self.to_cal_btn.setFixedSize(36, 32)
        self.to_cal_btn.setCursor(Qt.PointingHandCursor)
        self.to_cal_btn.setToolTip("Open Calendar")
        self.to_cal_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        self.to_cal_btn.clicked.connect(lambda: self._show_calendar(self.to_date))
        filter_layout.addWidget(self.to_cal_btn)
        
        # Employee filter
        filter_layout.addWidget(QLabel("Employee:"))
        self.employee_combo = QComboBox()
        self.employee_combo.setMinimumWidth(150)
        self.employee_combo.addItem("All Employees", None)
        self._load_employees()
        filter_layout.addWidget(self.employee_combo)
        
        # Apply filter button
        self.filter_btn = QPushButton("🔍 Apply Filter")
        self.filter_btn.setProperty("class", "primary")
        filter_layout.addWidget(self.filter_btn)
        
        filter_layout.addStretch()
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh")
        filter_layout.addWidget(self.refresh_btn)
        
        layout.addWidget(filter_frame)
        
        # Summary cards
        summary_frame = QFrame()
        summary_layout = QHBoxLayout(summary_frame)
        summary_layout.setSpacing(15)
        
        # Total Sales card
        self.sales_count_card = self._create_summary_card(
            "📦 Total Sales", "0", "#2196F3"
        )
        summary_layout.addWidget(self.sales_count_card)
        
        # Total Revenue card
        self.revenue_card = self._create_summary_card(
            "💰 Total Revenue", "Rs. 0.00", "#4CAF50"
        )
        summary_layout.addWidget(self.revenue_card)
        
        # Total Discount card
        self.discount_card = self._create_summary_card(
            "🏷️ Total Discounts", "Rs. 0.00", "#FF9800"
        )
        summary_layout.addWidget(self.discount_card)
        
        # Net Revenue card
        self.net_card = self._create_summary_card(
            "💵 Net Revenue", "Rs. 0.00", "#9C27B0"
        )
        summary_layout.addWidget(self.net_card)
        
        layout.addWidget(summary_frame)
        
        # Sales table
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(7)
        self.sales_table.setHorizontalHeaderLabels([
            "Invoice No", "Date", "Time", "Customer", "Employee", "Amount", "Actions"
        ])
        
        header = self.sales_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        self.sales_table.setColumnWidth(6, 120)  # Wider for View button
        
        self.sales_table.setAlternatingRowColors(True)
        self.sales_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.sales_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.sales_table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.sales_table)
    
    def _create_summary_card(self, title: str, value: str, color: str) -> QFrame:
        """Create a summary card widget."""
        card = QFrame()
        card.setProperty("class", "card")
        card.setStyleSheet(f"""
            QFrame[class="card"] {{
                border-left: 4px solid {color};
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #666; font-size: 11pt;")
        card_layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setObjectName("value_label")
        value_font = QFont()
        value_font.setPointSize(16)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {color};")
        card_layout.addWidget(value_label)
        
        return card
    
    def _connect_signals(self):
        """Connect widget signals."""
        self.period_combo.currentIndexChanged.connect(self._on_period_changed)
        self.filter_btn.clicked.connect(self._apply_filter)
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.sales_table.doubleClicked.connect(self._on_row_double_click)
    
    def _on_period_changed(self, index: int):
        """Handle period combo box change."""
        # Auto-apply for non-custom selections
        if index != 4:  # Not Custom Range
            self._apply_filter()
    
    def _show_calendar(self, date_edit: QDateEdit):
        """Show calendar popup for the given date edit widget."""
        from PySide6.QtWidgets import QCalendarWidget
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Date")
        dialog.setMinimumSize(400, 350)
        
        layout = QVBoxLayout(dialog)
        
        calendar = QCalendarWidget()
        calendar.setSelectedDate(date_edit.date())
        calendar.setGridVisible(True)
        calendar.setMinimumSize(380, 280)
        # Hide week numbers
        calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        layout.addWidget(calendar)
        
        btn_layout = QHBoxLayout()
        
        today_btn = QPushButton("Today")
        today_btn.setMinimumHeight(35)
        today_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; border: none; border-radius: 5px; font-weight: bold; padding: 8px 20px; } QPushButton:hover { background-color: #F57C00; }")
        today_btn.clicked.connect(lambda: calendar.setSelectedDate(QDate.currentDate()))
        btn_layout.addWidget(today_btn)
        
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(35)
        cancel_btn.setStyleSheet("QPushButton { background-color: #757575; color: white; border: none; border-radius: 5px; padding: 8px 20px; } QPushButton:hover { background-color: #616161; }")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("Select")
        ok_btn.setMinimumHeight(35)
        ok_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border: none; border-radius: 5px; font-weight: bold; padding: 8px 20px; } QPushButton:hover { background-color: #388E3C; }")
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        calendar.activated.connect(dialog.accept)
        
        if dialog.exec() == QDialog.Accepted:
            date_edit.setDate(calendar.selectedDate())
            self.period_combo.setCurrentIndex(4)  # Switch to Custom Range

    def _get_date_range(self) -> tuple:
        """Get the date range based on selected period."""
        today = date.today()
        period = self.period_combo.currentIndex()
        
        if period == 0:  # Today
            return today, today
        elif period == 1:  # Last 7 Days
            return today - timedelta(days=7), today
        elif period == 2:  # This Month
            first_of_month = today.replace(day=1)
            return first_of_month, today
        elif period == 3:  # Last Month
            first_of_this_month = today.replace(day=1)
            last_of_prev_month = first_of_this_month - timedelta(days=1)
            first_of_prev_month = last_of_prev_month.replace(day=1)
            return first_of_prev_month, last_of_prev_month
        else:  # Custom
            return self.from_date.date().toPython(), self.to_date.date().toPython()
    
    def _apply_filter(self):
        """Apply the selected filter and refresh data."""
        self.refresh_data()
    
    def _load_employees(self):
        """Load employees into the dropdown."""
        try:
            employees = EmployeeRepository.get_for_dropdown()
            for emp in employees:
                self.employee_combo.addItem(emp['name'], emp['id'])
        except Exception as e:
            print(f"Failed to load employees: {e}")
    
    def refresh_data(self):
        """Load and display sales data."""
        try:
            start_date, end_date = self._get_date_range()
            
            # Get sales for the date range
            sales = SaleRepository.get_by_date_range(start_date, end_date)
            
            # Filter by employee if selected
            selected_employee_id = self.employee_combo.currentData()
            if selected_employee_id:
                sales = [s for s in sales if s.employee_id == selected_employee_id]
            
            # Update table
            self._populate_table(sales)
            
            # Update summary cards
            self._update_summary(sales)
            
        except Exception as e:
            QMessageBox.warning(
                self, "Error",
                f"Failed to load sales data: {str(e)}",
                QMessageBox.Ok
            )
    
    def _populate_table(self, sales: List[Sale]):
        """Populate the sales table."""
        self.sales_table.setRowCount(len(sales))
        
        for row, sale in enumerate(sales):
            # Invoice No
            invoice_item = QTableWidgetItem(sale.invoice_no)
            invoice_item.setForeground(QColor("#2196F3"))
            font = invoice_item.font()
            font.setBold(True)
            invoice_item.setFont(font)
            self.sales_table.setItem(row, 0, invoice_item)
            
            # Date
            self.sales_table.setItem(row, 1, QTableWidgetItem(str(sale.sale_date)))
            
            # Time
            time_str = str(sale.sale_time)[:5] if sale.sale_time else ""
            self.sales_table.setItem(row, 2, QTableWidgetItem(time_str))
            
            # Customer
            customer = sale.customer_name or sale.customer_id
            if sale.customer_id == 'C000':
                customer = "Walk-in Customer"
            self.sales_table.setItem(row, 3, QTableWidgetItem(customer))
            
            # Employee
            self.sales_table.setItem(row, 4, QTableWidgetItem(sale.employee_name or sale.employee_id))
            
            # Amount
            amount_item = QTableWidgetItem(format_currency(sale.net_amount))
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            amount_item.setForeground(QColor("#4CAF50"))
            self.sales_table.setItem(row, 5, amount_item)
            
            # Actions - View Details button
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            
            view_btn = QPushButton("👁️ View")
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover { background-color: #1976D2; }
            """)
            view_btn.setCursor(Qt.PointingHandCursor)
            view_btn.clicked.connect(lambda _, s=sale: self._show_sale_details(s))
            actions_layout.addWidget(view_btn)
            
            self.sales_table.setCellWidget(row, 6, actions_widget)
            self.sales_table.setRowHeight(row, 50)  # Taller rows for better visibility
    
    def _update_summary(self, sales: List[Sale]):
        """Update the summary cards."""
        total_sales = len(sales)
        total_revenue = sum(float(s.total_amount) for s in sales)
        total_discount = sum(float(s.discount) for s in sales)
        net_revenue = sum(float(s.net_amount) for s in sales)
        
        # Update card values
        self.sales_count_card.findChild(QLabel, "value_label").setText(str(total_sales))
        self.revenue_card.findChild(QLabel, "value_label").setText(f"Rs. {total_revenue:,.2f}")
        self.discount_card.findChild(QLabel, "value_label").setText(f"Rs. {total_discount:,.2f}")
        self.net_card.findChild(QLabel, "value_label").setText(f"Rs. {net_revenue:,.2f}")
    
    def _on_row_double_click(self, index):
        """Handle double-click on a row to show details."""
        row = index.row()
        if row >= 0:
            invoice_no = self.sales_table.item(row, 0).text()
            sale = SaleRepository.get_by_id(invoice_no)
            if sale:
                self._show_sale_details(sale)
    
    def _show_sale_details(self, sale: Sale):
        """Show the sale details dialog."""
        # Reload to get full details
        full_sale = SaleRepository.get_by_id(sale.invoice_no)
        if full_sale:
            dialog = SaleDetailDialog(full_sale, self)
            dialog.exec()
