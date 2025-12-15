"""
=============================================================================
Report View
=============================================================================
Displays comprehensive sales and profit reports with filtering options.

Features:
    - Summary cards for Revenue, Cost, and Profit
    - Date range filtering (Today, 7 Days, 30 Days, Custom)
    - Top selling products table
    - Sales by category breakdown
    - Revenue vs Cost analysis

=============================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QFrame, QHeaderView, QMessageBox,
    QDateEdit, QGroupBox, QGridLayout, QScrollArea, QSizePolicy, QDialog,
    QCalendarWidget
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont, QColor

from decimal import Decimal
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any

from repositories.sale_repository import SaleRepository


class SummaryCard(QFrame):
    """A card widget displaying a metric with title, value, and optional subtitle."""
    
    def __init__(self, title: str, value: str = "0", subtitle: str = "", 
                 color: str = "#2196F3", parent=None):
        super().__init__(parent)
        self.color = color
        self._setup_ui(title, value, subtitle)
    
    def _setup_ui(self, title: str, value: str, subtitle: str):
        self.setStyleSheet(f"""
            SummaryCard {{
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                border-left: 4px solid {self.color};
            }}
        """)
        self.setMinimumHeight(110)
        self.setMinimumWidth(220)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: #666; font-size: 11pt;")
        layout.addWidget(self.title_label)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"color: {self.color}; font-size: 18pt; font-weight: bold;")
        self.value_label.setMinimumWidth(180)
        layout.addWidget(self.value_label)
        
        # Subtitle
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setStyleSheet("color: #999; font-size: 9pt;")
        layout.addWidget(self.subtitle_label)
    
    def set_value(self, value: str):
        """Update the displayed value."""
        self.value_label.setText(value)
    
    def set_subtitle(self, subtitle: str):
        """Update the subtitle text."""
        self.subtitle_label.setText(subtitle)


class ReportView(QWidget):
    """Main view for displaying sales and profit reports."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
        self.refresh_data()
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Outer layout for scroll area
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area - vertical only
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea { background-color: #F5F5F5; }")
        
        # Content widget
        content = QWidget()
        content.setStyleSheet("background-color: #F5F5F5;")
        main_layout = QVBoxLayout(content)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("📊 Sales & Profit Reports")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #333;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setMinimumHeight(35)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #43A047; }
        """)
        refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Filter section
        filter_group = QGroupBox("Date Filter")
        filter_layout = QHBoxLayout(filter_group)
        
        filter_layout.addWidget(QLabel("Period:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Today", "Last 7 Days", "Last 30 Days", "This Month", "Custom"])
        self.period_combo.setMinimumWidth(150)
        filter_layout.addWidget(self.period_combo)
        
        filter_layout.addSpacing(20)
        
        # From date with calendar button
        filter_layout.addWidget(QLabel("From:"))
        
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setCalendarPopup(False)
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        self.start_date.setMinimumWidth(120)
        self.start_date.setFixedHeight(35)
        filter_layout.addWidget(self.start_date)
        
        # Calendar button for start date
        self.start_cal_btn = QPushButton("📅")
        self.start_cal_btn.setFixedSize(38, 35)
        self.start_cal_btn.setCursor(Qt.PointingHandCursor)
        self.start_cal_btn.setToolTip("Open Calendar")
        self.start_cal_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        self.start_cal_btn.clicked.connect(lambda: self._show_calendar(self.start_date))
        filter_layout.addWidget(self.start_cal_btn)
        
        filter_layout.addSpacing(10)
        
        # To date with calendar button
        filter_layout.addWidget(QLabel("To:"))
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(False)
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        self.end_date.setMinimumWidth(120)
        self.end_date.setFixedHeight(35)
        filter_layout.addWidget(self.end_date)
        
        # Calendar button for end date
        self.end_cal_btn = QPushButton("📅")
        self.end_cal_btn.setFixedSize(38, 35)
        self.end_cal_btn.setCursor(Qt.PointingHandCursor)
        self.end_cal_btn.setToolTip("Open Calendar")
        self.end_cal_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        self.end_cal_btn.clicked.connect(lambda: self._show_calendar(self.end_date))
        filter_layout.addWidget(self.end_cal_btn)
        
        filter_layout.addSpacing(15)
        
        self.apply_btn = QPushButton("🔍 Apply Filter")
        self.apply_btn.setMinimumHeight(35)
        self.apply_btn.setMinimumWidth(120)
        self.apply_btn.setCursor(Qt.PointingHandCursor)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        filter_layout.addWidget(self.apply_btn)
        
        filter_layout.addStretch()
        
        main_layout.addWidget(filter_group)
        
        # Summary cards row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        self.sales_card = SummaryCard("Total Sales", "0", "Number of transactions", "#2196F3")
        cards_layout.addWidget(self.sales_card)
        
        self.revenue_card = SummaryCard("Total Revenue", "Rs. 0", "Gross revenue from sales", "#4CAF50")
        cards_layout.addWidget(self.revenue_card)
        
        self.cost_card = SummaryCard("Total Cost", "Rs. 0", "Cost of goods sold", "#FF9800")
        cards_layout.addWidget(self.cost_card)
        
        self.profit_card = SummaryCard("Net Profit", "Rs. 0", "Revenue - Cost", "#9C27B0")
        cards_layout.addWidget(self.profit_card)
        
        self.units_card = SummaryCard("Units Sold", "0", "Total items sold", "#00BCD4")
        cards_layout.addWidget(self.units_card)
        
        main_layout.addLayout(cards_layout)
        
        # Tables section
        tables_layout = QHBoxLayout()
        tables_layout.setSpacing(15)
        
        # Top Selling Products table
        top_products_group = QGroupBox("🏆 Top Selling Products")
        top_products_layout = QVBoxLayout(top_products_group)
        
        self.top_products_table = QTableWidget()
        self.top_products_table.setColumnCount(4)
        self.top_products_table.setHorizontalHeaderLabels([
            "Product", "Brand", "Units Sold", "Revenue"
        ])
        self.top_products_table.setMinimumHeight(250)
        self.top_products_table.setAlternatingRowColors(True)
        self.top_products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.top_products_table.verticalHeader().setVisible(False)
        
        header = self.top_products_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        top_products_layout.addWidget(self.top_products_table)
        tables_layout.addWidget(top_products_group)
        
        # Sales by Category table
        category_group = QGroupBox("📂 Sales by Category")
        category_layout = QVBoxLayout(category_group)
        
        self.category_table = QTableWidget()
        self.category_table.setColumnCount(4)
        self.category_table.setHorizontalHeaderLabels([
            "Category", "Sales Count", "Units Sold", "Revenue"
        ])
        self.category_table.setMinimumHeight(250)
        self.category_table.setAlternatingRowColors(True)
        self.category_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.category_table.verticalHeader().setVisible(False)
        
        cat_header = self.category_table.horizontalHeader()
        cat_header.setSectionResizeMode(0, QHeaderView.Stretch)
        cat_header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        cat_header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        cat_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        category_layout.addWidget(self.category_table)
        tables_layout.addWidget(category_group)
        
        main_layout.addLayout(tables_layout)
        
        # Profit margin info
        margin_frame = QFrame()
        margin_frame.setStyleSheet("""
            QFrame {
                background-color: #E8F5E9;
                border: 1px solid #4CAF50;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        margin_layout = QHBoxLayout(margin_frame)
        
        self.margin_label = QLabel("📈 Profit Margin: Calculating...")
        self.margin_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #2E7D32;")
        margin_layout.addWidget(self.margin_label)
        
        margin_layout.addStretch()
        
        self.margin_info = QLabel("Profit Margin = (Revenue - Cost) / Revenue × 100")
        self.margin_info.setStyleSheet("color: #666; font-size: 10pt;")
        margin_layout.addWidget(self.margin_info)
        
        main_layout.addWidget(margin_frame)
        
        # Spacer
        main_layout.addStretch()
        
        # Set content widget to scroll area
        scroll.setWidget(content)
        outer_layout.addWidget(scroll)
    
    def _connect_signals(self):
        """Connect widget signals to handlers."""
        self.period_combo.currentIndexChanged.connect(self._on_period_changed)
        self.apply_btn.clicked.connect(self._apply_filter)
        # Also trigger refresh when dates change
        self.start_date.dateChanged.connect(self._on_date_changed)
        self.end_date.dateChanged.connect(self._on_date_changed)
    
    def _on_date_changed(self):
        """Handle date change - set period to Custom."""
        # When user manually changes dates, switch to Custom
        if self.period_combo.currentText() != "Custom":
            self.period_combo.blockSignals(True)
            self.period_combo.setCurrentText("Custom")
            self.period_combo.blockSignals(False)
    
    def _on_period_changed(self, index: int):
        """Handle period selection change - update date fields."""
        period = self.period_combo.currentText()
        today = QDate.currentDate()
        
        if period == "Today":
            self.start_date.setDate(today)
            self.end_date.setDate(today)
        elif period == "Last 7 Days":
            self.start_date.setDate(today.addDays(-7))
            self.end_date.setDate(today)
        elif period == "Last 30 Days":
            self.start_date.setDate(today.addDays(-30))
            self.end_date.setDate(today)
        elif period == "This Month":
            self.start_date.setDate(QDate(today.year(), today.month(), 1))
            self.end_date.setDate(today)
        # For Custom, keep the current dates
        
        # Auto-apply filter when period changes
        self._apply_filter()
    
    def _show_calendar(self, date_edit: QDateEdit):
        """Show calendar popup for the given date edit widget."""
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
            self.period_combo.setCurrentText("Custom")

    def _apply_filter(self):
        """Apply the current date filter and refresh data."""
        self.refresh_data()
    
    def _get_date_range(self) -> tuple:
        """Get the selected date range based on period selection."""
        period = self.period_combo.currentText()
        today = date.today()
        
        if period == "Today":
            return today, today
        elif period == "Last 7 Days":
            return today - timedelta(days=7), today
        elif period == "Last 30 Days":
            return today - timedelta(days=30), today
        elif period == "This Month":
            first_of_month = today.replace(day=1)
            return first_of_month, today
        else:  # Custom
            start = self.start_date.date().toPython()
            end = self.end_date.date().toPython()
            return start, end
    
    def refresh_data(self):
        """Refresh all report data from the database."""
        try:
            start_date, end_date = self._get_date_range()
            
            # Get sales report summary (includes profit calculation)
            summary = SaleRepository.get_sales_report(start_date, end_date)
            
            # Update summary cards
            self.sales_card.set_value(str(summary.get('total_sales', 0)))
            
            revenue = summary.get('total_revenue', 0)
            cost = summary.get('total_cost', 0)
            profit = summary.get('gross_profit', 0)
            units = summary.get('total_units_sold', 0)
            
            self.revenue_card.set_value(f"Rs. {revenue:,.2f}")
            self.cost_card.set_value(f"Rs. {cost:,.2f}")
            self.profit_card.set_value(f"Rs. {profit:,.2f}")
            self.units_card.set_value(str(units))
            
            # Calculate and display profit margin
            if revenue > 0:
                margin = (profit / revenue) * 100
                self.margin_label.setText(f"📈 Profit Margin: {margin:.1f}%")
                
                # Color-code the margin
                if margin >= 30:
                    self.margin_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #2E7D32;")
                elif margin >= 15:
                    self.margin_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #FF9800;")
                else:
                    self.margin_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #F44336;")
            else:
                self.margin_label.setText("📈 Profit Margin: N/A (No sales)")
            
            # Get top selling products
            top_products = SaleRepository.get_top_selling_products(10, start_date, end_date)
            self._populate_top_products(top_products)
            
            # Get sales by category
            category_sales = SaleRepository.get_sales_by_category(start_date, end_date)
            self._populate_category_sales(category_sales)
            
            # Update date range display in cards
            date_range_text = f"From {start_date} to {end_date}"
            self.sales_card.set_subtitle(date_range_text)
            
        except Exception as e:
            QMessageBox.warning(
                self, "Error",
                f"Failed to load report data:\n{str(e)}",
                QMessageBox.Ok
            )
    
    def _populate_top_products(self, products: List[Dict[str, Any]]):
        """Populate the top selling products table."""
        self.top_products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            # Product name
            name_item = QTableWidgetItem(product.get('product_name', 'Unknown'))
            self.top_products_table.setItem(row, 0, name_item)
            
            # Brand
            brand_item = QTableWidgetItem(product.get('brand', '-'))
            self.top_products_table.setItem(row, 1, brand_item)
            
            # Units sold
            units_item = QTableWidgetItem(str(product.get('total_quantity', 0)))
            units_item.setTextAlignment(Qt.AlignCenter)
            self.top_products_table.setItem(row, 2, units_item)
            
            # Revenue
            revenue = product.get('total_revenue', 0)
            revenue_item = QTableWidgetItem(f"Rs. {revenue:,.2f}")
            revenue_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.top_products_table.setItem(row, 3, revenue_item)
    
    def _populate_category_sales(self, categories: List[Dict[str, Any]]):
        """Populate the sales by category table."""
        self.category_table.setRowCount(len(categories))
        
        for row, category in enumerate(categories):
            # Category name
            name_item = QTableWidgetItem(category.get('cat_name', 'Unknown'))
            self.category_table.setItem(row, 0, name_item)
            
            # Sales count
            count_item = QTableWidgetItem(str(category.get('sale_count', 0)))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.category_table.setItem(row, 1, count_item)
            
            # Units sold
            units_item = QTableWidgetItem(str(category.get('total_quantity', 0)))
            units_item.setTextAlignment(Qt.AlignCenter)
            self.category_table.setItem(row, 2, units_item)
            
            # Revenue
            revenue = category.get('total_revenue', 0)
            revenue_item = QTableWidgetItem(f"Rs. {revenue:,.2f}")
            revenue_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.category_table.setItem(row, 3, revenue_item)


# =============================================================================
# MODULE TEST
# =============================================================================

if __name__ == "__main__":
    """Test the report view when running this module directly."""
    
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
    view = ReportView()
    view.setWindowTitle("Reports Test")
    view.resize(1200, 800)
    view.show()
    
    sys.exit(app.exec())
