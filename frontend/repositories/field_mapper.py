"""
=============================================================================
Field Mapper
=============================================================================
Purpose: Centralized mapping from DB column names to UI-expected attribute names.
Prevents AttributeError exceptions by ensuring consistent naming across the app.

Mapping Rules Applied:
- DB Product_Code -> product_code
- DB Cat_Name -> category_name  
- DB Subcat_Name -> subcategory_name
- DB Phone -> phone_number
- DB Contact_Person -> contact_person
- DB Min_Stock_Level -> min_stock_level
- DB Quantity_In_Stock -> quantity_in_stock
- All other fields: snake_case conversion

Why Changed: Eliminates runtime AttributeError exceptions from DB/UI naming mismatches.
=============================================================================
"""

from typing import Any, Dict
from decimal import Decimal
from datetime import date, datetime


def to_snake_case(name: str) -> str:
    """Convert PascalCase/camelCase to snake_case."""
    result = []
    for i, char in enumerate(name):
        if char.isupper() and i > 0:
            result.append('_')
        result.append(char.lower())
    return ''.join(result)


def map_row_to_dict(row: Any) -> Dict[str, Any]:
    """Convert a database row object to a dictionary with snake_case keys."""
    if row is None:
        return {}
    
    result = {}
    for column in row.__dir__():
        if not column.startswith('_'):
            value = getattr(row, column, None)
            snake_key = to_snake_case(column)
            result[snake_key] = value
    
    return result


def map_product(row: Any) -> Dict[str, Any]:
    """Map product database row to UI-expected format."""
    if row is None:
        return {}
    
    return {
        'product_code': getattr(row, 'Product_Code', None),
        'product_name': getattr(row, 'Product_Name', None),
        'description': getattr(row, 'Description', None),
        'category_id': getattr(row, 'Cat_ID', None),
        'subcategory_id': getattr(row, 'Subcat_ID', None),
        'brand': getattr(row, 'Brand', None),
        'model': getattr(row, 'Model', None),
        'color': getattr(row, 'Color', None),
        'unit_price': getattr(row, 'Unit_Price', None),
        'retail_price': getattr(row, 'Retail_Price', None),
        'category_name': getattr(row, 'Cat_Name', getattr(row, 'category_name', None)),
        'subcategory_name': getattr(row, 'Subcat_Name', getattr(row, 'subcategory_name', None)),
    }


def map_category(row: Any) -> Dict[str, Any]:
    """Map category database row to UI-expected format."""
    if row is None:
        return {}
    
    return {
        'category_id': getattr(row, 'Cat_ID', None),
        'category_name': getattr(row, 'Cat_Name', None),
        'description': getattr(row, 'Description', None),
    }


def map_subcategory(row: Any) -> Dict[str, Any]:
    """Map subcategory database row to UI-expected format."""
    if row is None:
        return {}
    
    return {
        'subcategory_id': getattr(row, 'Subcat_ID', None),
        'subcategory_name': getattr(row, 'Subcat_Name', None),
        'category_id': getattr(row, 'Cat_ID', None),
        'description': getattr(row, 'Description', None),
    }


def map_customer(row: Any) -> Dict[str, Any]:
    """Map customer database row to UI-expected format."""
    if row is None:
        return {}
    
    return {
        'customer_id': getattr(row, 'Customer_ID', None),
        'customer_name': getattr(row, 'Customer_Name', None),
        'phone_number': getattr(row, 'Phone', None),
        'phone': getattr(row, 'Phone', None),
        'email': getattr(row, 'Email', None),
        'address': getattr(row, 'Address', None),
        'city': getattr(row, 'City', None),
        'loyalty_points': getattr(row, 'Loyalty_Points', 0),
    }


def map_supplier(row: Any) -> Dict[str, Any]:
    """Map supplier database row to UI-expected format."""
    if row is None:
        return {}
    
    return {
        'supplier_id': getattr(row, 'Supplier_ID', None),
        'supplier_name': getattr(row, 'Supplier_Name', None),
        'contact_person': getattr(row, 'Contact_Person', None),
        'phone_number': getattr(row, 'Phone', None),
        'phone': getattr(row, 'Phone', None),
        'email': getattr(row, 'Email', None),
        'address': getattr(row, 'Address', None),
        'city': getattr(row, 'City', None),
    }


def map_inventory(row: Any) -> Dict[str, Any]:
    """Map inventory database row to UI-expected format."""
    if row is None:
        return {}
    
    return {
        'product_code': getattr(row, 'Product_Code', None),
        'product_id': getattr(row, 'Product_Code', None),  # Alias
        'product_name': getattr(row, 'Product_Name', None),
        'quantity_in_stock': getattr(row, 'Quantity_In_Stock', 0),
        'min_stock_level': getattr(row, 'Min_Stock_Level', 0),
        'last_restocked': getattr(row, 'Last_Restocked', None),
        'category_name': getattr(row, 'Cat_Name', None),
        'subcategory_name': getattr(row, 'Subcat_Name', None),
    }


def map_employee(row: Any) -> Dict[str, Any]:
    """Map employee database row to UI-expected format."""
    if row is None:
        return {}
    
    return {
        'employee_id': getattr(row, 'Employee_ID', None),
        'employee_name': getattr(row, 'Employee_Name', None),
        'phone_number': getattr(row, 'Phone', None),
        'phone': getattr(row, 'Phone', None),
        'email': getattr(row, 'Email', None),
        'position': getattr(row, 'Position', None),
        'hire_date': getattr(row, 'Hire_Date', None),
        'salary': getattr(row, 'Salary', None),
        'username': getattr(row, 'Username', None),
        'password_hash': getattr(row, 'password_hash', None),
        'role': getattr(row, 'role', 'Employee'),
    }
