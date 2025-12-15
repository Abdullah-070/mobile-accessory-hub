"""
=============================================================================
Views Package - __init__.py
=============================================================================
This package contains all the UI views/screens for the application.

Views:
    - RoleSelectionView: Initial role selection (Admin/Employee)
    - RoleLoginView: Role-specific login screen
    - RoleSignupView: Role-specific signup screen
    - DashboardView: Main dashboard with navigation and stats
    - ProductListView: Product listing with search and filters
    - ProductFormView: Add/edit product form
    - SalePOSView: Point of sale interface
    - PurchaseFormView: Create purchase orders
    - InventoryView: Inventory management
    - CustomerView: Customer CRUD
    - SupplierView: Supplier CRUD
    - EmployeeView: Employee CRUD (Admin only)
    - ReportsView: Sales and inventory reports

=============================================================================
"""

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
from views.main_window import MainWindow

__all__ = [
    'RoleSelectionView',
    'RoleLoginView',
    'RoleSignupView',
    'DashboardView',
    'ProductListView',
    'ProductFormView',
    'SalePOSView',
    'SaleView',
    'InventoryView',
    'CustomerView',
    'SupplierView',
    'EmployeeView',
    'MainWindow',
]
