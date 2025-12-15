"""Check ALL column types in the actual database"""
import sys
sys.path.insert(0, 'frontend')

from db import execute_query

# Check column types for all ID columns
sql = """
SELECT 
    t.TABLE_NAME,
    c.COLUMN_NAME,
    c.DATA_TYPE,
    c.CHARACTER_MAXIMUM_LENGTH,
    c.NUMERIC_PRECISION
FROM INFORMATION_SCHEMA.TABLES t
INNER JOIN INFORMATION_SCHEMA.COLUMNS c ON t.TABLE_NAME = c.TABLE_NAME
WHERE c.COLUMN_NAME LIKE '%ID' OR c.COLUMN_NAME LIKE '%_Code'
ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION
"""

print("Checking all ID and Code column types in actual database:")
print("=" * 90)

try:
    results = execute_query(sql)
    for row in results:
        length = row.CHARACTER_MAXIMUM_LENGTH if row.CHARACTER_MAXIMUM_LENGTH else row.NUMERIC_PRECISION
        print(f"{row.TABLE_NAME:25} | {row.COLUMN_NAME:20} | {row.DATA_TYPE:15} | Length: {length}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
