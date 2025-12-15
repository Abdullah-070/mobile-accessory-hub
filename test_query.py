"""Test script to debug the product query issue"""
import sys
sys.path.insert(0, 'frontend')

from db import execute_query

# Test the exact query that's failing
sql = """
    SELECT 
        p.Product_Code, p.Subcat_ID, p.Product_Name, p.Brand, 
        p.Description, p.Cost_Price, p.Retail_Price, 
        p.Min_Stock_Level, p.Date_Added,
        s.Subcat_Name, c.Cat_Name,
        ISNULL(i.Current_Stock, 0) AS Current_Stock
    FROM PRODUCT p
    INNER JOIN SUBCATEGORY s ON p.Subcat_ID = s.Subcat_ID
    INNER JOIN CATEGORY c ON s.Cat_ID = c.Cat_ID
    LEFT JOIN INVENTORY i ON p.Product_Code = i.Product_Code
    WHERE p.Product_Code = ?
"""

product_code = 'PRD001'
print(f"Testing query with product_code: {product_code} (type: {type(product_code)})")

try:
    result = execute_query(sql, (product_code,), fetch='one')
    if result:
        print("SUCCESS! Product found:")
        print(f"  Product_Code: {result.Product_Code}")
        print(f"  Product_Name: {result.Product_Name}")
    else:
        print("No product found")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
