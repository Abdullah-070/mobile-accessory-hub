"""
=============================================================================
Smoke Check Script
=============================================================================
Quick validation script to test repository fetch operations.

Run this after making changes to verify basic functionality:
    python scripts/smoke_check.py

Tests:
    - Product fetch
    - Customer fetch
    - Supplier fetch
    - Inventory fetch
    - Category fetch

=============================================================================
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Tuple


def test_database_connection() -> Tuple[bool, str]:
    """Test database connectivity."""
    try:
        import db
        conn = db.get_connection()
        conn.close()
        return True, "Database connection successful"
    except Exception as e:
        return False, f"Database connection failed: {str(e)}"


def test_product_fetch() -> Tuple[bool, str]:
    """Test fetching products."""
    try:
        from repositories.product_repository import ProductRepository
        products = ProductRepository.get_all()
        if products:
            p = products[0]
            # Test attribute access
            _ = p.product_code
            _ = p.product_name
            _ = p.product_id  # Alias
            _ = p.price  # Alias
            return True, f"Products: {len(products)} loaded. First: {p.product_name}"
        return True, "Products: 0 loaded (empty table)"
    except Exception as e:
        return False, f"Product fetch failed: {str(e)}"


def test_customer_fetch() -> Tuple[bool, str]:
    """Test fetching customers."""
    try:
        from repositories.customer_repository import CustomerRepository
        customers = CustomerRepository.get_all()
        if customers:
            c = customers[0]
            # Test attribute access
            _ = c.customer_id
            _ = c.customer_name
            _ = c.phone
            _ = c.phone_number  # Alias
            return True, f"Customers: {len(customers)} loaded. First: {c.customer_name}"
        return True, "Customers: 0 loaded (empty table)"
    except Exception as e:
        return False, f"Customer fetch failed: {str(e)}"


def test_supplier_fetch() -> Tuple[bool, str]:
    """Test fetching suppliers."""
    try:
        from repositories.supplier_repository import SupplierRepository
        suppliers = SupplierRepository.get_all()
        if suppliers:
            s = suppliers[0]
            # Test attribute access
            _ = s.supplier_id
            _ = s.supplier_name
            _ = s.contact_person
            _ = s.contact_name  # Alias
            _ = s.phone
            _ = s.phone_number  # Alias
            return True, f"Suppliers: {len(suppliers)} loaded. First: {s.supplier_name}"
        return True, "Suppliers: 0 loaded (empty table)"
    except Exception as e:
        return False, f"Supplier fetch failed: {str(e)}"


def test_inventory_fetch() -> Tuple[bool, str]:
    """Test fetching inventory."""
    try:
        from repositories.inventory_repository import InventoryRepository
        inventory = InventoryRepository.get_all()
        if inventory:
            i = inventory[0]
            # Test attribute access
            _ = i.product_code
            _ = i.current_stock
            _ = i.is_low_stock
            return True, f"Inventory: {len(inventory)} items. First: {i.product_code} ({i.current_stock} in stock)"
        return True, "Inventory: 0 items (empty table)"
    except Exception as e:
        return False, f"Inventory fetch failed: {str(e)}"


def test_category_fetch() -> Tuple[bool, str]:
    """Test fetching categories."""
    try:
        from repositories.category_repository import CategoryRepository
        categories = CategoryRepository.get_all()
        if categories:
            c = categories[0]
            # Test attribute access
            _ = c.cat_id
            _ = c.cat_name
            return True, f"Categories: {len(categories)} loaded. First: {c.cat_name}"
        return True, "Categories: 0 loaded (empty table)"
    except Exception as e:
        return False, f"Category fetch failed: {str(e)}"


def run_smoke_tests():
    """Run all smoke tests and report results."""
    
    print("=" * 60)
    print("SMOKE CHECK - Mobile Accessory Inventory System")
    print("=" * 60)
    print()
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Product Repository", test_product_fetch),
        ("Customer Repository", test_customer_fetch),
        ("Supplier Repository", test_supplier_fetch),
        ("Inventory Repository", test_inventory_fetch),
        ("Category Repository", test_category_fetch),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        success, message = test_func()
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        print(f"       {message}")
        print()
        
        if success:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_smoke_tests()
    sys.exit(0 if success else 1)
