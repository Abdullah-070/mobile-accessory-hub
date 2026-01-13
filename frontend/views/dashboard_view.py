# COPILOT_MODIFIED: true  # 2025-12-09T15:15:00Z
"""
=============================================================================
Dashboard View
=============================================================================
This module provides the main dashboard screen after successful login.

Features:
    - Welcome message with user info
    - Quick action tiles for navigation
    - Recent sales summary
    - Low stock alerts
    - Sales statistics widgets
    - Role-based menu items (Admin vs Employee)

The dashboard serves as the central hub for:
    - Quick navigation to common tasks
    - At-a-glance business metrics
    - Alerts and notifications

Changes Applied:
- Employee role shows: POS, Inventory (view), Customers
- Admin role shows: All tiles except POS (Products, Suppliers, Employees, Reports, etc.)
- Uses error_reporter for centralized error handling

=============================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QTableWidget, QTableWidgetItem,
    QHeaderView, QSpacerItem, QSizePolicy, QGroupBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont
from decimal import Decimal

from repositories.employee_repository import Employee
from repositories.sale_repository import SaleRepository
from repositories.inventory_repository import InventoryRepository
from repositories.product_repository import ProductRepository
from utils import format_currency, format_date
from error_reporter import report_error


class DashboardTile(QPushButton):
    """
    A clickable tile button for the dashboard.
    
    Displays an emoji icon, title, and description.
    Used for quick navigation to different sections.
    """
    
    def __init__(self, icon: str, title: str, description: str, parent=None):
        """
        Initialize a dashboard tile.
        
        Args:
            icon: Emoji or icon character
            title: Tile title text
            description: Brief description text
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setProperty("class", "tile")
        self.setMinimumSize(180, 150)
        self.setCursor(Qt.PointingHandCursor)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 32pt;")
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: #757575; font-size: 9pt;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)


class StatCard(QFrame):
    """
    A card widget for displaying statistics.
    
    Shows a label and value with optional color styling.
    """
    
    def __init__(self, label: str, value: str, color: str = "#1976D2", parent=None):
        """
        Initialize a stat card.
        
        Args:
            label: Description label
            value: Value to display
            color: Color for the value text
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setProperty("class", "card")
        self.setMinimumHeight(100)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Value (large)
        self.value_label = QLabel(value)
        self.value_label.setAlignment(Qt.AlignCenter)
        value_font = QFont()
        value_font.setPointSize(24)
        value_font.setBold(True)
        self.value_label.setFont(value_font)
        self.value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(self.value_label)
        
        # Label (small)
        self.label_label = QLabel(label)
        self.label_label.setAlignment(Qt.AlignCenter)
        self.label_label.setStyleSheet("color: #757575; font-size: 10pt;")
        layout.addWidget(self.label_label)
    
    def set_value(self, value: str):
        """Update the displayed value."""
        self.value_label.setText(value)


class DashboardView(QWidget):
    """
    Main dashboard widget shown after login.
    
    Signals:
        navigate_to: Emitted when user clicks a navigation tile
        logout_requested: Emitted when user wants to logout
        
    The dashboard content adapts based on user role:
        - Admin: Full access to all tiles
        - Employee: Limited to sales and inventory
    """
    
    # Navigation signals
    navigate_to = Signal(str)  # Emits section name
    logout_requested = Signal()
    
    def __init__(self, parent=None):
        """
        Initialize the dashboard view.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Current logged-in user
        self.current_user: Employee = None
        
        # Stats
        self.todays_sales_value = 0
        self.low_stock_count = 0
        
        # Set up UI
        self._setup_ui()
        
        # Set up refresh timer (refresh every 5 minutes)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(300000)  # 5 minutes
    
    def _setup_ui(self):
        """Set up the user interface components."""
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # =====================================================================
        # HEADER SECTION
        # =====================================================================
        
        header_layout = QHBoxLayout()
        
        # Welcome message
        self.welcome_label = QLabel("Welcome!")
        welcome_font = QFont()
        welcome_font.setPointSize(18)
        welcome_font.setBold(True)
        self.welcome_label.setFont(welcome_font)
        header_layout.addWidget(self.welcome_label)
        
        header_layout.addStretch()
        
        # Refresh button
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.setProperty("class", "secondary")
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        self.refresh_button.clicked.connect(self.refresh_data)
        self.refresh_button.setToolTip("Refresh dashboard data")
        header_layout.addWidget(self.refresh_button)
        
        # User info and logout
        self.user_info_label = QLabel()
        self.user_info_label.setStyleSheet("color: #757575;")
        header_layout.addWidget(self.user_info_label)
        
        self.logout_button = QPushButton("Logout")
        self.logout_button.setProperty("class", "secondary")
        self.logout_button.setCursor(Qt.PointingHandCursor)
        self.logout_button.clicked.connect(self.logout_requested.emit)
        header_layout.addWidget(self.logout_button)
        
        main_layout.addLayout(header_layout)
        
        # =====================================================================
        # SCROLL AREA (for responsive content)
        # =====================================================================
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(25)
        
        # =====================================================================
        # STATISTICS ROW
        # =====================================================================
        
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.today_sales_card = StatCard("Today's Sales", "Rs. 0.00", "#4CAF50")
        stats_layout.addWidget(self.today_sales_card)
        
        self.products_card = StatCard("Total Products", "0", "#1976D2")
        stats_layout.addWidget(self.products_card)
        
        self.low_stock_card = StatCard("Low Stock Items", "0", "#FF5722")
        stats_layout.addWidget(self.low_stock_card)
        
        self.customers_card = StatCard("Total Customers", "0", "#9C27B0")
        stats_layout.addWidget(self.customers_card)
        
        scroll_layout.addLayout(stats_layout)
        
        # =====================================================================
        # QUICK ACTIONS SECTION
        # =====================================================================
        
        actions_label = QLabel("Quick Actions")
        actions_font = QFont()
        actions_font.setPointSize(14)
        actions_font.setBold(True)
        actions_label.setFont(actions_font)
        scroll_layout.addWidget(actions_label)
        
        # Tiles grid
        tiles_layout = QGridLayout()
        tiles_layout.setSpacing(15)
        
        # POS tile (Employee only)
        self.pos_tile = DashboardTile("💳", "POS", "Point of Sale")
        self.pos_tile.clicked.connect(lambda: self.navigate_to.emit("pos"))
        tiles_layout.addWidget(self.pos_tile, 0, 0)
        
        # Row 1 - Core features (4 tiles)
        self.products_tile = DashboardTile("📦", "Products", "Manage products")
        self.products_tile.clicked.connect(lambda: self.navigate_to.emit("products"))
        tiles_layout.addWidget(self.products_tile, 0, 0)
        
        self.inventory_tile = DashboardTile("📊", "Inventory", "Check stock levels")
        self.inventory_tile.clicked.connect(lambda: self.navigate_to.emit("inventory"))
        tiles_layout.addWidget(self.inventory_tile, 0, 1)
        
        self.customers_tile = DashboardTile("👥", "Customers", "Customer list")
        self.customers_tile.clicked.connect(lambda: self.navigate_to.emit("customers"))
        tiles_layout.addWidget(self.customers_tile, 0, 2)
        
        self.purchases_tile = DashboardTile("📥", "Purchases", "Record purchases")
        self.purchases_tile.clicked.connect(lambda: self.navigate_to.emit("purchases"))
        tiles_layout.addWidget(self.purchases_tile, 0, 3)
        
        # Row 2 - Admin features (4 tiles)
        self.sales_tile = DashboardTile("💰", "Sales", "View sales history")
        self.sales_tile.clicked.connect(lambda: self.navigate_to.emit("sales"))
        tiles_layout.addWidget(self.sales_tile, 1, 0)
        
        self.suppliers_tile = DashboardTile("🏭", "Suppliers", "Manage suppliers")
        self.suppliers_tile.clicked.connect(lambda: self.navigate_to.emit("suppliers"))
        tiles_layout.addWidget(self.suppliers_tile, 1, 1)
        
        self.reports_tile = DashboardTile("📈", "Reports", "View reports")
        self.reports_tile.clicked.connect(lambda: self.navigate_to.emit("reports"))
        tiles_layout.addWidget(self.reports_tile, 1, 2)
        
        self.employees_tile = DashboardTile("👤", "Employees", "Manage staff")
        self.employees_tile.clicked.connect(lambda: self.navigate_to.emit("employees"))
        tiles_layout.addWidget(self.employees_tile, 1, 3)
        
        scroll_layout.addLayout(tiles_layout)
        
        # =====================================================================
        # BOTTOM SECTION - Two columns
        # =====================================================================
        
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        
        # ---------------------------------------------------------------------
        # Recent Sales
        # ---------------------------------------------------------------------
        
        recent_sales_group = QGroupBox("Recent Sales")
        recent_sales_layout = QVBoxLayout(recent_sales_group)
        
        self.recent_sales_table = QTableWidget()
        self.recent_sales_table.setColumnCount(4)
        self.recent_sales_table.setHorizontalHeaderLabels(
            ["Date", "Customer", "Items", "Total"]
        )
        self.recent_sales_table.horizontalHeader().setStretchLastSection(True)
        self.recent_sales_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.recent_sales_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.recent_sales_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.recent_sales_table.setMaximumHeight(250)
        # Hide vertical header (row numbers) to show more content
        self.recent_sales_table.verticalHeader().setVisible(False)
        recent_sales_layout.addWidget(self.recent_sales_table)
        
        view_all_sales_btn = QPushButton("View All Sales")
        view_all_sales_btn.setProperty("class", "secondary")
        view_all_sales_btn.clicked.connect(lambda: self.navigate_to.emit("sales"))
        recent_sales_layout.addWidget(view_all_sales_btn, alignment=Qt.AlignRight)
        
        bottom_layout.addWidget(recent_sales_group, stretch=1)
        
        # ---------------------------------------------------------------------
        # Low Stock Alerts
        # ---------------------------------------------------------------------
        
        low_stock_group = QGroupBox("Low Stock Alerts")
        low_stock_layout = QVBoxLayout(low_stock_group)
        
        self.low_stock_table = QTableWidget()
        self.low_stock_table.setColumnCount(3)
        self.low_stock_table.setHorizontalHeaderLabels(
            ["Product", "Current", "Reorder"]
        )
        self.low_stock_table.horizontalHeader().setStretchLastSection(True)
        self.low_stock_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.low_stock_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.low_stock_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.low_stock_table.setMaximumHeight(250)
        low_stock_layout.addWidget(self.low_stock_table)
        
        view_inventory_btn = QPushButton("View Inventory")
        view_inventory_btn.setProperty("class", "secondary")
        view_inventory_btn.clicked.connect(lambda: self.navigate_to.emit("inventory"))
        low_stock_layout.addWidget(view_inventory_btn, alignment=Qt.AlignRight)
        
        bottom_layout.addWidget(low_stock_group, stretch=1)
        
        scroll_layout.addLayout(bottom_layout)
        
        # Add stretch at the bottom
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
    
    def set_user(self, employee: Employee):
        """
        Set the current logged-in user and update the UI accordingly.
        
        Args:
            employee: The logged-in Employee object
        """
        self.current_user = employee
        
        # Update welcome message
        self.welcome_label.setText(f"Welcome, {employee.employee_name}!")
        
        # Update user info
        self.user_info_label.setText(f"Role: {employee.role}")
        
        # Adjust UI based on role
        self._apply_role_restrictions()
        
        # Refresh data
        self.refresh_data()
    
    def _apply_role_restrictions(self):
        """
        Apply UI restrictions based on user role.
        
        Employee role: POS, Inventory (view), Customers
        Admin role: Products, Purchases, Suppliers, Employees, Reports, Inventory (full access), Customers
        
        Note: POS is only visible to employees (not admins).
        """
        
        if self.current_user is None:
            return
        
        is_admin = self.current_user.role.lower() == "admin"
        
        # POS is for employees only
        self.pos_tile.setVisible(not is_admin)
        
        # Both roles can access:
        self.inventory_tile.setVisible(True)
        self.customers_tile.setVisible(True)
        
        # Admin-only tiles: Products CRUD, Purchases, Suppliers, Employees, Reports, Sales
        self.products_tile.setVisible(is_admin)
        self.purchases_tile.setVisible(is_admin)
        self.sales_tile.setVisible(is_admin)
        self.suppliers_tile.setVisible(is_admin)
        self.employees_tile.setVisible(is_admin)
        self.reports_tile.setVisible(is_admin)
    
    def refresh_data(self):
        """Refresh all dashboard data from the database."""
        
        try:
            # Load recent sales
            self._load_recent_sales()
            
            # Load low stock items
            self._load_low_stock_items()
            
            # Load statistics
            self._load_statistics()
        
        except Exception as e:
            report_error("Dashboard Data Load Error", e, self)
    
    def _load_recent_sales(self):
        """Load the most recent sales into the table."""
        
        try:
            # Get recent sales (limit to 10)
            sales = SaleRepository.get_all()[:10]
            
            self.recent_sales_table.setRowCount(len(sales))
            
            for row, sale in enumerate(sales):
                # Load full sale details if not already loaded
                if not sale.details:
                    full_sale = SaleRepository.get_by_id(sale.invoice_no)
                    if full_sale:
                        sale = full_sale
                
                # Date
                date_item = QTableWidgetItem(
                    format_date(sale.sale_date) if sale.sale_date else ""
                )
                self.recent_sales_table.setItem(row, 0, date_item)
                
                # Customer (show ID or name if available)
                customer_text = str(sale.customer_id) if sale.customer_id else "Walk-in"
                customer_item = QTableWidgetItem(customer_text)
                self.recent_sales_table.setItem(row, 1, customer_item)
                
                # Items count - now showing actual count from details
                item_count = len(sale.details) if sale.details else 0
                items_item = QTableWidgetItem(str(item_count))
                self.recent_sales_table.setItem(row, 2, items_item)
                
                # Total
                total_item = QTableWidgetItem(
                    format_currency(sale.total_amount) if sale.total_amount else "Rs. 0.00"
                )
                total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.recent_sales_table.setItem(row, 3, total_item)
        
        except Exception as e:
            print(f"Error loading recent sales: {e}")
    
    def _load_low_stock_items(self):
        """Load low stock items into the table."""
        
        try:
            # Get low stock items
            low_stock_items = InventoryRepository.get_low_stock_items()
            
            self.low_stock_table.setRowCount(len(low_stock_items))
            self.low_stock_count = len(low_stock_items)
            
            for row, item in enumerate(low_stock_items):
                # Product name
                product_item = QTableWidgetItem(item.product_name or item.product_code)
                self.low_stock_table.setItem(row, 0, product_item)
                
                # Current quantity
                qty_item = QTableWidgetItem(str(item.current_stock))
                qty_item.setTextAlignment(Qt.AlignCenter)
                min_level = item.min_stock_level or 0
                if item.current_stock <= min_level // 2:
                    qty_item.setForeground(Qt.red)
                self.low_stock_table.setItem(row, 1, qty_item)
                
                # Min stock level
                min_item = QTableWidgetItem(str(min_level))
                min_item.setTextAlignment(Qt.AlignCenter)
                self.low_stock_table.setItem(row, 2, min_item)
            
            # Update the low stock card
            self.low_stock_card.set_value(str(self.low_stock_count))
        
        except Exception as e:
            print(f"Error loading low stock items: {e}")
    
    def _load_statistics(self):
        """Load dashboard statistics."""
        
        try:
            # Get total products count
            products = ProductRepository.get_all()
            self.products_card.set_value(str(len(products)))
            
            # Get today's sales total
            from datetime import date
            today = date.today()
            sales = SaleRepository.get_all()
            
            # Calculate today's sales total
            today_total = Decimal('0')
            for s in sales:
                if s.sale_date:
                    # sale_date is already a date object, no need to call .date()
                    sale_date = s.sale_date if isinstance(s.sale_date, date) else s.sale_date.date()
                    if sale_date == today:
                        today_total += (s.net_amount or s.total_amount or 0)
            
            self.today_sales_card.set_value(format_currency(today_total))
            
            # Customer count (exclude walk-in if needed)
            from repositories.customer_repository import CustomerRepository
            customers = CustomerRepository.get_all(include_walkin=False)
            self.customers_card.set_value(str(len(customers)))
        
        except Exception as e:
            print(f"Error loading statistics: {e}")
            import traceback
            traceback.print_exc()


# =============================================================================
# MODULE TEST
# =============================================================================

if __name__ == "__main__":
    """Test the dashboard view when running this module directly."""
    
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
    
    # Create dashboard
    dashboard = DashboardView()
    
    # Create a mock employee for testing
    mock_employee = Employee(
        employee_id=1,
        employee_name="Test Admin",
        username="admin",
        password_hash="",
        role="Admin",
        phone_number="555-0100",
        email="admin@store.com"
    )
    
    dashboard.set_user(mock_employee)
    
    def on_navigate(section):
        print(f"Navigate to: {section}")
    
    def on_logout():
        print("Logout requested")
    
    dashboard.navigate_to.connect(on_navigate)
    dashboard.logout_requested.connect(on_logout)
    
    dashboard.show()
    
    # Run application
    sys.exit(app.exec())
