# COPILOT_MODIFIED: true  # 2025-12-09T15:20:00Z
"""
=============================================================================
Main Window
=============================================================================
This module provides the main application window that contains all views.

Features:
    - Central stacked widget for view switching
    - Navigation sidebar
    - View management (create, show, hide)
    - Authentication state management
    - Global keyboard shortcuts

=============================================================================
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QPushButton, QFrame, QLabel, QMessageBox, QSizePolicy, QSpacerItem
)
import os
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QKeySequence, QShortcut, QCloseEvent, QIcon

from repositories.employee_repository import Employee
from views.role_selection_view import RoleSelectionView
from views.role_login_view import RoleLoginView
from views.role_signup_view import RoleSignupView
from views.dashboard_view import DashboardView
from views.product_list_view import ProductListView
from views.product_form_view import ProductFormView
from views.sale_pos_view import SalePOSView
from views.sale_view import SaleView
from views.inventory_view import InventoryView
from views.customer_view import CustomerView
from views.supplier_view import SupplierView
from views.employee_view import EmployeeView
from views.purchase_view import PurchaseView
from views.report_view import ReportView


class NavButton(QPushButton):
    """Navigation sidebar button with icon and text."""
    
    def __init__(self, icon: str, text: str, parent=None):
        super().__init__(f"{icon}  {text}", parent)
        
        self.setProperty("class", "nav")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(45)
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)


class MainWindow(QMainWindow):
    """
    Main application window.
    
    Manages all views and navigation between them.
    Handles authentication state and role-based access.
    """
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Current user
        self.current_user: Employee = None
        
        # View references
        self.role_selection_view: RoleSelectionView = None
        self.admin_login_view: RoleLoginView = None
        self.admin_signup_view: RoleSignupView = None
        self.employee_login_view: RoleLoginView = None
        # Note: employee_signup_view removed - only admins create employee accounts
        self.dashboard_view: DashboardView = None
        self.product_list_view: ProductListView = None
        self.product_form_view: ProductFormView = None
        self.pos_view: SalePOSView = None
        self.inventory_view: InventoryView = None
        self.customer_view: CustomerView = None
        self.supplier_view: SupplierView = None
        self.employee_view: EmployeeView = None
        
        # Navigation buttons
        self.nav_buttons = {}
        
        # Set up window
        self._setup_window()
        
        # Create main layout
        self._setup_main_layout()
        
        # Create views
        self._create_views()
        
        # Connect signals
        self._connect_signals()
        
        # Set up shortcuts
        self._setup_shortcuts()
        
        # Show login initially
        self._show_login()
    
    def _setup_window(self):
        """Configure window properties."""
        
        self.setWindowTitle("Mobile Accessory Inventory Management System")
        self.setMinimumSize(1200, 800)
        
        # Set application icon (appears in taskbar, window, and shortcuts)
        try:
            icon_path = os.path.join(
                os.path.dirname(__file__), 
                "..", "assets", "app_icon.ico"
            )
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            print(f"Warning: Could not load icon: {e}")
        
        # Start maximized
        self.showMaximized()
    
    def _setup_main_layout(self):
        """Set up the main layout structure."""
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # =====================================================================
        # SIDEBAR (Navigation)
        # =====================================================================
        
        self.sidebar = QFrame()
        self.sidebar.setProperty("class", "sidebar")
        self.sidebar.setFixedWidth(220)
        self.sidebar.setVisible(False)  # Hidden until login
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(5)
        
        # Logo/Brand
        brand_label = QLabel("📱 Mobile Accessory")
        brand_font = QFont()
        brand_font.setPointSize(12)
        brand_font.setBold(True)
        brand_label.setFont(brand_font)
        brand_label.setStyleSheet("color: white; padding: 10px;")
        brand_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(brand_label)
        
        sidebar_layout.addSpacing(20)
        
        # Navigation buttons
        self.nav_dashboard = NavButton("🏠", "Dashboard")
        self.nav_buttons["dashboard"] = self.nav_dashboard
        sidebar_layout.addWidget(self.nav_dashboard)
        
        self.nav_pos = NavButton("💳", "POS")
        self.nav_buttons["pos"] = self.nav_pos
        sidebar_layout.addWidget(self.nav_pos)
        
        self.nav_products = NavButton("📦", "Products")
        self.nav_buttons["products"] = self.nav_products
        sidebar_layout.addWidget(self.nav_products)
        
        self.nav_inventory = NavButton("📊", "Inventory")
        self.nav_buttons["inventory"] = self.nav_inventory
        sidebar_layout.addWidget(self.nav_inventory)
        
        self.nav_sales = NavButton("💰", "Sales")
        self.nav_buttons["sales"] = self.nav_sales
        sidebar_layout.addWidget(self.nav_sales)
        
        self.nav_purchases = NavButton("📥", "Purchases")
        self.nav_buttons["purchases"] = self.nav_purchases
        sidebar_layout.addWidget(self.nav_purchases)
        
        sidebar_layout.addSpacing(10)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #455A64;")
        separator.setFixedHeight(1)
        sidebar_layout.addWidget(separator)
        
        sidebar_layout.addSpacing(10)
        
        self.nav_customers = NavButton("👥", "Customers")
        self.nav_buttons["customers"] = self.nav_customers
        sidebar_layout.addWidget(self.nav_customers)
        
        self.nav_suppliers = NavButton("🏭", "Suppliers")
        self.nav_buttons["suppliers"] = self.nav_suppliers
        sidebar_layout.addWidget(self.nav_suppliers)
        
        self.nav_employees = NavButton("👤", "Employees")
        self.nav_buttons["employees"] = self.nav_employees
        sidebar_layout.addWidget(self.nav_employees)
        
        self.nav_reports = NavButton("📈", "Reports")
        self.nav_buttons["reports"] = self.nav_reports
        sidebar_layout.addWidget(self.nav_reports)
        
        # Spacer
        sidebar_layout.addStretch()
        
        # User info at bottom
        self.user_frame = QFrame()
        user_layout = QVBoxLayout(self.user_frame)
        user_layout.setContentsMargins(5, 10, 5, 10)
        
        self.user_name_label = QLabel("User Name")
        self.user_name_label.setStyleSheet("color: white; font-weight: bold;")
        user_layout.addWidget(self.user_name_label)
        
        self.user_role_label = QLabel("Role")
        self.user_role_label.setStyleSheet("color: #B0BEC5; font-size: 9pt;")
        user_layout.addWidget(self.user_role_label)
        
        self.logout_button = QPushButton("🚪 Logout")
        self.logout_button.setStyleSheet("""
            QPushButton {
                background-color: #455A64;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #546E7A;
            }
        """)
        self.logout_button.setCursor(Qt.PointingHandCursor)
        user_layout.addWidget(self.logout_button)
        
        sidebar_layout.addWidget(self.user_frame)
        
        main_layout.addWidget(self.sidebar)
        
        # =====================================================================
        # CONTENT AREA (Stacked Widget)
        # =====================================================================
        
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)
    
    def _create_views(self):
        """Create and add all views to the stack."""
        
        # Role selection view (initial)
        self.role_selection_view = RoleSelectionView()
        self.content_stack.addWidget(self.role_selection_view)
        
        # Admin login/signup views
        self.admin_login_view = RoleLoginView("Admin")
        self.content_stack.addWidget(self.admin_login_view)
        
        self.admin_signup_view = RoleSignupView("Admin")
        self.content_stack.addWidget(self.admin_signup_view)
        
        # Employee login view (no signup - admin creates employees)
        self.employee_login_view = RoleLoginView("Employee")
        self.content_stack.addWidget(self.employee_login_view)
        
        # Dashboard view
        self.dashboard_view = DashboardView()
        self.content_stack.addWidget(self.dashboard_view)
        
        # Product list view
        self.product_list_view = ProductListView()
        self.content_stack.addWidget(self.product_list_view)
        
        # POS view (created without user, will be set after login)
        self.pos_view = SalePOSView()
        self.content_stack.addWidget(self.pos_view)
        
        # Inventory view
        self.inventory_view = InventoryView()
        self.content_stack.addWidget(self.inventory_view)
        
        # Customer view
        self.customer_view = CustomerView()
        self.content_stack.addWidget(self.customer_view)
        
        # Supplier view
        self.supplier_view = SupplierView()
        self.content_stack.addWidget(self.supplier_view)
        
        # Employee view (will set current_user after login)
        self.employee_view = EmployeeView()
        self.content_stack.addWidget(self.employee_view)
        
        # Purchase view
        self.purchase_view = PurchaseView()
        self.content_stack.addWidget(self.purchase_view)
        
        # Sale view (for viewing sales history/reports)
        self.sale_view = SaleView()
        self.content_stack.addWidget(self.sale_view)
        
        # Report view (for profit/revenue reports)
        self.report_view = ReportView()
        self.content_stack.addWidget(self.report_view)
    
    def _connect_signals(self):
        """Connect all signals."""
        
        # Role selection
        self.role_selection_view.admin_login_requested.connect(self._show_admin_login)
        self.role_selection_view.admin_signup_requested.connect(self._show_admin_signup)
        self.role_selection_view.employee_login_requested.connect(self._show_employee_login)
        
        # Admin login/signup
        self.admin_login_view.login_successful.connect(self._on_login_success)
        self.admin_login_view.back_requested.connect(self._show_role_selection)
        self.admin_signup_view.signup_successful.connect(self._on_signup_success)
        self.admin_signup_view.back_requested.connect(self._show_role_selection)
        
        # Employee login
        self.employee_login_view.login_successful.connect(self._on_login_success)
        self.employee_login_view.back_requested.connect(self._show_role_selection)
        
        # Dashboard
        self.dashboard_view.navigate_to.connect(self._navigate_to)
        self.dashboard_view.logout_requested.connect(self._logout)
        
        # Sidebar navigation
        self.nav_dashboard.clicked.connect(lambda: self._navigate_to("dashboard"))
        self.nav_pos.clicked.connect(lambda: self._navigate_to("pos"))
        self.nav_products.clicked.connect(lambda: self._navigate_to("products"))
        self.nav_inventory.clicked.connect(lambda: self._navigate_to("inventory"))
        self.nav_sales.clicked.connect(lambda: self._navigate_to("sales"))
        self.nav_purchases.clicked.connect(lambda: self._navigate_to("purchases"))
        self.nav_customers.clicked.connect(lambda: self._navigate_to("customers"))
        self.nav_suppliers.clicked.connect(lambda: self._navigate_to("suppliers"))
        self.nav_employees.clicked.connect(lambda: self._navigate_to("employees"))
        self.nav_reports.clicked.connect(lambda: self._navigate_to("reports"))
        
        # Logout button
        self.logout_button.clicked.connect(self._logout)
        
        # Product views
        self.product_list_view.add_product_requested.connect(self._show_product_form_add)
        self.product_list_view.edit_product_requested.connect(self._show_product_form_edit)
        
        # POS view
        self.pos_view.navigate_back.connect(lambda: self._navigate_to("dashboard"))
        self.pos_view.sale_completed.connect(self._on_sale_completed)
        
        # Sale view
        self.sale_view.navigate_back.connect(lambda: self._navigate_to("dashboard"))
    
    def _setup_shortcuts(self):
        """Set up global keyboard shortcuts."""
        
        # F5: Refresh current view
        shortcut_refresh = QShortcut(QKeySequence("F5"), self)
        shortcut_refresh.activated.connect(self._refresh_current_view)
        
        # Ctrl+H: Go to dashboard
        shortcut_home = QShortcut(QKeySequence("Ctrl+H"), self)
        shortcut_home.activated.connect(lambda: self._navigate_to("dashboard"))
        
        # Ctrl+P: Go to POS
        shortcut_pos = QShortcut(QKeySequence("Ctrl+Shift+P"), self)
        shortcut_pos.activated.connect(lambda: self._navigate_to("pos"))
    
    def _show_login(self):
        """Show the role selection view."""
        self._show_role_selection()
    
    def _show_role_selection(self):
        """Show the role selection view."""
        self.sidebar.setVisible(False)
        self.content_stack.setCurrentWidget(self.role_selection_view)
    
    def _show_admin_login(self):
        """Show admin login view."""
        self.admin_login_view.clear_form()
        self.content_stack.setCurrentWidget(self.admin_login_view)
    
    def _show_admin_signup(self):
        """Show admin signup view."""
        self.admin_signup_view.clear_form()
        self.content_stack.setCurrentWidget(self.admin_signup_view)
    
    def _show_employee_login(self):
        """Show employee login view."""
        self.employee_login_view.clear_form()
        self.content_stack.setCurrentWidget(self.employee_login_view)
    
    def _on_signup_success(self, message: str):
        """Handle successful signup."""
        QMessageBox.information(self, "Success", message)
        self._show_role_selection()
    
    def _on_login_success(self, employee: Employee):
        """Handle successful login."""
        
        self.current_user = employee
        
        # Update user info in sidebar
        self.user_name_label.setText(employee.employee_name)
        self.user_role_label.setText(employee.role)
        
        # Set user for views that need it
        self.dashboard_view.set_user(employee)
        self.pos_view.current_user = employee
        
        # Apply role-based restrictions
        self._apply_role_restrictions()
        
        # Show sidebar and dashboard
        self.sidebar.setVisible(True)
        self._navigate_to("dashboard")
    
    def _apply_role_restrictions(self):
        """Apply UI restrictions based on user role."""
        
        if self.current_user is None:
            return
        
        is_admin = self.current_user.role.lower() == "admin"
        
        # POS is for employees only
        self.nav_pos.setVisible(not is_admin)
        
        # Admin-only navigation items
        self.nav_products.setVisible(is_admin)
        self.nav_sales.setVisible(is_admin)
        self.nav_purchases.setVisible(is_admin)
        self.nav_employees.setVisible(is_admin)
        self.nav_suppliers.setVisible(is_admin)
        self.nav_reports.setVisible(is_admin)
    
    def _navigate_to(self, section: str):
        """
        Navigate to a specific section.
        
        Args:
            section: Section name to navigate to
        """
        # Update nav button states
        for name, button in self.nav_buttons.items():
            button.setChecked(name == section)
        
        # Show appropriate view
        if section == "dashboard":
            self.content_stack.setCurrentWidget(self.dashboard_view)
            self.dashboard_view.refresh_data()
        
        elif section == "pos":
            self.content_stack.setCurrentWidget(self.pos_view)
            self.pos_view.refresh_data()  # Ensure products are loaded
        
        elif section == "products":
            self.content_stack.setCurrentWidget(self.product_list_view)
            self.product_list_view.refresh_data()
        
        elif section == "inventory":
            self.content_stack.setCurrentWidget(self.inventory_view)
            self.inventory_view.refresh_data()
        
        elif section == "customers":
            self.content_stack.setCurrentWidget(self.customer_view)
            self.customer_view.refresh_data()
        
        elif section == "suppliers":
            self.content_stack.setCurrentWidget(self.supplier_view)
            self.supplier_view.refresh_data()
        
        elif section == "employees":
            self.employee_view.current_user = self.current_user
            self.content_stack.setCurrentWidget(self.employee_view)
            self.employee_view.refresh_data()
        
        elif section == "purchases":
            self.content_stack.setCurrentWidget(self.purchase_view)
            self.purchase_view._load_purchases()
        
        elif section == "sales":
            self.content_stack.setCurrentWidget(self.sale_view)
            self.sale_view.refresh_data()
        
        elif section == "reports":
            self.content_stack.setCurrentWidget(self.report_view)
            self.report_view.refresh_data()
        
        else:
            # Default to dashboard
            self._navigate_to("dashboard")
    
    def _show_product_form_add(self):
        """Show the product form for adding a new product."""
        
        # Check if current user is admin
        is_admin = self.current_user and self.current_user.role.lower() == "admin"
        
        # Create new form for adding
        self.product_form_view = ProductFormView(product_id=None, is_admin=is_admin)
        self.product_form_view.saved.connect(self._on_product_saved)
        self.product_form_view.cancelled.connect(self._on_product_form_cancelled)
        
        # Replace in stack or add if not present
        self.content_stack.addWidget(self.product_form_view)
        self.content_stack.setCurrentWidget(self.product_form_view)
    
    def _show_product_form_edit(self, product_code: str):
        """Show the product form for editing an existing product."""
        
        # Check if current user is admin
        is_admin = self.current_user and self.current_user.role.lower() == "admin"
        
        # Create form for editing
        self.product_form_view = ProductFormView(product_id=product_code, is_admin=is_admin)
        self.product_form_view.saved.connect(self._on_product_saved)
        self.product_form_view.cancelled.connect(self._on_product_form_cancelled)
        
        self.content_stack.addWidget(self.product_form_view)
        self.content_stack.setCurrentWidget(self.product_form_view)
    
    def _on_product_saved(self):
        """Handle product saved event."""
        # Remove form from stack
        if self.product_form_view:
            self.content_stack.removeWidget(self.product_form_view)
            self.product_form_view.deleteLater()
            self.product_form_view = None
        
        # Return to product list
        self._navigate_to("products")
    
    def _on_product_form_cancelled(self):
        """Handle product form cancelled event."""
        # Remove form from stack
        if self.product_form_view:
            self.content_stack.removeWidget(self.product_form_view)
            self.product_form_view.deleteLater()
            self.product_form_view = None
        
        # Return to product list
        self._navigate_to("products")
    
    def _on_sale_completed(self, sale_id: int):
        """Handle sale completed event."""
        # Could show receipt or navigate somewhere
        pass
    
    def _refresh_current_view(self):
        """Refresh the current view's data."""
        
        current = self.content_stack.currentWidget()
        
        if hasattr(current, 'refresh_data'):
            current.refresh_data()
    
    def _logout(self):
        """Log out the current user."""
        
        reply = QMessageBox.question(
            self, "Logout",
            "Are you sure you want to log out?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.current_user = None
            self._show_login()
    
    def closeEvent(self, event: QCloseEvent):
        """Handle window close event."""
        
        if self.current_user is not None:
            reply = QMessageBox.question(
                self, "Exit",
                "Are you sure you want to exit the application?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


# =============================================================================
# MODULE TEST
# =============================================================================

if __name__ == "__main__":
    """Test the main window when running this module directly."""
    
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
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())
