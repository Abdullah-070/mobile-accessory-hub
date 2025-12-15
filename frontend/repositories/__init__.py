"""
=============================================================================
Repository Modules - __init__.py
=============================================================================
This package contains repository classes that encapsulate all database
operations for each entity in the Mobile Accessory Inventory System.

The repository pattern separates data access logic from business logic,
making the code more maintainable and testable.

Repositories:
    - CategoryRepository: CRUD for product categories
    - SubcategoryRepository: CRUD for product subcategories
    - ProductRepository: CRUD for products
    - InventoryRepository: Read/update inventory levels
    - SupplierRepository: CRUD for suppliers
    - CustomerRepository: CRUD for customers
    - EmployeeRepository: CRUD for employees with authentication
    - PurchaseRepository: Create purchases using stored procedure
    - SaleRepository: Create sales using stored procedure
    - PaymentRepository: CRUD for payments

Usage:
    from repositories import ProductRepository, SaleRepository
    
    # Get all products
    products = ProductRepository.get_all()
    
    # Create a sale
    result = SaleRepository.create_sale(...)

=============================================================================
"""

from repositories.category_repository import CategoryRepository
from repositories.subcategory_repository import SubcategoryRepository
from repositories.product_repository import ProductRepository
from repositories.inventory_repository import InventoryRepository
from repositories.supplier_repository import SupplierRepository
from repositories.customer_repository import CustomerRepository
from repositories.employee_repository import EmployeeRepository
from repositories.purchase_repository import PurchaseRepository
from repositories.sale_repository import SaleRepository
from repositories.payment_repository import PaymentRepository

__all__ = [
    'CategoryRepository',
    'SubcategoryRepository',
    'ProductRepository',
    'InventoryRepository',
    'SupplierRepository',
    'CustomerRepository',
    'EmployeeRepository',
    'PurchaseRepository',
    'SaleRepository',
    'PaymentRepository'
]
