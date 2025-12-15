"""Test the exact BASE_SELECT query"""
import sys
sys.path.insert(0, 'frontend')

from db import execute_query

# Test with the exact query from the repository
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
print(f"Testing with product_code: '{product_code}'")
print(f"Type: {type(product_code)}")
print(f"Parameter tuple: {(product_code,)}")
print("-" * 70)

try:
    print("Executing query...")
    row = execute_query(sql, (product_code,), fetch='one')
    if row:
        print("SUCCESS!")
        print(f"Product_Code: {row.Product_Code}")
        print(f"Product_Name: {row.Product_Name}")
        print(f"Subcat_ID: {row.Subcat_ID}")
    else:
        print("No result returned")
except Exception as e:
    print(f"ERROR OCCURRED:")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print()
    import traceback
    traceback.print_exc()
