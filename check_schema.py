"""Check actual database schema for Product_Code column type"""
import sys
sys.path.insert(0, 'frontend')

from db import execute_query

# Check the actual column type in the database
sql = """
SELECT 
    c.TABLE_NAME,
    c.COLUMN_NAME,
    c.DATA_TYPE,
    c.CHARACTER_MAXIMUM_LENGTH
FROM INFORMATION_SCHEMA.COLUMNS c
WHERE c.COLUMN_NAME = 'Product_Code'
ORDER BY c.TABLE_NAME
"""

print("Checking Product_Code column types in database:")
print("-" * 70)

try:
    results = execute_query(sql)
    for row in results:
        print(f"Table: {row.TABLE_NAME:20} | Column: {row.COLUMN_NAME:15} | Type: {row.DATA_TYPE:15} | Max Length: {row.CHARACTER_MAXIMUM_LENGTH}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
